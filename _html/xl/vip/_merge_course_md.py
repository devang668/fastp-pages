# -*- coding: utf-8 -*-
"""把 vip-qa/<课程>/ 下的每讲 md 串成总文档，输出到 vip-qa/all/。
每讲用 "## 第NN讲 · 标题" 组织，文件内原有的 "## " 提升为 "### "。
只新建文件。
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "vip-qa")
OUT = os.path.join(SRC, "all")

COURSES = [
    ("口语", 16),
    ("听力", 20),
    ("写作", 17),
    ("阅读", 22),
]


def read_md(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def merge(cname):
    d = os.path.join(SRC, cname)
    files = [f for f in os.listdir(d) if re.match(r"第\d+讲-.+\.md$", f)]
    items = []
    for fn in files:
        num = int(re.search(r"第(\d+)讲", fn).group(1))
        txt = read_md(os.path.join(d, fn))
        lines = txt.splitlines()
        title = ""
        body = []
        for ln in lines:
            if title == "" and ln.startswith("# "):
                title = ln[2:].strip()
                continue
            if ln.startswith("## "):
                ln = "### " + ln[3:]
            body.append(ln)
        items.append((num, title, body))
    items.sort(key=lambda x: x[0])
    out = ["# %s VIP · 问答精要（%d 讲通读）" % (cname, len(items)), ""]
    out.append("> 汇总自 vip-qa/%s/ 下各讲 md（源自已上线的 qa-NN.html）。" % cname)
    for num, title, body in items:
        while body and body[0].strip() == "":
            body = body[1:]
        out += ["", "## 第%02d讲 · %s" % (num, title), ""]
        out += body
    # 压缩连续空行：正文里最多保留一个空行
    res = []
    blank = 0
    for ln in out:
        if ln.strip() == "":
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        res.append(ln.rstrip())
    return "\n".join(res).strip() + "\n"


def main():
    os.makedirs(OUT, exist_ok=True)
    for cname, n in COURSES:
        md = merge(cname)
        fn = os.path.join(OUT, "%s · %d 讲问答精要.md" % (cname, n))
        with open(fn, "w", encoding="utf-8") as f:
            f.write(md)
        head = md.splitlines()[1] if len(md.splitlines()) > 1 else ""
        print("写出 %s  (%d 字符, %d 讲)" % (os.path.basename(fn), len(md), md.count("\n## 第")))


if __name__ == "__main__":
    main()