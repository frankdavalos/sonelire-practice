# Sonelire Practice

An informal, adult-led alphabet tool: an adult **Checks** what a **Learner** knows, records **Marks**, and uses the resulting **Results** to build a targeted **Practice deck**. A phone **Companion** can stand in for the paper scoring sheet.

## Language

### Who and what is measured

**Learner**:
One of two fixed, anonymous profiles ("Child 1", "Child 2") whose Results are kept separate.
_Avoid_: Child, student, user, profile

**Skill**:
What the adult asks for: the letter **name** or a familiar letter **sound**.
_Avoid_: Mode, type

**Case**:
Which letterforms are in play: **uppercase**, **lowercase**, or **mixed** (both forms as separate items).
_Avoid_: Deck type, alphabet

### Checking

**Check**:
One adult-led, feedback-free presentation of a fixed letter sequence to a Learner for one Skill and Case.
_Avoid_: Assessment, test, session, screening

**Form**:
The prepared, identified letter sequence for a Check (form ID, Skill, Case, order); never carries the Learner.
_Avoid_: Sheet (unless meaning the printed copy), assessment form

**Presentation**:
The child-facing phase of a Check, showing one large letter at a time; pausing is a screen within it, not a separate phase.
_Avoid_: Stimulus, display

**Marking**:
The adult-only phase of a Check after Presentation ends, in which Marks for shown letters are entered, imported, reviewed and saved.
_Avoid_: Scoring, enter results

**Shown count**:
How many letters of the Form were actually displayed before Presentation ended; only these can be marked.
_Avoid_: Progress, position

**Mark**:
The adult's recorded judgement for one shown letter: **Correct**, **Incorrect**, **Unsure** (unsure or no response), or **Skip** (not actually assessed).
_Avoid_: Score, response, answer, miss

**Unfinished check**:
A Check that has begun but whose Marks are not yet saved; at most one exists across both Learners.
_Avoid_: Draft, session, pending check

### Outcomes

**Result**:
The latest saved Mark for one Learner, Skill and letter, with its date and Form ID.
_Avoid_: Score, record, history

**Check record**:
The permanent, dated record of one saved Check: its Learner, Skill, Case, Form ID, Shown count and the Mark for each shown letter, Skips included. Never changed after saving, except that **Clear these results** removes the cleared letters' Marks from it, and deletes it if no Marks are left.
_Avoid_: Result, history entry, session log

**Check log**:
Every Check record saved on this device, kept beside the Results under its own storage key; the source for looking back over time.
_Avoid_: History (as a synonym for Results), audit log

**Backup file**:
A downloaded, versioned JSON copy of both Learners' Results and the whole Check log (`sonelire-backup-<YYYY-MM-DD>.json`), never the Unfinished check. Restoring one replaces all Results and the Check log after a preview; a damaged or wrong file is refused with nothing changed.
_Avoid_: Export (alone), sync, snapshot

**Needs practice**:
A letter whose Result is Incorrect or Unsure.
_Avoid_: Weak, failed, missed

**Improved**:
A letter whose latest non-Skip Mark in the Check log is Correct after an earlier Incorrect or Unsure. A letter that slips back to Incorrect or Unsure Needs practice again.
_Avoid_: Fixed, mastered, learned

**Standing**:
A letter's latest non-Skip Mark in the Check log for one Learner and Skill, or none if it has only Skips or no Marks.
_Avoid_: Status, current score

**Latest change**:
How each letter's Standing moved in the latest Check that includes any of the Case's letters, compared with its Standing just before that Check; the only notion of "recent" (no clock or date cutoff).
_Avoid_: Last 30 days, recent window, trend

**Recent win**:
A letter whose Standing became Correct in the Latest change after being Incorrect or Unsure; the newest part of Improved, marked ↑ on the grid.
_Avoid_: Recently improved, newly correct, progress

**Slipped back**:
A letter whose Standing became Incorrect or Unsure in the Latest change after being Correct; marked ↓ on the grid.
_Avoid_: Revisit, regressed, forgot

