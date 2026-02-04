import os
import time
from src.downloader import download_audio
from src.audio_processor import AudioProcessor
from src.note_generation_service import NoteGenerationService
from src.cleanup_service import FileCleanupService
from src.gemini_api_wrapper import GeminiAPIWrapper
from src.prompts import TRANSCRIPTION_PROMPT

class ProcessingPipeline:
    def __init__(self, config_manager):
        self.config = config_manager

    def execute_job(self, job) -> bool:
        """
        Executes the full pipeline for a single job.
        """
        api = GeminiAPIWrapper()
        api.key_manager.reset_quotas_if_needed()
        
        audio_path = None
        chunks = []
        transcript_path = None
        notes_path = None
        
        try:
            # 1. Download
            print(f"📥 [1/4] Downloading audio for: {job['name']}...")
            job['status'] = 'downloading'
            audio_path = download_audio(job)
            if not audio_path or not os.path.exists(audio_path):
                print(f"❌ Download failed or file missing for job: {job['name']}")
                job['status'] = 'failed'
                return False

            # 2. Audio Processing
            print(f"✂️ [2/4] Checking size and splitting audio: {audio_path}")
            job['status'] = 'processing'
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)
                
            segment_time = self.config.get("segment_time", 1800)
            
            # Map performance profile to thread count
            profile = self.config.get("performance_profile", "balanced")
            threads = 0 # Default (auto)
            if profile == "low":
                threads = 1 # Force single thread for low-end
            elif profile == "high":
                threads = 0 # Ffmpeg auto uses all cores
                
            chunks = AudioProcessor.process_for_transcription(
                audio_path, 
                segment_time=segment_time,
                output_dir=temp_dir,
                threads=threads
            )
            print(f"   - Audio split into {len(chunks)} chunk(s).")
            
            # 3. Transcription
            print(f"📝 [3/4] Transcribing {len(chunks)} chunks using Gemini...")
            transcript_path = os.path.join(temp_dir, f"{job['id']}_transcript.txt")
            
            # Implementation of 10s wait before chunks
            out_dir = os.path.dirname(transcript_path)
            if out_dir and not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)
            if os.path.exists(transcript_path):
                os.remove(transcript_path)

            any_success = False
            for i, chunk in enumerate(chunks):
                if i > 0:
                    print(f"      - Waiting 10s before next chunk...")
                    time.sleep(10)
                
                print(f"      - Processing chunk {i+1}/{len(chunks)}...")
                try:
                    text = api.generate_content_with_file(
                        file_path=chunk,
                        prompt=TRANSCRIPTION_PROMPT,
                        model_type="transcription"
                    )
                    if text:
                        with open(transcript_path, 'a', encoding='utf-8') as f:
                            f.write(text)
                            f.write("\n\n")
                        any_success = True
                    else:
                        print(f"      ⚠️ Warning: No text extracted from chunk {i+1}")
                        job['status'] = 'failed'
                        return False
                except Exception as e:
                    print(f"      ❌ Failed to get transcription for chunk {i+1}: {str(e)}")
                    job['status'] = 'failed'
                    return False

            if not any_success:
                print(f"❌ Transcription failed for job: {job['name']}")
                job['status'] = 'failed'
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
                job['status'] = 'failed'
                return False
            print(f"   - Notes generated: {final_notes_path}")

            # 5. Cleanup
            print(f"🧹 Cleaning up intermediate files...")
            files_to_cleanup = [audio_path, transcript_path]
            for c in chunks:
                if c != audio_path:
                    files_to_cleanup.append(c)
            FileCleanupService.cleanup_job_files(files_to_cleanup)
            
            job['status'] = 'completed'
            print(f"✅ Job '{job['name']}' completed successfully! Notes: {final_notes_path}")
            return True

        except Exception as e:
            print(f"❌ Exception in pipeline for job {job['id']}: {e}")
            job['status'] = 'failed'
            # Cleanup whatever we can on failure
            files_to_cleanup = [audio_path, transcript_path]
            if chunks:
                for c in chunks:
                    if c != audio_path:
                        files_to_cleanup.append(c)
            FileCleanupService.cleanup_job_files(files_to_cleanup)
            return False
