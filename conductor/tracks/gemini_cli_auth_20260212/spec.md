# Specification: Transition to Gemini CLI Auth & Internal API

## Overview
This track involves a major architectural shift: replacing the standard Gemini API key authentication with the internal OAuth2 flow and `v1internal` endpoints used by the Gemini CLI. We will adapt the existing round-robin cycling logic for account-based auth, implement size-based audio chunking, and ensure full data integrity by removing all truncation from requests and responses.

## Functional Requirements

### 1. Legacy Removal & Adaptation
-   **API Key Removal:** Remove `api_key_manager.py` and all references to standard Gemini API keys.
-   **Logic Adaptation:** Adapt the existing round-robin cycling logic to rotate between multiple `GeminiCliAuthRecord` objects instead of API keys.
-   **Request Usage Tracker:** Replace the quota tracker with a simple numeric logger that tracks:
    -   Account Email/ID.
    -   Model name.
    -   Total count of requests made (e.g., "Account A used gemini-2.0-flash 5 times").
    -   *Note:* This is for tracking only and will not be used for logic gates.
-   **Zero Truncation:** Ensure that NO request payloads (base64 audio) or API responses are shortened or truncated during processing. The full data must flow through the pipeline.

### 2. Gemini CLI Auth & Account Management
-   **Reference:** Use `gemini-cli-auth-files/gemini.ts` as the absolute source of truth for all auth and request logic.
-   **Credential Extraction:** Create a helper script (`src/gemini_creds_helper.py`) to extract `clientId` and `clientSecret` from `gemini-cli` (following the `extractGeminiCliCredentials` logic). If the CLI is missing, prompt the user to run the script elsewhere and paste the output.
-   **Auth Service (`src/gemini_auth_service.py`):**
    -   Implement PKCE-based OAuth2 flow (`generatePkce`, `buildAuthUrl`, `exchangeCodeForTokens`).
    -   **Remote Support:** Support manual entry for redirect URLs/codes for remote environments.
    -   **Auth Refresh:** Automatically refresh tokens every 90 minutes.
    -   **Error Logging:** Create an `error.json` file. If a request fails, save the **full, un-truncated** JSON response and request body to this file for debugging.

### 3. Audio Processing & Size-Based Chunking
-   **Processing:** Silence removal and frequency optimization (existing).
-   **Chunking Logic:** Replace duration-based chunking with a configurable `max_chunk_size_mb` (Default: 15 MB).
-   **Payload:** Convert audio chunks to base64 strings as required by the internal API.

### 4. Internal API Integration (`src/gemini_api_wrapper.py`)
-   **Reference:** Follow `gemini.ts` for endpoints, headers, and JSON body structure.
-   **Endpoints & Headers:** Use the `CODE_ASSIST_ENDPOINT` and `GEMINI_CLI_HEADERS` (User-Agent, X-Goog-Api-Client, Client-Metadata).
-   **Request Structure:** Implement the `v1internal:streamGenerateContent` request format, sending audio as base64 in `inline_data`.
-   **Model Management:** Load models from a new `models.json` file. The user will pick separate models for the transcription and note generation phases via the configuration.

## Non-Functional Requirements
-   **Data Integrity:** Complete payloads in all requests and `error.json`.
-   **Transparency:** Detailed error capture without any shortening.

## Acceptance Criteria
-   [ ] Existing cycling logic is adapted for multiple CLI accounts.
-   [ ] Tokens refresh automatically every 90 minutes.
-   [ ] Audio is chunked by size (MB) and sent as base64 to the internal API per `gemini.ts`.
-   [ ] `error.json` captures full, un-truncated error responses.
-   [ ] `models.json` allows configurable model selection for each step.
-   [ ] Request tracker correctly counts model usage per account.
