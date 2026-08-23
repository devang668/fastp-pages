import os, json, re

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
HTML = os.path.join(WT, "公众号", "_html")
PLAN = os.path.join(WT, "_html_undated_plan.json")

with open(PLAN, encoding="utf-8") as f:
    plan = json.load(f)

done=0; skipped=0; failed=[]
for p in plan:
    old=p["old"]; new=p["new"]
    src=os.path.join(HTML,old); dst=os.path.join(HTML,new)
    if not os.path.exists(src):
        failed.append(("missing-src",old)); continue
    if os.path.exists(dst):
        failed.append(("target-exists",new)); continue
    if old==new:
        skipped+=1; continue
    try:
        os.rename(src,dst); done+=1
    except Exception as e:
        failed.append((str(e),old))

print("renamed:",done," skipped:",skipped," failed:",len(failed))
for e,n in failed[:20]: print("   ",e,n)

# verify
html_files=[f for f in os.listdir(HTML) if f.lower().endswith(".html") and os.path.isfile(os.path.join(HTML,f))]
dated_re=re.compile(r"^\d{4}-\d{2}-\d{2}[_ ].*")
dated=sum(1 for f in html_files if dated_re.match(os.path.splitext(f)[0]))
undated=len(html_files)-dated
print(f"\nVERIFY _html: total={len(html_files)} dated={dated} undated={undated}")
print("remaining undated:")
for f in sorted(html_files):
    if not dated_re.match(os.path.splitext(f)[0]):
        print("   ", f)
