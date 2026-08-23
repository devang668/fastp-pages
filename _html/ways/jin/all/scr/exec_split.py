import os, json, shutil

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
JIN = os.path.join(WT, "公众号", "金渐成")
HTML = os.path.join(WT, "公众号", "_html")
MD = os.path.join(WT, "公众号", "_md")
MHTML = os.path.join(WT, "公众号", "_mhtml")
BACKUP = os.path.join(WT, "公众号", "_backup_undated")
MANIFEST = os.path.join(WT, "公众号", "_split_manifest.json")

with open(MANIFEST, encoding="utf-8") as f:
    plan = json.load(f)["plan"]

dirmap = {"html":HTML, "md":MD, "mhtml":MHTML}
done=0; replaced=0; failed=[]
for p in plan:
    jin = p["jin"]; typ = p["type"]; tdir = dirmap[typ]
    src = os.path.join(JIN, jin)
    if not os.path.exists(src):
        failed.append(("missing-src", jin)); continue
    # move undated twin to backup first
    if p["replaced"]:
        twin_path = os.path.join(tdir, p["replaced"])
        if os.path.exists(twin_path):
            dest = os.path.join(BACKUP, p["replaced"])
            # avoid name clash in backup
            if os.path.exists(dest):
                dest = dest + ".dup"
            shutil.move(twin_path, dest)
            replaced += 1
    # move jin file to target
    dst = os.path.join(tdir, jin)
    if os.path.exists(dst):
        failed.append(("target-exists", jin)); continue
    shutil.move(src, dst)
    done += 1

# update manifest with results
with open(MANIFEST, "w", encoding="utf-8") as f:
    json.dump({"done":done,"replaced":replaced,"failed":failed,"plan":plan},
              f, ensure_ascii=False, indent=2)

print("moved:", done, " replaced-to-backup:", replaced, " failed:", len(failed))
for e in failed[:20]: print("   ", e)

# verification
import re
def cnt(d, ext):
    return sum(1 for f in os.listdir(d) if f.lower().endswith(ext) and os.path.isfile(os.path.join(d,f)))
print("\nVERIFY:")
print("  _html html:", cnt(HTML,".html"), " (was 52 + 181 moved - 24 replaced =", 52+181-24, ")")
print("  _md md:", cnt(MD,".md"), " (was 208 + 181 moved - 181 replaced =", 208+181-181, ")")
print("  _mhtml mhtml:", cnt(MHTML,".mhtml"), " (was 0 + 170 =", 170, ")")
print("  _backup_undated:", cnt(BACKUP,""), " files")
print("  金渐成 remaining files:", sum(1 for f in os.listdir(JIN) if os.path.isfile(os.path.join(JIN,f))))
