#!/usr/bin/env python3
"""
PM Lesson Formatter — Phase 1
Reads a FEEDBACK_*.md report from pm_swarm.py, applies formatting transforms.
Can also run standalone on a lesson file without a report.

Usage:
  python3 pm_format.py concept-library/01-apis-and-integration/what-is-an-api.md
  python3 pm_format.py concept-library/01-apis-and-integration/what-is-an-api.md --from-report
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime
import anthropic

# Load .env from repo root
_env_path = Path(__file__).parent / '.env'
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        if '=' in _line and not _line.startswith('#'):
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 4000

FORMATTER_SYSTEM = """You are a curriculum design specialist.
Your job: take PM lesson content and restructure it for maximum scannability.
Rules:
- Do NOT change any factual content
- Do NOT reorder sections
- Do NOT add new information
- Do NOT change level markers (# FOUNDATION, # WORKING KNOWLEDGE, # STRATEGIC DEPTH)
- Do NOT change frontmatter
- DO convert dense prose decisions into comparison tables
- DO wrap key definitions in blockquote callouts (> **Term:** definition)
- DO add ⚠️ warning callouts for security/risk content
- DO structure company examples as cards (### Company — headline, **What:**, **Why:**, **Takeaway:**)
- DO add *What this reveals:* lines after each engineer question
- DO add a quick reference box at the top of Working Knowledge
- Output ONLY the reformatted markdown. No commentary."""


def load_formatting_flags(lesson_path: Path) -> list:
    """Try to load formatting flags from the swarm feedback report."""
    report_path = lesson_path.parent / f"FEEDBACK_{lesson_path.stem}.md"
    flags = []
    if report_path.exists():
        report = report_path.read_text()
        # Extract formatting flags section
        m = re.search(r'## Formatting flags(.+?)(?=##|\Z)', report, re.DOTALL)
        if m:
            for line in m.group(1).split('\n'):
                if line.strip().startswith('-'):
                    flags.append(line.strip()[1:].strip())
    return flags


def format_section(client, section_name: str, content: str, flags: list) -> str:
    """Format a single section using Claude."""
    flags_text = '\n'.join(f'- {f}' for f in flags) if flags else 'Apply standard formatting improvements.'

    prompt = f"""Reformat this section of a PM curriculum lesson for maximum scannability.
Section: {section_name}

Formatting flags from reader agents:
{flags_text}

CONTENT TO REFORMAT:
---
{content}
---

Apply the formatting transforms appropriate for this section type.
Output ONLY the reformatted markdown content. Keep the ## heading."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=FORMATTER_SYSTEM,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def format_lesson(lesson_path: Path, use_report: bool = False):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    text = lesson_path.read_text(encoding='utf-8')
    flags = load_formatting_flags(lesson_path) if use_report else []

    print(f"\nFormatting: {lesson_path.name}")
    print(f"Flags from report: {len(flags)}")
    print(f"Model: {MODEL}\n")

    # Split into frontmatter + body
    body = text
    frontmatter = ''
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            frontmatter = text[:end + 4]
            body = text[end + 4:]

    # Split body into sections
    sections = re.split(r'(?=^## )', body, flags=re.MULTILINE)
    formatted_sections = []

    for section in sections:
        if not section.strip():
            continue
        # Get section name
        name_match = re.match(r'^## (.+)$', section, re.MULTILINE)
        section_name = name_match.group(1) if name_match else 'unknown'

        # Strip trailing level-marker lines (# ═══ blocks) before sending to Claude.
        # The ## split puts them at the tail of the preceding section; Claude drops them.
        lines = section.rstrip('\n').split('\n')
        tail_markers = []
        while lines and re.match(r'^# ', lines[-1]):
            tail_markers.insert(0, lines.pop())
        section_body = '\n'.join(lines)
        marker_suffix = ('\n' + '\n'.join(tail_markers)) if tail_markers else ''

        # Sections that should NOT be reformatted
        skip_sections = ['the world before', 'related lessons', 'prerequisites']
        if any(skip in section_name.lower() for skip in skip_sections):
            formatted_sections.append(section_body + marker_suffix)
            print(f"  SKIP   {section_name}")
            continue

        # Get section-specific flags
        section_flags = [f for f in flags if section_name.lower() in f.lower()]

        print(f"  FORMAT {section_name}... ", end='', flush=True)
        formatted = format_section(client, section_name, section_body.strip(), section_flags)
        formatted_sections.append(formatted + marker_suffix)
        print("done")

    # Reassemble
    new_body = '\n\n'.join(formatted_sections)
    new_text = frontmatter + '\n' + new_body if frontmatter else new_body

    # Backup original
    backup_path = lesson_path.with_suffix('.md.bak')
    backup_path.write_text(text, encoding='utf-8')

    # Write formatted version
    lesson_path.write_text(new_text, encoding='utf-8')
    print(f"\n  Saved:   {lesson_path}")
    print(f"  Backup:  {backup_path}")
    print(f"  Words:   {len(text.split())} → {len(new_text.split())}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 pm_format.py <lesson.md> [--from-report]")
        sys.exit(1)
    lesson_path = Path(sys.argv[1])
    if not lesson_path.exists():
        print(f"Error: File not found: {lesson_path}")
        sys.exit(1)
    use_report = '--from-report' in sys.argv
    format_lesson(lesson_path, use_report)
