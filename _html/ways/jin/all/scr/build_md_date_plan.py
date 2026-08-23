import os, re, json
from collections import defaultdict

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
MD = os.path.join(WT, "公众号", "_md")
MAPFILE = os.path.join(WT, "jin-jiancheng", "jinjiancheng_articles_map.json")
RENAMEMAP = os.path.join(WT, "jin-jiancheng", "all_html_rename_map.json")

with open(MAPFILE, encoding="utf-8") as f:
    master = json.load(f)
by_title = defaultdict(list)
for e in master:
    t = e.get("title", "").strip()
    if not t:
        continue
    m = re.search(r"/articles/([^/]+)/(\d{4}-\d{2}-\d{2})", e.get("url", ""))
    by_title[t].append({"src": m.group(1) if m else "?", "date": m.group(2) if m else e.get("date", "")})

rename_date = {}
with open(RENAMEMAP, encoding="utf-8") as f:
    rm = json.load(f)
for e in rm:
    if e.get("status") != "OK":
        continue
    base = e.get("old", "")
    base = re.sub(r"^_html_", "", base)
    base = re.sub(r"^_md_", "", base)
    base = re.sub(r"^金渐成_", "", base)
    rename_date[os.path.splitext(base)[0]] = e.get("date", "")

dated_re = re.compile(r"^\d{4}-\d{2}-\d{2}[_ ].*")
md_files = [f for f in os.listdir(MD) if f.lower().endswith(".md") and os.path.isfile(os.path.join(MD, f))]
undated = [f for f in md_files if not dated_re.match(os.path.splitext(f)[0])]


def resolve(title):
    if title in rename_date and rename_date[title]:
        return rename_date[title], "verified-rename-map"
    es = by_title.get(title, [])
    if not es:
        for k, v in by_title.items():
            if k.startswith(title) or title.startswith(k):
                es = v
                break
    if not es:
        return None, None
    jc = [x for x in es if x["src"] == "jinjiancheng" and x["date"]]
    if jc:
        return jc[0]["date"], "master-jinjiancheng"
    return es[0]["date"], "master-" + es[0]["src"]


plan = []
nomatched = []
for f in sorted(undated):
    base = os.path.splitext(f)[0]
    date, src = resolve(base)
    if not date:
        prefix = None
        mm = re.search(r"nn", base)
        if mm:
            prefix = base[:mm.start()]
        else:
            mi = base.find("n")
            if mi > 0:
                prefix = base[:mi]
        if prefix:
            date, src = resolve(prefix)
    if date:
        newname = date + "_" + f
        plan.append({"old": f, "new": newname, "date": date, "source": src})
    else:
        nomatched.append(f)

with open(os.path.join(WT, "_md_undated_plan.json"), "w", encoding="utf-8") as fp:
    json.dump(plan, fp, ensure_ascii=False, indent=2)

print("PLAN (date prefix added, title text preserved):", len(plan))
print("NO MATCH (leave undated):", len(nomatched))
for p in plan:
    print(f"  {p['date']} [{p['source']}]  {p['new'][:60]}")
print("\nUNMATCHED:")
for f in nomatched:
    print("   ", f)
