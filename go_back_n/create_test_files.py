import os

sizes = {
    "10KB.txt": 10 * 1024,
    "50KB.txt": 50 * 1024,
    "100KB.txt": 100 * 1024,
    "500KB.txt": 500 * 1024,
    "1MB.txt": 1 * 1024 * 1024,
    "5MB.txt": 5 * 1024 * 1024,
    "10MB.txt": 10 * 1024 * 1024,
    "50MB.txt": 50 * 1024 * 1024,
    "100MB.txt": 100 * 1024 * 1024,
}

os.makedirs("tests/test_files", exist_ok=True)

for filename, size in sizes.items():
    path = f"tests/test_files/{filename}"
    with open(path, "wb") as f:
        f.write(b"A" * size)
    print(f"Created {path}")