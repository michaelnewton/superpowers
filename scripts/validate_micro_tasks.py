#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def load_document(path: Path):
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")

    if suffix == ".json":
        return json.loads(text)

    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise SystemExit(
                "YAML validation requires PyYAML. Install it or export JSON instead."
            ) from exc
        return yaml.safe_load(text)

    raise SystemExit(f"Unsupported file type: {path.suffix}")


def ensure(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_task(task: dict, ids: set[str], errors: list[str]) -> None:
    task_id = task.get("id")
    ensure(isinstance(task_id, str) and task_id, "Task is missing a valid id", errors)

    title = task.get("title")
    ensure(
        isinstance(title, str) and title.strip(),
        f"{task_id or '<unknown>'}: missing title",
        errors,
    )

    task_type = task.get("type")
    ensure(
        isinstance(task_type, str) and task_type.strip(),
        f"{task_id or '<unknown>'}: missing type",
        errors,
    )

    description = task.get("description")
    ensure(
        isinstance(description, str) and description.strip(),
        f"{task_id or '<unknown>'}: missing description",
        errors,
    )

    acceptance = task.get("acceptance_criteria")
    ensure(
        isinstance(acceptance, list) and len(acceptance) > 0,
        f"{task_id or '<unknown>'}: missing acceptance_criteria",
        errors,
    )

    estimated = task.get("estimated_minutes")
    ensure(
        isinstance(estimated, int) and estimated > 0,
        f"{task_id or '<unknown>'}: estimated_minutes must be a positive integer",
        errors,
    )

    exception_flag = task.get("exception", False)
    ensure(
        estimated is None
        or (estimated <= 10 or exception_flag is True),
        f"{task_id or '<unknown>'}: estimated_minutes exceeds 10 without exception=true",
        errors,
    )

    parent_id = task.get("parent_id")
    ensure(
        parent_id is None or parent_id in ids,
        f"{task_id or '<unknown>'}: parent_id {parent_id!r} does not exist",
        errors,
    )

    depends_on = task.get("depends_on", [])
    ensure(
        isinstance(depends_on, list),
        f"{task_id or '<unknown>'}: depends_on must be a list",
        errors,
    )
    if isinstance(depends_on, list):
        for dep in depends_on:
            ensure(
                dep in ids,
                f"{task_id or '<unknown>'}: depends_on {dep!r} does not exist",
                errors,
            )


def validate_document(doc: dict) -> list[str]:
    errors: list[str] = []

    ensure(isinstance(doc, dict), "Document root must be an object", errors)
    if not isinstance(doc, dict):
        return errors

    ensure(doc.get("version") == 1, "version must be 1", errors)

    task_id_prefix = doc.get("task_id_prefix")
    ensure(
        isinstance(task_id_prefix, str) and re.fullmatch(r"[A-Z]{3}", task_id_prefix) is not None,
        "task_id_prefix must be a 3-letter uppercase string",
        errors,
    )

    tasks = doc.get("tasks")
    ensure(isinstance(tasks, list) and len(tasks) > 0, "tasks must be a non-empty list", errors)
    if not isinstance(tasks, list) or not tasks:
        return errors

    ids: list[str] = []
    for task in tasks:
        if not isinstance(task, dict):
            errors.append("Each task must be an object")
            continue
        task_id = task.get("id")
        if isinstance(task_id, str):
            ids.append(task_id)

    if len(ids) != len(set(ids)):
        errors.append("Task IDs must be unique")

    id_set = set(ids)
    for task in tasks:
        if isinstance(task, dict):
            validate_task(task, id_set, errors)
            task_id = task.get("id")
            if (
                isinstance(task_id_prefix, str)
                and re.fullmatch(r"[A-Z]{3}", task_id_prefix) is not None
                and isinstance(task_id, str)
            ):
                ensure(
                    re.fullmatch(rf"{task_id_prefix}-\d{{3}}", task_id) is not None,
                    f"{task_id}: id must match {task_id_prefix}-NNN",
                    errors,
                )

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_micro_tasks.py <path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    try:
        document = load_document(path)
        errors = validate_document(document)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Validation error: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    task_count = len(document["tasks"])
    print(f"Validation passed: {task_count} tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