**Still learning**:
A letter that Needs practice and did not just Slip back, whether it struggled before or was first checked in the latest Check.
_Avoid_: Struggling, weak, still needs practice (Struggled before's wider list)

**Not checked yet**:
A letter with no Result, or whose only Result is Skip (so no Standing); neither a strength nor a weakness.
_Avoid_: Not assessed, yet to check, unchecked, unknown

**Practice deck**:
An ordered set of letter cards for practice, either all letters of a Case or only those that Need practice.
_Avoid_: Flashcards, lesson

### Companion transfer

**Companion**:
The phone page that acts as a private scoring sheet for one Form.
_Avoid_: Phone app, remote, controller

**Companion record**:
The Companion's locally stored Marks and position for one Form, independent of the Unfinished check.
_Avoid_: Companion session, draft

**Form code**:
The versioned text encoding of a Form (`SON1A.…`) carried to the Companion in a QR link.
_Avoid_: Assessment link, form URL

**Results code**:
The versioned text encoding of a Form plus Marks (`SON1R.…`) carried back by QR, pasted code or text file.
_Avoid_: Return code, export

**Import**:
Validating a Results code against the Unfinished check and replacing its Marks.
_Avoid_: Sync, merge, upload

## Relationships

- A **Learner** has at most one **Result** per **Skill** per letter; uppercase and lowercase are different letters.
- A **Check** has exactly one **Form**, one **Learner**, one **Skill** and one **Case**.
- A **Check** produces one **Mark** per shown letter (the first **Shown count** letters of the **Form**).
- Saving a **Check** turns each **Mark** into the **Learner's** **Result** for that letter, except that **Skip** never overwrites an existing **Result**.
- Saving a **Check** also adds one **Check record** to the **Check log**; saving the same **Form** again replaces its **Check record**. A discarded **Unfinished check** is never recorded.
- **Results** keep only the latest **Mark**; the **Check log** keeps every saved **Mark**, so it can show what a **Learner** struggled with before.
- A **Backup file** holds **Results** and **Check records** for both **Learners**; restoring it leaves the **Unfinished check** and the selected **Learner** alone.
- Within one Learner, Skill and Case, each letter is exactly one of **Recent win**, Correct (no group), **Slipped back**, **Still learning** or **Not checked yet**, decided by its **Standing** before and after the **Latest change**; every letter that Needs practice is either **Slipped back** or **Still learning**.
- With only one Check there is no **Latest change** to compare against: no **Recent wins**, no **Slipped back**, and every letter that Needs practice is **Still learning**.
- A **Practice deck** for "Needs practice" is derived from **Results**; practising never changes **Results**.
- A **Companion record** belongs to exactly one **Form** and knows nothing about the **Learner**.
- An **Import** succeeds only when the **Results code's** **Form** matches the **Unfinished check's** **Form** and has no **Marks** beyond the **Shown count**.

## Example dialogue

> **Dev:** "If the parent ends Presentation after 10 letters, does the Results code still carry 52 Marks?"
> **Domain expert:** "It carries 52 positions, but only the first 10 (the Shown count) may hold Marks. A Mark beyond that means the phone and iPad got out of step, so Import rejects it."
> **Dev:** "And a Skip on letter `b` when `b` already has an Incorrect Result?"
> **Domain expert:** "The Result stays Incorrect, so `b` still Needs practice. Skip means it wasn't assessed, not that it was learned."

## Flagged ambiguities

- "assessment", "letter check" and "session" were used for the same thing. Resolved: **Check**. The **Assess** tab name and the README's "assessment" are UI/marketing wording.
- "score" (code: `scores`, `saveScores`, `setScore`) and "mark" (UI, protocol) were used for the same thing. Resolved: **Mark**. "Score" is avoided.
- "draft" (stored field `draft`) and "unfinished check" (UI). Resolved: **Unfinished check**. The stored field keeps its name; `storage.js` exposes it as `unfinishedCheck`.
- "miss" (stored value) and "Incorrect" (UI, wire char `I`). Resolved: **Incorrect**. The stored value `'miss'` remains for compatibility with existing localStorage data until a migration is decided.
- "scoring" (stored status, `startScoring`) and "Enter results" (UI) name the same phase. Resolved: **Marking**. The stored statuses `'present'` and `'paused'` both mean **Presentation**; only Presentation and Marking are real phases.
- "session" was also used for the phone's local state ("Clear this companion session"). Resolved: that is the **Companion record**, distinct from the **Unfinished check**.
- "Not assessed" (glossary, stats row, code: `notAssessed`), "Not checked" (grid cells) and "Yet to check" (mockups) named the same letters. Resolved: **Not checked yet**, matching **Check**. The `notAssessed` field may keep its name.
