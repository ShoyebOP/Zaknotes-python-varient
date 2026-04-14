# Implementation Plan: Rclone Remote Pushing Integration

## Phase 1: Configuration Management [checkpoint: 930c2d2]
- [x] Task: Create `src/rclone_config_manager.py` to manage rclone credentials (remote name and path) stored in `keys/rclone_keys.json`. (7281c7d)
- [x] Task: Update `ConfigManager` in `src/config_manager.py` to include the `rclone_integration_enabled` flag in `DEFAULT_CONFIG`. (076e09b)
- [x] Task: Write unit tests for `RcloneConfigManager` in `tests/test_rclone_config.py`. (9a60e60)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Configuration Management' (Protocol in workflow.md) (930c2d2)

## Phase 2: Rclone Service Implementation [checkpoint: 353e45f]
- [x] Task: Create `src/rclone_service.py` implementing a `push_note(local_path, remote_dest)` method using `subprocess.run` to execute `rclone copy`. (49be88a)
- [x] Task: Implement robust error handling and logging for the `rclone` command. (49be88a)
- [x] Task: Write unit tests for `RcloneService` in `tests/test_rclone_service.py` (mocking subprocess calls). (4d093b1)
- [x] Task: Conductor - User Manual Verification 'Phase 2: Rclone Service Implementation' (Protocol in workflow.md) (353e45f)

## Phase 3: Pipeline Integration [checkpoint: a2ac91d]
- [x] Task: Update `ProcessingPipeline` in `src/pipeline.py` to import and initialize `RcloneService` and `RcloneConfigManager`. (0313364)
- [x] Task: Modify `execute_job` to include a Step 5.1: Rclone Integration, running sequentially after the Notion push. (983f2d2)
- [x] Task: Ensure appropriate cleanup logic if pushing is successful. (983f2d2)
- [x] Task: Update `tests/test_pipeline.py` or create `tests/test_rclone_pipeline.py` to verify the sequential pushing logic. (be74f67)
- [x] Task: Conductor - User Manual Verification 'Phase 3: Pipeline Integration' (Protocol in workflow.md) (a2ac91d)

## Phase 4: CLI Menu Integration [checkpoint: 8fef007]
- [x] Task: Implement `manage_rclone_settings()` in `zaknotes.py` to allow users to configure and toggle the Rclone integration. (66048a1)
- [x] Task: Add a new entry "Manage Rclone Settings" to the `main_menu()` in `zaknotes.py`. (8673322)
- [x] Task: Implement the warning message when both Rclone and Notion integrations are enabled. (66048a1)
- [x] Task: Update `tests/test_cli_structure.py` to verify the new menu option and configuration flow. (70b423c)
- [x] Task: Conductor - User Manual Verification 'Phase 4: CLI Menu Integration' (Protocol in workflow.md) (8fef007)

## Phase 5: Final Verification [checkpoint: 3481d71]
- [x] Task: Perform end-to-end manual testing of the complete flow: local generation -> Notion push -> Rclone push. (29713c2)
- [x] Task: Verify that enabling/disabling via the menu works as expected and persists correctly. (29713c2)
- [x] Task: Conductor - User Manual Verification 'Phase 5: Final Verification' (Protocol in workflow.md) (3481d71)
