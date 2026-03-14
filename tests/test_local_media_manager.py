import unittest
import os
import shutil
import time
from src.local_media_manager import LocalMediaManager

class TestLocalMediaManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_uploads"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        self.manager = LocalMediaManager(uploads_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_file(self, filename):
        path = os.path.join(self.test_dir, filename)
        with open(path, 'w') as f:
            f.write("test content")
        return path

    def test_get_available_files_empty(self):
        self.assertEqual(self.manager.get_available_files(), [])

    def test_get_available_files_filtering(self):
        self.create_test_file("audio.mp3")
        self.create_test_file("video.mp4")
        self.create_test_file("doc.txt")  # Should be ignored
        files = self.manager.get_available_files()
        self.assertEqual(len(files), 2)
        self.assertIn("audio.mp3", files)
        self.assertIn("video.mp4", files)

    def test_get_available_files_chronological(self):
        self.create_test_file("file1.mp3")
        time.sleep(0.01) # Ensure different modification times
        self.create_test_file("file2.mp3")
        time.sleep(0.01)
        self.create_test_file("file0.mp3")
        
        files = self.manager.get_available_files()
        self.assertEqual(files, ["file1.mp3", "file2.mp3", "file0.mp3"])

    def test_map_files_to_names_default(self):
        self.create_test_file("Biology_Lecture.mp3")
        jobs = self.manager.map_files_to_names()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["name"], "Biology_Lecture")
        self.assertEqual(jobs[0]["original_filename"], "Biology_Lecture.mp3")

    def test_map_files_to_names_provided(self):
        self.create_test_file("f1.mp3")
        self.create_test_file("f2.mp3")
        jobs = self.manager.map_files_to_names(["Biology", "History"])
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["name"], "Biology")
        self.assertEqual(jobs[1]["name"], "History")

    def test_map_files_to_names_partial_names(self):
        self.create_test_file("f1.mp3")
        self.create_test_file("f2.mp3")
        # Only 1 name provided for 2 files
        jobs = self.manager.map_files_to_names(["Biology"])
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["name"], "Biology")
        self.assertEqual(jobs[1]["name"], "f2")

if __name__ == '__main__':
    unittest.main()
