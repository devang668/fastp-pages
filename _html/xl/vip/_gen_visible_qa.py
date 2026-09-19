# -*- coding: utf-8 -*-
"""把口语/听力/写作的问答内容渲染成 yuedu/qa-04 同款「答案直接可见」样式:
   概要定位段 + 本讲问答速览表 + 逐题详解(不用点击)，输出到 vip/visible/{speaking,tli,writing}/。
   以 yuedu/qa-04.html / yuedu-index.html 为模板，样式与阅读题库完全一致；只新建文件。
"""
import io
import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
MDROOT = os.path.join(ROOT, "vip-qa")
OUTROOT = os.path.join(ROOT, "visible")

# True=直接覆盖上线目录 speaking/tli/writing 的 qa-NN.html（替换前自动备份到 _pre_visible_backup/）
LIVE = True

TPL_QA = io.open(os.path.join(ROOT, "yuedu", "qa-04.html"), encoding="utf-8").read()
TPL_INDEX = io.open(os.path.join(ROOT, "yuedu", "yuedu-index.html"), encoding="utf-8").read()

# 课程中文名 -> (英文子目录, 上线课程索引页, 讲数)
COURSES = [
    ("口语", "speaking", "speaking-index.html", 16),
    ("听力", "tli", "tli-index.html", 20),
    ("写作", "writing", "writing-qa-index.html", 17),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s):
    s = esc(s)
    s = re.sub(r"\[([^\]]*)\]\(([^)]*)\)",
               lambda m: '<a href="' + m.group(2) + '">' + m.group(1) + "</a>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s


def core(a):
    a0 = a.replace("**", "").strip()
    a0 = re.split(r"[。！？；\n]", a0)[0].strip()
    if len(a0) > 84:
        a0 = a0[:84] + "…"
    return a0


def split_qa(p):
    parts = p.split("**")
    pairs = []
    i = 1
    while i + 1 < len(parts):
        q = parts[i].strip()
        a = re.sub(r"^发言人[：:]?\s*", "", parts[i + 1]).strip()
        if q:
            pairs.append((q, a))
        i += 2
    return pairs


def parse_lesson(path, sub, note_prefix):
    """解析 vip-qa 的每讲 md -> dict(title, abstract, qalist, note)"""
    txt = io.open(path, encoding="utf-8").read()
    lines = txt.splitlines()
    title = lines[0][2:].strip() if lines and lines[0].startswith("# ") else ""
    paras = []
    cur = []
    for ln in lines[1:]:
        s = ln.strip()
        if not s:
            if cur:
                paras.append(" ".join(cur))
                cur = []
        else:
            cur.append(s)
    if cur:
        paras.append(" ".join(cur))
    abstract = ""
    qalist = []
    note = ""
    for p in paras:
        if p.startswith("## "):
            continue
        cm = re.match(r"^\*\*(\d{1,2}:\d{2})\s*(.*?)\*\*\s*(.*)$", p)
        if cm:
            qalist.append(((cm.group(1) + " " + cm.group(2)).strip(), cm.group(3).strip()))
            continue
        if p.startswith("**") and ("？" in p or "发言人" in p):
            qalist.extend(split_qa(p))
            continue
        m = re.search(r"\[([^\]]*)\]\(([^)]*)\)", p)
        if m and m.group(2).startswith("lesson-"):
            note = inline(re.sub(r"\]\(lesson-", "](" + note_prefix + "lesson-", p))
            continue
        if not abstract:
            abstract = p
    return {"title": title, "abstract": abstract, "qalist": qalist, "note": note}


def build_qa_page(course_cn, sub, idx_file, num, total, lessons, live):
    html = TPL_QA
    nn = "%02d" % num
    L = lessons[num - 1]
    ttl = "第%s讲 · %s · 问答精要" % (nn, L["title"])
    html = re.sub(r"<title>.*?</title>", lambda m: "<title>" + esc(ttl) + "</title>",
                  html, count=1, flags=re.S)
    html = re.sub(r'<div class="logo">[^<]*<span> · 第 \d+ 讲问答</span></div>',
                  '<div class="logo">' + esc(course_cn + " VIP") + '<span> · 第 ' + nn + " 讲问答</span></div>",
                  html, count=1)
    # topbar 课程目录链接：live=同目录索引，visible=回指上线目录
    if live:
        idx_href = idx_file
    else:
        idx_href = "../../" + sub + "/" + idx_file
    html = html.replace('<a href="yuedu-index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">阅读目录</a>',
                        '<a href="' + idx_href + '" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">' + course_cn + "目录</a>")
    # 左侧目录
    lis = []
    for j, la in enumerate(lessons, 1):
        cls = ' class="active"' if j == num else ""
        lis.append('      <li><a%s href="qa-%02d.html">第%02d讲 · %s</a></li>'
                   % (cls, j, j, esc(la["title"])))
    html = re.sub(r"<h3>阅读问答（22 讲）</h3>\s*<ul>.*?</ul>",
                  "<h3>" + course_cn + "问答（" + str(total) + " 讲）</h3>\n    <ul>\n" + "\n".join(lis) + "\n    </ul>",
                  html, count=1, flags=re.S)
    # 仅 visible 一级目录深时把链接加深一级；live 模式落在 vip/<sub>/，与模板深度一致，保持原样
    if not live:
        html = html.replace('<a class="back" href="../index.html">VIP 总目录</a>',
                            '<a class="back" href="../../index.html">VIP 总目录</a>')
        html = html.replace('<a class="back" href="../../../index.html">站点首页</a>',
                            '<a class="back" href="../../../../index.html">站点首页</a>')
        # topbar 与其余残留的「首页」链接(模板深度为 vip/yuedu,这里多一级)
        html = html.replace('href="../../../index.html"', 'href="../../../../index.html"')
    # 右侧本页问答 TOC
    tocs = []
    for i, (q, a) in enumerate(L["qalist"], 1):
        tocs.append('<li><a href="#q%d">Q%d. %s</a></li>' % (i, i, inline(q)))
    html = re.sub(r"<h4>本页问答</h4>\s*<ul>.*?</ul>",
                  "<h4>本页问答</h4>\n    <ul>\n" + "\n".join(tocs) + "\n    </ul>",
                  html, count=1, flags=re.S)
    # 主内容
    main = []
    main.append("  <main class=\"col-main\">")
    main.append("    <h1>第%s讲 · %s</h1>" % (nn, esc(L["title"])))
    if L["abstract"]:
        main.append("    <blockquote><p><b>本讲定位：</b>%s</p></blockquote>" % esc(L["abstract"]))
    if L["qalist"]:
        main.append("    <h2><a id=\"overview\"></a>本讲问答速览（关键信息）</h2>")
        main.append("    <table>")
        main.append("      <thead><tr><th style=\"width:54px;\">编号</th><th style=\"width:38%;\">问题</th><th>核心答案</th></tr></thead>")
        main.append("      <tbody>")
        for i, (q, a) in enumerate(L["qalist"], 1):
            main.append("      <tr><td><b>Q%d</b></td><td>%s</td><td>%s</td></tr>"
                        % (i, inline(q), esc(core(a))))
        main.append("      </tbody>")
        main.append("    </table>")
        main.append("")
        main.append("    <h2><a id=\"detail\"></a>逐题详解</h2>")
        for i, (q, a) in enumerate(L["qalist"], 1):
            main.append("    <h2><a id=\"q%d\"></a>Q%d. %s</h2>" % (i, i, inline(q)))
            main.append("    <p class=\"qakey\">%s</p>" % inline(a))
    elif L["note"]:
        main.append("    <p>%s</p>" % L["note"])
    main.append("  </main>")
    html = re.sub(r'<main class="col-main">.*?</main>',
                  lambda m: "\n".join(main), html, count=1, flags=re.S)
    return html


def build_index(course_cn, sub, total, lessons):
    html = TPL_INDEX
    html = re.sub(r"<title>.*?</title>",
                  lambda m: "<title>" + esc(course_cn + " VIP · 问答精要 " + str(total) + " 讲") + "</title>",
                  html, count=1, flags=re.S)
    html = re.sub(r'<div class="logo">[^<]*<span> · \d+ 讲问答</span></div>',
                  '<div class="logo">' + esc(course_cn + " VIP") + "<span> · %d 讲问答</span></div>" % total,
                  html, count=1)
    html = re.sub(r"<h1>[^<]*·\s*问答精要（\d+ 讲）</h1>",
                  "<h1>" + esc(course_cn + " VIP") + " · 问答精要（%d 讲）</h1>" % total,
                  html, count=1)
    lis = []
    cards = []
    for j, la in enumerate(lessons, 1):
        lis.append('      <li><a href="qa-%02d.html">第%02d讲 · %s</a></li>' % (j, j, esc(la["title"])))
        cards.append('      <a class="card" href="qa-%02d.html"><h3>第%02d讲</h3><p>%s</p><span class="tag">问答精要</span></a>'
                     % (j, j, esc(la["title"])))
    html = re.sub(r"<h3>阅读问答（22 讲）</h3>\s*<ul>.*?</ul>",
                  "<h3>" + course_cn + "问答（" + str(total) + " 讲）</h3>\n    <ul>\n" + "\n".join(lis) + "\n    </ul>",
                  html, count=1, flags=re.S)
    html = re.sub(r'<div class="cards">.*?</div>',
                  "<div class=\"cards\">\n" + "\n".join(cards) + "\n    </div>",
                  html, count=1, flags=re.S)
    html = html.replace('<a class="back" href="../index.html">VIP 总目录</a>',
                        '<a class="back" href="../../index.html">VIP 总目录</a>')
    html = html.replace('<a class="back" href="../../../index.html">站点首页</a>',
                        '<a class="back" href="../../../../index.html">站点首页</a>')
    html = html.replace('href="../../../index.html"', 'href="../../../../index.html"')
    html = re.sub(r"<h1>雅思阅读 VIP · 问答精要（22 讲）</h1>", "", html, count=1)
    return html


def main():
    for course_cn, sub, idx, total in COURSES:
        mdroot = os.path.join(MDROOT, course_cn)
        files = {}
        for fn in os.listdir(mdroot):
            m = re.match(r"第(\d+)讲-", fn)
            if m:
                files[int(m.group(1))] = os.path.join(mdroot, fn)
        lessons = []
        note_prefix = "" if LIVE else "../../" + sub + "/"
        for n in range(1, total + 1):
            if n not in files:
                print("缺 md:", course_cn, n)
                continue
            lessons.append(parse_lesson(files[n], sub, note_prefix))
        if LIVE:
            out = os.path.join(ROOT, sub)
            bdir = os.path.join(ROOT, "_pre_visible_backup", sub)
            os.makedirs(bdir, exist_ok=True)
            for n in range(1, total + 1):
                src = os.path.join(out, "qa-%02d.html" % n)
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(bdir, "qa-%02d.html" % n))
            print("已备份原 %s qa 页 -> _pre_visible_backup/%s" % (course_cn, sub))
        else:
            out = os.path.join(OUTROOT, sub)
            os.makedirs(out, exist_ok=True)
        for n, L in enumerate(lessons, 1):
            pg = build_qa_page(course_cn, sub, idx, n, total, lessons, LIVE)
            op = os.path.join(out, "qa-%02d.html" % n)
            io.open(op, "w", encoding="utf-8").write(pg)
            print("qa-%02d  %s  (%d 题)" % (n, L["title"][:28], len(L["qalist"])))
        if not LIVE:
            idx_html = build_index(course_cn, sub, total, lessons)
            io.open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(idx_html)
            print("index.html  %s" % course_cn)


if __name__ == "__main__":
    main()