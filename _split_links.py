import json, os, math

file_path = 'MEGA_LINKS.json'
with open(file_path, encoding='utf-8') as f:
    data = f.read()

size_bytes = len(data.encode('utf-8'))
max_size = 45 * 1024  # 45KB margin

chunks = []
start = 0
while start < len(data):
    end = min(start + max_size, len(data))
    if end < len(data):
        cut = data.rfind(',', start, end)
        if cut > start:
            end = cut + 1
    chunk = data[start:end]
    if chunk.startswith(','):
        chunk = chunk[1:]
    chunks.append(chunk)
    start = end

print(f'Total size: {size_bytes} bytes')
print(f'Chunks: {len(chunks)}')
for i, c in enumerate(chunks):
    sz = len(c.encode('utf-8'))
    label = f'MEGA_LINKS' if i == 0 else f'MEGA_LINKS_{i}'
    print(f'  {label}: {sz} bytes')
    fname = f'MEGA_LINKS_part_{i}.txt'
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(c)

print('\nFiles created:')
for i in range(len(chunks)):
    fname = f'MEGA_LINKS_part_{i}.txt'
    sz = os.path.getsize(fname)
    print(f'  {fname}  ({sz} bytes)')
