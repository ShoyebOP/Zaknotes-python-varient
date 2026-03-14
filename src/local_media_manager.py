import os
from typing import List, Dict

class LocalMediaManager:
    def __init__(self, uploads_dir: str = "uploads"):
        self.uploads_dir = uploads_dir
        self.supported_extensions = {".mp3", ".mp4", ".m4a", ".wav", ".mkv"}

    def get_available_files(self) -> List[str]:
        """Returns a list of supported media files in the uploads directory, sorted by modification time."""
        if not os.path.exists(self.uploads_dir):
            return []
        
        files = [
            f for f in os.listdir(self.uploads_dir)
            if os.path.isfile(os.path.join(self.uploads_dir, f)) and 
               os.path.splitext(f)[1].lower() in self.supported_extensions
        ]
        # Sort by modification time to represent "chronological" order of upload
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.uploads_dir, x)))
        return files

    def map_files_to_names(self, names: List[str] = None) -> List[Dict[str, str]]:
        """
        Maps names to available files.
        If names is None or empty, uses filenames as names.
        If names are provided, maps them chronologically to files.
        """
        files = self.get_available_files()
        if not files:
            return []

        mapped_jobs = []
        for i, filename in enumerate(files):
            # Determine job name
            if names and i < len(names):
                job_name = names[i]
            else:
                # Default to filename without extension
                job_name = os.path.splitext(filename)[0]
            
            mapped_jobs.append({
                "name": job_name,
                "file_path": os.path.join(self.uploads_dir, filename),
                "original_filename": filename
            })
            
        return mapped_jobs
