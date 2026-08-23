import os, re, json
from collections import defaultdict

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
HTML = os.path.join(WT, "公众号", "_html")
MAPFILE = os.path.join(WT, "jin-jiancheng", "jinjiancheng_articles_map.json")
RENAMEMAP = os.path.join(WT, "jin-jiancheng", "all_html_rename_map.json")

with open(MAPFILE, encoding="utf-8") as f:
    master = json.load(f)
master_titles = [e.get("title","").strip() for e in master]

with open(RENAMEMAP, encoding="utf-8") as f:
    rm = json.load(f)
rm_titles = [os.path.splitext(re.sub(r"^_html_","",e.get("old","")))[0] for e in rm if e.get("status")=="OK"]

dated_re = re.compile(r"^\d{4}-\d{2}-\d{2}[_ ].*")
html_files = [f for f in os.listdir(HTML) if f.lower().endswith(".html") and os.path.isfile(os.path.join(HTML,f))]
undated = [f for f in html_files if not dated_re.match(os.path.splitext(f)[0])]
# only the 17 unmatched (those containing nn)
nn_files = [f for f in undated if "nn" in os.path.splitext(f)[0]]

print("=== 17 nn files: search map by prefix-before-nn ===")
for f in sorted(nn_files):
    base = os.path.splitext(f)[0]
    prefix = base.split("nn")[0]
    # find map titles that start with prefix, or prefix starts with map title
    cand = [t for t in master_titles if t.startswith(prefix) or prefix.startswith(t)]
    # also check rename map
    rcand = [t for t in rm_titles if t.startswith(prefix) or prefix.startswith(t)]
    print(f"\n* {base[:40]}...")
    print(f"   prefix='{prefix[:30]}'")
    if cand:
        for t in cand[:3]:
            print(f"   MAP  : {t}")
    if rcand:
        for t in rcand[:3]:
            print(f"   RENAMEMAP: {t}")
    if not cand and not rcand:
        print("   -> NO CANDIDATE in maps")
