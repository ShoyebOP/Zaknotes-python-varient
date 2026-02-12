# Implementation Plan: Transition to Gemini CLI Auth & Internal API

This plan outlines the steps to replace the standard Gemini API key authentication with the internal Gemini CLI OAuth2 flow and internal endpoints, as specified in `spec.md`.

## Phase 1: Preparation & Legacy Removal [checkpoint: 79e2b86]
- [x] Task: Remove Legacy API Key Management
    - [x] Delete `src/api_key_manager.py`.
    - [x] Remove `api_key_manager` references from `src/pipeline.py` and `src/gemini_api_wrapper.py`.
    - [x] Delete `tests/test_api_key_manager.py`, `tests/test_api_rotation.py`, and `tests/test_proactive_quota.py`.
- [x] Task: Remove Truncation and Shortening Logic
    - [x] Audit `src/gemini_api_wrapper.py` and logging statements to remove any logic that truncates request/response data.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Preparation & Legacy Removal' (Protocol in workflow.md)

## Phase 2: Models & Usage Tracking [checkpoint: 53fea55]
- [x] Task: Implement `models.json`
    - [x] Create `models.json` with a list of available models for transcription and note generation.
    - [x] Update `src/config_manager.py` to allow selecting different models for different pipeline stages.
- [x] Task: Implement Request Usage Tracker
    - [x] Create a simple JSON-based logger to track model usage count per account email.
    - [x] Write unit tests for the usage tracker.
    - [x] Implement the usage tracker.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Models & Usage Tracking' (Protocol in workflow.md)

## Phase 3: Auth Service & Credential Helper [checkpoint: 05579bc]
- [x] Task: Create Gemini Credential Helper
    - [x] Implement `src/gemini_creds_helper.py` to extract `clientId` and `clientSecret` from `gemini-cli` (following `gemini.ts`).
    - [x] Add logic to handle cases where the CLI is missing by prompting for manual input.
- [x] Task: Implement Gemini Auth Service
    - [x] Write unit tests for PKCE flow, token exchange, and refresh logic (mocking Google OAuth endpoints).
    - [x] Implement `src/gemini_auth_service.py` with:
        - [x] PKCE challenge/verifier generation.
        - [x] Token exchange and refresh (90-min interval).
        - [x] Manual entry mode for remote auth.
        - [x] Project discovery (`loadCodeAssist`/`onboardUser`).
- [x] Task: Adapt Rotation Logic
    - [x] Modify the existing cycling logic to rotate between multiple `GeminiCliAuthRecord` objects.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Auth Service & Credential Helper' (Protocol in workflow.md)

## Phase 4: Audio Processing & Chunking [checkpoint: 6a483c6]
- [x] Task: Implement Size-Based Chunking
    - [x] Write unit tests for size-based chunking logic.
    - [x] Update `src/audio_processor.py` to replace duration-based chunking with size-based chunking (configurable `max_chunk_size_mb`).
    - [x] Implement base64 encoding for audio chunks.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Audio Processing & Chunking' (Protocol in workflow.md)

## Phase 5: Internal API Integration [checkpoint: 9377b46]
- [x] Task: Implement `v1internal` API Wrapper
    - [x] Write unit tests for `streamGenerateContent` request/response handling (mocking `cloudcode-pa.googleapis.com`).
    - [x] Update `src/gemini_api_wrapper.py` to use endpoints, headers, and request structure from `gemini.ts`.
    - [x] Implement error logging to `error.json` (full un-truncated payloads).
- [x] Task: Conductor - User Manual Verification 'Phase 5: Internal API Integration' (Protocol in workflow.md)

## Phase 6: Pipeline Integration & Final Testing [checkpoint: ba55a24]
- [x] Task: Integrate Auth and API into Pipeline
    - [x] Update `src/pipeline.py` to use the new `GeminiAuthService` and updated `GeminiApiWrapper`.
- [x] Task: Update Menu and CLI Interface
    - [x] Add options to the main menu for adding/managing Gemini CLI accounts.
- [x] Task: End-to-End Verification
    - [x] Run the full pipeline with multiple accounts to verify cycling, refresh, and successful note generation.
- [x] Task: Conductor - User Manual Verification 'Phase 6: Pipeline Integration & Final Testing' (Protocol in workflow.md)
