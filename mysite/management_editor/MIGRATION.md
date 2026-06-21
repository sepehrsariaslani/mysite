# Migration Notes (`mysite.api` -> `mysite.management_editor`)

## What moved

- Editor payload/load/save/history/restore logic moved to:
  - `mysite.management_editor.api`
  - `mysite.management_editor.target_resolver`
  - `mysite.management_editor.overrides`
  - `mysite.management_editor.history`
  - `mysite.management_editor.store`
  - `mysite.management_editor.errors`

## Backward compatibility

- Public routes remain unchanged:
  - `mysite.api.get_management_visual_editor_payload`
  - `mysite.api.save_management_visual_editor_changes`
  - `mysite.api.get_management_visual_editor_history`
  - `mysite.api.restore_management_visual_editor_history`

- `mysite/api.py` now acts as thin facade and delegates to `management_editor.api`.

## Save-path hardening

- Save now always returns parseable JSON payloads.
- `target_file` only mode works without mandatory `route`.
- Error payload contract is unified (`ok`, `message`, `exc_type`, `exception`).
