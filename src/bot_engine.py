from .browser_driver import BrowserDriver
from .pdf_converter_py import PdfConverter
from .job_manager import JobManager
from .downloader import download_audio
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import time
import os
import glob

# --- CONFIGURATION ---
TARGET_MODEL_NAME = "Gemini 3 Pro Preview"
TARGET_MODEL_ID = "model-carousel-row-models/gemini-3-pro-previe"
TARGET_SYSTEM_INSTRUCTION = "note generator"

TEMP_DIR = "temp" 
DOWNLOAD_DIR = "downloads"
ENABLE_STABILITY_CHECK = True 

os.makedirs(TEMP_DIR, exist_ok=True)

class AIStudioBot:
    def __init__(self):
        self.driver = BrowserDriver()
        self.page = None
        self.converter = PdfConverter()

    def ensure_connection(self):
        print("🤖 Bot: Connecting to session...")
        if not self.driver.connect(): 
            raise Exception("Could not connect to browser.")
        
        context = self.driver.context
        context.grant_permissions(["clipboard-read", "clipboard-write"])
        
        found = False
        for p in context.pages:
            if "aistudio" in p.url:
                self.page = p
                found = True
                p.bring_to_front()
                break
        
        if not found:
            print("   Opening new AI Studio tab...")
            self.page = context.new_page()
        
        # Always navigate to new chat to ensure fresh state
        if self.page.url != "https://aistudio.google.com/prompts/new_chat":
             self.page.goto("https://aistudio.google.com/prompts/new_chat")
        
        try: self.page.wait_for_load_state("networkidle", timeout=10000)
        except: pass

    def select_model(self):
        print(f"🤖 Bot: Checking Model ({TARGET_MODEL_NAME})...")
        try:
            card_selector = "button.model-selector-card"
            card = self.page.wait_for_selector(card_selector, timeout=10000)
            current_text = card.text_content().strip()
            
            if TARGET_MODEL_NAME in current_text:
                print(f"   ✅ Verified: Already on {TARGET_MODEL_NAME}.")
                return

            print(f"   Mismatch. Switching from '{current_text}'...")
            
            target_btn_selector = f'button[id="{TARGET_MODEL_ID}"]'
            
            for attempt in range(3):
                print(f"   Selection attempt {attempt + 1}...")
                card.click()
                
                try:
                    target_btn = self.page.wait_for_selector(target_btn_selector, timeout=5000)
                    target_btn.click()
                    print(f"   ✅ Switched to {TARGET_MODEL_NAME}")
                    return
                except PlaywrightTimeoutError:
                    print("   Target model not immediately visible, trying to switch to 'All' tab...")
                    all_btn = self.page.locator("button[data-test-category-button='']").filter(has_text="All")
                    if all_btn.is_visible():
                        all_btn.click()
                        try:
                            target_btn = self.page.wait_for_selector(target_btn_selector, timeout=3000)
                            target_btn.click()
                            print(f"   ✅ Switched to {TARGET_MODEL_NAME} (via 'All' tab)")
                            return
                        except:
                            pass
                
                print("   Retrying model sidebar interaction...")
                time.sleep(1)

            raise Exception(f"Failed to select model {TARGET_MODEL_NAME} after 3 attempts.")
            
        except Exception as e:
            print(f"   ❌ Model selection error: {e}")
            raise

    def select_system_instruction(self):
        instruction_name = TARGET_SYSTEM_INSTRUCTION
        print(f"🤖 Bot: Checking System Instruction ({instruction_name})...")
        try:
            card_selector = "button.system-instructions-card"
            card = self.page.wait_for_selector(card_selector, timeout=10000)
            
            dropdown_selector = ".mat-mdc-select-trigger"
            
            for attempt in range(3):
                print(f"   Instruction selection attempt {attempt + 1}...")
                card.click()
                
                try:
                    dropdown = self.page.wait_for_selector(dropdown_selector, timeout=5000)
                    current_val = dropdown.text_content().strip()
                    
                    if instruction_name in current_val:
                         print(f"   ✅ Already using '{instruction_name}'.")
                    else:
                        print("   Setting instruction...")
                        dropdown.click()
                        
                        option = self.page.locator("mat-option").filter(has_text=instruction_name).first
                        option.wait_for(state="visible", timeout=5000)
                        option.click()
                        print(f"   ✅ Selected: {instruction_name}")
                    
                    # Explicitly close the sidebar after selection
                    try:
                        self.page.locator('button[aria-label="Close panel"]').click(timeout=2000)
                        print("   Closed system prompt panel.")
                    except:
                        pass
                    
                    return # SUCCESS
                    
                except PlaywrightTimeoutError:
                    print("   System instruction dropdown not visible. Retrying sidebar click...")
                    time.sleep(1)

            raise Exception(f"Failed to select system instruction {instruction_name} after 3 attempts.")

        except Exception as e:
            print(f"   ❌ System Instruction selection error: {e}")
            raise

    def _get_clean_text_length(self, locator):
        """Calculates text length excluding 'Thinking' blocks and UI labels."""
        return locator.evaluate("""(element) => {
            // Target only the prompt chunks which contain the actual response
            const chunks = element.querySelectorAll('ms-prompt-chunk');
            let totalLength = 0;
            
            chunks.forEach(chunk => {
                const clone = chunk.cloneNode(true);
                // Remove thinking blocks
                const thoughts = clone.querySelectorAll('ms-thought-chunk');
                thoughts.forEach(t => t.remove());
                
                // Get text from the cleaned chunk
                totalLength += clone.innerText.trim().length;
            });
            
            return totalLength;
        }""")

    def restart_session(self):
        """Hard reset: closes current driver/browser and reconnects."""
        print("🔄 Bot: Restarting browser session (hard reset)...")
        try:
            if self.driver:
                self.driver.close()
        except Exception as e:
            print(f"   (Internal) Error during driver close: {e}")
        
        self.page = None # Clear stale page reference
        time.sleep(2) # Give OS time to release resources
        self.driver = BrowserDriver()
        self.ensure_connection()

    def generate_notes(self, audio_path):
        if not os.path.exists(audio_path):
            print(f"❌ File not found: {audio_path}")
            return None, None

        filename = os.path.basename(audio_path)
        name_no_ext = os.path.splitext(filename)[0]
        output_filename = f"{name_no_ext}.md"
        output_path = os.path.join(TEMP_DIR, output_filename)

        print(f"🤖 Bot: Uploading {filename}...")
        
        try:
            # 1. Open Menu
            print("   Clicking '+' to load menu...")
            self.page.locator('button[data-test-id="add-media-button"]').click()
            
            # 2. TARGET HIDDEN INPUT
            print("   Targeting hidden input...")
            file_input = self.page.locator("input[data-test-upload-file-input]")
            file_input.set_input_files(audio_path, timeout=60000)
            print("   ✅ File injected successfully.")

            # Press escape to close the media menu and prevent interception
            self.page.keyboard.press("Escape")
            print("   Pressed 'Escape' to close media popup. Waiting 2s for upload stability...")
            time.sleep(2)

            # 3. WAIT FOR RUN
            print("   Waiting for 'Run'...")
            run_btn = self.page.locator('ms-run-button button[aria-label="Run"]').first
            
            for _ in range(300):
                if run_btn.is_enabled():
                    print("   🚀 Run Clicked!")
                    run_btn.click()
                    break
                time.sleep(1)
            else:
                raise Exception("Timeout: Run button never enabled.")

            # 4. WAIT FOR COMPLETION
            print("⏳ Waiting for generation to start...")
            last_model_turn = self.page.locator("ms-chat-turn").filter(
                has=self.page.locator("[data-turn-role='Model']")
            ).last
            
            # Wait up to 30s for the response block to appear
            try:
                last_model_turn.wait_for(state="visible", timeout=30000)
                last_model_turn.scroll_into_view_if_needed()
            except:
                raise Exception("Timeout: AI response block never appeared.")

            print("⏳ Monitoring AI response growth (ignoring thoughts)...")
            
            # Phase A: Wait for actual text to appear (ignoring thoughts)
            start_wait_time = time.time()
            while True:
                clean_len = self._get_clean_text_length(last_model_turn)
                if clean_len > 0:
                    print("   🚀 Response text started.")
                    break
                
                if time.time() - start_wait_time > 600: # Wait up to 10 mins for thinking to finish
                    print("   ⚠️ Timed out waiting for text start after 10m. Assuming empty or done.")
                    break
                
                if int(time.time() - start_wait_time) % 10 == 0:
                    print(f"   ... Thinking / Waiting ({int(time.time() - start_wait_time)}s) ...")
                time.sleep(1)

            # Phase B: Monitor Growth
            last_length = 0
            stable_seconds = 0
            start_monitoring_time = time.time()
            
            while stable_seconds < 15:
                current_length = self._get_clean_text_length(last_model_turn)
                elapsed = int(time.time() - start_monitoring_time)
                
                if current_length > last_length:
                    last_length = current_length
                    stable_seconds = 0
                    if elapsed % 5 == 0:
                        print(f"   ... Growing ({current_length} chars, {elapsed}s) ...")
                else:
                    stable_seconds += 1
                
                # Safety timeout (20 mins max generation)
                if elapsed > 1200:
                    print("   ⚠️ Hit max generation limit (20m). Proceeding.")
                    break

                time.sleep(1)
            
            print(f"   ✅ Generation finished (stable for 15s, total {elapsed}s).")
            
            # 5. EXTRACTION
            print("   Extracting text...")
            last_model_turn.scroll_into_view_if_needed()
            time.sleep(1) # Settle layout
            last_model_turn.hover()
            
            more_btn = last_model_turn.locator("button[aria-label='Open options']").first
            more_btn.click()
            
            copy_btn = self.page.get_by_text("Copy as markdown").first
            copy_btn.click()
            
            time.sleep(1)
            final_text = self.page.evaluate("navigator.clipboard.readText()")
            
            if not final_text:
                 raise Exception("Failed to extract text from clipboard.")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_text)
            
            print(f"   💾 Saved Markdown to: {output_path}")
            
            # 6. PDF CONVERSION
            print("   Converting to PDF...")
            html_path = output_path.replace(".md", ".html")
            pdf_path = output_path.replace(".md", ".pdf")
            
            self.converter.convert_md_to_html(output_path, html_path)
            self.converter.convert_html_to_pdf(html_path, pdf_path, playwright_instance=self.driver.playwright)
            
            print(f"   ✅ PDF saved to: {pdf_path}")
            
            return final_text, pdf_path

        except Exception as e:
            print(f"❌ Notes generation failed: {e}")
            return None, None

    def close(self):
        self.driver.close()
        self.driver.stop_all()

