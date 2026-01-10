# Plan: Replace AI Studio with Gemini CLI for Audio Processing

This plan outlines the steps to transition the Zaknotes pipeline from browser-based automation to a direct integration with the Gemini CLI, incorporating robust audio processing and fail-fast job management.

## Phase 1: Environment Setup & Configuration [checkpoint: 4feb04d]
- [x] Task: Prepare project structure by creating the `pdfs/` directory. ba412ce
- [x] Task: Update `zaknotes.py` CLI menu: b224d9d
    - Remove "Refresh Browser Profile".
    - Add "Configure Gemini Models" to allow setting models for transcription and note generation.
    - Add "Cleanup Stranded Audio Chunks" utility.
- [x] Task: Implement `ConfigManager` to persist model preferences and other settings in a `config.json` file. 04b22fc
- [x] Task: Conductor - User Manual Verification 'Phase 1: Environment Setup & Configuration' (Protocol in workflow.md) 4feb04d
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Environment Setup & Configuration' (Protocol in workflow.md)

## Phase 2: Audio Processing Module (ffmpeg Integration)
- [ ] Task: TDD - Implement `AudioProcessor.get_file_size` and `AudioProcessor.is_under_limit` (20MB threshold).
- [ ] Task: TDD - Implement `AudioProcessor.reencode_audio` using `ffmpeg` to reduce bitrate if a file/chunk exceeds 20MB.
- [ ] Task: TDD - Implement `AudioProcessor.split_into_chunks` using `ffmpeg` to create 30-minute segments.
- [ ] Task: TDD - Implement `AudioProcessor.process_for_transcription` to orchestrate the "Check Size -> Split if needed -> Re-validate chunk sizes" logic.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Audio Processing Module (ffmpeg Integration)' (Protocol in workflow.md)

## Phase 3: Gemini CLI Integration
- [ ] Task: TDD - Implement `GeminiCLIWrapper.run_command` to handle subprocess execution of the `gemini` tool and capture JSON output/errors.
- [ ] Task: TDD - Implement `TranscriptionService.transcribe_chunks` to process audio files/chunks, extract text from JSON, and append to a job-specific `.txt` file.
- [ ] Task: TDD - Implement `NoteGenerationService.generate` to send the consolidated transcript to Gemini (using the specified prompt) and save the `.md` output.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Gemini CLI Integration' (Protocol in workflow.md)

## Phase 4: Pipeline Orchestration & Fail-Fast Logic
- [ ] Task: TDD - Implement `ProcessingPipeline.execute_job` to link downloader, audio processing, transcription, note generation, and existing PDF conversion.
- [ ] Task: Implement Batch Management logic: If one job in a session fails, update the status of all other "in-progress" or "queued" jobs in that batch to `failed`.
- [ ] Task: Implement `FileCleanupService` for automatic deletion of intermediate files (chunks, `.txt`, `.md`) after each successful stage and final completion.
- [ ] Task: Integrate the new pipeline into `zaknotes.py`'s `run_processing_pipeline`.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Pipeline Orchestration & Fail-Fast Logic' (Protocol in workflow.md)
