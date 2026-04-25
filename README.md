# ROC-A Study App

A browser-based study application for the **Canadian ROC-A (Restricted Operator Certificate - Aeronautical)** exam. It runs as a static website on GitHub Pages and keeps progress private in your browser.

Live site: <https://jawad-rizwan.github.io/roc-a-study-app/>

## Features

- Practice exams with randomized questions and answer choices
- Configurable 10, 25, or 50 question exams
- Optional 45-minute countdown timer
- Topic filtering and weak-topic practice
- Detailed exam review with explanations
- Lesson modules with end-of-module quizzes
- Flashcard decks with shuffle, click-to-flip, and keyboard navigation
- Searchable reference material
- Topic mastery, exam history, and question statistics
- Browser-only progress storage

## Progress Storage

Progress is saved in this browser using `localStorage` under the key `rocaStudyProgress:v1`.

Your progress is never uploaded anywhere. It stays on the current browser and device. Clearing site data, clearing browser storage, using a different browser, or using a different device will remove or hide that saved progress.

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

Opening `index.html` directly from the filesystem is not recommended because browsers may block loading the JSON data files via `fetch`.

## Deployment

The `.github/workflows/build.yml` workflow deploys the repository root to GitHub Pages on every push to `master`.

No executable, installer, Python runtime, or build artifact is produced.

## Content Source

All study material is based on **RIC-21 - Study Guide for the Restricted Operator Certificate with Aeronautical Qualification (ROC-A)**, Issue 3, February 2010, published by Industry Canada, Spectrum Management and Telecommunications. Updated October 2011.

This application is an independent study tool and is not affiliated with or endorsed by Industry Canada or the Government of Canada.

## License

MIT License - see [LICENSE](LICENSE) for details.
