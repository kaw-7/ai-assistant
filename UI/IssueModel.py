# -*- coding: utf-8 -*-
"""What the issue viewer shows of an issue - status, title, kind and IDs.

The AI writes the status in many spellings ("NO RISK", "No Risk.", "RISK",
"Risk exists", "NO_RISK" ...).  :func:`status_key` maps all of them onto the
three keys the viewer works with; :func:`set_status` writes the value back in
the spelling of ``ui_config``.  An issue keeps its original spelling until its
status is changed in the viewer.
"""
from __future__ import annotations

import re

try:
    import UI.ui_config as uiConf
except ImportError:
    import ui_config as uiConf

RISK_EXISTS = "risk_exists"
NO_RISK = "no_risk"
NOT_EVALUATED = "not_evaluated"

STATUS_KEYS = (RISK_EXISTS, NO_RISK, NOT_EVALUATED)

STATUS_LABELS = {
    RISK_EXISTS: "Risk exists",
    NO_RISK: "No risk",
    NOT_EVALUATED: "Not evaluated",
}

# the value written into the report when the status is changed in the viewer
_STORED_STATUS = {
    RISK_EXISTS: uiConf.RISK_EXISTS,
    NO_RISK: uiConf.NO_RISK,
    NOT_EVALUATED: uiConf.NOT_EVALUATED,
}

# checked in this order: "no risk" contains "risk", "not evaluated" contains "not"
_STATUS_PATTERNS = (
    (NOT_EVALUATED, re.compile(r"not.?evaluated", re.IGNORECASE)),
    (NO_RISK, re.compile(r"\bno.?risk", re.IGNORECASE)),
    (RISK_EXISTS, re.compile(r"\brisk(.?exists?)?\b", re.IGNORECASE)),
)

MARKER_PREFIX = "MARKER!"

# "bugfix: Fixed ..." - the prefix of the release note entry names its kind
_KIND_PREFIXES = {
    "bugfix": "Bug fix",
    "improved": "Improvement",
    "new": "New feature",
    "removed": "Removed",
    "security fix": "Security fix",
}
_PREFIX_PATTERN = re.compile(r"^\s*([A-Za-z][A-Za-z ]{1,15}):\s*")


def status_key(item: dict) -> str:
    """One of :data:`STATUS_KEYS`; an empty or unknown status is not evaluated."""
    text = (item.get(uiConf.STATUS) or "").strip()
    for key, pattern in _STATUS_PATTERNS:
        if pattern.search(text):
            return key
    return NOT_EVALUATED


def set_status(item: dict, key: str) -> None:
    item[uiConf.STATUS] = _STORED_STATUS[key]


def is_marker(item: dict) -> bool:
    """The AI marks entries that are no defect correction (new, improved...)."""
    return (item.get(uiConf.DESCRIPTION) or "").strip().startswith(MARKER_PREFIX)


def _split_prefix(text: str) -> tuple[str | None, str]:
    match = _PREFIX_PATTERN.match(text)
    if match and match.group(1).strip().lower() in _KIND_PREFIXES:
        return match.group(1).strip().lower(), text[match.end():]
    return None, text


def title(item: dict) -> str:
    """The one line naming the issue in the list and above the details."""
    description = (item.get(uiConf.DESCRIPTION) or "").strip()
    if description and not is_marker(item):
        return description.splitlines()[0]
    # a marker carries no title of its own - the release note entry is the title
    defect = (item.get(uiConf.DEFECT_DESCRIPTION) or "").strip()
    _prefix, rest = _split_prefix(defect)
    first_line = rest.strip().splitlines()[0] if rest.strip() else ""
    return first_line or description or "(no description)"


def kind(item: dict) -> str:
    """'Bug fix', 'Improvement' ... or '' when the release note does not say."""
    prefix, _rest = _split_prefix((item.get(uiConf.DEFECT_DESCRIPTION) or "").strip())
    if prefix:
        return _KIND_PREFIXES[prefix]
    return "Improvement" if is_marker(item) else ""


def defect_ids(item: dict) -> list[str]:
    raw = item.get(uiConf.DEFECT_ID) or ""
    return [part.strip() for part in re.split(r"[,;\n]", raw) if part.strip()]


def matches_query(item: dict, query: str) -> bool:
    """Case insensitive search in the ID, the title and the defect description."""
    query = query.strip().lower()
    if not query:
        return True
    haystack = " ".join((
        item.get(uiConf.DEFECT_ID) or "",
        title(item),
        item.get(uiConf.DEFECT_DESCRIPTION) or "",
    )).lower()
    return query in haystack
