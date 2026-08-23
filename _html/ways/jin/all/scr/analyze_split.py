import os, re

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
JIN = os.path.join(WT, "公众号", "金渐成")
HTML = os.path.join(WT, "公众号", "_html")
MD = os.path.join(WT, "公众号", "_md")

# base title = strip leading DATE_ and extension
def base_title(fn):
    b = os.path.splitext(fn)[0]
    b = re.sub(r"^\d{4}-\d{2}-\d{2}[_ ]", "", b)
    return b

jin_html = [f for f in os.listdir(JIN) if f.lower().endswith(".html") and os.path.isfile(os.path.join(JIN,f))]
jin_md   = [f for f in os.listdir(JIN) if f.lower().endswith(".md") and os.path.isfile(os.path.join(JIN,f))]
jin_mhtml = [f for f in os.listdir(JIN) if f.lower().endswith(".mhtml") and os.path.isfile(os.path.join(JIN,f))]

html_target_base = {base_title(f):f for f in os.listdir(HTML) if f.lower().endswith((".html",)) and os.path.isfile(os.path.join(HTML,f))}
md_target_base = {base_title(f):f for f in os.listdir(MD) if f.lower().endswith((".md",)) and os.path.isfile(os.path.join(MD,f))}

print("金渐成: html=%d md=%d mhtml=%d" % (len(jin_html), len(jin_md), len(jin_mhtml)))
print("_html has %d files, _md has %d files" % (len(os.listdir(HTML)), len(os.listdir(MD))))

# overlap by base title
html_overlap = [f for f in jin_html if base_title(f) in html_target_base]
md_overlap   = [f for f in jin_md if base_title(f) in md_target_base]
print("\nOVERLAP (same base title already in target):")
print("  jin html that ALSO exist in _html (undated):", len(html_overlap))
print("  jin md   that ALSO exist in _md   (undated):", len(md_overlap))

# Are _html/_md files dated at all?
dated_in_html = sum(1 for f in os.listdir(HTML) if re.match(r"^\d{4}-\d{2}-\d{2}", f))
dated_in_md   = sum(1 for f in os.listdir(MD) if re.match(r"^\d{4}-\d{2}-\d{2}", f))
print("\nAlready-dated files in _html:", dated_in_html, " in _md:", dated_in_md)

# titles in _html/_md NOT covered by 金渐成 (would remain)
html_only_target = [f for f in os.listdir(HTML) if base_title(f) not in {base_title(x) for x in jin_html}]
md_only_target = [f for f in os.listdir(MD) if base_title(f) not in {base_title(x) for x in jin_md}]
print("\nFiles in _html NOT in 金渐成 (stay as-is):", len(html_only_target))
print("Files in _md   NOT in 金渐成 (stay as-is):", len(md_only_target))

print("\nSample html overlaps:")
for f in html_overlap[:8]:
    print("   jin:", f, "  -> _html has:", html_target_base[base_title(f)])
print("\nSample md overlaps:")
for f in md_overlap[:8]:
    print("   jin:", f, "  -> _md has:", md_target_base[base_title(f)])
