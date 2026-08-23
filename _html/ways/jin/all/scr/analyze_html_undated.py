import os, re, json
from collections import defaultdict

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
HTML = os.path.join(WT, "公众号", "_html")
MAPFILE = os.path.join(WT, "jin-jiancheng", "jinjiancheng_articles_map.json")
RENAMEMAP = os.path.join(WT, "jin-jiancheng", "all_html_rename_map.json")

with open(MAPFILE, encoding="utf-8") as f:
    master = json.load(f)
by_title = defaultdict(list)
for e in master:
    t = e.get("title","").strip()
    if not t: continue
    m = re.search(r"/articles/([^/]+)/(\d{4}-\d{2}-\d{2})", e.get("url",""))
    src = m.group(1) if m else "?"
    dt = m.group(2) if m else e.get("date","")
    by_title[t].append({"src":src,"date":dt})

rename_date = {}
with open(RENAMEMAP, encoding="utf-8") as f:
    rm = json.load(f)
for e in rm:
    if e.get("status")!="OK": continue
    base = re.sub(r"^_html_","",e.get("old",""))
    rename_date[os.path.splitext(base)[0]] = e.get("date","")

dated_re = re.compile(r"^\d{4}-\d{2}-\d{2}[_ ].*")

html_files = [f for f in os.listdir(HTML) if f.lower().endswith(".html") and os.path.isfile(os.path.join(HTML,f))]
undated = [f for f in html_files if not dated_re.match(os.path.splitext(f)[0])]
print("total html:", len(html_files), " dated:", len(html_files)-len(undated), " undated:", len(undated))

print("\n=== UNDATED FILES + date lookup ===")
matched=0; unmatched=[]
for f in sorted(undated):
    base = os.path.splitext(f)[0]
    date=None; src=None
    if base in rename_date and rename_date[base]:
        date=rename_date[base]; src="verified-rename-map"
    else:
        entries = by_title.get(base, [])
        jc=[x for x in entries if x["src"]=="jinjiancheng" and x["date"]]
        if jc:
            date=jc[0]["date"]; src="master-jinjiancheng"
        elif entries:
            date=entries[0]["date"]; src="master-"+entries[0]["src"]
    if date:
        matched+=1
        print(f"  {date} [{src}]  {f}")
    else:
        unmatched.append(f)
print(f"\nmatched: {matched}  unmatched: {len(unmatched)}")
for f in unmatched:
    print("   UNMATCHED:", f)
