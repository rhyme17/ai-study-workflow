# Prompt Library

Use these prompts with allowed course materials only.

## Fast Source Entry

```text
Use the provided course file to create a fast study entry. First give a compact source card with scope, extraction quality, and visual-check caveats. Then offer exactly three choices: new learning, exam review, or material generation. Recommend one choice based on the user's goal. If the user chooses new learning and has not studied the topic, start with one tiny learning block and at most 1-2 low-stakes readiness questions. If the user chooses exam review, end with 6-10 closed-book diagnostic questions and do not show answers yet.
```

## Course Triage

```text
You are helping me prepare for a university exam. Use only the materials I provide. First make a source-quality note: scope, extraction gaps, sparse pages, and anything that needs human check. Then build a table with topic, likely exam relevance, evidence source, confidence level, main risk, and next review action. Do not invent priorities without evidence.
```

## Closed-Book Diagnostic

```text
Create a diagnostic quiz from the provided materials in the likely exam format. Show questions only; do not show answers, hints, or worked solutions yet. After I answer, grade strictly and classify every mistake as concept, procedure, memory, speed, or careless.
```

## Socratic Repair

```text
I will explain this concept in my own words. Do not give a full answer first. Find gaps, ask up to five Socratic questions, then give one transfer problem to check whether I can apply it.
```

## Rubric Feedback

```text
Grade my answer against the rubric or scoring criteria. Separate feedback into correct, missing, incorrect, and next practice task. Cite the source section when possible.
```

## New Knowledge Map

```text
Help me learn this topic from scratch. First give a compact concept skeleton and teach the first small block in plain language. Ask at most one quick check before continuing. Do not start with a long prerequisite quiz unless I say I have already learned this topic or ask to be tested. For the near practice problem and transfer problem, stop after the question and wait for my answer before revealing the solution.
```

## Anti-Dependency Check

```text
Test whether I understand this without relying on your wording. Ask one question at a time. If my answer is shallow, ask for reasoning, edge cases, or a new example before moving on.
```

## Card Generation

```text
Turn these graded mistakes into concise active-recall cards. Each card should test one idea only, include a source tag, and avoid vague prompts like "explain X". Prefer cloze, why/how, compare/contrast, and error-correction cards. If a source is unclear or conflicting, mark the card as needs human check instead of finalizing the back.
```
