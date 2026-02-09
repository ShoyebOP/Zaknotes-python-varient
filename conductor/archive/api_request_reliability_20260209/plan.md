# Implementation Plan: API Request Timeout, Retry, and Key Rotation

## Phase 1: Configuration Updates [checkpoint: 55154a8]
- [x] Task: Update `ConfigManager.DEFAULT_CONFIG` with new API settings. (commit: d062514)
    - Add `api_timeout`: 300
    - Add `api_max_retries`: 3
    - Add `api_retry_delay`: 10
- [x] Task: Verify `config.json` is updated with default values if they are missing. (commit: 5957711)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Configuration Updates' (Protocol in workflow.md) (commit: 55154a8)

## Phase 2: Key Rotation Logic [checkpoint: 40ff836]
- [x] Task: Modify `APIKeyManager` to support round-robin key selection. (commit: a6cf61f)
    - Add a `last_key_index` tracker (can be persistent or in-memory for the session).
    - Update `get_available_key(model)` to start searching from the key after the last one used.
- [x] Task: Update `tests/test_api_key_manager.py` to verify that consecutive calls to `get_available_key` return different keys when multiple are available. (commit: 2f9de57)
- [x] Task: Conductor - User Manual Verification 'Phase 2: Key Rotation Logic' (Protocol in workflow.md) (commit: 40ff836)

## Phase 3: Timeout and Retry Implementation [checkpoint: c159d1d]
- [x] Task: Update `GeminiAPIWrapper.__init__` to load timeout and retry config from `ConfigManager`. (commit: e12e5c3)
- [x] Task: Modify `GeminiAPIWrapper._get_client` to apply `api_timeout` to the `genai.Client`. (commit: e12e5c3)
- [x] Task: Implement retry loop in `GeminiAPIWrapper.generate_content` for timeout exceptions. (commit: e12e5c3)
- [x] Task: Implement retry loop in `GeminiAPIWrapper.generate_content_with_file`. (commit: e12e5c3)
- [x] Task: Conductor - User Manual Verification 'Phase 3: Timeout and Retry Implementation' (Protocol in workflow.md) (commit: c159d1d)

## Phase 4: Verification [checkpoint: 1389c5c]
- [x] Task: Create `tests/test_api_reliability_mechanisms.py` to test both rotation and timeout/retry behavior together. (commit: 080ab3f)
- [x] Task: Verify key exhaustion behavior triggers a switch to a new (rotated) key. (commit: 080ab3f)
- [x] Task: Conductor - User Manual Verification 'Phase 4: Verification' (Protocol in workflow.md) (commit: 1389c5c)
