# Specification: API Request Reliability (Timeout, Retry, and Rotation)

## Overview
This track implements a robust timeout and retry mechanism for all Gemini API interactions, alongside a mandatory round-robin API key rotation strategy. This ensures high availability, prevents single-key rate-limiting, and handles slow or hanging API requests gracefully.

## Functional Requirements

### 1. Mandatory Key Rotation (Round-Robin)
- The system must NOT stick to a single API key until exhaustion.
- For every new request (transcription or note generation), the `APIKeyManager` must provide the *next* available key in a round-robin fashion.
- If multiple keys are available and non-exhausted, each consecutive request should use a different key.

### 2. Configurable Timeout
- A new configuration setting `api_timeout` will be added to `config.json`.
- **Default value:** 300 seconds (5 minutes).
- This timeout applies to all `google-genai` client operations, including file uploads and content generation.

### 3. Configurable Retry Logic
- Two new configuration settings will be added to `config.json`:
    - `api_max_retries`: Maximum retries for a timed-out request. (Default: 3)
    - `api_retry_delay`: Wait time (seconds) before retrying a timed-out request. (Default: 10)

### 4. Timeout Handling and Retries
- If a request to the Gemini API exceeds the `api_timeout`:
    1. The application will catch the timeout exception.
    2. It will log the timeout event.
    3. It will wait for `api_retry_delay` seconds.
    4. It will retry the request using the same API key (to avoid burning another key's quota for the same task prematurely), up to `api_max_retries` times.

### 5. Key Exhaustion on Persistent Timeout
- If a request fails due to a timeout after the maximum number of retries:
    1. The API key used for that request will be marked as "exhausted" for the specific model.
    2. The application will then rotate to the next available API key for subsequent attempts.

## Non-Functional Requirements
- **Logging:** All timeouts, retry attempts, and key rotations must be clearly logged in the debug logs.
- **Maintainability:** Rotation logic should reside in `APIKeyManager`, while timeout/retry logic resides in `GeminiAPIWrapper`.

## Acceptance Criteria
- [ ] Consecutive API calls use different non-exhausted keys (if available).
- [ ] `config.json` includes `api_timeout`, `api_max_retries`, and `api_retry_delay`.
- [ ] A simulated timeout triggers a retry after the specified delay using the *same* key for the retry attempts of that specific request.
- [ ] After 3 consecutive timeouts for the same request, the key is marked as exhausted.
- [ ] The application continues with the next available key after a key is marked exhausted.

## Out of Scope
- Implementing timeouts for non-Gemini API network requests.
- Changing the existing 503 retry behavior (which waits 10 minutes and retries indefinitely).
