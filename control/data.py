#!/usr/bin/env python3
"""
PM·Control data pipeline.
Reads: concept-library/_CONCEPT_INDEX.md + all FEEDBACK_*.md reports
Writes: control/data.json
Run: python3 control/data.py
"""

import json, re, os
from pathlib import Path
from datetime import datetime, timezone

REPO        = Path(__file__).parent.parent
CONCEPT_LIB = REPO / 'concept-library'
OUTPUT      = Path(__file__).parent / 'data.json'

# ── helpers ──────────────────────────────────────────────────────────────────

def parse_manifest():
    """Parse _CONCEPT_INDEX.md → list of modules each with lessons list."""
    path = CONCEPT_LIB / '_CONCEPT_INDEX.md'
    if not path.exists():
        return []

    modules, cur = [], None
    for line in path.read_text(encoding='utf-8').splitlines():

        # Module heading e.g. "## Module 01 — APIs & Integration"
        mh = re.match(r'^##\s+Module\s+(\d+)\s*[—\-]+\s*(.+)', line)
        if mh:
            cur = {'id': mh.group(1).zfill(2),
                   'title': mh.group(2).strip(),
                   'lessons': []}
            modules.append(cur)
            continue

        # Table row e.g. "| 01.04 | Rate Limiting | file.md | ready | persona |"
        if line.startswith('|') and cur:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if not cells or not re.match(r'^\d{2}\.\d{2}$', cells[0]):
                continue
            cur['lessons'].append({
                'id':     cells[0],
                'title':  cells[1] if len(cells) > 1 else '',
                'file':   cells[2] if len(cells) > 2 else '',
                'status': cells[3] if len(cells) > 3 else '—',
                'writer': cells[4] if len(cells) > 4 else '',
            })
    return modules


def parse_feedback(lesson_file: str) -> dict:
    """Parse a FEEDBACK_*.md report and return structured data."""
    stem   = Path(lesson_file).stem          # e.g. "what-is-an-api"

    # Find the matching FEEDBACK file
    matches = list(CONCEPT_LIB.rglob(f'FEEDBACK_{stem}.md'))
    if not matches:
        return {}

    f    = matches[0]
    text = f.read_text(encoding='utf-8')

    def first_float(pattern):
        m = re.search(pattern, text, re.IGNORECASE)
        try:    return round(float(m.group(1)), 1) if m else None
        except: return None

    def count(pattern):
        return len(re.findall(pattern, text))

    avg       = first_float(r'[Aa]verage\s+score[^\d]*([0-9.]+)')
    f_score   = first_float(r'\|\s*[Ff]oundation\s*\|\s*([0-9.]+)')
    w_score   = first_float(r'\|\s*[Ww]orking\s*\|\s*([0-9.]+)')
    s_score   = first_float(r'\|\s*[Ss]trategic\s*\|\s*([0-9.]+)')
    health_m  = re.search(r'[Hh]ealth[^\w]*(EXCELLENT|GOOD|NEEDS_WORK|POOR)', text)
    mtime     = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat()

    return {
        'score':           avg,
        'health':          health_m.group(1) if health_m else None,
        'criticals':       count(r'\[CRITICAL\]'),
        'highs':           count(r'\[HIGH\]'),
        'mediums':         count(r'\[MEDIUM\]'),
        'run_formatter':   bool(re.search(r'run_formatter.*true', text, re.IGNORECASE)),
        'last_run':        mtime,
        'scores_by_level': {
            'foundation': f_score,
            'working':    w_score,
            'strategic':  s_score,
        },
    }


def word_count(file_path: str) -> int:
    full = CONCEPT_LIB / file_path
    if not full.exists():
        return 0
    return len(full.read_text(encoding='utf-8').split())


# ── main ─────────────────────────────────────────────────────────────────────

def build():
    modules = parse_manifest()
    lessons = []
    scores  = []
    total_critical = 0

    for mod in modules:
        for les in mod['lessons']:
            fb  = parse_feedback(les['file']) if les['file'] else {}
            wc  = word_count(les['file'])     if les['file'] else 0
            sc  = fb.get('score')

            if sc: scores.append(sc)
            total_critical += fb.get('criticals', 0)

            lessons.append({
                'id':            les['id'],
                'title':         les['title'],
                'module_id':     mod['id'],
                'module_title':  mod['title'],
                'file':          les['file'],
                'status':        les['status'],
                'writer':        les['writer'],
                'word_count':    wc,
                **fb,
            })

    avg_score = round(sum(scores) / len(scores), 1) if scores else None

    data = {
        'generated_at': datetime.now(tz=timezone.utc).isoformat(),
        'summary': {
            'total_lessons':     sum(len(m['lessons']) for m in modules),
            'lessons_scored':    len(scores),
            'avg_score':         avg_score,
            'total_critical':    total_critical,
            'feedback_reports':  len(scores),
            'modules_total':     len(modules),
        },
        'modules':  modules,
        'lessons':  lessons,
        'agents': [
            {'id':'P1',  'name':'Priya',       'role':'Non-tech biz PM',        'level':'foundation'},
            {'id':'P2',  'name':'Arjun',        'role':'Ex-engineer PM',          'level':'strategic'},
            {'id':'P3',  'name':'Sofia',        'role':'MBA PM',                  'level':'foundation'},
            {'id':'P4',  'name':'Rahul',        'role':'Aspiring PM / SDE',       'level':'foundation'},
            {'id':'P5',  'name':'Meera',        'role':'Growth / Data PM',        'level':'working'},
            {'id':'P6',  'name':'Lena',         'role':'Designer → PM',           'level':'foundation'},
            {'id':'P7',  'name':'Vikram',       'role':'Enterprise B2B PM',       'level':'working'},
            {'id':'P8',  'name':'Anya',         'role':'Consumer startup PM',     'level':'working'},
            {'id':'P9',  'name':'Zain',         'role':'Gen-Z AI-native PM',      'level':'strategic'},
            {'id':'P10', 'name':'Deepa',        'role':'Senior PM / HoP',         'level':'strategic'},
            {'id':'D1',  'name':'Nadia',        'role':'Senior product designer', 'level':'working'},
            {'id':'SYN', 'name':'Synthesizer',  'role':'Cross-agent synthesis',   'level':'all'},
            {'id':'FMT', 'name':'Formatter',    'role':'Markdown formatter',      'level':'all'},
        ],
    }

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(f'✓ Written: {OUTPUT}')
    print(f'  Lessons: {data["summary"]["total_lessons"]} total, '
          f'{data["summary"]["lessons_scored"]} scored')
    print(f'  Avg score: {avg_score}')
    print(f'  Critical flags: {total_critical}')
    return data


if __name__ == '__main__':
    build()
