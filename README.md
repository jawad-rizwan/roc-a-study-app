# ROC-A Study App

A desktop study application to prepare for the **Canadian ROC-A (Restricted Operator Certificate - Aeronautical)** exam. Built with Python and CustomTkinter for a clean, modern interface.

The ROC-A is required by operators of radiotelephone equipment on board aircraft and at aeronautical land stations using aeronautical mobile frequencies in Canada. This app covers all the material from the official **RIC-21 Study Guide** published by Industry Canada.

---

## Features

### Practice Exams
- Multiple-choice questions covering all exam topics
- Configurable question count (10, 25, or 50 questions)
- Optional 45-minute countdown timer
- Filter by topic to focus on weak areas
- Questions and answer choices are randomized each attempt
- Flag questions for review during the exam
- Detailed post-exam review with explanations for every question

### Flashcards
- **8 study decks** organized by topic:
  - ITU Phonetic Alphabet (A-Z with pronunciations + number pronunciations)
  - Procedural Words & Phrases (ROGER, WILCO, MAYDAY, etc.)
  - Distress & Urgency Procedures (MAYDAY and PAN PAN formats)
  - What NOT to Say on Radio (common mistakes to avoid)
  - Frequency Band Assignments (108-136 MHz)
  - Aeronautical Definitions
  - Regulations & Legal
  - Call Signs & Station Types
- Click or press **Space** to flip cards
- **Arrow keys** for quick navigation
- Shuffle mode for randomized study

### Reference Material
- Searchable, organized view of all study content
- Phonetic alphabet table with pronunciations
- Complete procedural words glossary
- Communication priority order (10 levels)
- Frequency band assignments
- Distress/urgency call formats (step-by-step)
- Ground station types and call sign examples
- Readability scale (1-5)
- Number transmission rules
- Aeronautical term definitions
- Filter by topic using the segmented button bar

### Progress Tracking
- Scores saved automatically after each exam
- Topic mastery percentage bars (color-coded)
- Exam history with date, score, and time taken
- Weakest topic identification with one-click "Practice Weak Topics" button
- Per-question statistics (attempts, correct rate)
- Progress persists between sessions (saved locally)

### Interface
- Modern dark/light mode toggle
- Sidebar navigation for quick switching between features
- Responsive layout that adapts to window size

---

## Topics Covered

Based on the official **RIC-21 Study Guide** (Industry Canada, Spectrum Management and Telecommunications):

| Topic | Description |
|-------|-------------|
| **Regulations** | Communication priorities, privacy of communications, control of communications, interference rules, false distress signal penalties |
| **Operating Procedures** | Speech techniques, time/date format (UTC), ITU phonetic alphabet, number transmission, procedural words, call signs, radiotelephone calling procedures, message handling, signal checks |
| **Emergency Communications** | MAYDAY procedures - distress call, distress message, acknowledgment, relay (MAYDAY RELAY), silence imposition (SEELONCE), cancellation (SEELONCE FEENEE), emergency frequency (121.5 MHz) |
| **Urgency Communications** | PAN PAN procedures - urgency signal, urgency message format, cancellation |
| **Definitions & Equipment** | Aeronautical terms, frequency assignments (108-136 MHz), equipment fundamentals, radio station licences |

---

## Installation

### Option 1: Run from Source

**Prerequisites:** Python 3.10 or higher

```bash
# Clone the repository
git clone https://github.com/jawad-rizwan/roc-a-study-app.git
cd roc-a-study-app

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 2: Pre-built Executable (Windows)

Download the latest `ROCAStudyApp.exe` from the [Releases](https://github.com/jawad-rizwan/roc-a-study-app/releases) page and double-click to run. No Python installation required.

---

## Building the Executable

To build a standalone `.exe` yourself:

```bash
# Install dependencies
pip install -r requirements.txt

# Build using the spec file
pyinstaller roca_study_app.spec
```

The executable will be created at `dist/ROCAStudyApp.exe`.

**Note:** The spec file handles bundling CustomTkinter's theme files and the application's data files automatically.

---

## How to Use

### Starting a Practice Exam
1. Click **Practice Exam** in the sidebar
2. Select which topics to include (or leave all checked)
3. Choose the number of questions (10, 25, or 50)
4. Enable or disable the 45-minute timer
5. Click **Start Exam**
6. Answer questions using the radio buttons
7. Use **Previous**/**Next** to navigate between questions
8. Flag questions you want to revisit
9. Click **Submit Exam** when done
10. Review your results and read explanations for each question

### Studying Flashcards
1. Click **Flashcards** in the sidebar
2. Select a deck from the dropdown
3. Click the card or press **Space** to flip between question and answer
4. Use **arrow keys** or the Previous/Next buttons to navigate
5. Enable **Shuffle** for randomized card order

### Using Reference Material
1. Click **Reference** in the sidebar
2. Type in the search bar to filter content (e.g., "MAYDAY", "phonetic", "frequency")
3. Use the topic filter buttons to narrow by category
4. Browse tables, glossaries, and step-by-step procedures

### Tracking Your Progress
1. Click **Progress** in the sidebar
2. View your overall statistics (exams taken, average score, total questions)
3. Check topic mastery bars to identify weak areas
4. Click **Practice Weak Topics** to start an exam focused on your lowest-scoring topics
5. Scroll down to review your exam history

---

## Data Storage

- **Application data** (questions, flashcards, reference material) is bundled with the app
- **Progress data** is saved locally:
  - **Windows:** `%APPDATA%\ROCAStudyApp\progress.json`
  - **Linux/Mac:** `~/.config/ROCAStudyApp/progress.json`

Your progress is never uploaded anywhere - it stays on your computer.

---

## Content Source

All study material is based on **RIC-21 - Study Guide for the Restricted Operator Certificate with Aeronautical Qualification (ROC-A)**, Issue 3, February 2010, published by Industry Canada, Spectrum Management and Telecommunications. Updated October 2011.

This application is an independent study tool and is not affiliated with or endorsed by Industry Canada or the Government of Canada.

---

## License

MIT License - see [LICENSE](LICENSE) for details.
