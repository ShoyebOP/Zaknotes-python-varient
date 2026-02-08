# Implementation Plan: System Instruction Integration & Transcription Refinement

## Phase 1: Preparation and Environment
- [x] Task: Review `src/gemini_api_wrapper.py` and `src/prompts.py` to identify all injection points for `system_instruction`.
- [x] Task: Audit `tests/` to identify all tests mocking or asserting Gemini API calls.
- [x] Task: Conductor - User Manual Verification 'Preparation and Environment' (Protocol in workflow.md) [047bfa7]

## Phase 2: Prompt Refinement (src/prompts.py)
- [x] Task: Update `TRANSCRIPTION_PROMPT` to include Clean Verbatim and Language Preservation (Bangla/English) rules. [ab8c774]
- [x] Task: Conductor - User Manual Verification 'Prompt Refinement' (Protocol in workflow.md) [047bfa7]

## Phase 3: API Wrapper Refactor (src/gemini_api_wrapper.py)
- [x] Task: Modify `GeminiAPIWrapper.generate_content` (or equivalent method) to accept and pass `system_instruction` to the `google-genai` SDK. [ab8c774]
- [x] Task: Update calls within `src/gemini_api_wrapper.py` to ensure `system_instruction` is correctly utilized for both transcription and note generation. [ab8c774]
- [x] Task: Conductor - User Manual Verification 'API Wrapper Refactor' (Protocol in workflow.md) [047bfa7]

## Phase 4: Test Suite Updates
- [x] Task: Update `tests/test_gemini_api_wrapper.py` to verify that `system_instruction` is being passed correctly to the mocked Gemini client. [047bfa7]
- [x] Task: Update any integration tests in `tests/test_note_generation_service.py` or `tests/test_audio_processor.py` that rely on the old prompt structure. [047bfa7]
- [x] Task: Verify Clean Verbatim and Language Preservation rules via a specialized test case (e.g., mocking a mixed-language audio response). [047bfa7]
- [x] Task: Conductor - User Manual Verification 'Test Suite Updates' (Protocol in workflow.md) [047bfa7]

## Phase 5: Verification and Finalization
- [x] Task: Run full test suite with coverage reporting. [047bfa7]
- [x] Task: Perform a manual dry-run with the CLI to ensure transcription and note generation still work end-to-end. [047bfa7]
- [x] Task: Conductor - User Manual Verification 'Verification and Finalization' (Protocol in workflow.md) [047bfa7]
