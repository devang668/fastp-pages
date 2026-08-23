import json, os, re, sys

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
JIN = os.path.join(WT, "金渐成")
MAPFILE = os.path.join(WT, "jin-jiancheng", "jinjiancheng_articles_map.json")
RENAMEMAP = os.path.join(WT, "jin-jiancheng", "all_html_rename_map.json")

# Load master map: title -> date
with open(MAPFILE, encoding="utf-8") as f:
    master = json.load(f)
title_to_date = {}
dup_titles = []
for e in master:
    t = e.get("title", "").strip()
    d = e.get("date", "").strip()
    if not t or not d:
        continue
    if t in title_to_date and title_to_date[t] != d:
        dup_titles.append((t, title_to_date[t], d))
    title_to_date[t] = d

# Load rename map as fallback/verify: old->date (strip _html_ prefix, strip ext)
rename_date = {}
with open(RENAMEMAP, encoding="utf-8") as f:
    rm = json.load(f)
for e in rm:
    if e.get("status") != "OK":
        continue
    old = e.get("old", "")
    d = e.get("date", "")
    base = re.sub(r"^_html_", "", old)
    base = os.path.splitext(base)[0]
    rename_date[base] = d

# Gather files in 金渐成 (html/md, maxdepth 1)
files = []
for fn in os.listdir(JIN):
    fp = os.path.join(JIN, fn)
    if not os.path.isfile(fp):
        continue
    if not fn.lower().endswith((".html", ".md")):
        continue
    files.append(fn)

# split into titles (strip ext)
dated_re = re.compile(r"^\d{4}-\d{2}-\d{2}[_ ].*")
matched, unmatched, already = [], [], []
for fn in sorted(files):
    base = os.path.splitext(fn)[0]
    if dated_re.match(base):
        already.append(fn)
        continue
    # exact title match
    if base in title_to_date:
        matched.append((fn, title_to_date[base]))
    elif base in rename_date:
        matched.append((fn, rename_date[base]))
    else:
        unmatched.append(fn)

print("== COUNTS ==")
print("total html/md files:", len(files))
print("already dated (skip):", len(already))
print("matched (will rename):", len(matched))
print("unmatched (no date):", len(unmatched))
print("master map entries:", len(master), "unique titles:", len(title_to_date))
print("rename map entries usable:", len(rename_date))
if dup_titles:
    print("WARNING dup titles in master:", len(dup_titles), dup_titles[:5])

print("\n== UNMATCHED TITLES (first 40) ==")
for fn in unmatched[:40]:
    print("  ", fn)

print("\n== SAMPLE MATCHED (first 15) ==")
for fn, d in matched[:15]:
    print(f"  {d}  <-  {fn}")

# also: do any 金渐成 titles appear in master map but the BASE differs? try substring/contains quick check for unmatched
print("\n== UNMATCHED but close? (substring scan) ==")
for fn in unmatched[:30]:
    base = os.path.splitext(fn)[0]
    hits = [t for t in title_to_date if base in t or t in base]
    if hits:
        print(f"  {fn}  ~  {hits[:3]}")
