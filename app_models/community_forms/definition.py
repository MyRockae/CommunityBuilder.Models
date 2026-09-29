"""Allowlisted form definition + answer validation. Used by Models and the API."""
from __future__ import annotations

import re
from typing import Any

FIELD_TYPES = frozenset(
    {
        "short_text",
        "long_text",
        "email",
        "number",
        "date",
        "single_choice",
        "multiple_choice",
    }
)
CHOICE_TYPES = frozenset({"single_choice", "multiple_choice"})
SHOW_IF_OPS = frozenset({"eq", "neq", "contains"})

MAX_FIELDS = 50
MAX_OPTIONS = 20
MAX_LABEL = 255
MAX_FIELD_ID = 40
MAX_SHORT_TEXT = 500
MAX_LONG_TEXT = 5000
MAX_NUMBER = 1e12
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
FIELD_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,39}$")


class FormDefinitionError(ValueError):
    pass


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _field_map(fields: list[dict]) -> dict[str, dict]:
    return {f["id"]: f for f in fields}


def validate_definition(definition: Any) -> dict:
    if definition is None:
        return {"fields": []}
    if not isinstance(definition, dict):
        raise FormDefinitionError("Definition must be an object.")
    fields = definition.get("fields")
    if fields is None:
        fields = []
    if not isinstance(fields, list):
        raise FormDefinitionError("fields must be a list.")
    if len(fields) > MAX_FIELDS:
        raise FormDefinitionError(f"At most {MAX_FIELDS} fields are allowed.")

    seen_ids: set[str] = set()
    normalized: list[dict] = []
    for index, raw in enumerate(fields):
        if not isinstance(raw, dict):
            raise FormDefinitionError(f"Field {index + 1} must be an object.")
        field_id = _as_str(raw.get("id")).strip()
        if not FIELD_ID_RE.match(field_id):
            raise FormDefinitionError(
                f"Field {index + 1} needs a stable id (letters, numbers, underscore)."
            )
        if field_id in seen_ids:
            raise FormDefinitionError(f"Duplicate field id '{field_id}'.")
        seen_ids.add(field_id)

        field_type = _as_str(raw.get("type")).strip()
        if field_type not in FIELD_TYPES:
            raise FormDefinitionError(f"Unsupported field type '{field_type}'.")

        label = _as_str(raw.get("label")).strip()
        if not label:
            raise FormDefinitionError(f"Field '{field_id}' needs a label.")
        if len(label) > MAX_LABEL:
            raise FormDefinitionError(f"Field '{field_id}' label is too long.")

        required = bool(raw.get("required", False))
        item: dict[str, Any] = {
            "id": field_id,
            "type": field_type,
            "label": label,
            "required": required,
        }

        if field_type in CHOICE_TYPES:
            options = raw.get("options") or []
            if not isinstance(options, list) or not options:
                raise FormDefinitionError(f"Field '{field_id}' needs options.")
            if len(options) > MAX_OPTIONS:
                raise FormDefinitionError(
                    f"Field '{field_id}' allows at most {MAX_OPTIONS} options."
                )
            opt_ids: set[str] = set()
            clean_opts = []
            for opt in options:
                if not isinstance(opt, dict):
                    raise FormDefinitionError(f"Field '{field_id}' options must be objects.")
                oid = _as_str(opt.get("id")).strip()
                olabel = _as_str(opt.get("label")).strip()
                if not FIELD_ID_RE.match(oid):
                    raise FormDefinitionError(f"Field '{field_id}' has an invalid option id.")
                if oid in opt_ids:
                    raise FormDefinitionError(f"Field '{field_id}' has a duplicate option id.")
                if not olabel or len(olabel) > MAX_LABEL:
                    raise FormDefinitionError(f"Field '{field_id}' has an invalid option label.")
                opt_ids.add(oid)
                clean_opts.append({"id": oid, "label": olabel})
            item["options"] = clean_opts

        show_if = raw.get("showIf") or raw.get("show_if")
        if show_if:
            if not isinstance(show_if, dict):
                raise FormDefinitionError(f"Field '{field_id}' showIf must be an object.")
            dep = _as_str(show_if.get("fieldId") or show_if.get("field_id")).strip()
            op = _as_str(show_if.get("op")).strip()
            if op not in SHOW_IF_OPS:
                raise FormDefinitionError(f"Field '{field_id}' has an invalid showIf op.")
            if dep == field_id:
                raise FormDefinitionError(f"Field '{field_id}' cannot depend on itself.")
            prior_ids = {f["id"] for f in normalized}
            if dep not in prior_ids:
                raise FormDefinitionError(
                    f"Field '{field_id}' showIf must target an earlier field."
                )
            item["showIf"] = {
                "fieldId": dep,
                "op": op,
                "value": show_if.get("value"),
            }

        normalized.append(item)

    return {"fields": normalized}


