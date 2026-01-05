# Plan: Project Unification and Cleanup

This plan outlines the steps to reorganize the Zaknotes codebase, clean up legacy files, and implement a unified CLI entry point.

## Phase 1: Project Structure Reorganization
- [x] **Task 1: Setup New Directory Structure** aa1ff20
  - Create the `src/` directory.
  - Move Python modules: `bot_engine.py`, `browser_driver.py`, `cookie_manager.py`, `downloader.py`, `find_vimeo_url.py`, `job_manager.py`, `pdf_converter_py.py` to `src/`.
  - Move resource directories: `ui_elements/` and `pdf_converter/` to `src/`.
- [ ] **Task 2: Cleanup Legacy Artifacts**
  - Delete all `test_*.py` files from the root directory.
  - Delete `__pycache__` directories.
- [ ] **Task 3: Refactor Imports and Paths**
  - Update all `import` statements in the moved modules to handle the new directory structure.
  - Update any hardcoded file paths (e.g., to `ui_elements` or `style.css`) within the modules to reflect their new locations relative to `src/`.
- [ ] **Task 4: Git Ignore Updates**
  - **Action**: Update `.gitignore` to explicitly exclude `src/ui_elements/` and ensure `__pycache__/` and `*.pyc` are effectively ignored.
  - **Verification**: Run `git status --ignored` or check `git check-ignore` to confirm these paths are ignored.
- [ ] **Task 5: Verify Module Integrity**
  - **Write Tests**: Create a basic sanity test to ensure all modules can be imported without errors in the new structure.
  - **Implement**: Adjust code until sanity tests pass.
- [ ] **Task: Conductor - User Manual Verification 'Project Structure Reorganization' (Protocol in workflow.md)**

## Phase 2: Unified CLI Implementation (`zaknotes.py`)
- [ ] **Task 1: Implement Menu Framework**
  - **Write Tests**: Define tests for the CLI menu structure and user input handling.
  - **Implement**: Create `zaknotes.py` in the root with a loop that displays the 3 options and handles exit.
- [ ] **Task 2: Integrate Option 1 - Start Note Generation**
  - **Implement**: Link the "Process Videos" menu option to the existing logic in `src/job_manager.py`.
- [ ] **Task 3: Implement Option 2 - Refresh Browser Profile**
  - **Write Tests**: Define tests for directory deletion and browser launch triggers.
  - **Implement**: Add logic to `zaknotes.py` to delete `browser_profile/` and launch a non-headless browser via `browser_driver.py`.
- [ ] **Task 4: Integrate Option 3 - Refresh Cookies**
  - **Implement**: Link the "Refresh Cookies" menu option to `src/cookie_manager.py`.
- [ ] **Task: Conductor - User Manual Verification 'Unified CLI Implementation' (Protocol in workflow.md)**

## Phase 3: Final Integration & QA
- [ ] **Task 1: End-to-End Flow Verification**
  - Manually verify that a full "Note Generation" run works as expected from the new `zaknotes.py` entry point.
- [ ] **Task 2: Documentation & Cleanup**
  - Ensure any README instructions are updated (if applicable).
  - Perform a final check for any lingering unused files.
- [ ] **Task: Conductor - User Manual Verification 'Final Integration & QA' (Protocol in workflow.md)**
