# Specification: Notion Integration for Zaknotes

## Overview
This track implements a direct integration with Notion, allowing generated notes to be automatically pushed to a specific Notion database. It includes configuration management for Notion credentials and a utility to process existing local notes.

## Functional Requirements

### 1. Configuration Management
- **Notion Credentials:** Store `NOTION_SECRET` and `DATABASE_ID` in `keys/notion_keys.json`.
- **Toggle Integration:** Add a boolean entry `notion_integration_enabled` in `config.json` to enable/disable the push-to-notion step.
- **Menu Integration:** 
    - Update `Manage API Keys` in the main menu to include an option for setting up Notion credentials.

### 2. Pipeline Integration
- **Post-Generation Step:** If `notion_integration_enabled` is true, the pipeline will:
    1.  Convert the generated Markdown note to Notion-compatible blocks.
    2.  Create a new page in the configured Notion database.
    3.  Set the page title to the filename (underscores replaced with spaces, extension removed).
    4.  Push the content blocks to the new page.
- **Cleanup:** 
    - Upon successful push to Notion, the local `.md` file in `notes/` must be deleted.
    - **Fallback:** If the Notion push fails, the local `.md` file is preserved, and the job status is set to `completed_local_only` to prevent data loss.

### 3. "Process Old Notes" Feature
- **Menu Integration:** Add "Process Old Notes" to the `Start Note Generation` sub-menu.
- **Behavior:** 
    - Scans the `notes/` directory for all `.md` files.
    - Pushes each note to Notion using the same logic as the pipeline.
    - Deletes the local file only after a successful push.

### 4. Documentation & Cleanup
- **Documentation:** Update `README.md` and any relevant product documentation to include setup and usage instructions for the Notion integration.
- **Repository Cleanup:** After the track is fully implemented and verified, the `md2notion/` directory (containing the reference repository) must be deleted from the project.

## Technical Details
- Use `notion-client` for API interactions.
- **CRITICAL WARNING:** While the `md2notion/` repository provides a baseline for Markdown parsing, its logic is several months old. **Do not accept its implementation as absolute.** Always cross-reference with the latest Notion API documentation (especially regarding block types, character limits, and request structures) to ensure reliability.
- Adapt the parsing logic into a dedicated service (e.g., `src/notion_service.py`) instead of importing the raw repo.
- Ensure large notes are handled correctly (Notion API has a 100-block limit per request and a 2000-character limit per rich text object).

## Acceptance Criteria
- Notion credentials can be saved and updated via the CLI menu.
- The `notion_integration_enabled` flag correctly controls whether notes are pushed to Notion.
- New notes are successfully pushed to Notion with the correct title and formatting.
- Local notes are deleted ONLY after a successful Notion push.
- The "Process Old Notes" option successfully migrates existing files from `notes/` to Notion.
- Failures in Notion communication do not result in the loss of the generated Markdown note.
- `README.md` reflects the new features.
- The `md2notion/` directory is removed.

## Out of Scope
- Support for multiple Notion databases.
- Syncing changes back from Notion to local storage.
