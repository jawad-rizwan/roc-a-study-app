# ROC-A Study App

A static study application for the **Canadian ROC-A (Restricted Operator Certificate - Aeronautical)** exam. It runs on GitHub Pages and keeps progress private on your device.

Live site: <https://jawad-rizwan.github.io/roc-a-study-app/>

## Features

- Practice exams with randomized questions and answer choices
- Configurable 10, 25, or 50 question exams
- Optional 45-minute countdown timer
- Topic filtering and weak-topic practice
- Detailed exam review with explanations
- Lesson modules with end-of-module quizzes
- Guided study plan with a recommended learn/reinforce/test/review flow
- Flashcard decks with smart review, confidence ratings, shuffle, click-to-flip, and keyboard navigation
- Searchable reference material
- Printable quick study sheets for high-yield tables and call formats
- Practice mode with instant explanations after each answer
- Mistake review for drilling previously missed questions
- Topic mastery, exam-readiness score, exam history, and question statistics
- Progress export/import for backups or device moves
- Offline support after the first successful load
- Local-only progress storage

## Progress Storage

Progress is saved locally on your device using the site storage key `rocaStudyProgress:v1`.

Your progress is never uploaded anywhere. Clearing site data or using a different device will remove or hide that saved progress.

Use the **Reset Progress** button on the Progress page if you want to clear all saved progress for this site.

## Local Development

This is a no-build static site. Serve the repository root with any static file server:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

Opening `index.html` directly from the filesystem is not recommended because the JSON data files are loaded over HTTP.

## Offline Use

The site registers a service worker and caches the app shell plus study data after the first successful load. After that, the main app, lessons, exams, flashcards, reference material, and study sheets can load without a network connection on the same device.

If a new version is deployed, reload the page while online to refresh the cached files.

## Printable Study Sheets

Use the **Study Sheets** page and click **Print Study Sheets** to print or save a PDF of the highest-yield reference material, including phonetic alphabet, number pronunciation, priorities, frequencies, readability scale, distress/urgency formats, and common phrases to avoid.

## Deployment

The `.github/workflows/build.yml` workflow deploys the repository root to GitHub Pages on every push to `master`.

No executable, installer, Python runtime, or build artifact is produced.

## Content Source

All study material is based on **RIC-21 - Study Guide for the Restricted Operator Certificate with Aeronautical Qualification (ROC-A)**, Issue 3, February 2010, published by Industry Canada, Spectrum Management and Telecommunications. Updated October 2011.

This application is an independent study tool and is not affiliated with or endorsed by Industry Canada or the Government of Canada.

## License

MIT License - see [LICENSE](LICENSE) for details.