def show_if_matches(rule: dict, answer: Any) -> bool:
    op = rule.get("op")
    expected = rule.get("value")
    if op == "eq":
        if isinstance(answer, list):
            return _as_str(expected) in [_as_str(x) for x in answer]
        return _as_str(answer) == _as_str(expected)
    if op == "neq":
        if isinstance(answer, list):
            return _as_str(expected) not in [_as_str(x) for x in answer]
        return _as_str(answer) != _as_str(expected)
    if op == "contains":
        needle = _as_str(expected)
        if isinstance(answer, list):
            return needle in [_as_str(x) for x in answer]
        return needle.lower() in _as_str(answer).lower()
    return False


def field_is_visible(field: dict, answers: dict, fields_by_id: dict[str, dict]) -> bool:
    rule = field.get("showIf")
    if not rule:
        return True
    dep = fields_by_id.get(rule.get("fieldId"))
    if not dep:
        return False
    if not field_is_visible(dep, answers, fields_by_id):
        return False
    return show_if_matches(rule, answers.get(dep["id"]))


def _validate_value(field: dict, value: Any) -> Any:
    field_type = field["type"]
    field_id = field["id"]
    if field_type == "short_text":
        text = _as_str(value).strip()
        if len(text) > MAX_SHORT_TEXT:
            raise FormDefinitionError(f"'{field['label']}' is too long.")
        return text
    if field_type == "long_text":
        text = _as_str(value).strip()
        if len(text) > MAX_LONG_TEXT:
            raise FormDefinitionError(f"'{field['label']}' is too long.")
        return text
    if field_type == "email":
        text = _as_str(value).strip()
        if text and not EMAIL_RE.match(text):
            raise FormDefinitionError(f"'{field['label']}' must be a valid email.")
        if len(text) > MAX_LABEL:
            raise FormDefinitionError(f"'{field['label']}' is too long.")
        return text
    if field_type == "number":
        if value in ("", None):
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise FormDefinitionError(f"'{field['label']}' must be a number.")
        if not (number == number) or abs(number) > MAX_NUMBER:
            raise FormDefinitionError(f"'{field['label']}' is out of range.")
        return number
    if field_type == "date":
        text = _as_str(value).strip()
        if text and not DATE_RE.match(text):
            raise FormDefinitionError(f"'{field['label']}' must be YYYY-MM-DD.")
        return text
    option_ids = {o["id"] for o in field.get("options") or []}
    if field_type == "single_choice":
        choice = _as_str(value).strip()
        if choice and choice not in option_ids:
            raise FormDefinitionError(f"'{field['label']}' has an invalid choice.")
        return choice
    if field_type == "multiple_choice":
        if value in ("", None):
            return []
        if not isinstance(value, list):
            raise FormDefinitionError(f"'{field['label']}' must be a list of choices.")
        cleaned = []
        seen = set()
        for item in value:
            oid = _as_str(item).strip()
            if oid not in option_ids:
                raise FormDefinitionError(f"'{field['label']}' has an invalid choice.")
            if oid in seen:
                continue
            seen.add(oid)
            cleaned.append(oid)
        return cleaned
    raise FormDefinitionError(f"Unsupported field '{field_id}'.")


def normalize_answers(definition: dict, raw_answers: Any) -> dict:
    if raw_answers is None:
        raw_answers = {}
    if not isinstance(raw_answers, dict):
        raise FormDefinitionError("Answers must be an object.")
    fields = (definition or {}).get("fields") or []
    by_id = _field_map(fields)
    cleaned: dict[str, Any] = {}
    for field in fields:
        fid = field["id"]
        visible = field_is_visible(field, cleaned, by_id)
        if not visible:
            continue
        value = _validate_value(field, raw_answers.get(fid))
        empty = value in ("", None, [])
        if field.get("required") and empty:
            raise FormDefinitionError(f"'{field['label']}' is required.")
        cleaned[fid] = value
    return cleaned
