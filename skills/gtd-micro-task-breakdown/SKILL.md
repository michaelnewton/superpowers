---
name: gtd-micro-task-breakdown
description: Use when you have an implementation plan and need to export it as a dependency-aware GTD micro-task file instead of implementing code
---

# GTD Micro Task Breakdown

Convert an implementation plan into tiny, testable, dependency-aware execution tasks and export them to a structured file for later tooling.

**Announce at start:** "I'm using the gtd-micro-task-breakdown skill to export a micro-execution task file."

## When To Use

Use this skill when:
- The user has an implementation plan and wants execution broken into very small next actions
- The output should be a machine-consumable task file
- The user does **not** want the implementation executed yet

Do not use this skill to create backlog tickets directly. This skill only exports the intermediate task file.

## Output Location

Default output:
- `.project/tasks/micro_execution_plan.json`

If the user explicitly asks for YAML, write:
- `.project/tasks/micro_execution_plan.yaml`

Prefer JSON by default.

## Hard Rules

- Do not modify application code
- Do not run implementation tasks
- Do not add backlog items to external tools
- Read the implementation plan once, then work from the extracted task structure
- Keep tasks small enough to be completed in 5-10 minutes unless an explicit exception is required

## Granularity Rules

Each generated task must be:
- One small next action
- 5-10 minutes max
- A single functional change
- Testable in isolation
- Clear about its dependency and parent relationship
- Narrow in scope, do not combine backend, frontend, and database work unless truly trivial

Split large steps aggressively. Prefer more tasks over fewer tasks when the plan supports that decomposition.

## Required Schema

Each export must have:

```json
{
  "version": 1,
  "project": "sample-project",
  "task_id_prefix": "SAM",
  "source_plan": "docs/superpowers/plans/feature.md",
  "generated_at": "2026-05-12T18:00:00+10:00",
  "tasks": [
    {
      "id": "SAM-001",
      "parent_id": null,
      "title": "Create project folder structure",
      "type": "setup",
      "status": "pending",
      "estimated_minutes": 5,
      "depends_on": [],
      "description": "Create the minimal backend, frontend, tests, and docs folders.",
      "acceptance_criteria": [
        "Required folders exist.",
        "No application logic is added."
      ],
      "test_command": null,
      "files_expected": [
        "backend/",
        "frontend/",
        "tests/"
      ]
    }
  ]
}
```

## Task Design Guidance

- Use project-scoped stable IDs: `<PREFIX>-001`, `<PREFIX>-002`, ...
- Set `task_id_prefix` to a 3-letter uppercase prefix derived from the project name, for example `SAM`, `API`, `WEB`
- Every task id must use that prefix
- Use `parent_id` to group related sub-work under a larger track when useful
- Use `depends_on` only for real execution constraints
- `type` should be a concise category such as `setup`, `backend`, `frontend`, `database`, `test`, `docs`, `infra`, or `integration`
- `status` should start as `pending`
- `estimated_minutes` should usually be `5` or `10`
- Every task needs a concrete description
- Every task needs at least one acceptance criterion
- Include `test_command` when there is a meaningful isolated verification command; otherwise `null`
- Include `files_expected` whenever the plan makes the file or folder impact knowable

## Workflow

1. Read the implementation plan and extract the major tasks or phases.
2. Expand each plan task into the smallest reasonable next actions.
3. Add parent-child relationships where they help preserve structure.
4. Add dependencies so execution order is explicit.
5. Write the export file to `.project/tasks/`.
6. Run `python3 scripts/validate_micro_tasks.py <path-to-file>`.
7. If validation fails, fix the file and rerun the validator.

## Validation Standard

The export is invalid if:
- IDs are not unique
- `task_id_prefix` is missing or malformed
- Any task ID does not match the project prefix format
- `parent_id` points to a missing task
- `depends_on` contains a missing task
- Any task exceeds 10 minutes without an explicit `exception: true`
- Any task is missing `description`
- Any task is missing `acceptance_criteria`
- Any task is missing `type`

## Final Response

Report:
- Which file was created
- How many tasks were exported
- Whether validation passed

Do not describe implementation progress, because no implementation should have happened.
