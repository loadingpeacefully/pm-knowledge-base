#!/usr/bin/env python3
"""
build_lessons_json.py
Reads _CONCEPT_INDEX.md + all lesson .md files → writes dashboard/lessons.json
Run: python3 control/build_lessons_json.py
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).parent.parent
INDEX = REPO / 'concept-library' / '_CONCEPT_INDEX.md'
OUT   = REPO / 'dashboard' / 'lessons.json'


def parse_index(text: str) -> list[dict]:
    lessons = []
    mod_map = {}

    for raw in text.split('\n'):
        line = raw.strip()
        if not line:
            continue
        if re.match(r'^## Pipeline', line, re.IGNORECASE):
            break

        mh = re.match(r'^## Module (\d{2})\s*[—\-–]\s*(.+)$', line)
        if mh:
            num, name = mh.group(1), mh.group(2).strip()
            mod_map[num] = name
            continue

        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        lesson_id = cells[0] if cells else ''
        if not re.match(r'^\d{2}\.\d{2}$', lesson_id):
            continue

        title    = cells[1] if len(cells) > 1 else ''
        file     = cells[2] if len(cells) > 2 else ''
        raw_st   = (cells[3] if len(cells) > 3 else '').lower().replace('—', '').replace('–', '').strip()
        writer   = cells[4] if len(cells) > 4 else ''
        mod_num  = lesson_id[:2]
        status   = 'ready' if raw_st == 'ready' else 'draft' if raw_st == 'draft' else 'none'

        lessons.append({
            'id':           lesson_id,
            'title':        title,
            'module_id':    mod_num,
            'module_title': mod_map.get(mod_num, 'Module ' + mod_num),
            'status':       status,
            'writer':       writer,
            'file':         file,
        })

    return lessons


def build():
    index_text = INDEX.read_text(encoding='utf-8')
    lessons = parse_index(index_text)

    loaded = 0
    for lesson in lessons:
        path = REPO / 'concept-library' / lesson['file'] if lesson['file'] else None
        if path and path.exists():
            lesson['content'] = path.read_text(encoding='utf-8')
            loaded += 1
        else:
            lesson['content'] = None

    payload = {
        'generated_at': datetime.now(tz=timezone.utc).isoformat(),
        'lessons':      lessons,
    }

    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')

    size_kb = round(OUT.stat().st_size / 1024)
    print(f'dashboard/lessons.json written')
    print(f'  Lessons total  : {len(lessons)}')
    print(f'  Content loaded : {loaded}')
    print(f'  File size      : {size_kb} KB')


if __name__ == '__main__':
    build()
