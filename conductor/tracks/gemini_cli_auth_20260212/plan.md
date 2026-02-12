# Implementation Plan: Transition to Gemini CLI Auth & Internal API

This plan outlines the steps to replace the standard Gemini API key authentication with the internal Gemini CLI OAuth2 flow and internal endpoints, as specified in `spec.md`.

## Phase 1: Preparation & Legacy Removal
- [x] Task: Remove Legacy API Key Management
    - [x] Delete `src/api_key_manager.py`.
    - [x] Remove `api_key_manager` references from `src/pipeline.py` and `src/gemini_api_wrapper.py`.
    - [x] Delete `tests/test_api_key_manager.py`, `tests/test_api_rotation.py`, and `tests/test_proactive_quota.py`.
- [x] Task: Remove Truncation and Shortening Logic
    - [x] Audit `src/gemini_api_wrapper.py` and logging statements to remove any logic that truncates request/response data.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Preparation & Legacy Removal' (Protocol in workflow.md)

## Phase 2: Models & Usage Tracking
- [ ] Task: Implement `models.json`
    - [ ] Create `models.json` with a list of available models for transcription and note generation.
    - [ ] Update `src/config_manager.py` to allow selecting different models for different pipeline stages.
- [ ] Task: Implement Request Usage Tracker
    - [ ] Create a simple JSON-based logger to track model usage count per account email.
    - [ ] Write unit tests for the usage tracker.
    - [ ] Implement the usage tracker.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Models & Usage Tracking' (Protocol in workflow.md)

## Phase 3: Auth Service & Credential Helper
- [ ] Task: Create Gemini Credential Helper
    - [ ] Implement `src/gemini_creds_helper.py` to extract `clientId` and `clientSecret` from `gemini-cli` (following `gemini.ts`).
    - [ ] Add logic to handle cases where the CLI is missing by prompting for manual input.
- [ ] Task: Implement Gemini Auth Service
    - [ ] Write unit tests for PKCE flow, token exchange, and refresh logic (mocking Google OAuth endpoints).
    - [ ] Implement `src/gemini_auth_service.py` with:
        - [ ] PKCE challenge/verifier generation.
        - [ ] Token exchange and refresh (90-min interval).
        - [ ] Manual entry mode for remote auth.
        - [ ] Project discovery (`loadCodeAssist`/`onboardUser`).
- [ ] Task: Adapt Rotation Logic
    - [ ] Modify the existing cycling logic to rotate between multiple `GeminiCliAuthRecord` objects.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Auth Service & Credential Helper' (Protocol in workflow.md)

## Phase 4: Audio Processing & Chunking
- [ ] Task: Implement Size-Based Chunking
    - [ ] Write unit tests for size-based chunking logic.
    - [ ] Update `src/audio_processor.py` to replace duration-based chunking with size-based chunking (configurable `max_chunk_size_mb`).
    - [ ] Implement base64 encoding for audio chunks.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Audio Processing & Chunking' (Protocol in workflow.md)

## Phase 5: Internal API Integration
- [ ] Task: Implement `v1internal` API Wrapper
    - [ ] Write unit tests for `streamGenerateContent` request/response handling (mocking `cloudcode-pa.googleapis.com`).
    - [ ] Update `src/gemini_api_wrapper.py` to use endpoints, headers, and request structure from `gemini.ts`.
    - [ ] Implement error logging to `error.json` (full un-truncated payloads).
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Internal API Integration' (Protocol in workflow.md)

## Phase 6: Pipeline Integration & Final Testing
- [ ] Task: Integrate Auth and API into Pipeline
    - [ ] Update `src/pipeline.py` to use the new `GeminiAuthService` and updated `GeminiApiWrapper`.
- [ ] Task: Update Menu and CLI Interface
    - [ ] Add options to the main menu for adding/managing Gemini CLI accounts.
- [ ] Task: End-to-End Verification
    - [ ] Run the full pipeline with multiple accounts to verify cycling, refresh, and successful note generation.
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Pipeline Integration & Final Testing' (Protocol in workflow.md)
