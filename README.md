# Sonelire Practice

**From sounds to stories.**

A simple, parent-led alphabet practice and letter assessment website for young learners. Sonelire Practice helps families identify which letters a child knows, focus practice on letters that need work, and check progress through subsequent informal assessments.

[**Open Sonelire Practice**](https://frankdavalos.github.io/sonelire-practice/sonelire-practice.html) · [**How to use Sonelire Practice**](HOW_TO_USE.md)

## Version 2.1 — digital companion

Use a phone as a private scoring sheet while the iPad displays the assessment letters. Scan the assessment QR before starting, mark responses on the phone, advance the iPad separately, then import the phone results for review. No backend or live synchronization is needed. The original paper workflow remains available.

## Version 2 foundation

Version 2 adds a complete **Assess → Review → Practice → Reassess** workflow to the original letter flashcards. It is designed for a shared iPad, but also works in modern desktop and mobile browsers. No installation, account or server-side database is required.

| Feature | Description |
| --- | --- |
| Two learner profiles | Separate results for Child 1 and Child 2, without entering personal information. |
| Letter practice | Uppercase, lowercase or mixed-case flashcards, in shuffled or alphabetical order. |
| Letter checks | Adult-led checks of letter names or familiar letter sounds. |
| Digital phone companion | Scan a QR to open the matching form; record and recover marks locally, undo or revise, then transfer a results QR, code or text file. |
| Printable companion sheets | Record responses on paper in the same order as the on-screen letters. |
| Child-facing presentation | Large letters with no scoring buttons or correctness feedback; a discreet Pause control remains available. |
| Post-check scoring | Enter correct, incorrect, unsure/no response or skipped marks after presentation. |
| Results | View the latest recorded performance for each letter, case and skill. |
| Targeted practice | Generate a deck of letters marked incorrect or unsure. |
| Local persistence | Save results and resume one unfinished check in the same browser. |
| Andika typography | Literacy-oriented letterforms with large, high-contrast text. |

## Quick start

1. Open the [website](https://frankdavalos.github.io/sonelire-practice/sonelire-practice.html) and select **Child 1** or **Child 2**.
2. Choose **Practice** for ordinary flashcards, or **Assess** to conduct a letter check.
3. For a check, select the skill, case and order, then choose **Prepare check**. Choose **Phone companion QR** and scan with your phone, or print the companion sheet / copy the displayed order onto paper.
4. Choose **Begin check**, ask the child for each letter name or familiar sound, and record responses privately on the phone or paper. Tap to advance the iPad separately after scoring each item.
5. After the check, import phone marks (QR link, code or text file) or enter paper marks, review and save, then open **Results** and select **Practice letters needing work**.
6. Reassess after practice to update the child's letter results.

See the [step-by-step parent guide](HOW_TO_USE.md) for scoring, navigation, practice suggestions and troubleshooting.

## Privacy and storage

Sonelire Practice stores its learner results and unfinished check in the browser's `localStorage`. There are no login accounts, application analytics, audio recordings, or server-side student records. The learner labels are fixed and anonymous.

- Data is separate between browsers, devices and browser storage contexts; it does not synchronize. The phone companion stores its unfinished form separately. Transfer is explicit.
- Clearing site data, using private browsing or browser storage eviction can cause records to be lost.
- The companion can export and import one assessment’s marks; there is no complete database export, backup or recovery feature.
- Andika is loaded from Google Fonts; this makes a third-party font request, but the application does not send assessment results to that service. Hosting providers may retain ordinary request logs.
- Results are stored locally, not encrypted by the application, and are accessible to others using the same browser profile.

Do not use this prototype to store official or sensitive student records. An internet connection is needed for initial hosted access and reliable font loading. There is no service worker or guaranteed offline mode.

## Educational scope

Sonelire Practice is an informal, adult-administered alphabet knowledge tool, not a standardized reading screener or diagnostic instrument. It supports letter naming and parent-directed letter-sound checks, not a validated phoneme assessment. Some letters have multiple legitimate sounds; adults should decide which responses to accept before a check and apply the same rule consistently.

The practice deck is based on the latest recorded incorrect or unsure responses. Practice itself does not modify assessment results. Uppercase and lowercase results and name/sound results are kept separate. The app does not calculate validated mastery levels, reading risk, percentiles or grade-level benchmarks.

This is a lightweight companion prototype for the larger Sonelire literacy assessment and practice project, not its professional edition.

## Run or deploy

The application is a small static website: `sonelire-practice.html`, `companion.html`, the plain scripts `vocabulary.js`, `companion-protocol.js`, `check.js`, `results.js`, `check-log.js`, `storage.js` and `companion-record.js`, and `libs/qr.js`. The QR encoder is bundled locally with license notices in `libs/QR-LICENSE.txt`. There is no build step, npm installation, API or database server.

To run locally from the repository directory:

```bash
python3 -m http.server 8000
```

Open <http://localhost:8000/sonelire-practice.html>. For use on another device, host the file on a static web server or use the public GitHub Pages link above. Local and hosted URLs have separate browser storage.

To publish updates using the existing GitHub Pages deployment:

1. If any script changed (`vocabulary.js`, `companion-protocol.js`, `check.js`, `results.js`, `check-log.js`, `storage.js`, `companion-record.js` or `libs/qr.js`), bump the release token: the `?v=` value on every `<script src>` in both `sonelire-practice.html` and `companion.html`, for example `?v=2.1.1` to `?v=2.1.2`. GitHub Pages lets browsers cache each file for 10 minutes, so without a new token a new page can run with an old cached script. `tests/release-token.test.js` checks that every script carries the same token. It can't tell whether you bumped it.
2. Commit and push. The pre-push hook (see [Testing](#testing)) runs the suite first.

```bash
git add sonelire-practice.html companion.html vocabulary.js companion-protocol.js check.js results.js check-log.js storage.js companion-record.js libs/ README.md HOW_TO_USE.md tests/
git commit -m "Update Sonelire Practice"
git push
```

The application uses [Andika](https://software.sil.org/andika/) via Google Fonts. A sans-serif fallback is used if the font cannot load.

## Project files

| File | Purpose |
| --- | --- |
| [`sonelire-practice.html`](sonelire-practice.html) | Main application |
| [`companion.html`](companion.html) | Phone scoring interface |
| [`vocabulary.js`](vocabulary.js) | Shared Cases and Marks (labels, keys, wire and stored values) |
| [`companion-protocol.js`](companion-protocol.js) | Versioned Form and Results code encoding, companion links, QR rendering |
| [`check.js`](check.js) | Check lifecycle: Form preparation, Presentation, Marking, Import, save |
| [`results.js`](results.js) | Each Learner's Results: recording a saved Check, letter status and totals, Needs practice letters, clearing |
| [`check-log.js`](check-log.js) | The Check log: one Check record per saved Check, the list of past Checks, each letter's history, letters still needing practice or Improved, and its saved form |
| [`storage.js`](storage.js) | Loads and saves the Learner, Results and Unfinished check, and the Check log under its own key, through storage adapters (browser or in-memory) |
| [`companion-record.js`](companion-record.js) | The phone's Companion record: Marks, position, undo, restoring its saved copy and producing the Results code |
| [`CONTEXT.md`](CONTEXT.md), [`docs/adr/`](docs/adr/) | Domain glossary and architecture decisions |
| `libs/` | Bundled QR encoder and license notices |
| `tests/` | Module tests; `tests/browser/` holds the browser scenarios |
| [`README.md`](README.md) | Project overview, features and deployment |
| [`HOW_TO_USE.md`](HOW_TO_USE.md) | Parent-friendly usage guide |

## Release limitations

Version 2.1 retains the latest recorded result per learner, letter and skill rather than a complete longitudinal assessment history. Only one unfinished check can be saved at a time. Skipping a letter in a later check does not erase an existing result for that letter. There is no automated speech recognition, audio playback, cross-device sync, CSV export or full PWA functionality.

For a new issue or suggestion, use the repository's [Issues page](https://github.com/frankdavalos/sonelire-practice/issues).

## Digital companion privacy and limitations

Assessment links contain a form ID, skill, case and letter order, not learner labels. Results links also contain response marks in the URL fragment (not sent as part of the HTTP request). Codes and text files are not encrypted; keep them private. Browser history or other apps may retain links. Clear phone companion records with **Clear this companion session** once the iPad results are saved. No automatic deletion or synchronization is provided.

The QR return uses the device’s native Camera app to open a link, not an in-page camera scanner. Use the same browser storage context as the active check; a home-screen web app or private tab may have separate storage. If the QR opens the wrong context, transfer the code or text file privately and import in the original scoring screen. Avoid editing the same assessment in multiple tabs. Phone and iPad navigation are independent.

## Testing

`scripts/test.sh` runs the whole suite from any directory: the node unit tests (`node --test tests/`, Node 18+), then the browser scenarios in `tests/browser/` under pytest. Each scenario is independent and opens fresh devices, so one failure doesn't hide the others; extra arguments go to pytest (`scripts/test.sh -k companion`). It exits non-zero if anything fails, and fails with an install hint if pytest or Python Playwright is missing rather than skipping the browser tests. `SONELIRE_COVERAGE=1 scripts/test.sh` also reports how much of each page's inline script the scenarios ran.

One-time setup per clone:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
git config core.hooksPath .githooks
```

`requirements-dev.txt` pins Playwright and pytest, plus Pillow and pyzbar for independent QR image decoding (optional; pyzbar needs the system zbar library, `libzbar0` on Debian/Ubuntu or `zbar` elsewhere). The browser tests drive a system Chromium, so `playwright install` is not needed.

Run the suite with `scripts/test.sh`. It uses `.venv/bin/python` when present; set `PYTHON` to use another interpreter and `CHROMIUM` for the browser executable (default `/usr/bin/chromium`).

The `.githooks/pre-push` hook runs `scripts/test.sh` and blocks the push if it fails. Pushing to `main` deploys GitHub Pages, so this hook is the deploy gate. It tests the working tree, so commit or set aside unrelated edits before pushing. `git push --no-verify` skips it; use that only as a deliberate exception.

The browser tests load the pages from the working tree at their published URL (Playwright routing, no network) with real browser storage, not a deployed server. Real-device Camera, browser storage and deployed Pages testing remain necessary.
