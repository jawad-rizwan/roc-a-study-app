const DATA_PATHS = {
  questions: "data/questions.json",
  flashcards: "data/flashcards.json",
  reference: "data/reference.json",
  lessons: "data/lessons.json",
};

const PROGRESS_KEY = "rocaStudyProgress:v1";
const DEFAULT_TIME_LIMIT_SECONDS = 45 * 60;
const TOPICS = {
  regulations: "Regulations",
  operating_procedures: "Operating Procedures",
  emergency_communications: "Emergency Communications",
  urgency_communications: "Urgency Communications",
  definitions_and_equipment: "Definitions & Equipment",
};
const TOPIC_COLORS = {
  regulations: "#0c5f7f",
  operating_procedures: "#16815f",
  emergency_communications: "#c83e36",
  urgency_communications: "#ca7a1b",
  definitions_and_equipment: "#6e5b2f",
};

const app = document.querySelector("#app");
const navLinks = [...document.querySelectorAll(".nav-link")];

const state = {
  data: null,
  view: "home",
  exam: null,
  reviewSession: null,
  flashcards: {
    deckId: "",
    cards: [],
    index: 0,
    flipped: false,
    shuffle: false,
  },
  reference: {
    query: "",
    topic: "all",
  },
  lesson: {
    currentId: "",
    quiz: null,
  },
  progress: loadProgress(),
  timerId: null,
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function loadProgress() {
  try {
    const raw = localStorage.getItem(PROGRESS_KEY);
    if (!raw) return defaultProgress();
    return { ...defaultProgress(), ...JSON.parse(raw) };
  } catch {
    return defaultProgress();
  }
}

function defaultProgress() {
  return {
    version: "1.0",
    lastUpdated: new Date().toISOString(),
    examHistory: [],
    questionStats: {},
    flashcardStats: {},
    topicMastery: {},
    lessonCompletions: {},
  };
}

function saveProgress() {
  state.progress.lastUpdated = new Date().toISOString();
  try {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify(state.progress));
  } catch {
    alert("Progress could not be saved. Browser storage may be disabled or full.");
  }
}

function resetProgress() {
  if (!confirm("Reset all saved progress in this browser? This cannot be undone.")) {
    return;
  }
  state.progress = defaultProgress();
  saveProgress();
  render();
}

function shuffle(items) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function topicName(topic) {
  return TOPICS[topic] || topic;
}

function getQuestionById(id) {
  return state.data.questions.find((question) => question.id === id);
}

function getStats() {
  const exams = state.progress.examHistory;
  const totalQuestions = Object.values(state.progress.questionStats)
    .reduce((sum, stats) => sum + (stats.attempts || 0), 0);
  const average = exams.length
    ? exams.reduce((sum, exam) => sum + exam.scorePercent, 0) / exams.length
    : 0;
  const best = exams.length
    ? Math.max(...exams.map((exam) => exam.scorePercent))
    : 0;
  return {
    exams: exams.length,
    totalQuestions,
    average: round1(average),
    best: round1(best),
  };
}

function round1(value) {
  return Math.round(value * 10) / 10;
}

function recomputeMastery() {
  const topicTotals = {};
  state.data.questions.forEach((question) => {
    const stats = state.progress.questionStats[question.id];
    if (!stats) return;
    if (!topicTotals[question.topic]) {
      topicTotals[question.topic] = { totalAttempts: 0, totalCorrect: 0 };
    }
    topicTotals[question.topic].totalAttempts += stats.attempts || 0;
    topicTotals[question.topic].totalCorrect += stats.correct || 0;
  });

  state.progress.topicMastery = {};
  Object.entries(topicTotals).forEach(([topic, totals]) => {
    const masteryPercent = totals.totalAttempts
      ? round1((totals.totalCorrect / totals.totalAttempts) * 100)
      : 0;
    state.progress.topicMastery[topic] = { ...totals, masteryPercent };
  });
}

function weakestTopics(limit = 3) {
  return Object.entries(state.progress.topicMastery)
    .sort((a, b) => (a[1].masteryPercent || 0) - (b[1].masteryPercent || 0))
    .slice(0, limit)
    .map(([topic, stats]) => ({ topic, percent: stats.masteryPercent || 0 }));
}

function setView(view) {
  state.view = view;
  navLinks.forEach((link) => link.classList.toggle("active", link.dataset.view === view));
  clearTimer();
  if (view !== "exam" && state.exam && !state.exam.submitted) {
    startTimer();
  }
  render();
  app.focus({ preventScroll: true });
}

function clearTimer() {
  if (state.timerId) {
    clearInterval(state.timerId);
    state.timerId = null;
  }
}

