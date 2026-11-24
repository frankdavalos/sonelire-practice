# Sonelire Practice

**From sounds to stories.**

A simple, parent-led alphabet practice and letter assessment website for young learners. Sonelire Practice helps families identify which letters a child knows, focus practice on letters that need work, and check progress through subsequent informal assessments.

[**Open Sonelire Practice**](https://frankdavalos.github.io/sonelire-practice/sonelire-practice.html) · [**How to use Sonelire Practice**](HOW_TO_USE.md)

## Version 2

Version 2 adds a complete **Assess → Review → Practice → Reassess** workflow to the original letter flashcards. It is designed for a shared iPad, but also works in modern desktop and mobile browsers. No installation, account or server-side database is required.

| Feature | Description |
| --- | --- |
| Two learner profiles | Separate results for Child 1 and Child 2, without entering personal information. |
| Letter practice | Uppercase, lowercase or mixed-case flashcards, in shuffled or alphabetical order. |
| Letter checks | Adult-led checks of letter names or familiar letter sounds. |
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
3. For a check, select the skill, case and order, then choose **Prepare check**. Print the companion sheet or copy the displayed order onto paper.
4. Choose **Begin check**, ask the child for each letter name or familiar sound, and record responses privately on paper. Tap to advance.
5. Enter and save the marks after the check, then open **Results** and select **Practice letters needing work**.
6. Reassess after practice to update the child's letter results.

See the [step-by-step parent guide](HOW_TO_USE.md) for scoring, navigation, practice suggestions and troubleshooting.

## Privacy and storage

Sonelire Practice stores its learner results and unfinished check in the browser's `localStorage`. There are no login accounts, application analytics, audio recordings, or server-side student records. The learner labels are fixed and anonymous.

- Data is separate between browsers, devices and browser storage contexts; it does not synchronize.
- Clearing site data, using private browsing or browser storage eviction can cause records to be lost.
- This version has no data export, import, backup or recovery feature.
- Andika is loaded from Google Fonts; this makes a third-party font request, but the application does not send assessment results to that service. Hosting providers may retain ordinary request logs.
- Results are stored locally, not encrypted by the application, and are accessible to others using the same browser profile.

Do not use this prototype to store official or sensitive student records. An internet connection is needed for initial hosted access and reliable font loading. There is no service worker or guaranteed offline mode.

## Educational scope

Sonelire Practice is an informal, adult-administered alphabet knowledge tool, not a standardized reading screener or diagnostic instrument. It supports letter naming and parent-directed letter-sound checks, not a validated phoneme assessment. Some letters have multiple legitimate sounds; adults should decide which responses to accept before a check and apply the same rule consistently.

The practice deck is based on the latest recorded incorrect or unsure responses. Practice itself does not modify assessment results. Uppercase and lowercase results and name/sound results are kept separate. The app does not calculate validated mastery levels, reading risk, percentiles or grade-level benchmarks.

This is a lightweight companion prototype for the larger Sonelire literacy assessment and practice project, not its professional edition.

## Run or deploy

The application is a single file: `sonelire-practice.html`. It contains the HTML, CSS and vanilla JavaScript. There is no build step, npm installation, API or database server.

To run locally from the repository directory:

```bash
python3 -m http.server 8000
```

Open <http://localhost:8000/sonelire-practice.html>. For use on another device, host the file on a static web server or use the public GitHub Pages link above. Local and hosted URLs have separate browser storage.

To publish updates using the existing GitHub Pages deployment:

```bash
git add sonelire-practice.html README.md HOW_TO_USE.md
git commit -m "Update Sonelire Practice"
git push
```

The application uses [Andika](https://software.sil.org/andika/) via Google Fonts. A sans-serif fallback is used if the font cannot load.

## Project files

| File | Purpose |
| --- | --- |
| [`sonelire-practice.html`](sonelire-practice.html) | Complete application |
| [`README.md`](README.md) | Project overview, features and deployment |
| [`HOW_TO_USE.md`](HOW_TO_USE.md) | Parent-friendly usage guide |

## Release limitations

Version 2 retains the latest recorded result per learner, letter and skill rather than a complete longitudinal assessment history. Only one unfinished check can be saved at a time. Skipping a letter in a later check does not erase an existing result for that letter. There is no automated speech recognition, audio playback, cross-device sync, CSV export or full PWA functionality.

For a new issue or suggestion, use the repository's [Issues page](https://github.com/frankdavalos/sonelire-practice/issues).
