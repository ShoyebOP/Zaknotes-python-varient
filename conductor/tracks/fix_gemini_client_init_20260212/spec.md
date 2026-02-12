# Specification: Fix `google-genai` Client Initialization Error

## Overview
The application is failing during the transcription phase with a `TypeError: Client.__init__() got an unexpected keyword argument 'config'`. This error appeared suddenly after the project was working correctly for multiple sessions. The project uses `uv` for dependency management, and the user frequently clones the repository into GitHub Codespaces, which might lead to environment discrepancies.

## Functional Requirements
- Identify the correct way to initialize the `google-genai` `Client` based on the currently installed version.
- Update `src/gemini_api_wrapper.py` to fix the `TypeError`.
- Ensure the fix is robust against minor version differences or clarifies the required version in `pyproject.toml`.

## Non-Functional Requirements
- **Reliability:** The fix should restore the transcription functionality across different environments (local and Codespaces).
- **Maintainability:** Use idiomatic patterns for the `google-genai` SDK.

## Acceptance Criteria
- [ ] The command `zaknotes.py` (or equivalent `uv run` command) can successfully initiate a transcription task without the `Client.__init__` error.
- [ ] Automated tests for `GeminiAPIWrapper` pass.
- [ ] The environment is synchronized using `uv sync` and verified to work.

## Out of Scope
- Upgrading to a completely different AI provider.
- Major refactoring of the `JobManager` or `Pipeline` unless directly required by the fix.
