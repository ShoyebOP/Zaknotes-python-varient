# Implementation Plan: Reliability, UI, and Local Media Refinements

## Phase 1: Reliability - Exponential Backoff and Empty Chunk Retry [checkpoint: d57df60]

- [x] Task 1: Implement Exponential Backoff Logic. [153a906]
    - [x] Create a utility for exponential backoff in `src/gemini_api_wrapper.py` or a dedicated module.
    - [x] Update all static delays (retry, post-chunk, post-generation) to use the new backoff utility.
    - [x] Add unit tests for the backoff utility.
- [x] Task 2: Implement Empty Transcription Chunk Detection. [812f862]
    - [x] Update `src/gemini_api_wrapper.py` (or the relevant service) to identify empty/whitespace responses.
    - [x] Implement an indefinite retry loop for empty chunks using the new exponential backoff.
    - [x] Ensure that a chunk is only marked as "completed" in the state file if it contains non-empty text.
    - [x] Add unit tests to simulate empty Gemini responses and verify the retry behavior.
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: UI/UX - Interactive Local Media and Time-Based Chunking [checkpoint: 26666f6]

- [x] Task 1: Restore Time-Based Chunking. [f4e86cf]
    - [x] Remove the file-based chunking logic from `src/audio_processor.py`.
    - [x] Ensure the existing time-based chunking logic (default 30 mins) is functional.
    - [x] Verify that the "configure audio chunks" menu option correctly updates this setting.
    - [x] Add unit tests for time-based chunking.
- [x] Task 2: Integrate Local Media into the Interactive Menu. [f4e86cf]
    - [x] Modify the main entry point (e.g., `zaknotes.py`) to add a "Process Local Media" option under "start note generation".
    - [x] Update the menu logic to handle the new option, ensuring it triggers the existing local media processing flow.
    - [x] Maintain consistent file naming and chronology logic for local media.
    - [x] Add a basic integration test for the new menu option.
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
