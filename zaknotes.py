#!/usr/bin/env python3
import os
import sys
import shutil
from src.job_manager import JobManager
from src.cookie_manager import interactive_update as refresh_cookies
from src.config_manager import ConfigManager
from src.pipeline import ProcessingPipeline
from src.cleanup_service import FileCleanupService

def configure_gemini_models():
    config = ConfigManager()
    curr_t = config.get("transcription_model")
    curr_n = config.get("note_generation_model")
    
    print("\n--- Configure Gemini Models ---")
    print(f"Current Transcription Model: {curr_t}")
    print(f"Current Note Generation Model: {curr_n}")
    
    new_t = input(f"Enter new Transcription Model (leave blank to keep '{curr_t}'): ").strip()
    if new_t:
        config.set("transcription_model", new_t)
        
    new_n = input(f"Enter new Note Generation Model (leave blank to keep '{curr_n}'): ").strip()
    if new_n:
        config.set("note_generation_model", new_n)
        
    config.save()
    print("✅ Configuration saved.")

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

def launch_manual_browser():
    print("Browser automation placeholder triggered")

def main_menu():
    while True:
        print("\n==============================")
        print("       ZAKNOTES MENU")
        print("==============================")
        print("1. Start Note Generation")
        print("2. Configure Gemini Models")
        print("3. Cleanup Stranded Audio Chunks")
        print("4. Refresh Cookies")
        print("5. Launch Browser")
        print("6. Exit")
        print("------------------------------")
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            start_note_generation()
        elif choice == '2':
            configure_gemini_models()
        elif choice == '3':
            cleanup_stranded_chunks()
        elif choice == '4':
            refresh_cookies()
        elif choice == '5':
            launch_manual_browser()
        elif choice == '6':
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
