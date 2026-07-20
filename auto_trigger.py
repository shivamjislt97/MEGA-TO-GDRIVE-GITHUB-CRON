import json, subprocess, sys, time

try:
    d = json.load(open('completed_links.json'))
except Exception:
    d = {'folders': {}}

folders = d.get('folders', {})
oversized_raw = d.get('oversized', [])
all_done = True
remaining = 0

# Check normal folders
for name, f in folders.items():
    total = f.get('total', 0)
    done = f.get('done', 0)
    oversized_count = f.get('oversized_count', 0)
    status = f.get('status', 'pending')
    effective_done = done + oversized_count
    if status != 'completed' or effective_done < total:
        all_done = False
        remaining += total - effective_done
        print(f'  [{name}] {done}/{total} (ov:{oversized_count}) ({status})', file=sys.stderr)

# Check oversized (structured format) — only if not already marked completed
if isinstance(oversized_raw, dict):
    ov = oversized_raw
    total = ov.get('total', 0)
    done = ov.get('done', 0)
    status = ov.get('status', 'completed')
    if status != 'completed' and total > 0 and done < total:
        all_done = False
        remaining += total - done
        print(f'  [OVERSIZED] {done}/{total} uploaded | status: {status}', file=sys.stderr)
elif isinstance(oversized_raw, list):
    # legacy flat array — count items as remaining
    for ov in oversized_raw:
        all_done = False
        remaining += 1
        print(f'  [OVERSIZED] {ov.get("filename", "?")} ({ov.get("target_folder", "?")})', file=sys.stderr)
    if oversized_raw:
        print(f'  [HINT] Next run will migrate oversized to structured format', file=sys.stderr)

# Also check chunks_history for in-progress oversized — only if not already completed
try:
    ch = json.load(open('chunks_history.json'))
    for v in ch.get('videos', []):
        if v.get('status') not in ('gdrive_uploaded', 'done'):
            all_done = False
except Exception:
    pass

if remaining > 0:
    max_attempts = 3
    for attempt in range(max_attempts):
        r = subprocess.run(
            ['gh', 'workflow', 'run', 'MEGA to Google Drive Transfer', '--ref', 'main'],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            print(f'Triggered next cycle ({remaining} files remaining)')
            break
        print(f'Attempt {attempt+1}/{max_attempts} failed: {r.stderr.strip()}')
        if attempt < max_attempts - 1:
            time.sleep(10)
    else:
        print('All trigger attempts failed')
        sys.exit(1)
elif folders and all_done:
    print('All folders completed — no more cycles')
else:
    print('No pending work — no more cycles')
