# Implementation Plan: Gemini API Integration & Refactor

This plan outlines the migration from the Gemini CLI to the official Google Generative AI API, including API key management, quota tracking, and output refactoring.

## Phase 1: Environment & Dependency Setup [checkpoint: e0e215a]
- [x] Task: Add `google-genai` using `uv add google-genai`. 7b480f7
- [x] Task: Create `keys/` directory and ensure it is ignored by git. 9a28f6d
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) e0e215a

## Phase 2: API Key & Quota Management [checkpoint: 8e1d2e3]
- [x] Task: Implement `src/api_key_manager.py` for managing keys and tracking usage. 1511e80
    - [x] Sub-task: Implement `APIKeyManager` class with `add_key`, `remove_key`, `list_keys` methods.
    - [x] Sub-task: Implement `get_available_key(model)` logic with cycling and quota checking.
    - [x] Sub-task: Implement `reset_quotas_if_needed()` using `worldtimeapi.org` or similar for PT midnight.
- [x] Task: Add API Key Management to the main menu in `zaknotes.py`. bc6c60a
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) 8e1d2e3

## Phase 3: Gemini API Wrapper & Prompt Refactor [checkpoint: f9eaa58]
- [x] Task: Modify `src/prompts.py` to remove file path references from `NOTE_GENERATION_PROMPT`. dc3d2b8
- [x] Task: Create `src/gemini_api_wrapper.py` using `google-genai`. 9162e14
    - [x] Sub-task: Implement `generate_content` method that handles API calls and key rotation.
    - [x] Sub-task: Hardcode model names: `gemini-2.5-flash` and `gemini-3-flash-preview`.
- [x] Task: Update `src/transcription_service.py` and `src/note_generation_service.py` to use `GeminiAPIWrapper`. 425d495
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md) f9eaa58

## Phase 4: Audio Processing & Output Refactor [checkpoint: 00375ca]
- [x] Task: Update `src/audio_processor.py`. b5524a5
    - [x] Sub-task: Support configurable `segment_time` (default 1800s).
    - [x] Sub-task: Retain silence removal but increase the silence threshold for safety (e.g., `-50dB`).
    - [x] Sub-task: Hardlock the bitrate to an optimal transcription value (e.g., `48k` or `64k`) and remove scaling logic.
- [x] Task: Add "Configure Audio Chunking Time" (default 30m) to the main menu in `zaknotes.py`. 8aa1f88
- [x] Task: Refactor `src/pipeline.py`. 00375ca
    - [x] Sub-task: Add a 10-second wait (`time.sleep(10)`) before processing each audio chunk.
    - [x] Sub-task: Remove PDF conversion steps and `PdfConverter` dependency.
    - [x] Sub-task: Update pipeline to save Markdown output to a `notes/` directory.
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md) 00375ca

## Phase 5: Cleanup & Final Integration [checkpoint: f829428]
- [x] Task: Remove `src/gemini_wrapper.py` and `src/pdf_converter_py.py`. c7535bc
- [x] Task: Clean up `zaknotes.py` menu (remove model selector, old Gemini CLI refs). aa783d1
- [x] Task: Verify overall flow and ensure quota tracking/resetting is triggered before each video. f829428
- [x] Task: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md) f829428
