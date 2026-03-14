import os
import time
import shutil
from src.downloader import download_audio, get_expected_audio_path
from src.audio_processor import AudioProcessor
from src.note_generation_service import NoteGenerationService
from src.cleanup_service import FileCleanupService
from src.gemini_api_wrapper import GeminiAPIWrapper
from src.prompts import TRANSCRIPTION_PROMPT
from src.job_manager import JobManager
from src.notion_service import NotionService
from src.notion_config_manager import NotionConfigManager

class ProcessingPipeline:
    def __init__(self, config_manager, api_wrapper=None, job_manager=None):
        self.config = config_manager
        self.manager = job_manager or JobManager()
        self.api = api_wrapper or GeminiAPIWrapper()
        self.notion_config = NotionConfigManager()

    def execute_job(self, job) -> bool:
        """
        Executes the full pipeline for a single job with resumption support.
        Supports both URL-based and local file-based jobs.
        """
        
        audio_path = None
        chunks = []
        transcript_path = None
        notes_path = None
        
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)

        try:
            # 1. Source Acquisition (Download or Local)
            is_local = "file_path" in job
            
            if is_local:
                audio_path = job["file_path"]
                if not os.path.exists(audio_path):
                    print(f"❌ Local file missing: {audio_path}")
                    self.manager.update_job_status(job['id'], 'failed')
                    return False
                print(f"📂 [1/4] Using local file: {audio_path}")
                # Ensure status is at least DOWNLOADED for local files to enter next step
                if job.get('status') == 'queue' or job.get('status') == 'downloading':
                    job['status'] = 'DOWNLOADED'
                    self.manager.update_job_status(job['id'], 'DOWNLOADED')
            else:
                # URL-based: 1. Download
                audio_path = get_expected_audio_path(job)
                skip_download = False
                ready_states = ['DOWNLOADED', 'SILENCE_REMOVED', 'BITRATE_MODIFIED', 'CHUNKED']
                if job.get('status') in ready_states or job.get('status', '').startswith('TRANSCRIBING_CHUNK_'):
                    if os.path.exists(audio_path):
                        print(f"⏩ Skipping download: {audio_path} already exists.")
                        skip_download = True
                elif os.path.exists(audio_path):
                    print(f"⏩ Audio file {audio_path} already exists. Skipping download and setting status to DOWNLOADED.")
                    job['status'] = 'DOWNLOADED'
                    self.manager.update_job_status(job['id'], 'DOWNLOADED')
                    skip_download = True
                
                if not skip_download:
                    print(f"📥 [1/4] Downloading audio for: {job['name']}...")
                    self.manager.update_job_status(job['id'], 'downloading')
                    audio_path = download_audio(job)
                    if not audio_path or not os.path.exists(audio_path):
                        print(f"❌ Download failed or file missing for job: {job['name']}")
                        self.manager.update_job_status(job['id'], 'failed')
                        return False
                    self.manager.update_job_status(job['id'], 'DOWNLOADED')
                    job['status'] = 'DOWNLOADED'

            # 2. Audio Processing (Granular steps)
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            extension = os.path.splitext(audio_path)[1] or ".mp3"
            prepared_path = os.path.join(temp_dir, f"{base_name}_prepared{extension}")
            
            # 2.1 Silence Removal & Bitrate (Combined for simplicity in state)
            if job.get('status') == 'DOWNLOADED':
                print(f"✂️ [2/4] Processing audio (silence removal & bitrate): {audio_path}")
                if not os.path.exists(prepared_path):
                    silence_removed_path = prepared_path + ".nosilence" + extension
                    if AudioProcessor.remove_silence(audio_path, silence_removed_path):
                        if AudioProcessor.reencode_to_optimal(silence_removed_path, prepared_path):
                            self.manager.update_job_status(job['id'], 'BITRATE_MODIFIED')
                            job['status'] = 'BITRATE_MODIFIED'
                        else:
                            shutil.copy2(silence_removed_path, prepared_path)
                            self.manager.update_job_status(job['id'], 'BITRATE_MODIFIED')
                            job['status'] = 'BITRATE_MODIFIED'
                        try: os.remove(silence_removed_path)
                        except: pass
                    else:
                        if AudioProcessor.reencode_to_optimal(audio_path, prepared_path):
                            self.manager.update_job_status(job['id'], 'BITRATE_MODIFIED')
                            job['status'] = 'BITRATE_MODIFIED'
                        else:
                            shutil.copy2(audio_path, prepared_path)
                            self.manager.update_job_status(job['id'], 'BITRATE_MODIFIED')
                            job['status'] = 'BITRATE_MODIFIED'
                else:
                    print(f"⏩ Prepared audio already exists.")
                    self.manager.update_job_status(job['id'], 'BITRATE_MODIFIED')
                    job['status'] = 'BITRATE_MODIFIED'

            # 2.2 Chunking
            if job.get('status') == 'BITRATE_MODIFIED':
                chunks = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.startswith(f"job_{job['id']}_chunk_")])
                if not chunks:
                    print(f"✂️ Splitting audio into chunks based on size...")
                    max_size_mb = self.config.get("max_chunk_size_mb", 15)
                    output_pattern = os.path.join(temp_dir, f"job_{job['id']}_chunk_%03d{extension}")
                    
                    chunks = AudioProcessor.process_for_transcription(prepared_path, max_size_mb=max_size_mb, output_dir=temp_dir, output_pattern=output_pattern)
                    
                    if not chunks:
                        print(f"❌ Error: Size-based chunking failed to produce chunks for job {job['id']}")
                        self.manager.update_job_status(job['id'], 'failed')
                        return False

                    self.manager.update_job_status(job['id'], 'CHUNKED')
                    job['status'] = 'CHUNKED'
                else:
                    print(f"⏩ Skipping chunking: {len(chunks)} chunk(s) already exist.")
                    self.manager.update_job_status(job['id'], 'CHUNKED')
                    job['status'] = 'CHUNKED'
            
            # Re-verify chunks existence for next step (Transcription)
            if not chunks and (job.get('status') == 'CHUNKED' or job.get('status', '').startswith('TRANSCRIBING_CHUNK_')):
                chunks = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.startswith(f"job_{job['id']}_chunk_")])
            
            if not chunks and (job.get('status') == 'CHUNKED' or job.get('status', '').startswith('TRANSCRIBING_CHUNK_')):
                chunks = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.startswith(f"job_{job['id']}_chunk_")])
                if not chunks:
                    print(f"❌ Error: Status is {job['status']} but no chunks found for job {job['id']}")
                    self.manager.update_job_status(job['id'], 'failed')
                    return False

            # 3. Transcription
            print(f"📝 [3/4] Transcribing {len(chunks)} chunks using Gemini...")
            safe_name = job['name'].replace(" ", "_").replace("/", "-")
            transcript_path = os.path.join(temp_dir, f"{safe_name}_transcript.txt")
            
            # Ensure the directory for transcript exists
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)

            # Count existing chunks in the transcript file for resumption
            # Each chunk is separated by \n\n
            completed_chunks = 0
            if os.path.exists(transcript_path):
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Split by double newline and filter empty parts
                    completed_chunks = len([p for p in content.split("\n\n") if p.strip()])
            
            any_success = completed_chunks > 0

            for i, chunk in enumerate(chunks):
                chunk_index = i + 1
                if chunk_index <= completed_chunks:
                    print(f"      - Chunk {chunk_index}/{len(chunks)} already transcribed in {transcript_path}. Skipping.")
                    continue

                if any_success: # If we processed at least one chunk (resumed or new)
                    print(f"      - Waiting 10s before next chunk...")
                    time.sleep(10)
                
                print(f"      - Processing chunk {chunk_index}/{len(chunks)}...")
                self.manager.update_job_status(job['id'], f'TRANSCRIBING_CHUNK_{chunk_index}')
                try:
                    text = self.api.generate_content_with_file(
                        file_path=chunk,
                        prompt="Please transcribe this audio chunk.",
                        model_type="transcription",
                        system_instruction=TRANSCRIPTION_PROMPT
                    )
                    if text:
                        with open(transcript_path, 'a', encoding='utf-8') as f:
                            f.write(text)
                            f.write("\n\n")
                        any_success = True
                    else:
                        print(f"      ⚠️ Warning: No text extracted from chunk {chunk_index}")
                        self.manager.update_job_status(job['id'], 'failed')
                        return False
                except Exception as e:
                    print(f"      ❌ Failed to get transcription for chunk {chunk_index}: {str(e)}")
                    self.manager.update_job_status(job['id'], 'failed')
                    return False

            if not any_success:
                print(f"❌ Transcription failed for job: {job['name']}")
                self.manager.update_job_status(job['id'], 'failed')
                return False
            print(f"   - Transcription complete: {transcript_path}")

            # 4. Note Generation
            print(f"🗒️ [4/4] Generating study notes...")
            safe_name = job['name'].replace(" ", "_").replace("/", "-")
            notes_dir = "notes"
            if not os.path.exists(notes_dir):
                os.makedirs(notes_dir, exist_ok=True)
            
            final_notes_path = os.path.join(notes_dir, f"{safe_name}.md")
            
            if not NoteGenerationService.generate(transcript_path, final_notes_path):
                print(f"❌ Note generation failed for job: {job['name']}")
                self.manager.update_job_status(job['id'], 'failed')
                return False
            print(f"   - Notes generated: {final_notes_path}")

            # 5. Notion Integration (Post-generation)
            pushed_to_notion = False
            if self.config.get("notion_integration_enabled", False):
                print(f"🚀 [5/5] Pushing to Notion...")
                notion_secret, database_id = self.notion_config.get_credentials()
                
                if not notion_secret or not database_id:
                    print("⚠️ Notion credentials not configured. Skipping Notion push.")
                else:
                    try:
                        notion_service = NotionService(notion_secret, database_id)
                        
                        # Title: replace underscores with spaces, remove extension
                        title = os.path.splitext(os.path.basename(final_notes_path))[0].replace("_", " ")
                        
                        with open(final_notes_path, 'r', encoding='utf-8') as f:
                            markdown_content = f.read()
                        
                        url = notion_service.create_page(title, markdown_content)
                        if url:
                            print(f"✅ Successfully pushed to Notion: {url}")
                            pushed_to_notion = True
                        else:
                            print("❌ Notion push failed: No URL returned.")
                    except Exception as e:
                        print(f"❌ Notion push failed with exception: {e}")

            # 6. Cleanup
            print(f"🧹 Cleaning up intermediate files...")
            files_to_cleanup = [audio_path, transcript_path, prepared_path]
            for c in chunks:
                if c not in files_to_cleanup:
                    files_to_cleanup.append(c)
            
            # If successfully pushed to Notion, also cleanup the final md file
            if pushed_to_notion:
                files_to_cleanup.append(final_notes_path)
                self.manager.update_job_status(job['id'], 'completed')
                print(f"✅ Job '{job['name']}' completed and pushed to Notion!")
            else:
                if self.config.get("notion_integration_enabled", False):
                    # If enabled but failed, keep local file and mark specially
                    self.manager.update_job_status(job['id'], 'completed_local_only')
                    print(f"✅ Job '{job['name']}' completed locally (Notion push failed). Notes: {final_notes_path}")
                else:
                    self.manager.update_job_status(job['id'], 'completed')
                    print(f"✅ Job '{job['name']}' completed successfully! Notes: {final_notes_path}")

            FileCleanupService.cleanup_job_files(files_to_cleanup)
            return True

        except Exception as e:
            print(f"❌ Exception in pipeline for job {job['id']}: {e}")
            self.manager.update_job_status(job['id'], 'failed')
            return False
