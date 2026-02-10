# Implementation Plan - Notion Integration

This plan outlines the integration of Notion as an automated storage backend for generated notes, including configuration, pipeline integration, and legacy note migration.

## Phase 1: Configuration & Credential Management [checkpoint: c4b30e2]
- [x] Task: Create `keys/notion_keys.json` structure and initial configuration `notion_integration_enabled` in `config.json` 83caee6
- [x] Task: Implement `src/notion_config_manager.py` to handle Notion-specific credentials and settings cde23c2
- [x] Task: Update `zaknotes.py` main menu (`Manage API Keys`) to include Notion setup options 91f1a29
- [x] Task: Conductor - User Manual Verification 'Phase 1: Configuration & Credential Management' (Protocol in workflow.md)

## Phase 2: Notion Integration Service
- [x] Task: Create `src/notion_service.py` skeleton with basic Notion API connectivity tests 6d4d9bb
- [x] Task: Implement Markdown to Notion block parsing (adapted from `md2notion/` with modern API checks) e5a9cff
- [ ] Task: Implement Notion page creation and block batching (100 blocks/2000 chars limits)
- [ ] Task: Implement error handling for API failures and rate limits
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Notion Integration Service' (Protocol in workflow.md)

## Phase 3: Pipeline & Feature Integration
- [ ] Task: Integrate Notion service into `src/pipeline.py` as a post-generation step
- [ ] Task: Implement conditional local file deletion based on Notion push success
- [ ] Task: Implement "Process Old Notes" logic and add it to the `Start Note Generation` menu in `zaknotes.py`
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Pipeline & Feature Integration' (Protocol in workflow.md)

## Phase 4: Finalization & Cleanup
- [ ] Task: Update `README.md` with Notion integration setup and usage instructions
- [ ] Task: Delete the `md2notion/` directory and all its contents
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Finalization & Cleanup' (Protocol in workflow.md)
