#!/usr/bin/env python3
import os
import sys
import shutil
from src.job_manager import JobManager
from src.cookie_manager import interactive_update as refresh_cookies
from src.api_key_manager import APIKeyManager
from src.config_manager import ConfigManager
from src.pipeline import ProcessingPipeline
from src.cleanup_service import FileCleanupService

def manage_api_keys():
    manager = APIKeyManager()
    while True:
        keys = manager.list_keys()
        print("\n--- Manage Gemini API Keys ---")
        if not keys:
            print("No API keys configured.")
        else:
            print("Configured Keys:")
            for i, k in enumerate(keys, 1):
                # Mask key for display
                masked = k['key'][:4] + "..." + k['key'][-4:] if len(k['key']) > 8 else "****"
                print(f"{i}. {masked}")
        
        print("\n1. Add API Key")
        print("2. Remove API Key")
        print("3. Back to Main Menu")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            key = input("Enter new Gemini API Key: ").strip()
            if key:
                if manager.add_key(key):
                    print("✅ API Key added.")
                else:
                    print("❌ Key already exists.")
        elif choice == '2':
            if not keys:
                print("❌ No keys to remove.")
                continue
            idx = input("Enter the number of the key to remove: ").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(keys):
                    manager.remove_key(keys[idx]['key'])
                    print("✅ API Key removed.")
                else:
                    print("❌ Invalid number.")
            except ValueError:
                print("❌ Please enter a number.")
        elif choice == '3':
            break
        else:
            print("❌ Invalid choice.")

def cleanup_stranded_chunks():
    print("\n🧹 Cleaning up all intermediate files...")
    FileCleanupService.cleanup_all_temp_files()
    print("✅ Cleanup complete.")

def run_processing_pipeline(manager):
    config = ConfigManager()
    pipeline = ProcessingPipeline(config)
    
    pending_jobs = manager.get_pending_from_last_150()
    if not pending_jobs:
        print("No pending jobs to process.")
        return

    print(f"\n🚀 Starting pipeline for {len(pending_jobs)} jobs...")
    
    for job in pending_jobs:
        print(f"\n--- Processing Job: {job['name']} ---")
        success = pipeline.execute_job(job)
        
        # Save progress after each job
        manager.save_history()
        
        if not success:
            print(f"⚠️ Job '{job['name']}' failed. Failing all remaining jobs in batch...")
            manager.fail_pending()
            break
    
    print("\n🏁 Pipeline execution finished.")

def start_note_generation():
    manager = JobManager()
    
    while True:
        print("\n--- Note Generation Sub-Menu ---")
        print("1. Start New Jobs (Cancel Old Jobs)")
        print("2. Start New Jobs (Add to Queue)")
        print("3. Cancel All Old Jobs")
        print("4. Process Old Jobs")
        print("5. Back to Main Menu")
        print("--------------------------------")
        
        sub_choice = input("Enter your choice (1-5): ").strip()
        
        if sub_choice == '1':
            manager.cancel_pending()
            print("✅ Old jobs cancelled.")
            file_names = input("Give me the file names (separated by comma/pipe/newline): ")
            urls = input("Give the URLS for the files: ")
            if file_names.strip() and urls.strip():
                manager.add_jobs(file_names, urls)
                run_processing_pipeline(manager)
            break
            
        elif sub_choice == '2':
            file_names = input("Give me the file names (separated by comma/pipe/newline): ")
            urls = input("Give the URLS for the files: ")
            if file_names.strip() and urls.strip():
                manager.add_jobs(file_names, urls)
                run_processing_pipeline(manager)
            break
            
        elif sub_choice == '3':
            manager.cancel_pending()
            print("✅ All old jobs cancelled.")
            break
            
        elif sub_choice == '4':
            run_processing_pipeline(manager)
            break
            
        elif sub_choice == '5':
            break
        else:
            print("❌ Invalid choice.")

def main_menu():
    while True:
        print("\n==============================")
        print("       ZAKNOTES MENU")
        print("==============================")
        print("1. Start Note Generation")
        print("2. Manage API Keys")
        print("3. Cleanup Stranded Audio Chunks")
        print("4. Refresh Cookies")
        print("5. Exit")
        print("------------------------------")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            start_note_generation()
        elif choice == '2':
            manage_api_keys()
        elif choice == '3':
            cleanup_stranded_chunks()
        elif choice == '4':
            refresh_cookies()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
        sys.exit(0)
