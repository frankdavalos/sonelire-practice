# Keep Check records under their own storage key; Results stay the stored truth

Looking back at what a Learner struggled with needs every saved Mark, but a Result keeps only the latest one. Each saved Check therefore also becomes a **Check record** in a **Check log**, stored under its own localStorage key (`sonelire-check-log-v1`, `{version: 1, checks, lastBackup}`). The v1 blob (`sonelire-practice-v2`) is untouched, so ADR 0001 still holds. The Check log is new data, so it uses the CONTEXT.md vocabulary directly (`incorrect`, not `'miss'`).

A Check is saved by writing the Check log first and the v1 blob second. If the Check log write fails, the v1 blob is not written and the Check stays in Marking. If the second write fails after the first succeeded, saving again replaces the Check record with the same Form ID instead of adding a second one. When the browser's storage can't be reached at page load, the page works in memory for that visit, so Checks can still be saved until a reload. Saved data that is reachable but unreadable is replaced by the next save, as before.

## Considered Options

- **Add the Check log inside the v1 blob**: rejected. A page from an older release that is still open would save the blob without the new field and silently delete the history; old code never touches a separate key.
- **Work Results out from the Check log** (one source of truth): rejected for now. It changes the stored shape and the Results module, the migration ADR 0001 avoids, for no visible gain. Reopen it if undoing a mistaken Check is ever needed, since Results alone cannot restore the Mark a Check overwrote.
- **Seed the Check log from existing Results**: not needed. All saved data so far is test data, so history starts empty.
