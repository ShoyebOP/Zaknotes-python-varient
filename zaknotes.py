#!/usr/bin/env python3
import os
import sys
import shutil
from src.job_manager import JobManager
from src.cookie_manager import interactive_update as refresh_cookies
from src.browser_driver import BrowserDriver

def refresh_browser_profile():
    print("🧹 Cleaning up browser profile...")
    profile_dir = "browser_profile"
    if os.path.exists(profile_dir):
        shutil.rmtree(profile_dir)
        print(f"✅ Deleted {profile_dir}")
    else:
        print("ℹ️ No existing profile found.")
    
    print("🚀 Launching browser for manual login...")
    print("Please login to Google AI Studio and other necessary sites.")
    print("Close the browser window when finished.")
    
    driver = BrowserDriver()
    driver.launch_browser()
    # Since it's Popen in background, we might want to wait or just inform user
    print("\n✅ Browser launched. Follow the steps in the browser window.")

def run_processing_pipeline(manager):
    # Import here to avoid circular dependencies and only when needed
    from src.bot_engine import AIStudioBot, process_job
    
    pending_jobs = manager.get_pending_from_last_150()
    
    if not pending_jobs:
        print("📭 No pending jobs in queue.")
        return

    print(f"📂 Found {len(pending_jobs)} pending jobs to process.")
    bot = AIStudioBot()
    try:
        for job in pending_jobs:
            process_job(bot, manager, job)
    finally:
        bot.close()

def start_note_generation():
    manager = JobManager()
    
    while True:
        print("\n--- Note Generation Sub-Menu ---")
        print("1. Start New Jobs (Cancel Pending)")
        print("2. Start New Jobs (Include Pending)")
        print("3. Cancel Old Pending Jobs")
        print("4. Start Old Pending Jobs")
        print("5. Back to Main Menu")
        print("--------------------------------")
        
        sub_choice = input("Enter your choice (1-5): ").strip()
        
        if sub_choice == '1':
            manager.cancel_pending()
            print("✅ Old pending jobs cancelled.")
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
            print("✅ Old pending jobs cancelled.")
            break
            
        elif sub_choice == '4':
            run_processing_pipeline(manager)
            break
            
        elif sub_choice == '5':
            break
        else:
            print("❌ Invalid choice.")

def launch_manual_browser():
    print("\n🚀 Launching Browser for manual inspection...")
    print("📂 Using profile: browser_profile")
    print("------------------------------------------")
    driver = BrowserDriver()
    try:
        if driver.launch_browser():
            print("\n✅ Browser is running.")
            input("\nPress Enter to close browser and return to menu...")
    except Exception as e:
        print(f"❌ Failed to launch browser: {e}")
    finally:
        driver.close()

def main_menu():
    while True:
        print("\n==============================")
        print("       ZAKNOTES MENU")
        print("==============================")
        print("1. Start Note Generation")
        print("2. Refresh Browser Profile")
        print("3. Refresh Cookies")
        print("4. Launch Browser")
        print("5. Exit")
        print("------------------------------")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            start_note_generation()
        elif choice == '2':
            refresh_browser_profile()
        elif choice == '3':
            refresh_cookies()
        elif choice == '4':
            launch_manual_browser()
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
