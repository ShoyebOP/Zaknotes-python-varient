# Specification: Gemini API Integration & Refactor

## Overview
This track involves migrating the Zaknotes project from using the `gemini` CLI tool to the official Gemini API (`google-generativeai`). This includes implementing a robust API key management system with quota tracking and automatic key cycling, simplifying audio processing, and refactoring the output from PDF to raw Markdown.

## Functional Requirements
- **Gemini API Migration:**
    - Replace `GeminiCLIWrapper` with a new `GeminiAPIWrapper` using `google-genai`.
    - Hardcode models: `gemini-2.5-flash` for transcription and `gemini-3-flash-preview` for note generation.
    - Remove all model selection logic from the CLI and configuration.
- **API Key Management:**
    - Create an API key manager (similar to `cookie_manager.py`) to add, remove, and list API keys.
    - Store keys and their usage data in a persistent file (e.g., `keys/api_keys.json`).
- **Quota Tracking & Key Cycling:**
    - Implement a tracking system for each API key: 20 requests per day per model.
    - Automatically cycle to the next available API key when the current key's quota for the required model is exhausted.
    - Quota resets at midnight Pacific Time (PT).
- **Accurate Time Synchronization:**
    - Fetch the current time from a public time API (e.g., `worldtimeapi.org`) before starting each new video to ensure accurate quota resets regardless of server local time.
- **Audio Processing Simplification & Refinement:**
    - Support configurable `segment_time` (default 1800s / 30m).
    - Retain silence removal but increase the silence threshold for safety (e.g., `-50dB`).
    - Hardlock the bitrate to an optimal transcription value (e.g., `48k` or `64k`) and remove scaling logic.
- **Output Refactor:**
    - Remove PDF generation logic (Pandoc, Playwright PDF).
    - Save notes as raw Markdown files in a dedicated `notes/` directory.
- **CLI Cleanup:**
    - Remove Gemini CLI related options from the main menu and sub-menus.
    - Remove model configuration options.
    - Add "Configure Audio Chunking Time" to the main menu.
- **Processing Flow:**
    - Add a 10-second wait before processing each audio chunk.
- **Meta-Instruction (Agent):**
    - The agent (Gemini CLI) is instructed to push changes to the remote repository automatically after successful task completion.

## Non-Functional Requirements
- **Reliability:** The system should gracefully handle API key failures or empty key lists.
- **Accuracy:** Quota tracking must be precise to avoid "429 Too Many Requests" errors from the Gemini API.

## Acceptance Criteria
- [ ] Gemini CLI is no longer used or referenced in the active codebase.
- [ ] API keys can be managed via the CLI.
- [ ] Transcription uses `gemini-2.5-flash` and note generation uses `gemini-3-flash-preview`.
- [ ] API key cycling works correctly when quotas are hit.
- [ ] Quota resets occur correctly at midnight PT.
- [ ] Audio is chunked into configurable parts (default 30m).
- [ ] Output is saved as `.md` files in `notes/` directory.
- [ ] No PDF files are generated.

## Out of Scope
- Support for other LLM providers.
- Advanced UI/TUI (remains planned but not part of this track).
