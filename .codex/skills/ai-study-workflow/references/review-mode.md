# Review Mode

Use review mode for finals, exams, quizzes, retakes, and course review when the student has already seen most material.

## Goal

Maximize exam readiness by finding weak points quickly, repairing them, and testing again under realistic conditions.

## Required Inputs

- course name and exam date
- exam format if known
- allowed course materials
- AI policy or safe assumption
- student's current confidence by topic
- available study hours

If any input is missing, ask at most one important question. If the answer is not essential, proceed with a stated assumption.
If the user provides source files, perform the source pass in `source-ingestion.md` before triage.

## Interaction Protocol

Use this mode as a coach for active recall:

- In the first turn, prefer a short diagnostic over a full multi-day plan when exam timing is unclear or speed matters.
- Do not show diagnostic answers in the same response as the questions.
- Do not create final card backs before the student attempts the relevant question, unless the user explicitly requests prebuilt cards.
- Stop after a diagnostic set, mock set, or transfer task and ask the student to answer.
- When grading, separate `correct`, `missing`, `incorrect`, `next drill`, and `card candidate`.
- Mark any source conflict, unclear exam scope, or extraction gap as `needs human check`.

## Fast First Turn

When course material is provided and the user wants efficient review, start with:

1. One-line source card and caveat.
2. 6-10 closed-book diagnostic questions.
3. A request for the student's answers.

Do not produce the full study plan until after grading the diagnostic, unless the user explicitly asks for a plan first.

## Core Loop

1. **Course triage**
   - Build a topic table: topic, evidence of importance, confidence, risk, next action.
   - Do not let AI invent priorities without evidence from syllabus, lectures, assignments, or allowed past papers.
   - Include a human-check list for unclear exam scope or conflicting source examples.
   - For slide decks, confirm whether appendix, optional, or additional slides are in exam scope before ranking them high.

2. **Closed-book diagnostic**
   - Generate practice questions from allowed materials.
   - Hide answers until the student attempts them.
   - Grade using a rubric or explicit scoring points.
   - Ask for the student's answers before giving worked solutions.

3. **Mistake taxonomy**
   - Classify each miss as concept, procedure, memory, speed, or careless.
   - Prioritize concept and procedure mistakes before memory and speed issues.

4. **AI tutoring repair**
   - Make the student explain the idea in 3-5 sentences.
   - Ask Socratic questions before giving a polished explanation.
   - End with one transfer problem.

5. **Card generation**
   - Create 1-3 active-recall cards per real mistake.
   - Keep one idea per card.
   - Add a source tag such as `lecture-7`, `assignment-3`, or `mock-1`.
   - Prefer draft fronts before diagnosis and complete backs after grading.

6. **Timed mock**
   - Run a realistic timed set 3-5 days before the exam.
   - Track score, time, recurring mistake types, and next priorities.

## 7-Day Finals Plan

| Day | Focus | Output |
| --- | --- | --- |
| D-7 | Course triage and first diagnostic | topic table, weak-point list |
| D-6 | Repair highest-risk topics | cards, transfer problems |
| D-5 | Repair second-risk topics | cards, short quiz |
| D-4 | Timed mock 1 | score, error taxonomy |
| D-3 | Error-driven repair | hard-card list |
| D-2 | Timed mock 2 | final risk list |
| D-1 | Light review only | formula/definition/error sheet |

## Daily Block

For a 3-hour day:

1. 30 min: spaced review and hard cards
2. 60 min: highest-risk topic repair
3. 45 min: practice and transfer problems
4. 30 min: AI grading and mistake taxonomy
5. 15 min: cards and next-day plan

## Completion Signals

- The student can explain core topics without notes.
- The student can solve unseen problems under time pressure.
- The student's recurring mistake types are shrinking.
- The final 24 hours are review-only, not first-time learning.
- A second diagnostic or mock shows improvement on the highest-risk mistake categories.