def process_job(bot, job_manager, job):
    """Processes a single job with retry/restart logic"""
    try:
        # Update status to downloading
        job['status'] = 'downloading'
        job_manager.save_history()
        
        # Phase 2: Download
        audio_path = download_audio(job)
        
        # Update status to processing
        job['status'] = 'processing'
        job_manager.save_history()
        
        # Phase 3: AI Studio Automation with Hard Reset Recovery
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                bot.ensure_connection()
                bot.select_model()
                bot.select_system_instruction()
                
                text, pdf_path = bot.generate_notes(audio_path)
                
                if pdf_path:
                    job['status'] = 'completed'
                    job['pdf_path'] = pdf_path
                    print(f"\n✨ SUCCESSFULLY COMPLETED: {job['name']}")
                    return # SUCCESS
                else:
                    raise Exception("PDF path not generated")

            except Exception as e:
                print(f"   ⚠️ Interaction failure on attempt {attempt + 1}: {e}")
                if attempt < max_attempts - 1:
                    print("   🔄 Attempting hard reset and retry...")
                    bot.restart_session()
                    time.sleep(2)
                else:
                    # Final attempt failed
                    job['status'] = 'failed'
                    job['error'] = str(e)
                    print(f"\n❌ FAILED AFTER {max_attempts} ATTEMPTS: {job['name']}")
            
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)
        print(f"❌ CRITICAL JOB ERROR ({job['name']}): {e}")
    
    job_manager.save_history()

if __name__ == "__main__":
    job_manager = JobManager()
    file_names = input("Give me the file names: ")
    urls = input("Give the URLS for the files: ")
    job_manager.add_jobs(file_names, urls)
    pending_jobs = job_manager.get_pending_from_last_150()
    
    if not pending_jobs:
        print("📭 No pending jobs in queue.")
    else:
        print(f"📂 Found {len(pending_jobs)} pending jobs to process.")
        bot = AIStudioBot()
        try:
            for job in pending_jobs:
                process_job(bot, job_manager, job)
                # Small delay between jobs
                time.sleep(3)
        finally:
            bot.close()
