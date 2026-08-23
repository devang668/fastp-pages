import json, os, re

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
JIN = os.path.join(WT, "金渐成")
MAPFILE = os.path.join(WT, "jin-jiancheng", "jinjiancheng_articles_map.json")
RENAMEMAP = os.path.join(WT, "jin-jiancheng", "all_html_rename_map.json")

with open(MAPFILE, encoding="utf-8") as f:
    master = json.load(f)
# group by title
from collections import defaultdict
by_title = defaultdict(list)
for e in master:
    t = e.get("title","").strip()
    if t:
        by_title[t].append(e)

dups = {t:es for t,es in by_title.items() if len(es) > 1}
print("total duplicate titles:", len(dups))

# which dup titles appear in 金渐成?
jin_titles = set()
for fn in os.listdir(JIN):
    if fn.lower().endswith((".html",".md")):
        jin_titles.add(os.path.splitext(fn)[0])

# load rename map date by stripped base
rename_date = {}
with open(RENAMEMAP, encoding="utf-8") as f:
    rm = json.load(f)
for e in rm:
    if e.get("status")!="OK": continue
    base = re.sub(r"^_html_","",e.get("old",""))
    rename_date[os.path.splitext(base)[0]] = e.get("date","")

print("\n=== DUP TITLES THAT EXIST IN 金渐成 (these are risky) ===")
risky = 0
for t,es in dups.items():
    if t in jin_titles:
        risky += 1
        print(f"\n* TITLE: {t}")
        for e in es:
            print(f"    date={e['date']}  url={e['url']}")
        rv = rename_date.get(t)
        print(f"    rename-map verified date: {rv if rv else '(none)'}")
print(f"\nrisky dup titles present in 金渐成: count above")

# Also list dup titles NOT in 金渐成 (not relevant to this rename)
not_in = [t for t in dups if t not in jin_titles]
print(f"\ndup titles NOT in 金渐成 (irrelevant here): {len(not_in)}")
