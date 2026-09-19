# -*- coding: utf-8 -*-
"""把 vip-qa/all/ 下四门课的总文档合并成一个全集文件（只新建，不动原文件）。
层级：全集 # → 课程 ## → 讲次 ### → 小节 ####。
"""
import io
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
ALL = os.path.join(ROOT, "vip-qa", "all")

FILES = [
    ("口语", 16, "口语 · 16 讲问答精要.md"),
    ("听力", 20, "听力 · 20 讲问答精要.md"),
    ("写作", 17, "写作 · 17 讲问答精要.md"),
    ("阅读", 22, "阅读 · 22 讲问答精要.md"),
]
OUT = os.path.join(ALL, "雅思 VIP · 问答精要全集（75 讲）.md")


def main():
    out = ["# 雅思 VIP · 问答精要全集（75 讲）", ""]
    out.append("> 四门课合并：口语 16 + 听力 20 + 写作 17 + 阅读 22 = 75 讲；源自已上线的 qa 页面问答精要。")
    for cname, n, fn in FILES:
        lines = io.open(os.path.join(ALL, fn), encoding="utf-8").read().splitlines()
        out += ["", "## %s（%d 讲）" % (cname, n)]
        for ln in lines[1:]:          # 跳过原文件的一级总标题
            if ln.startswith("## "):
                ln = "### " + ln[3:]
            elif ln.startswith("### "):
                ln = "#### " + ln[4:]
            out.append(ln)
    text = "\n".join(out).strip() + "\n"
    io.open(OUT, "w", encoding="utf-8").write(text)
    print("写出 %s (%d 字符)" % (os.path.basename(OUT), len(text)))


if __name__ == "__main__":
    main()