from __future__ import annotations

import re


CAPTION_RE = re.compile(r"^\s*((?:Fig\.|Figure|Table)\s+[A-Za-z0-9IVXLCDM]+)\s*[:.\-]?\s*(.*)", re.IGNORECASE)
FIGURE_MENTION_RE = re.compile(r"\b(?:Fig\.|Figure)\s+([A-Za-z0-9IVXLCDM]+)\b", re.IGNORECASE)
TABLE_MENTION_RE = re.compile(r"\bTable\s+([A-Za-z0-9IVXLCDM]+)\b", re.IGNORECASE)
REFERENCE_ITEM_RE = re.compile(r"^\s*(?:\[\d+\]|\d+\.)\s+")
NUMBERED_HEADING_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+[A-Z][^\n]{2,}$")


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def is_probable_caption(text: str) -> bool:
    return bool(CAPTION_RE.match(text))


def caption_label(text: str) -> str | None:
    match = CAPTION_RE.match(text)
    if not match:
        return None
    label = match.group(1)
    label = re.sub(r"^Fig\.", "Figure", label, flags=re.IGNORECASE)
    return " ".join(label.split())


def caption_kind(text: str) -> str | None:
    label = caption_label(text)
    if not label:
        return None
    return "table" if label.lower().startswith("table") else "figure"


def strip_caption_label(text: str) -> str:
    match = CAPTION_RE.match(text)
    if not match:
        return text.strip()
    return match.group(2).strip() or text.strip()


def fix_english_hyphenation(text: str) -> str:
    return re.sub(r"([A-Za-z])-\s+([a-z])", r"\1\2", text)


def has_terminal_punctuation(text: str) -> bool:
    return text.rstrip().endswith((".", "!", "?", ":", ";", ")", "]"))

