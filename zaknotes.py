#!/usr/bin/env python3
import os
import sys
import shutil
import logging
import json
from src.job_manager import JobManager

# Configure logging to show INFO level and above on terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

from src.cookie_manager import interactive_update as refresh_cookies
from src.notion_config_manager import NotionConfigManager
from src.notion_service import NotionService
from src.config_manager import ConfigManager
from src.pipeline import ProcessingPipeline
from src.cleanup_service import FileCleanupService
from src.gemini_auth_service import GeminiAuthService
from src.gemini_creds_helper import main as run_creds_helper

def manage_gemini_accounts():
    auth_service = GeminiAuthService()
    while True:
        accounts = auth_service.accounts
        print("\n--- Manage Gemini CLI Accounts ---")
        if not accounts:
            print("No accounts configured.")
        else:
            print("Configured Accounts:")
            for i, acc in enumerate(accounts, 1):
                status_icon = "✅" if acc.get("status") == "valid" else "❌"
                print(f"{i}. {acc['email']} [{status_icon} {acc['status']}]")
        
        print("\n1. Add New Account (Login)")
        print("2. Run Credential Helper (Extract/Manual IDs)")
        print("3. Refresh All Tokens")
        print("4. Back to Main Menu")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            creds = run_creds_helper()
            if not creds:
                continue
            
            import asyncio
            auth_service = GeminiAuthService() # Reload
            verifier, challenge = auth_service.generate_pkce()
            auth_url = auth_service.build_auth_url(creds['clientId'], challenge, verifier)
            
            print(f"\n1. Open this URL in your browser:\n{auth_url}\n")
            print("2. Login and authorize.")
            print("3. Paste the final redirect URL (http://localhost:8085/...) or the 'code' parameter here.")
            
            callback_input = input("\nPaste here: ").strip()
            if not callback_input:
                print("❌ No input provided.")
                continue
                
            code = callback_input
            if "code=" in callback_input:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(callback_input)
                params = parse_qs(parsed.query)
                code = params.get("code", [None])[0]
            
            if not code:
                print("❌ Could not extract code from input.")
                continue
                
            print("🔄 Exchanging code for tokens...")
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                record = loop.run_until_complete(auth_service.exchange_code_for_tokens(
                    creds['clientId'], creds['clientSecret'], code, verifier
                ))
                print(f"✅ Success! Logged in as {record['email']}")
            except Exception as e:
                print(f"❌ Login failed: {e}")
                
        elif choice == '2':
            run_creds_helper()
        elif choice == '3':
            import asyncio
            print("🔄 Refreshing all accounts...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            for acc in auth_service.accounts:
                try:
                    loop.run_until_complete(auth_service.refresh_token(acc))
                    print(f"✅ Refreshed {acc['email']}")
                except Exception as e:
                    print(f"❌ Failed to refresh {acc['email']}: {e}")
        elif choice == '4':
            break
        else:
            print("❌ Invalid choice.")

def manage_notion_settings():
    config = ConfigManager()
    notion_manager = NotionConfigManager()
    
    while True:
        enabled = config.get("notion_integration_enabled", False)
        secret, db_id = notion_manager.get_credentials()
        
        print("\n--- Manage Notion Integration ---")
        print(f"1. Integration Enabled: {'✅ Yes' if enabled else '❌ No'}")
        print(f"2. Set Notion Secret (Current: {secret[:4]}...{secret[-4:] if len(secret) > 8 else '****'})")
        print(f"3. Set Database ID (Current: {db_id})")
        print("4. Back to Main Menu")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            config.set("notion_integration_enabled", not enabled)
            config.save()
            print(f"✅ Integration {'enabled' if not enabled else 'disabled'}.")
        elif choice == '2':
            val = input("Enter Notion API Secret: ").strip()
            if val:
                _, curr_db = notion_manager.get_credentials()
                notion_manager.set_credentials(val, curr_db)
                print("✅ Notion Secret updated.")
        elif choice == '3':
            val = input("Enter Notion Database ID: ").strip()
            if val:
                curr_secret, _ = notion_manager.get_credentials()
                notion_manager.set_credentials(curr_secret, val)
                print("✅ Database ID updated.")
        elif choice == '4':
            break
        else:
            print("❌ Invalid choice.")

def configure_audio_chunking():
    config = ConfigManager()
    curr_time = config.get("segment_time", 1800)
    print("\n--- Configure Audio Chunking Time ---")
    print(f"Current Chunk Time: {curr_time}s ({curr_time/60:.1f}m)")
    
    val = input(f"Enter new chunk time in seconds (leave blank to keep '{curr_time}'): ").strip()
    if val:
        try:
            val_int = int(val)
            if val_int < 60:
                print("❌ Chunk time must be at least 60 seconds.")
            else:
                config.set("segment_time", val_int)
                config.save()
                print("✅ Configuration saved.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

def configure_user_agent():
    config = ConfigManager()
    curr_ua = config.get("user_agent")
    print("\n--- Configure Browser User-Agent ---")
    print(f"Current User-Agent: {curr_ua}")
    
    val = input("Enter new User-Agent (leave blank to keep current): ").strip()
    if val:
        config.set("user_agent", val)
        config.save()
        print("✅ Configuration saved.")

def cleanup_stranded_chunks():
    print("\n--- Cleanup Options ---")
    print("1. Purge Everything (Regardless of status)")
    print("2. Purge Completed/Cancelled Only (Preserve pending/failed jobs)")
    print("3. Back")
    
    choice = input("Enter your choice (1-3): ").strip()
    manager = JobManager()
    
    if choice == '1':
        print("\n🧹 Cleaning up ALL intermediate files...")
        FileCleanupService.cleanup_all_temp_files()
        print("✅ Full cleanup complete.")
    elif choice == '2':
        # Filter strictly for non-resumable jobs
        jobs_to_purge = [j for j in manager.history if j.get('status') in ['completed', 'cancelled', 'no_link_found']]
        if not jobs_to_purge:
            print("No completed/cancelled jobs found to purge.")
            return
        print(f"\n🧹 Cleaning up all files for {len(jobs_to_purge)} non-pending jobs...")
        FileCleanupService.cleanup_all_temp_files(jobs_to_purge=jobs_to_purge)
        print("✅ Targeted cleanup complete.")
    elif choice == '3':
        return
    else:
        print("❌ Invalid choice.")

def run_processing_pipeline(manager):
    config = ConfigManager()
    pipeline = ProcessingPipeline(config, job_manager=manager)
    
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

def process_old_notes():
    config = ConfigManager()
    if not config.get("notion_integration_enabled", False):
        print("❌ Notion integration is disabled. Please enable it in 'Manage Notion Settings' first.")
        return

    notion_manager = NotionConfigManager()
    notion_secret, database_id = notion_manager.get_credentials()
    if not notion_secret or not database_id:
        print("❌ Notion credentials not configured. Please set them in 'Manage Notion Settings' first.")
        return

    notes_dir = "notes"
    if not os.path.exists(notes_dir):
        print(f"❌ Notes directory '{notes_dir}' does not exist.")
        return

    md_files = [f for f in os.listdir(notes_dir) if f.endswith(".md")]
    if not md_files:
        print("No old notes found in 'notes/' directory.")
        return

    print(f"🚀 Found {len(md_files)} notes. Starting push to Notion...")
    
    try:
        notion_service = NotionService(notion_secret, database_id)
        success_count = 0
        
        for filename in md_files:
            file_path = os.path.join(notes_dir, filename)
            title = os.path.splitext(filename)[0].replace("_", " ")
            
            print(f"--- Pushing: {title} ---")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                url = notion_service.create_page(title, content)
                if url:
                    print(f"✅ Pushed: {url}")
                    os.remove(file_path)
                    success_count += 1
                else:
                    print(f"❌ Failed to push '{filename}': No URL returned.")
            except Exception as e:
                print(f"❌ Error pushing '{filename}': {e}")
        
        print(f"\n🏁 Finished! Successfully pushed {success_count}/{len(md_files)} notes.")
    except Exception as e:
        print(f"❌ Failed to initialize Notion service: {e}")

def start_note_generation():
    manager = JobManager()
    
    while True:
        print("\n--- Note Generation Sub-Menu ---")
        print("1. Start New Jobs (Cancel Old Jobs)")
        print("2. Start New Jobs (Add to Queue)")
        print("3. Cancel All Old Jobs")
        print("4. Process Queued Jobs")
        print("5. Process Old Notes (Push to Notion)")
        print("6. Back to Main Menu")
        print("--------------------------------")
        
        sub_choice = input("Enter your choice (1-6): ").strip()
        
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
            process_old_notes()
            break
            
        elif sub_choice == '6':
            break
        else:
            print("❌ Invalid choice.")

def configure_gemini_models():
    config = ConfigManager()
    models_file = "models.json"
    
    available_models = []
    if os.path.exists(models_file):
        try:
            with open(models_file, 'r') as f:
                data = json.load(f)
                available_models = data.get("models", [])
        except Exception:
            pass
            
    if not available_models:
        print("❌ No models found in models.json.")
        return

    while True:
        curr_trans = config.get("transcription_model")
        curr_note = config.get("note_generation_model")
        
        print("\n--- Configure Gemini Models ---")
        print(f"1. Transcription Model: {curr_trans}")
        print(f"2. Note Generation Model: {curr_note}")
        print("3. Back to Main Menu")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice in ['1', '2']:
            target_key = "transcription_model" if choice == '1' else "note_generation_model"
            print(f"\nAvailable Models:")
            for i, model in enumerate(available_models, 1):
                print(f"{i}. {model}")
            
            sel = input(f"Select a model (1-{len(available_models)}): ").strip()
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(available_models):
                    config.set(target_key, available_models[idx])
                    config.save()
                    print(f"✅ {target_key} updated to {available_models[idx]}")
                else:
                    print("❌ Invalid selection.")
            except ValueError:
                print("❌ Please enter a number.")
        elif choice == '3':
            break
        else:
            print("❌ Invalid choice.")

def main_menu():
    while True:
        print("\n==============================")
        print("       ZAKNOTES MENU")
        print("==============================")
        print("1. Start Note Generation")
        print("2. Manage Gemini Accounts")
        print("3. Manage Notion Settings")
        print("4. Configure Gemini Models")
        print("5. Configure Audio Chunking")
        print("6. Configure Browser User-Agent")
        print("7. Cleanup Stranded Audio Chunks")
        print("8. Refresh Cookies")
        print("9. Exit")
        print("------------------------------")
        
        choice = input("Enter your choice (1-9): ").strip()
        
        if choice == '1':
            start_note_generation()
        elif choice == '2':
            manage_gemini_accounts()
        elif choice == '3':
            manage_notion_settings()
        elif choice == '4':
            configure_gemini_models()
        elif choice == '5':
            configure_audio_chunking()
        elif choice == '6':
            configure_user_agent()
        elif choice == '7':
            cleanup_stranded_chunks()
        elif choice == '8':
            refresh_cookies()
        elif choice == '9':
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

import argparse

from src.local_media_manager import LocalMediaManager

def main():
    parser = argparse.ArgumentParser(description="Zaknotes: Automated Class Note Generation")
    parser.add_argument("--local", nargs="*", help="Process local media files in uploads/ folder. Can take optional class names.")
    # Future flag for cleanup (Phase 4)
    # parser.add_argument("--cleanup-uploads", action="store_true", help="Purge the uploads/ folder.")
    
    args, unknown = parser.parse_known_args()
    
    if args.local is not None:
        manager = JobManager()
        local_manager = LocalMediaManager()
        
        # args.local is a list of strings if provided, or an empty list if --local is used alone
        mapped_jobs = local_manager.map_files_to_names(args.local)
        
        if not mapped_jobs:
            print("❌ No supported media files found in 'uploads/' directory.")
            return

        print(f"📂 Found {len(mapped_jobs)} local files to process.")
        
        # Add to JobManager history
        from datetime import datetime
        new_jobs = []
        for i, job_info in enumerate(mapped_jobs):
            new_job = {
                "id": f"local_{datetime.now().timestamp()}_{i}",
                "name": job_info["name"],
                "file_path": job_info["file_path"],
                "status": "queue",
                "added_at": str(datetime.now())
            }
            new_jobs.append(new_job)
        
        manager.history.extend(new_jobs)
        manager.save_history()
        
        # Run pipeline
        run_processing_pipeline(manager)
    else:
        main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
        sys.exit(0)
