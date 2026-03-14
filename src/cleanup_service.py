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
    def cleanup_uploads(uploads_dir="uploads"):
        """Purges everything in the uploads folder (except .gitkeep)."""
        print("🧹 Purging everything in uploads...")
        if os.path.exists(uploads_dir):
            for f in os.listdir(uploads_dir):
                if f == ".gitkeep": continue
                path = os.path.join(uploads_dir, f)
                try:
                    if os.path.isfile(path): os.remove(path)
                    elif os.path.isdir(path): shutil.rmtree(path)
                    print(f"Cleanup: Deleted {path}")
                except Exception as e:
                    print(f"Cleanup: Failed to delete {path}: {e}")

    @staticmethod
    def cleanup_all_temp_files(temp_dir="temp", downloads_dir="downloads", uploads_dir="uploads", jobs_to_purge=None, include_uploads=False):
        """
        Manually cleans up intermediate files.
        If jobs_to_purge is provided, only files related to those specific jobs are removed.
        Otherwise, everything in the directories is removed (except .gitkeep).
        """
        if jobs_to_purge is not None:
            # Targeted cleanup: Purge EVERYTHING for these specific jobs
            print(f"🧹 Purging all intermediate files for {len(jobs_to_purge)} jobs...")
            for job in jobs_to_purge:
                safe_name = job['name'].replace(" ", "_").replace("/", "-")
                # 1. Temp directory (chunks and transcripts)
                if os.path.exists(temp_dir):
                    for f in os.listdir(temp_dir):
                        if f.startswith(f"job_{job['id']}_") or f.startswith(f"{job['id']}_") or f.startswith(safe_name):
                            path = os.path.join(temp_dir, f)
                            try:
                                if os.path.isfile(path): os.remove(path)
                                elif os.path.isdir(path): shutil.rmtree(path)
                                print(f"Targeted Cleanup: Deleted {path}")
                            except: pass
                
                # 2. Downloads directory (main audio and partials)
                from src.downloader import get_expected_audio_path
                audio_path = get_expected_audio_path(job)
                if os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                        print(f"Targeted Cleanup: Deleted {audio_path}")
                    except: pass
                
                if os.path.exists(downloads_dir):
                    safe_name = job['name'].replace(" ", "_").replace("/", "-")
                    for f in os.listdir(downloads_dir):
                        if f.startswith(safe_name) and any(f.endswith(ext) for ext in [".part", ".ytdl", ".mp3"]):
                            path = os.path.join(downloads_dir, f)
                            try:
                                os.remove(path)
                                print(f"Targeted Cleanup: Deleted {path}")
                            except: pass
        else:
            # Option 1: Purge Everything regardless of status
            print("🧹 Purging EVERYTHING in temp and downloads...")
            
            if os.path.exists(temp_dir):
                for f in os.listdir(temp_dir):
                    if f == ".gitkeep": continue
                    path = os.path.join(temp_dir, f)
                    try:
                        if os.path.isfile(path): os.remove(path)
                        elif os.path.isdir(path): shutil.rmtree(path)
                        print(f"Full Cleanup: Deleted {path}")
                    except: pass

            if os.path.exists(downloads_dir):
                for f in os.listdir(downloads_dir):
                    if f == ".gitkeep" or f == "temp": continue
                    path = os.path.join(downloads_dir, f)
                    try:
                        if os.path.isfile(path): os.remove(path)
                        elif os.path.isdir(path): shutil.rmtree(path)
                        print(f"Full Cleanup: Deleted {path}")
                    except: pass
            
            if include_uploads:
                FileCleanupService.cleanup_uploads(uploads_dir)
