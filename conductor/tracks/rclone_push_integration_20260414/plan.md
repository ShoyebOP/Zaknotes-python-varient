# Implementation Plan: Rclone Remote Pushing Integration

## Phase 1: Configuration Management
- [ ] Task: Create `src/rclone_config_manager.py` to manage rclone credentials (remote name and path) stored in `keys/rclone_keys.json`.
- [ ] Task: Update `ConfigManager` in `src/config_manager.py` to include the `rclone_integration_enabled` flag in `DEFAULT_CONFIG`.
- [ ] Task: Write unit tests for `RcloneConfigManager` in `tests/test_rclone_config.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Configuration Management' (Protocol in workflow.md)

## Phase 2: Rclone Service Implementation
- [ ] Task: Create `src/rclone_service.py` implementing a `push_note(local_path, remote_dest)` method using `subprocess.run` to execute `rclone copy`.
- [ ] Task: Implement robust error handling and logging for the `rclone` command.
- [ ] Task: Write unit tests for `RcloneService` in `tests/test_rclone_service.py` (mocking subprocess calls).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Rclone Service Implementation' (Protocol in workflow.md)

## Phase 3: Pipeline Integration
- [ ] Task: Update `ProcessingPipeline` in `src/pipeline.py` to import and initialize `RcloneService` and `RcloneConfigManager`.
- [ ] Task: Modify `execute_job` to include a Step 5.1: Rclone Integration, running sequentially after the Notion push.
- [ ] Task: Ensure appropriate cleanup logic if pushing is successful.
- [ ] Task: Update `tests/test_pipeline.py` or create `tests/test_rclone_pipeline.py` to verify the sequential pushing logic.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Pipeline Integration' (Protocol in workflow.md)

## Phase 4: CLI Menu Integration
- [ ] Task: Implement `manage_rclone_settings()` in `zaknotes.py` to allow users to configure and toggle the Rclone integration.
- [ ] Task: Add a new entry "Manage Rclone Settings" to the `main_menu()` in `zaknotes.py`.
- [ ] Task: Implement the warning message when both Rclone and Notion integrations are enabled.
- [ ] Task: Update `tests/test_cli_structure.py` to verify the new menu option and configuration flow.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: CLI Menu Integration' (Protocol in workflow.md)

## Phase 5: Final Verification
- [ ] Task: Perform end-to-end manual testing of the complete flow: local generation -> Notion push -> Rclone push.
- [ ] Task: Verify that enabling/disabling via the menu works as expected and persists correctly.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Final Verification' (Protocol in workflow.md)
