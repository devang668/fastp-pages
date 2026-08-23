import os, re, json, shutil

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
JIN = os.path.join(WT, "公众号", "金渐成")
HTML = os.path.join(WT, "公众号", "_html")
MD = os.path.join(WT, "公众号", "_md")
MHTML = os.path.join(WT, "公众号", "_mhtml")
BACKUP = os.path.join(WT, "公众号", "_backup_undated")
MANIFEST = os.path.join(WT, "公众号", "_split_manifest.json")

for d in (HTML, MD, MHTML, BACKUP):
    os.makedirs(d, exist_ok=True)

def base_title(fn):
    b = os.path.splitext(fn)[0]
    b = re.sub(r"^\d{4}-\d{2}-\d{2}[_ ]", "", b)
    return b

def target_index(folder):
    # base title -> filename (undated twin if present)
    idx = {}
    for f in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, f)):
            idx[base_title(f)] = f
    return idx

html_idx = target_index(HTML)
md_idx = target_index(MD)
mhtml_idx = target_index(MHTML)

plan = []
# html
for f in sorted(os.listdir(JIN)):
    if not f.lower().endswith(".html"): continue
    if not os.path.isfile(os.path.join(JIN, f)): continue
    bt = base_title(f)
    twin = html_idx.get(bt)
    plan.append({"type":"html","jin":f,"target_dir":"_html",
                 "replaced": twin if (twin and twin!=f) else None})
# md
for f in sorted(os.listdir(JIN)):
    if not f.lower().endswith(".md"): continue
    if not os.path.isfile(os.path.join(JIN, f)): continue
    bt = base_title(f)
    twin = md_idx.get(bt)
    plan.append({"type":"md","jin":f,"target_dir":"_md",
                 "replaced": twin if (twin and twin!=f) else None})
# mhtml
for f in sorted(os.listdir(JIN)):
    if not f.lower().endswith(".mhtml"): continue
    if not os.path.isfile(os.path.join(JIN, f)): continue
    bt = base_title(f)
    twin = mhtml_idx.get(bt)
    plan.append({"type":"mhtml","jin":f,"target_dir":"_mhtml",
                 "replaced": twin if (twin and twin!=f) else None})

# write checkpoint BEFORE moving
with open(MANIFEST, "w", encoding="utf-8") as fp:
    json.dump({"plan":plan}, fp, ensure_ascii=False, indent=2)

print("checkpoint written:", MANIFEST, "total moves:", len(plan))
print("  html:", sum(1 for p in plan if p['type']=='html'),
      " md:", sum(1 for p in plan if p['type']=='md'),
      " mhtml:", sum(1 for p in plan if p['type']=='mhtml'))
print("  will replace (move to backup):",
      sum(1 for p in plan if p['replaced']))
