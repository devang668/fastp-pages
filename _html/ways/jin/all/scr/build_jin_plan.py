import json, os, re
from collections import defaultdict

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
JIN = os.path.join(WT, "金渐成")
MAPFILE = os.path.join(WT, "jin-jiancheng", "jinjiancheng_articles_map.json")
RENAMEMAP = os.path.join(WT, "jin-jiancheng", "all_html_rename_map.json")
PLAN = os.path.join(WT, "金渐成_rename_map.json")

with open(MAPFILE, encoding="utf-8") as f:
    master = json.load(f)
# group master entries by title; record source section from url
by_title = defaultdict(list)
for e in master:
    t = e.get("title","").strip()
    if not t: continue
    m = re.search(r"/articles/([^/]+)/(\d{4}-\d{2}-\d{2})", e.get("url",""))
    src = m.group(1) if m else "?"
    dt = m.group(2) if m else e.get("date","")
    by_title[t].append({"src":src,"date":dt})

# rename map verified dates (stripped base)
rename_date = {}
with open(RENAMEMAP, encoding="utf-8") as f:
    rm = json.load(f)
for e in rm:
    if e.get("status")!="OK": continue
    base = re.sub(r"^_html_","",e.get("old",""))
    rename_date[os.path.splitext(base)[0]] = e.get("date","")

dated_re = re.compile(r"^\d{4}-\d{2}-\d{2}[_ ].*")
plan = []
src_count = defaultdict(int)
for fn in sorted(os.listdir(JIN)):
    fp = os.path.join(JIN, fn)
    if not os.path.isfile(fp): continue
    if not fn.lower().endswith((".html",".md")): continue
    base, ext = os.path.splitext(fn)
    if dated_re.match(base):
        continue  # skip already dated
    date = None; source = None
    # priority 1: verified rename-map date
    if base in rename_date and rename_date[base]:
        date = rename_date[base]; source = "verified-rename-map"
    else:
        entries = by_title.get(base, [])
        # priority 2: jinjiancheng source
        jc = [x for x in entries if x["src"]=="jinjiancheng" and x["date"]]
        if jc:
            date = jc[0]["date"]; source = "master-jinjiancheng"
        elif entries:
            date = entries[0]["date"]; source = "master-" + entries[0]["src"]
    if not date:
        source = "UNRESOLVED"
    new = (date + "_" + fn) if date else fn
    plan.append({"old":fn,"new":new,"date":date or "","source":source})
    src_count[source]+=1

with open(PLAN, "w", encoding="utf-8") as f:
    json.dump(plan, f, ensure_ascii=False, indent=2)

print("plan written:", PLAN, "entries:", len(plan))
print("source breakdown:")
for k,v in sorted(src_count.items(), key=lambda x:-x[1]):
    print(f"  {k}: {v}")
unres = [p for p in plan if p["source"]=="UNRESOLVED"]
print("UNRESOLVED:", len(unres))
for p in unres: print("   ", p["old"])
print("\n== 13 risky dup titles resolution (verified vs others) ==")
risky = ["新的开始","摸着石头过河","一定要扛下去","一切都是最好的安排","一切还是老样子",
"神话破灭","穿过冬天","经历本身就是答案","勒紧裤腰带","制服的诱惑","该来的终于来了",
"有些话只能点到为止","越无知越自信"]
for t in risky:
    matches = [p for p in plan if p["old"].startswith(t+".")]
    for p in matches:
        print(f"  {p['date']}  [{p['source']}]  {p['old']}")
