"""
Downloads every card image listed in cards.json from Google Drive into ./images/,
saved under the exact filename cards.json expects, and checks the Drive filename
matches. The images must be shared as "Anyone with the link can view".

Usage:  pip install requests
        python download_images.py
"""
import json, os, re, requests

cards = json.load(open("cards.json", encoding="utf-8"))
os.makedirs("images", exist_ok=True)
mismatches, failures = [], []

for c in cards:
    url = f"https://drive.google.com/uc?export=download&id={c['driveId']}"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        if not r.headers.get("Content-Type", "").startswith("image/"):
            raise ValueError("not an image (is the file shared publicly?)")
    except Exception as e:
        failures.append(f"{c['name']}: {e}")
        continue

    drive_name = re.search(r'filename="?([^";]+)', r.headers.get("Content-Disposition", ""))
    expected = os.path.basename(c["image"])
    if drive_name and drive_name.group(1) != expected:
        mismatches.append(f"{c['name']}: Drive file is '{drive_name.group(1)}', saved as '{expected}'")

    with open(c["image"], "wb") as f:
        f.write(r.content)
    print("saved", c["image"])

print(f"\nDone: {len(cards) - len(failures)}/{len(cards)} downloaded.")
for m in mismatches: print("NAME CHECK:", m)
for f in failures:   print("FAILED:", f)
