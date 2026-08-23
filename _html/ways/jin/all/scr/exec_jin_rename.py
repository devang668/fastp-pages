import json, os

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
JIN = os.path.join(WT, "金渐成")
PLAN = os.path.join(WT, "金渐成_rename_map.json")

with open(PLAN, encoding="utf-8") as f:
    plan = json.load(f)

done = 0; skipped = 0; failed = []
for p in plan:
    old = p["old"]; new = p["new"]
    src = os.path.join(JIN, old)
    dst = os.path.join(JIN, new)
    if not os.path.exists(src):
        failed.append(("missing-src", old)); continue
    if os.path.exists(dst):
        failed.append(("target-exists", new)); continue
    if old == new:
        skipped += 1; continue
    try:
        os.rename(src, dst)
        done += 1
    except Exception as e:
        failed.append((str(e), old))

print("renamed:", done)
print("skipped (no change):", skipped)
print("failed:", len(failed))
for e, n in failed[:20]:
    print("   ", e, n)

# verify
import glob
html_total = len([f for f in os.listdir(JIN) if f.lower().endswith('.html') and os.path.isfile(os.path.join(JIN,f))])
md_total = len([f for f in os.listdir(JIN) if f.lower().endswith('.md') and os.path.isfile(os.path.join(JIN,f))])
import re
dated_re = re.compile(r"^\d{4}-\d{2}-\d{2}[_ ].*")
html_dated = sum(1 for f in os.listdir(JIN) if f.lower().endswith('.html') and os.path.isfile(os.path.join(JIN,f)) and dated_re.match(f))
md_dated = sum(1 for f in os.listdir(JIN) if f.lower().endswith('.md') and os.path.isfile(os.path.join(JIN,f)) and dated_re.match(f))
print(f"\nVERIFY: html total={html_total} dated={html_dated} | md total={md_total} dated={md_dated}")
print("remaining undated html:", html_total-html_dated, " undated md:", md_total-md_dated)
