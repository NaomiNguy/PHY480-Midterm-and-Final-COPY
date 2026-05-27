# Final Project Grading Rubric

## PHY 480, Michigan State University — Spring 2026

### Professor Sean Couch

## Purpose

This rubric defines the shared grading expectations for the final projects. Each topic also has its own **technical 100-point rubric** inside the corresponding `FINAL.md` file. The shared rubric below covers the workflow evidence that should appear in your repository as you extend your midterm work into a final project.

## Scoring structure

Raw total: **125 points**

- **Stage 1 - Midterm baseline and scope declaration:** 5 points
- **Stage 2 - Midpoint implementation evidence:** 10 points
- **Stage 3 - Final carry-forward response and reproducibility:** 10 points
- **Stage 4 - Final instructor review using the project-specific FINAL.md rubric:** 100 points

If needed for gradebook entry, the raw score can be normalized to the assignment scale used in the course gradebook.

## Stage 1 - Midterm baseline and scope declaration (5 points)

This stage checks whether you have anchored the final project to a visible midterm baseline and identified a realistic extension path.

### Stage 1 full credit (5 points)

- The repository clearly identifies a midterm baseline commit, tag, or branch.
- You state which project topic you are extending.
- You record a short plan for the final extension, including the later-course methods you intend to add.

### Stage 1 partial credit (2-4 points)

- A baseline is implied but not documented clearly.
- The intended final extension is present but too vague to evaluate well.

### Stage 1 no credit (0 points)

- There is no clear midterm baseline or scope declaration.
- The repository gives no evidence that the final is an extension of prior work.

## Stage 2 - Midpoint implementation evidence (10 points)

This stage checks whether the repository shows real technical progress toward the final extension before the last submission push.

### Stage 2 full credit (10 points)

- The repository shows meaningful intermediate commits after the midterm baseline.
- At least one new later-course method is partially implemented and testable.
- Documentation or commit messages make the development path understandable.
- The work is organized well enough that someone reviewing the repository can see how the midterm code is being extended.

### Stage 2 partial credit (5-9 points)

- Some extension work is visible, but the history is thin or hard to interpret.
- Implementation exists but is poorly organized, missing tests, or only partially connected to the midterm code.

### Stage 2 no credit (0 points)

- There is no meaningful checkpoint evidence before the final submission.
- The repository appears to jump from the midterm baseline to a last-minute dump of work.

## Stage 3 - Final carry-forward response and reproducibility (10 points)

This stage checks whether you documented how the final grew out of the midterm and whether the final analysis can be rerun by someone else.

### Stage 3 full credit (10 points)

- `docs/README.md` includes a clear carry-forward record.
- The documentation explains which midterm code was reused, what changed, and why.
- The documentation provides runnable commands for regenerating the final outputs.
- The repository structure and README make the final workflow easy to follow.

### Stage 3 partial credit (5-9 points)

- Some carry-forward explanation is present, but it is incomplete or vague.
- Reproduction commands are missing pieces, unclear, or inconsistent with the repo contents.

### Stage 3 no credit (0 points)

- There is no meaningful carry-forward explanation.
- The final work is not reproducible from the repository documentation.

## Stage 4 - Final instructor review (100 points)

The technical grading of the final project comes from the project-specific rubric in the corresponding `FINAL.md` file.

Project-specific final rubrics:

- `projects/midterm_project_01_normal_modes/FINAL.md`
- `projects/midterm_project_02_exoplanet_dft/FINAL.md`
- `projects/midterm_project_03_grav_potential_2d/FINAL.md`
- `projects/midterm_project_04_multivar_relaxation/FINAL.md`

In addition to the topic-specific categories in those files, all common project expectations from `projects/README.md` still apply.

## Evidence the instructor may use

The instructor may use the following evidence when applying this rubric:

- repository contents and file organization
- commit history
- tests and whether they target the actual numerical methods used
- reproducibility of commands, figures, and tables
- clarity of the carry-forward record
- the degree to which later-course methods are integrated into the reused midterm codebase

## Notes on scoring philosophy

- A technically strong final project should still show visible continuity with the midterm.
- A repository that starts over from scratch can lose credit even if the end result looks polished.
- Reproducibility and validation remain part of the grade, not optional extras.
- A final project should be judged on both numerical quality and evidence of a disciplined computational workflow.
- The carry-forward evidence in Stage 3 (shared rubric) and the carry-forward category in the project-specific rubric (Stage 4) evaluate different things: Stage 3 focuses on documentation and reproducibility of the transition; Stage 4 focuses on whether the midterm code is technically integrated into the final implementation. There is some intentional overlap, but you will not lose points twice for the same evidence.
- Refer to `projects/final-project-workflow.md` for suggested stage deadlines.
