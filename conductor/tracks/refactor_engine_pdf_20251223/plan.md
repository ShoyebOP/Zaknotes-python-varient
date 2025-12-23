# Plan: Refactor Bot Engine & PDF Conversion

## Phase 1: Repository Cleanup & Setup
- [x] Task: Cleanup obsolete files and artifacts [199dfd5]
- [x] Task: Initialize testing environment (pytest) and update dependencies [e23c920]
- [ ] Task: Conductor - User Manual Verification 'Cleanup & Setup' (Protocol in workflow.md)

## Phase 2: Bot Engine - Foundation & Selection
- [ ] Task: Write Tests: Browser connection and model/instruction selection
- [ ] Task: Refactor `browser_driver.py` and `bot_engine.py` for reliable connection and fresh chat navigation
- [ ] Task: Implement model and system instruction selection using `ui_elements/` selectors
- [ ] Task: Conductor - User Manual Verification 'Bot Engine Foundation' (Protocol in workflow.md)

## Phase 3: Bot Engine - Upload & Extraction
- [ ] Task: Write Tests: File upload and clean Markdown extraction
- [ ] Task: Implement robust file upload via direct DOM injection
- [ ] Task: Implement completion verification and clean extraction using "Copy as Markdown" flow
- [ ] Task: Conductor - User Manual Verification 'Bot Engine Upload & Extraction' (Protocol in workflow.md)

## Phase 4: Python-Native PDF Conversion
- [ ] Task: Write Tests: MD to HTML and HTML to PDF conversion
- [ ] Task: Implement MD to HTML conversion using Pandoc
- [ ] Task: Implement HTML to PDF conversion using Playwright Python `page.pdf()` with CSS injection
- [ ] Task: Conductor - User Manual Verification 'PDF Conversion' (Protocol in workflow.md)

## Phase 5: Integration & Final Polish
- [ ] Task: Write Tests: End-to-end integration of the pipeline
- [ ] Task: Integrate components into a unified execution flow in `bot_engine.py`
- [ ] Task: Final verification and code style polish
- [ ] Task: Conductor - User Manual Verification 'Integration & Final Polish' (Protocol in workflow.md)
