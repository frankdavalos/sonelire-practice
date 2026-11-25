# Keep the v1 localStorage shape; translate to domain names inside the modules

The saved browser data (`sonelire-practice-v2`, `version: 1`, and the Companion's `sonelire-companion-v1:*` keys) uses pre-glossary names: `draft`, `scores`, the status `'scoring'`, the Mark value `'miss'`, and `'present'`/`'paused'` as separate statuses. We keep that shape exactly. The Check, Results and vocabulary modules translate between it and the [CONTEXT.md](../../CONTEXT.md) language (Unfinished check, Marks, Marking, Incorrect, Presentation) only inside `restore()`/`toStored()` and the vocabulary mapping, so callers never see the old names. Parents' existing Results and Unfinished checks must keep loading, and the app has no backup, export or recovery to fall back on if a migration goes wrong.

## Considered Options

- **Versioned migration to domain names** (bump `version`, rewrite stored data on load): rejected for now. It risks irrecoverable loss of local-only records, and it gains nothing callers can see once the translation is behind the module interface. Reopen it if the stored shape has to change for another reason, and do both changes in one migration.
