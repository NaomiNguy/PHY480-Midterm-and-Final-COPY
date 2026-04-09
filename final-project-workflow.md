# Final Project Workflow

## PHY 480, Michigan State University — Spring 2026

### Professor Sean Couch

## Overview

The final project extends the work you already completed for your midterm project. You should remain in the same topic area and continue building in the same repository unless the instructor explicitly approves a different arrangement.

The technical requirements for each topic live in the corresponding `FINAL.md` file inside that project directory. This shared workflow document explains how the final should be organized, how the midterm code should be carried forward, and what repository evidence the instructor will expect to see.

## Relationship to the midterm repository

Your final project should look like a genuine extension of the midterm, not a disconnected rewrite.

You are expected to:

1. Keep the same project topic.
2. Reuse meaningful parts of your midterm code, tests, and documentation.
3. Refactor earlier code where needed so the final methods fit cleanly into the same codebase.
4. Preserve a visible history of the transition from the midterm baseline to the final implementation.

You should **not** discard the midterm implementation and replace it with a completely new repository or a single last-minute script.

## Required carry-forward record

This is the **canonical specification** for the carry-forward record. The individual `FINAL.md` files reference this section rather than restating it.

Your final `docs/README.md` must include a short section titled `Midterm carry-forward record` or equivalent. That section should identify:

1. The commit, tag, or branch that best represents your completed midterm baseline.
2. Which midterm modules, functions, and tests you reused directly.
3. Which parts of the midterm code you refactored or replaced, and why.
4. Which later-course numerical methods were added for the final.
5. If you received peer review feedback on your midterm, at least one suggestion you addressed in your final refactoring.

This record is part of the grading evidence. If the repository does not show clear reuse of the midterm work, the project will not meet the carry-forward expectation.

## Recommended milestones

The final project should move through the following stages. Refer to `projects/final-project-grading-rubric.md` for how each stage is scored.

| Stage | Milestone | Suggested deadline |
| ----- | --------- | ------------------ |
| 1 | Freeze midterm baseline + scope declaration | **Apr 9** |
| 2 | Midpoint implementation checkpoint | **Apr 16** |
| 3 | Validation, comparison, and carry-forward record | **Apr 23** |
| 4 | Final submission | **May 1** |

### Stage 1 — Freeze the midterm baseline

Before starting the final extension:

1. Identify a clean baseline commit for the midterm version.
2. Create a branch or tag so that the midterm state is easy to inspect later.
3. Write a short scope note in your README or issue tracker describing which final-extension parts you plan to complete first.

### Stage 2 — Integrate the new numerical methods

This is the main implementation stage.

1. Extend the existing `src/` code rather than hiding work in notebooks only.
2. Add tests as you add each new solver or analysis step.
3. Keep the original midterm analysis runnable while you build the final features.
4. Commit in small steps that separate refactors, solver additions, tests, and figure generation.

### Stage 3 — Validate and compare

Before the final submission is complete, your repository should show explicit validation work:

1. Comparison against the original midterm results where appropriate.
2. Checks on convergence, stability, or parameter sensitivity.
3. Reproducible commands for regenerating tables and plots.
4. Clear explanation of where the new methods agree or disagree with the original midterm model.

### Stage 4 — Final polish and submission

At the end of the workflow, the repository should contain:

1. Updated source code in `src/`.
2. Updated or expanded tests in `tests/`.
3. Final figures and tables referenced in `docs/README.md`.
4. A complete carry-forward record.
5. A clean explanation of how to rerun the final analysis from the repo root.

## GitHub workflow expectations

The same workflow expectations from the midterm still apply.

1. Use branches when you are making substantial changes.
2. Commit early and often.
3. Keep Ruff and pytest passing throughout the project when possible.
4. Use GitHub history to make the progression from baseline to final easy to follow.

Recommended commit categories:

- baseline tag or branch setup
- refactor of midterm code into reusable functions
- implementation of each new later-course method
- tests for each new method
- figure generation and README updates

## Deliverable packaging

Unless a project-specific `FINAL.md` says otherwise, a complete final repository should include:

1. `src/` code that contains both the retained midterm functionality and the new final-method extensions.
2. `tests/` that cover both reused and newly added numerical methods.
3. `docs/README.md` describing the scientific question, numerical methods, validation strategy, and reproduction commands.
4. Clearly named figures and tables that are referenced from the documentation.

Notebook exploration is fine, but the graded implementation must live in `src/` as importable Python modules with a `main()` guard. Notebooks should not be the only place where core numerical methods are implemented.

## Final submission checklist

Before submitting, confirm all of the following:

- The original midterm prompt file `README.md` in your topic directory is still valid as the baseline prompt.
- You completed the corresponding `FINAL.md` extension tasks for your topic.
- Your repository clearly reuses midterm code instead of starting over.
- The new final methods use material from the later part of the course.
- Your tests cover the new solvers or sampling procedures.
- Your plots and tables can be regenerated from commands written in the README.
- Your carry-forward record explains what changed between midterm and final.
- Your Git history shows a real development workflow.
