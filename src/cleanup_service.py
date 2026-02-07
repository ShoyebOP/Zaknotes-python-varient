import os
import shutil

class FileCleanupService:
    @staticmethod
    def cleanup_job_files(files: list):
        """Deletes a list of files if they exist."""
        for f in files:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                    print(f"Cleanup: Deleted {f}")
                except Exception as e:
                    print(f"Cleanup: Failed to delete {f}: {e}")

    @staticmethod
    def cleanup_all_temp_files(temp_dir="temp", downloads_dir="downloads", jobs_to_purge=None):
        """
        Manually cleans up intermediate files.
        If jobs_to_purge is provided, only files related to those jobs are removed.
        Otherwise, everything is removed.
        """
        if jobs_to_purge is not None:
            # Targeted cleanup
            print(f"🧹 Purging files for {len(jobs_to_purge)} jobs...")
            for job in jobs_to_purge:
                # 1. Chunks in temp
                if os.path.exists(temp_dir):
                    for f in os.listdir(temp_dir):
                        if f.startswith(f"job_{job['id']}_") or f.startswith(f"{job['id']}_"):
                            path = os.path.join(temp_dir, f)
                            try:
                                if os.path.isfile(path): os.remove(path)
                                elif os.path.isdir(path): shutil.rmtree(path)
                                print(f"Targeted Cleanup: Deleted {path}")
                            except: pass
                
                # 2. Audio in downloads
                # We need to calculate the expected name
                from src.downloader import get_expected_audio_path
                audio_path = get_expected_audio_path(job)
                if os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                        print(f"Targeted Cleanup: Deleted {audio_path}")
                    except: pass
                
                # 3. Partial downloads
                if os.path.exists(downloads_dir):
                    safe_name = job['name'].replace(" ", "_").replace("/", "-")
                    for f in os.listdir(downloads_dir):
                        if f.startswith(safe_name) and any(f.endswith(ext) for f in [f] for ext in [".part", ".ytdl"]):
                            path = os.path.join(downloads_dir, f)
                            try:
                                os.remove(path)
                                print(f"Targeted Cleanup: Deleted {path}")
                            except: pass
        else:
            # Original behavior: Purge everything
            # Cleanup temp
            if os.path.exists(temp_dir):
                for f in os.listdir(temp_dir):
                    if f == ".gitkeep": continue
                    path = os.path.join(temp_dir, f)
                    try:
                        if os.path.isfile(path): os.remove(path)
                        elif os.path.isdir(path): shutil.rmtree(path)
                        print(f"Manual Cleanup: Deleted {path}")
                    except Exception as e:
                        print(f"Manual Cleanup: Failed to delete {path}: {e}")

            # Cleanup downloads (only mp3/part files and the temp folder)
            if os.path.exists(downloads_dir):
                for f in os.listdir(downloads_dir):
                    if f == ".gitkeep": continue
                    
                    path = os.path.join(downloads_dir, f)
                    
                    # Special handling for downloads/temp
                    if f == "temp" and os.path.isdir(path):
                        for sub_f in os.listdir(path):
                            if sub_f == ".gitkeep": continue
                            sub_path = os.path.join(path, sub_f)
                            try:
                                if os.path.isfile(sub_path): os.remove(sub_path)
                                elif os.path.isdir(sub_path): shutil.rmtree(sub_path)
                                print(f"Manual Cleanup: Deleted {sub_path}")
                            except Exception as e:
                                print(f"Manual Cleanup: Failed to delete {sub_path}: {e}")
                        continue

                    # We only want to delete audio files and partial downloads in the root downloads dir
                    if f.lower().endswith((".mp3", ".part", ".ytdl", ".m4a", ".webm")):
                        try:
                            os.remove(path)
                            print(f"Manual Cleanup: Deleted {path}")
                        except Exception as e:
                            print(f"Manual Cleanup: Failed to delete {path}: {e}")
