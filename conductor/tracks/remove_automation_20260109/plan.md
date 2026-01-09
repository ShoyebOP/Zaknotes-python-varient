# Plan: Remove Browser Automation and UI Elements

## Phase 1: Logic Replacement & Placeholder Implementation [checkpoint: eefa041]
- [x] Task: Create `tests/test_placeholders.py` to verify that `zaknotes.py` functions (e.g., `refresh_browser_profile`, `launch_manual_browser`) can be called without error and produce expected log output. 1bf68a4
- [x] Task: Modify `zaknotes.py` to remove imports of `BrowserDriver`, `AIStudioBot`, `process_job` and replace their usage with log messages (e.g., "Browser automation placeholder triggered"). 1bf68a4
- [x] Task: Verify that `zaknotes.py` no longer references the to-be-deleted modules. 1bf68a4
- [x] Task: Conductor - User Manual Verification 'Logic Replacement & Placeholder Implementation' (Protocol in workflow.md) 1bf68a4

## Phase 2: Selenium to Playwright Migration [checkpoint: 4da882a]
- [x] Task: Create `tests/test_find_vimeo_url.py` to test the current Vimeo URL extraction logic (Red Phase). c44aa8d
- [x] Task: Refactor `src/find_vimeo_url.py` to use `playwright` instead of `selenium`. c44aa8d
- [x] Task: Verify that `src/find_vimeo_url.py` correctly extracts Vimeo URLs using Playwright. c44aa8d
- [x] Task: Remove `selenium` from `requirements.txt`. c44aa8d
- [x] Task: Conductor - User Manual Verification 'Selenium to Playwright Migration' (Protocol in workflow.md) 5eb052f

## Phase 3: Component Removal
- [x] Task: Delete `src/browser_driver.py`. bbfba2f
- [x] Task: Delete `src/bot_engine.py`. bbfba2f
- [x] Task: Delete `src/ui_elements/` directory. bbfba2f
- [x] Task: Delete `tests/` directory (excluding the newly created `test_placeholders.py` and `test_find_vimeo_url.py`). *I will back up these specific test files, delete the rest of `tests/`, and restore them.* bbfba2f
- [x] Task: Conductor - User Manual Verification 'Component Removal' (Protocol in workflow.md) bbfba2f

## Phase 4: Cleanup & Verification
- [ ] Task: Audit `requirements.txt` and remove any dependencies that are now strictly unused (like `webdriver-manager` if present).
- [ ] Task: Final verification that the application starts and video download references are intact.
- [ ] Task: Conductor - User Manual Verification 'Cleanup & Verification' (Protocol in workflow.md)
