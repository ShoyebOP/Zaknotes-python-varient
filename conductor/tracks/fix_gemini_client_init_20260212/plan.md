# Plan: Fix `google-genai` Client Initialization Error

## Phase 1: Diagnosis & Environment Alignment
- [x] Task: Environment Synchronization c477d8c
    - [x] Run `uv sync` to ensure local environment matches `uv.lock`.
    - [x] Verify the installed version of `google-genai` using `uv run pip show google-genai`.
- [x] Task: Root Cause Identification c477d8c
    - [x] Examine `src/gemini_api_wrapper.py` to identify where `Client` is initialized with `config`.
    - [x] Consult `google-genai` documentation or SDK source to confirm valid `__init__` arguments for the installed version.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Diagnosis & Environment Alignment' (Protocol in workflow.md)

## Phase 2: Implementation & Bug Fix
- [x] Task: Reproduce Error with Unit Test c477d8c
    - [x] Create/Update `tests/test_gemini_api_wrapper.py` to instantiate `GeminiAPIWrapper` and trigger the error.
    - [x] Confirm the test fails with the specific `TypeError`.
- [x] Task: Fix Client Initialization c477d8c
    - [x] Modify `src/gemini_api_wrapper.py` to correctly initialize the `Client` (e.g., move `config` to the method calls like `models.generate_content` if that is the correct pattern for the current SDK version).
- [x] Task: Verify Fix c477d8c
    - [x] Run the newly created/updated unit test and ensure it passes (Green phase).
    - [x] Run all existing tests in `tests/` to ensure no regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implementation & Bug Fix' (Protocol in workflow.md)

## Phase 3: Final Verification
- [ ] Task: End-to-End Test
    - [ ] Run a small transcription job using `zaknotes.py` to confirm the entire pipeline works.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Verification' (Protocol in workflow.md)
