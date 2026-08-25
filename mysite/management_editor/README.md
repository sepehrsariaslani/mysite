# Management Editor Module

This package isolates the `management-editor` backend domain from `mysite/api.py`.

## Public flow

1. `mysite.api.*` whitelisted methods stay unchanged (backward compatible routes).
2. Those methods delegate to `mysite.management_editor.api`.
3. Domain services are split into:
- `target_resolver.py`: route/file/component resolution + preview route.
- `overrides.py`: visual/content normalization + managed CSS extraction/upsert.
- `history.py`: source history snapshot/restore serialization.
- `store.py`: page override JSON storage.
- `errors.py`: JSON-safe error payloads for save endpoint.

## Save contract

`save_management_visual_editor_changes` is guaranteed to return parseable JSON payloads, including errors:

- `ok: false`
- `message`
- `exc_type`
- `exception`

This avoids HTML error bodies that caused `Unexpected token '<'` in frontend parsing.

## Notes

- No DB migration is required.
- Existing API route names remain unchanged.
- Component-only editing is supported (save with `target_file` without mandatory `route`).