function startTimer() {
  clearTimer();
  if (!state.exam?.timeLimitSeconds) return;
  state.timerId = setInterval(() => {
    if (!state.exam) return;
    if (timeRemaining(state.exam) <= 0) {
      submitExam(true);
      return;
    }
    updateTimerText();
  }, 1000);
}

function timeRemaining(exam) {
  if (!exam.timeLimitSeconds) return null;
  const elapsed = Math.floor((Date.now() - exam.startTime) / 1000);
  return Math.max(0, exam.timeLimitSeconds - elapsed);
}

function formatDuration(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}m ${String(seconds).padStart(2, "0")}s`;
}

function formatTimer(seconds) {
  if (seconds === null) return "No limit";
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function updateTimerText() {
  const timer = document.querySelector("[data-exam-timer]");
  if (timer && state.exam) timer.textContent = formatTimer(timeRemaining(state.exam));
}

function hero(title, subtitle, eyebrow = "ROC-A Study App") {
  return `
    <section class="hero">
      <p class="eyebrow">${escapeHtml(eyebrow)}</p>
      <h1>${escapeHtml(title)}</h1>
      <p class="muted">${escapeHtml(subtitle)}</p>
    </section>
  `;
}

function render() {
  if (!state.data) return;
  const renderers = {
    home: renderHome,
    lessons: renderLessons,
    exam: renderExam,
    flashcards: renderFlashcards,
    reference: renderReference,
    progress: renderProgress,
  };
  app.innerHTML = renderers[state.view]?.() || renderHome();
}

function renderHome() {
  const stats = getStats();
  return `
    ${hero("Study the ROC-A material with everything saved in your browser.", "Lessons, practice exams, flashcards, reference material, and private progress tracking for the Canadian ROC-A exam.")}
    <section class="grid three">
      ${statCard("Exams Taken", stats.exams)}
      ${statCard("Average Score", `${stats.average}%`)}
      ${statCard("Questions Answered", stats.totalQuestions)}
    </section>
    <section class="grid two" style="margin-top: 18px;">
      <div class="panel">
        <h2>Quick Start</h2>
        <p class="muted">Jump into the next useful study activity.</p>
        <div class="actions">
          <button class="btn" type="button" data-view="exam">Start Practice Exam</button>
          <button class="btn green" type="button" data-view="flashcards">Study Flashcards</button>
          <button class="btn amber" type="button" data-view="reference">Browse Reference</button>
        </div>
      </div>
      <div class="panel">
        <h2>Focus Areas</h2>
        ${renderWeakTopics()}
      </div>
    </section>
    <section class="panel" style="margin-top: 18px;">
      <h2>Topic Mastery</h2>
      ${renderMasteryBars()}
    </section>
  `;
}

function statCard(label, value) {
  return `
    <div class="panel stat">
      <strong>${escapeHtml(value)}</strong>
      <span class="muted">${escapeHtml(label)}</span>
    </div>
  `;
}

function renderWeakTopics() {
  const weak = weakestTopics();
  if (!weak.length) {
    return `<p class="muted">Take a practice exam to identify weak topics.</p>`;
  }
  return `
    <p>${weak.map((item) => `${escapeHtml(topicName(item.topic))} (${item.percent}%)`).join(", ")}</p>
    <button class="btn red" type="button" data-action="practice-weak">Practice Weak Topics</button>
  `;
}

function renderMasteryBars() {
  return Object.entries(TOPICS).map(([topic, label]) => {
    const mastery = state.progress.topicMastery[topic] || {};
    const pct = mastery.masteryPercent || 0;
    const attempts = mastery.totalAttempts || 0;
    return `
      <div class="progress-row">
        <strong>${escapeHtml(label)}</strong>
        <div class="bar" aria-label="${escapeHtml(label)} mastery">
          <span style="width: ${pct}%; background: ${TOPIC_COLORS[topic]};"></span>
        </div>
        <span>${attempts ? `${pct}%` : "--"}</span>
      </div>
    `;
  }).join("");
}

function renderExam() {
  if (state.exam && !state.exam.submitted) return renderActiveExam();
  return `
    ${hero("Build a practice exam.", "Choose topics, question count, and whether to use the 45-minute timer.", "Practice Exam")}
    <section class="panel">
      <div class="form-row">
        <label><strong>Topics</strong></label>
        <div class="check-grid">
          ${Object.entries(TOPICS).map(([key, label]) => `
            <label class="check-card">
              <input type="checkbox" data-exam-topic="${escapeHtml(key)}" checked>
              <span>${escapeHtml(label)}</span>
            </label>
          `).join("")}
        </div>
      </div>
      <div class="grid two">
        <label class="form-row">
          <strong>Questions</strong>
          <select data-exam-count>
            <option value="10">10 questions</option>
            <option value="25" selected>25 questions</option>
            <option value="50">50 questions</option>
          </select>
        </label>
        <label class="check-card" style="align-self: end;">
          <input type="checkbox" data-exam-timed checked>
          <span>Use 45-minute timer</span>
        </label>
      </div>
      <div class="actions">
        <button class="btn" type="button" data-action="start-exam">Start Exam</button>
      </div>
    </section>
    ${state.reviewSession ? renderExamReview(state.reviewSession) : ""}
  `;
}

function makeExamQuestions(topics, count) {
  const pool = state.data.questions.filter((question) => topics.includes(question.topic));
  return shuffle(pool).slice(0, count).map((question) => {
    const order = shuffle(question.choices.map((_, index) => index));
    return {
      ...question,
      choices: order.map((index) => question.choices[index]),
      correct_index: order.indexOf(question.correct_index),
    };
  });
}

function startExamFromForm() {
  const topics = [...document.querySelectorAll("[data-exam-topic]:checked")]
    .map((input) => input.dataset.examTopic);
  if (!topics.length) {
    alert("Please select at least one topic.");
    return;
  }
  const count = Number(document.querySelector("[data-exam-count]").value);
  const timed = document.querySelector("[data-exam-timed]").checked;
  const questions = makeExamQuestions(topics, count);
  if (!questions.length) {
    alert("No questions are available for the selected topics.");
    return;
  }
  state.exam = {
    examId: `exam_${Date.now()}`,
    questions,
    userAnswers: Object.fromEntries(questions.map((question) => [question.id, null])),
    flagged: [],
    currentIndex: 0,
    startTime: Date.now(),
    timeLimitSeconds: timed ? DEFAULT_TIME_LIMIT_SECONDS : null,
    submitted: false,
  };
  state.reviewSession = null;
  startTimer();
  render();
}

function renderActiveExam() {
  const exam = state.exam;
  const question = exam.questions[exam.currentIndex];
  const selected = exam.userAnswers[question.id];
  return `
    <section class="panel">
      <div class="exam-top">
        <div>
          <p class="eyebrow">Practice Exam</p>
          <h2>Question ${exam.currentIndex + 1} of ${exam.questions.length}</h2>
        </div>
        <div class="timer" data-exam-timer>${formatTimer(timeRemaining(exam))}</div>
      </div>
      <span class="topic-badge">${escapeHtml(topicName(question.topic))}</span>
      <div class="question-card" style="margin-top: 14px;">
        <h3>${escapeHtml(question.question)}</h3>
        ${question.choices.map((choice, index) => `
          <button class="choice-card ${selected === index ? "selected" : ""}" type="button" data-action="answer-exam" data-choice="${index}">
            <strong>${String.fromCharCode(65 + index)}.</strong>
            <span>${escapeHtml(choice)}</span>
          </button>
        `).join("")}
        <label class="check-card">
          <input type="checkbox" data-action="toggle-flag" ${exam.flagged.includes(question.id) ? "checked" : ""}>
          <span>Flag for review</span>
        </label>
      </div>
      <div class="question-nav">
        ${exam.questions.map((item, index) => `
          <button
            class="q-dot ${index === exam.currentIndex ? "current" : ""} ${exam.userAnswers[item.id] !== null ? "answered" : ""} ${exam.flagged.includes(item.id) ? "flagged" : ""}"
            type="button"
            data-action="go-question"
            data-index="${index}"
            aria-label="Go to question ${index + 1}"
          >${index + 1}</button>
        `).join("")}
      </div>
      <div class="actions">
        <button class="btn secondary" type="button" data-action="prev-question" ${exam.currentIndex === 0 ? "disabled" : ""}>Previous</button>
        <button class="btn secondary" type="button" data-action="next-question" ${exam.currentIndex === exam.questions.length - 1 ? "disabled" : ""}>Next</button>
        <button class="btn red" type="button" data-action="submit-exam">Submit Exam</button>
      </div>
    </section>
  `;
}

function answerExam(choice) {
  const question = state.exam.questions[state.exam.currentIndex];
  state.exam.userAnswers[question.id] = Number(choice);
  render();
}

function submitExam(auto = false) {
  const exam = state.exam;
  if (!exam) return;
  if (!auto) {
    const unanswered = Object.values(exam.userAnswers).filter((answer) => answer === null).length;
    const message = unanswered
      ? `You have ${unanswered} unanswered question(s). Submit anyway?`
      : "Submit your exam?";
    if (!confirm(message)) return;
  }

  clearTimer();
  const record = recordExam(exam);
  state.reviewSession = { ...exam, record };
  state.exam = null;
  setView("exam");
}

function recordExam(exam) {
  let correct = 0;
  const topicBreakdown = {};
  exam.questions.forEach((question) => {
    if (!topicBreakdown[question.topic]) {
      topicBreakdown[question.topic] = { correct: 0, total: 0 };
    }
    topicBreakdown[question.topic].total += 1;
    const userAnswer = exam.userAnswers[question.id];
    const isCorrect = userAnswer !== null && userAnswer === question.correct_index;
    if (isCorrect) {
      correct += 1;
      topicBreakdown[question.topic].correct += 1;
    }
    if (!state.progress.questionStats[question.id]) {
      state.progress.questionStats[question.id] = { attempts: 0, correct: 0, lastSeen: "" };
    }
    state.progress.questionStats[question.id].attempts += 1;
    state.progress.questionStats[question.id].lastSeen = new Date().toISOString();
    if (isCorrect) state.progress.questionStats[question.id].correct += 1;
  });

  const total = exam.questions.length;
  const timeTakenSeconds = exam.timeLimitSeconds
    ? exam.timeLimitSeconds - timeRemaining(exam)
    : Math.floor((Date.now() - exam.startTime) / 1000);
  const record = {
    examId: exam.examId,
    timestamp: new Date().toISOString(),
    totalQuestions: total,
    correct,
    scorePercent: total ? round1((correct / total) * 100) : 0,
    timeTakenSeconds,
    topicBreakdown,
    incorrectQuestionIds: exam.questions
      .filter((question) => exam.userAnswers[question.id] !== question.correct_index)
      .map((question) => question.id),
  };
  state.progress.examHistory.push(record);
  recomputeMastery();
  saveProgress();
  return record;
}

function renderExamReview(session) {
  const { record } = session;
  const resultClass = record.scorePercent >= 80
    ? "result-good"
    : record.scorePercent >= 60
      ? "result-mid"
      : "result-bad";
  return `
    <section class="panel" style="margin-top: 18px;">
      <p class="eyebrow">Exam Review</p>
      <h2 class="${resultClass}">${record.correct}/${record.totalQuestions} (${record.scorePercent}%)</h2>
      <p class="muted">Completed in ${formatDuration(record.timeTakenSeconds)}.</p>
      <div class="actions">
        <button class="btn ghost" type="button" data-action="review-all">Show All</button>
        <button class="btn red" type="button" data-action="review-incorrect">Incorrect Only</button>
      </div>
      <div data-review-list>${renderReviewQuestions(session, "all")}</div>
    </section>
  `;
}

function renderReviewQuestions(session, mode) {
  return session.questions
    .map((question, index) => {
      const userAnswer = session.userAnswers[question.id];
      const isCorrect = userAnswer !== null && userAnswer === question.correct_index;
      if (mode === "incorrect" && isCorrect) return "";
      return `
        <article class="review-card">
          <span class="topic-badge">${escapeHtml(topicName(question.topic))}</span>
          <h3>Q${index + 1}. ${escapeHtml(question.question)}</h3>
          ${question.choices.map((choice, choiceIndex) => {
            const classes = [
              choiceIndex === question.correct_index ? "correct" : "",
              userAnswer === choiceIndex && choiceIndex !== question.correct_index ? "wrong" : "",
            ].join(" ");
            const suffix = choiceIndex === question.correct_index
              ? " Correct answer"
              : userAnswer === choiceIndex
                ? " Your answer"
                : "";
            return `<div class="choice-card ${classes}"><strong>${String.fromCharCode(65 + choiceIndex)}.</strong><span>${escapeHtml(choice)}${suffix ? ` (${suffix.trim()})` : ""}</span></div>`;
          }).join("")}
          ${question.explanation ? `<p class="muted"><strong>Explanation:</strong> ${escapeHtml(question.explanation)}</p>` : ""}
        </article>
      `;
    })
    .join("");
}

function renderLessons() {
  if (state.lesson.quiz) return renderLessonQuiz();
  if (state.lesson.currentId) return renderLessonContent();
  return `
    ${hero("Learn the material module by module.", "Study each lesson, then complete the quiz to mark it finished.", "Lessons")}
    <section class="grid two">
      ${state.data.lessons.map((lesson) => {
        const completed = state.progress.lessonCompletions[lesson.id];
        return `
          <article class="lesson-card">
            <span class="pill">Module ${lesson.order}</span>
            <h2>${escapeHtml(lesson.title)}</h2>
            <p class="muted">${escapeHtml(lesson.description)}</p>
            <p>${lesson.sections.length} sections | ${(lesson.quiz_question_ids || []).length} quiz questions</p>
            ${completed ? `<p class="result-good"><strong>Completed:</strong> ${completed.scorePercent}%</p>` : ""}
            <button class="btn" type="button" data-action="open-lesson" data-lesson-id="${escapeHtml(lesson.id)}">${completed ? "Review" : "Start"}</button>
          </article>
        `;
      }).join("")}
    </section>
  `;
}

function renderLessonContent() {
  const lesson = state.data.lessons.find((item) => item.id === state.lesson.currentId);
  if (!lesson) {
    state.lesson.currentId = "";
    return renderLessons();
  }
  return `
    <section class="panel">
      <div class="actions">
        <button class="btn ghost" type="button" data-action="back-lessons">Back to Lessons</button>
      </div>
      <p class="eyebrow">Module ${lesson.order}</p>
      <h1>${escapeHtml(lesson.title)}</h1>
      <p class="muted">${lesson.sections.length} sections | ${(lesson.quiz_question_ids || []).length} quiz questions</p>
      ${lesson.sections.map(renderLessonSection).join("")}
      <div class="actions">
        <button class="btn green" type="button" data-action="start-lesson-quiz">Take the Quiz</button>
      </div>
    </section>
  `;
}

function renderLessonSection(section) {
  if (section.type === "text") {
    return `<article class="lesson-card"><h3>${escapeHtml(section.title || "")}</h3>${paragraphs(section.content)}</article>`;
  }
  if (section.type === "key_points") {
    return `<article class="lesson-card"><h3>${escapeHtml(section.title || "Key Points")}</h3><ul>${(section.points || []).map((point) => `<li>${escapeHtml(point)}</li>`).join("")}</ul></article>`;
  }
  if (section.type === "example") {
    return `<article class="lesson-card"><h3>${escapeHtml(section.title || "Example")}</h3><pre>${escapeHtml(section.content || "")}</pre></article>`;
  }
  if (section.type === "warning") {
    return `<article class="lesson-card"><span class="pill">Important</span>${paragraphs(section.content)}</article>`;
  }
  if (section.type === "table") {
    return `<article class="lesson-card"><h3>${escapeHtml(section.title || "")}</h3>${renderTable(section.columns || [], section.rows || [])}</article>`;
  }
  return "";
}

function paragraphs(content) {
  return String(content || "")
    .split(/\n{2,}/)
    .map((part) => `<p>${escapeHtml(part).replaceAll("\n", "<br>")}</p>`)
    .join("");
}

function startLessonQuiz() {
  const lesson = state.data.lessons.find((item) => item.id === state.lesson.currentId);
  const questions = (lesson.quiz_question_ids || []).map(getQuestionById).filter(Boolean);
  if (!questions.length) {
    alert("This lesson does not have quiz questions.");
    return;
  }
  state.lesson.quiz = {
    lessonId: lesson.id,
    questions,
    answers: {},
    index: 0,
    results: null,
  };
  render();
}

function renderLessonQuiz() {
  const quiz = state.lesson.quiz;
  if (quiz.results) return renderLessonQuizResults();
  const question = quiz.questions[quiz.index];
  const selected = quiz.answers[question.id];
  return `
    <section class="panel">
      <div class="exam-top">
        <div>
          <p class="eyebrow">Lesson Quiz</p>
          <h2>Question ${quiz.index + 1} of ${quiz.questions.length}</h2>
        </div>
        <button class="btn ghost" type="button" data-action="cancel-lesson-quiz">Back to Lesson</button>
      </div>
      <article class="question-card">
        <h3>${escapeHtml(question.question)}</h3>
        ${question.choices.map((choice, index) => `
          <button class="choice-card ${selected === index ? "selected" : ""}" type="button" data-action="answer-lesson-quiz" data-choice="${index}">
            <strong>${String.fromCharCode(65 + index)}.</strong>
            <span>${escapeHtml(choice)}</span>
          </button>
        `).join("")}
      </article>
      <div class="actions">
        <button class="btn secondary" type="button" data-action="prev-lesson-question" ${quiz.index === 0 ? "disabled" : ""}>Previous</button>
        <button class="btn secondary" type="button" data-action="next-lesson-question" ${quiz.index === quiz.questions.length - 1 ? "disabled" : ""}>Next</button>
        <button class="btn green" type="button" data-action="submit-lesson-quiz">Submit Quiz</button>
      </div>
    </section>
  `;
}

function submitLessonQuiz() {
  const quiz = state.lesson.quiz;
  const unanswered = quiz.questions.length - Object.keys(quiz.answers).length;
  if (unanswered && !confirm(`You have ${unanswered} unanswered question(s). Submit anyway?`)) {
    return;
  }
  let correct = 0;
  quiz.questions.forEach((question) => {
    if (quiz.answers[question.id] === question.correct_index) correct += 1;
  });
  const scorePercent = round1((correct / quiz.questions.length) * 100);
  quiz.results = { correct, total: quiz.questions.length, scorePercent };
  state.progress.lessonCompletions[quiz.lessonId] = {
    correct,
    total: quiz.questions.length,
    scorePercent,
    completedAt: new Date().toISOString(),
  };
  saveProgress();
  render();
}

function renderLessonQuizResults() {
  const quiz = state.lesson.quiz;
  const result = quiz.results;
  return `
    <section class="panel">
      <p class="eyebrow">Quiz Results</p>
      <h1>${result.correct}/${result.total} (${result.scorePercent}%)</h1>
      <div class="actions">
        <button class="btn" type="button" data-action="finish-lesson-quiz">Back to Lessons</button>
        <button class="btn amber" type="button" data-action="retry-lesson-quiz">Retry Quiz</button>
      </div>
      ${quiz.questions.map((question, index) => {
        const userAnswer = quiz.answers[question.id];
        const isCorrect = userAnswer === question.correct_index;
        return `
          <article class="review-card">
            <h3>Q${index + 1}. ${escapeHtml(question.question)}</h3>
            <p class="${isCorrect ? "result-good" : "result-bad"}"><strong>${isCorrect ? "Correct" : "Incorrect"}</strong></p>
            ${!isCorrect ? `<p>Your answer: ${escapeHtml(userAnswer === undefined ? "No answer" : question.choices[userAnswer])}</p>` : ""}
            <p>Correct answer: ${escapeHtml(question.choices[question.correct_index])}</p>
            ${question.explanation ? `<p class="muted">${escapeHtml(question.explanation)}</p>` : ""}
          </article>
        `;
      }).join("")}
    </section>
  `;
}

function renderFlashcards() {
  if (!state.flashcards.deckId) {
    state.flashcards.deckId = state.data.decks[0]?.deck_id || "";
    loadFlashcardDeck();
  }
  const deck = state.data.decks.find((item) => item.deck_id === state.flashcards.deckId);
  const card = state.flashcards.cards[state.flashcards.index];
  return `
    ${hero("Flip through topic decks.", "Click the card or press Space to flip. Arrow keys move between cards.", "Flashcards")}
    <section class="grid two">
      <div class="panel">
        <h2>Decks</h2>
        <div class="grid">
          ${state.data.decks.map((item) => `
            <button class="deck-card ${item.deck_id === state.flashcards.deckId ? "active" : ""}" type="button" data-action="select-deck" data-deck-id="${escapeHtml(item.deck_id)}">
              <strong>${escapeHtml(item.title)}</strong>
              <p class="muted">${escapeHtml(topicName(item.topic))} | ${item.cards.length} cards</p>
            </button>
          `).join("")}
        </div>
      </div>
      <div>
        <div class="panel" style="margin-bottom: 18px;">
          <h2>${escapeHtml(deck?.title || "Flashcards")}</h2>
          <label class="check-card">
            <input type="checkbox" data-action="toggle-card-shuffle" ${state.flashcards.shuffle ? "checked" : ""}>
            <span>Shuffle this deck</span>
          </label>
        </div>
        <button class="flashcard" type="button" data-action="flip-card">
          <span>
            <strong>${state.flashcards.flipped ? "Answer" : "Question"}</strong>
            <p>${escapeHtml(card ? (state.flashcards.flipped ? card.back : card.front) : "No card selected")}</p>
          </span>
        </button>
        <div class="actions" style="margin-top: 16px;">
          <button class="btn secondary" type="button" data-action="prev-card" ${state.flashcards.index === 0 ? "disabled" : ""}>Previous</button>
          <span class="pill">${state.flashcards.index + 1} / ${state.flashcards.cards.length}</span>
          <button class="btn secondary" type="button" data-action="next-card" ${state.flashcards.index >= state.flashcards.cards.length - 1 ? "disabled" : ""}>Next</button>
        </div>
      </div>
    </section>
  `;
}

function loadFlashcardDeck() {
  const deck = state.data.decks.find((item) => item.deck_id === state.flashcards.deckId);
  const cards = deck ? deck.cards : [];
  state.flashcards.cards = state.flashcards.shuffle ? shuffle(cards) : [...cards];
  state.flashcards.index = 0;
  state.flashcards.flipped = false;
}

function flipCard() {
  const card = state.flashcards.cards[state.flashcards.index];
  if (!card) return;
  state.flashcards.flipped = !state.flashcards.flipped;
  if (state.flashcards.flipped) {
    if (!state.progress.flashcardStats[card.id]) {
      state.progress.flashcardStats[card.id] = { views: 0, lastSeen: "" };
    }
    state.progress.flashcardStats[card.id].views += 1;
    state.progress.flashcardStats[card.id].lastSeen = new Date().toISOString();
    saveProgress();
  }
  render();
}

function renderReference() {
  const sections = getReferenceSections();
  return `
    ${hero("Search the ROC-A reference.", "Filter procedures, tables, definitions, and priority rules.", "Reference")}
    <section class="panel">
      <div class="grid two">
        <label class="form-row">
          <strong>Search</strong>
          <input type="text" data-reference-query value="${escapeHtml(state.reference.query)}" placeholder="MAYDAY, phonetic, frequency...">
        </label>
        <label class="form-row">
          <strong>Topic</strong>
          <select data-reference-topic>
            <option value="all">All topics</option>
            ${Object.entries(TOPICS).map(([key, label]) => `<option value="${key}" ${state.reference.topic === key ? "selected" : ""}>${escapeHtml(label)}</option>`).join("")}
          </select>
        </label>
      </div>
    </section>
    <section style="margin-top: 18px;">
      ${sections.length ? sections.map(renderReferenceSection).join("") : `<div class="empty">No reference results found.</div>`}
    </section>
  `;
}

function getReferenceSections() {
  const query = state.reference.query.trim().toLowerCase();
  return state.data.referenceSections.filter((section) => {
    if (state.reference.topic !== "all" && section.topic !== state.reference.topic) return false;
    if (!query) return true;
    return JSON.stringify(section).toLowerCase().includes(query);
  });
}

function renderReferenceSection(section) {
  let body = "";
  if (section.type === "table") body = renderTable(section.columns || [], section.rows || []);
  if (section.type === "glossary") {
    body = (section.entries || []).map((entry) => `<p><strong>${escapeHtml(entry.term)}</strong><br>${escapeHtml(entry.definition)}</p>`).join("");
  }
  if (section.type === "ordered_list") {
    body = `<ol>${(section.items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>`;
  }
  if (section.type === "procedure") {
    body = `<ol>${(section.steps || []).map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ol>`;
  }
  return `
    <article class="reference-card">
      <span class="topic-badge">${escapeHtml(topicName(section.topic))}</span>
      <h2>${escapeHtml(section.title)}</h2>
      ${body}
    </article>
  `;
}

function renderTable(columns, rows) {
  return `
    <div class="table-wrap">
      <table>
        <thead><tr>${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("")}</tr></thead>
        <tbody>
          ${rows.map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderProgress() {
  const stats = getStats();
  return `
    ${hero("Your progress stays on this device.", "Scores, topic mastery, lesson completions, and flashcard views are saved in browser storage.", "Progress")}
    <section class="grid four">
      ${statCard("Exams", stats.exams)}
      ${statCard("Avg Score", `${stats.average}%`)}
      ${statCard("Questions", stats.totalQuestions)}
      ${statCard("Best Score", `${stats.best}%`)}
    </section>
    <section class="panel" style="margin-top: 18px;">
      <h2>Topic Mastery</h2>
      ${renderMasteryBars()}
    </section>
    <section class="panel" style="margin-top: 18px;">
      <div class="actions" style="justify-content: space-between;">
        <h2 style="margin: 0;">Exam History</h2>
        <button class="btn red" type="button" data-action="reset-progress">Reset Progress</button>
      </div>
      ${renderExamHistory()}
    </section>
  `;
}

function renderExamHistory() {
  if (!state.progress.examHistory.length) {
    return `<p class="muted">No exams taken yet.</p>`;
  }
  return [...state.progress.examHistory].reverse().map((record) => `
    <article class="review-card">
      <div class="exam-top">
        <strong>${new Date(record.timestamp).toLocaleDateString()}</strong>
        <span class="pill">${formatDuration(record.timeTakenSeconds)}</span>
      </div>
      <h3>${record.correct}/${record.totalQuestions} (${record.scorePercent}%)</h3>
      <p class="muted">${Object.entries(record.topicBreakdown).map(([topic, breakdown]) => `${topicName(topic)} ${breakdown.correct}/${breakdown.total}`).join(" | ")}</p>
    </article>
  `).join("");
}

document.addEventListener("click", (event) => {
  const viewButton = event.target.closest("[data-view]");
  if (viewButton) {
    setView(viewButton.dataset.view);
    return;
  }

  const actionButton = event.target.closest("[data-action]");
  if (!actionButton) return;
  const action = actionButton.dataset.action;

  if (action === "start-exam") startExamFromForm();
  if (action === "answer-exam") answerExam(actionButton.dataset.choice);
  if (action === "toggle-flag") {
    const question = state.exam.questions[state.exam.currentIndex];
    state.exam.flagged = state.exam.flagged.includes(question.id)
      ? state.exam.flagged.filter((id) => id !== question.id)
      : [...state.exam.flagged, question.id];
    render();
  }
  if (action === "go-question") {
    state.exam.currentIndex = Number(actionButton.dataset.index);
    render();
  }
  if (action === "prev-question" && state.exam.currentIndex > 0) {
    state.exam.currentIndex -= 1;
    render();
  }
  if (action === "next-question" && state.exam.currentIndex < state.exam.questions.length - 1) {
    state.exam.currentIndex += 1;
    render();
  }
  if (action === "submit-exam") submitExam(false);
  if (action === "review-all" && state.reviewSession) {
    document.querySelector("[data-review-list]").innerHTML = renderReviewQuestions(state.reviewSession, "all");
  }
  if (action === "review-incorrect" && state.reviewSession) {
    document.querySelector("[data-review-list]").innerHTML = renderReviewQuestions(state.reviewSession, "incorrect");
  }
  if (action === "practice-weak") {
    state.view = "exam";
    navLinks.forEach((link) => link.classList.toggle("active", link.dataset.view === "exam"));
    render();
    const weak = weakestTopics().map((item) => item.topic);
    document.querySelectorAll("[data-exam-topic]").forEach((input) => {
      input.checked = weak.includes(input.dataset.examTopic);
    });
  }
  if (action === "open-lesson") {
    state.lesson.currentId = actionButton.dataset.lessonId;
    state.lesson.quiz = null;
    render();
  }
  if (action === "back-lessons") {
    state.lesson.currentId = "";
    state.lesson.quiz = null;
    render();
  }
  if (action === "start-lesson-quiz") startLessonQuiz();
  if (action === "cancel-lesson-quiz") {
    if (confirm("Leave the quiz? Your answers will be lost.")) {
      state.lesson.quiz = null;
      render();
    }
  }
  if (action === "answer-lesson-quiz") {
    const quiz = state.lesson.quiz;
    quiz.answers[quiz.questions[quiz.index].id] = Number(actionButton.dataset.choice);
    render();
  }
  if (action === "prev-lesson-question" && state.lesson.quiz.index > 0) {
    state.lesson.quiz.index -= 1;
    render();
  }
  if (action === "next-lesson-question" && state.lesson.quiz.index < state.lesson.quiz.questions.length - 1) {
    state.lesson.quiz.index += 1;
    render();
  }
  if (action === "submit-lesson-quiz") submitLessonQuiz();
  if (action === "finish-lesson-quiz") {
    state.lesson.currentId = "";
    state.lesson.quiz = null;
    render();
  }
  if (action === "retry-lesson-quiz") startLessonQuiz();
  if (action === "select-deck") {
    state.flashcards.deckId = actionButton.dataset.deckId;
    loadFlashcardDeck();
    render();
  }
  if (action === "toggle-card-shuffle") {
    state.flashcards.shuffle = actionButton.checked;
    loadFlashcardDeck();
    render();
  }
  if (action === "flip-card") flipCard();
  if (action === "prev-card" && state.flashcards.index > 0) {
    state.flashcards.index -= 1;
    state.flashcards.flipped = false;
    render();
  }
  if (action === "next-card" && state.flashcards.index < state.flashcards.cards.length - 1) {
    state.flashcards.index += 1;
    state.flashcards.flipped = false;
    render();
  }
  if (action === "reset-progress") resetProgress();
});

document.addEventListener("input", (event) => {
  if (event.target.matches("[data-reference-query]")) {
    const cursor = event.target.selectionStart;
    state.reference.query = event.target.value;
    render();
    const input = document.querySelector("[data-reference-query]");
    if (input) {
      input.focus();
      input.setSelectionRange(cursor, cursor);
    }
  }
});

document.addEventListener("change", (event) => {
  if (event.target.matches("[data-reference-topic]")) {
    state.reference.topic = event.target.value;
    render();
  }
});

document.addEventListener("keydown", (event) => {
  if (state.view !== "flashcards") return;
  if (event.key === " ") {
    event.preventDefault();
    flipCard();
  }
  if (event.key === "ArrowLeft" && state.flashcards.index > 0) {
    state.flashcards.index -= 1;
    state.flashcards.flipped = false;
    render();
  }
  if (event.key === "ArrowRight" && state.flashcards.index < state.flashcards.cards.length - 1) {
    state.flashcards.index += 1;
    state.flashcards.flipped = false;
    render();
  }
});

async function init() {
  try {
    const [questions, flashcards, reference, lessons] = await Promise.all(
      Object.values(DATA_PATHS).map((path) => fetch(path).then((response) => {
        if (!response.ok) throw new Error(`Failed to load ${path}`);
        return response.json();
      })),
    );
    state.data = {
      questions: questions.questions || [],
      decks: flashcards.decks || [],
      referenceSections: reference.sections || [],
      lessons: lessons.lessons || [],
    };
    recomputeMastery();
    render();
  } catch (error) {
    app.innerHTML = `
      <section class="loading-card">
        <p class="eyebrow">Load error</p>
        <h1>Could not load the study data.</h1>
        <p class="muted">${escapeHtml(error.message)}</p>
      </section>
    `;
  }
}

init();
