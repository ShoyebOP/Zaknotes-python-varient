# Implementation Plan: Gemini API Integration & Refactor

This plan outlines the migration from the Gemini CLI to the official Google Generative AI API, including API key management, quota tracking, and output refactoring.

## Phase 1: Environment & Dependency Setup
- [x] Task: Add `google-generativeai` using `uv add google-generativeai`. a0d72aa
- [~] Task: Create `keys/` directory and ensure it is ignored by git.
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: API Key & Quota Management
- [ ] Task: Implement `src/api_key_manager.py` for managing keys and tracking usage.
    - [ ] Sub-task: Implement `APIKeyManager` class with `add_key`, `remove_key`, `list_keys` methods.
    - [ ] Sub-task: Implement `get_available_key(model)` logic with cycling and quota checking.
    - [ ] Sub-task: Implement `reset_quotas_if_needed()` using `worldtimeapi.org` or similar for PT midnight.
- [ ] Task: Add API Key Management to the main menu in `zaknotes.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Gemini API Wrapper & Prompt Refactor
- [ ] Task: Modify `src/prompts.py` to remove file path references from `NOTE_GENERATION_PROMPT`.
- [ ] Task: Create `src/gemini_api_wrapper.py` using `google-generativeai`.
    - [ ] Sub-task: Implement `generate_content` method that handles API calls and key rotation.
    - [ ] Sub-task: Hardcode model names: `gemini-2.5-flash` and `gemini-3-flash-preview`.
- [ ] Task: Update `src/transcription_service.py` and `src/note_generation_service.py` to use `GeminiAPIWrapper`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Audio Processing & Output Refactor
- [ ] Task: Update `src/audio_processor.py`.
    - [ ] Sub-task: Support configurable `segment_time` (default 1800s).
    - [ ] Sub-task: Retain silence removal but increase the silence threshold for safety (e.g., `-50dB`).
    - [ ] Sub-task: Hardlock the bitrate to an optimal transcription value (e.g., `48k` or `64k`) and remove scaling logic.
- [ ] Task: Add "Configure Audio Chunking Time" (default 30m) to the main menu in `zaknotes.py`.
- [ ] Task: Refactor `src/pipeline.py`.
    - [ ] Sub-task: Add a 10-second wait (`time.sleep(10)`) before processing each audio chunk.
    - [ ] Sub-task: Remove PDF conversion steps and `PdfConverter` dependency.
    - [ ] Sub-task: Update pipeline to save Markdown output to a `notes/` directory.
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)

## Phase 5: Cleanup & Final Integration
- [ ] Task: Remove `src/gemini_wrapper.py` and `src/pdf_converter_py.py`.
- [ ] Task: Clean up `zaknotes.py` menu (remove model selector, old Gemini CLI refs).
- [ ] Task: Verify overall flow and ensure quota tracking/resetting is triggered before each video.
- [ ] Task: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md)
