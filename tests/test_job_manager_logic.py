import os
import json
import unittest
from src.job_manager import JobManager, HISTORY_FILE

class TestJobManager(unittest.TestCase):
    def setUp(self):
        # Backup existing history if any
        self.backup_history = None
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                self.backup_history = f.read()
        
        # Start with fresh history
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        self.manager = JobManager()

    def tearDown(self):
        # Restore backup
        if self.backup_history:
            with open(HISTORY_FILE, 'w') as f:
                f.write(self.backup_history)
        elif os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)

    def test_cancel_pending_all(self):
        # Create more than 150 jobs
        for i in range(200):
            self.manager.history.append({
                "id": str(i),
                "name": f"Job {i}",
                "url": "http://example.com",
                "status": "queue",
                "added_at": "2026-01-01"
            })
        self.manager.save_history()
        
        # Cancel pending
        self.manager.cancel_pending()
        
        # Verify ALL are cancelled
        for job in self.manager.history:
            self.assertEqual(job['status'], 'cancelled', f"Job {job['id']} was not cancelled")

    def test_get_pending_accurate(self):
        # Create more than 150 jobs
        for i in range(200):
            self.manager.history.append({
                "id": str(i),
                "name": f"Job {i}",
                "url": "http://example.com",
                "status": "queue",
                "added_at": "2026-01-01"
            })
        
        pending = self.manager.get_pending_from_last_150()
        # It should now return ALL 200 jobs if we refactor it or use a new method
        self.assertEqual(len(pending), 200)

    def test_get_pending_includes_failed_jobs(self):
        # 1. Pending Job
        self.manager.history.append({
            "id": "1", "name": "Pending Job", "url": "http://p.com", "status": "queue"
        })
        # 2. Failed Job
        self.manager.history.append({
            "id": "2", "name": "Failed Job", "url": "http://f.com", "status": "failed"
        })
        # 3. Completed Job (Should NOT be included)
        self.manager.history.append({
            "id": "3", "name": "Done Job", "url": "http://d.com", "status": "completed"
        })
        # 4. Cancelled Job (Should NOT be included)
        self.manager.history.append({
            "id": "4", "name": "Cancelled Job", "url": "http://c.com", "status": "cancelled"
        })
        
        self.manager.save_history()
        
        # Act
        to_process = self.manager.get_pending_from_last_150()
        
        # Assert
        ids = [j['id'] for j in to_process]
        self.assertIn("1", ids, "Pending job should be processed")
        self.assertIn("2", ids, "Failed job should be retried")
        self.assertNotIn("3", ids, "Completed job should be ignored")
        self.assertNotIn("4", ids, "Cancelled job should be ignored")
        self.assertEqual(len(to_process), 2)

    def test_cancel_pending_clears_failed_jobs(self):
        # Setup
        self.manager.history.append({
            "id": "1", "name": "Pending Job", "url": "p.com", "status": "queue"
        })
        self.manager.history.append({
            "id": "2", "name": "Failed Job", "url": "f.com", "status": "failed"
        })
        self.manager.save_history()
        
        # Act
        self.manager.cancel_pending()
        
        # Assert
        for job in self.manager.history:
            self.assertEqual(job['status'], 'cancelled', f"Job {job['id']} should be cancelled")

if __name__ == '__main__':
    unittest.main()
