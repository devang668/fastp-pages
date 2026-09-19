# -*- coding: utf-8 -*-
"""把已上线的 qa-NN.html 反解成每讲 md，输出到 vip-qa/<课程>/ 下。
只新建文件，不改动/删除任何已有 html 或 md。生成格式与 md2qa.py 兼容，可再生成页面。
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTROOT = os.path.join(ROOT, "vip-qa")

# (中文目录名, html 子目录名) —— speaking=tli 之外的对应关系
COURSES = [
    ("口语", "speaking"),
    ("听力", "tli"),
    ("写作", "writing"),
    ("阅读", "yuedu"),
]

ILLEGAL = set(chr(92) + '/:*?"<>|')


def decode(t):
    return (t.replace("&quot;", '"').replace("&amp;", "&")
             .replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'"))


def md_inline(t):
    """把 HTML 行内标记还原成 md：<b>/<strong> -> **，<code> -> `，<a> -> [](),并剥掉其余标签。"""
    t = decode(t)
    t = t.replace("<strong>", "**").replace("</strong>", "**")
    t = t.replace("<b>", "**").replace("</b>", "**")
    t = t.replace("<code>", "`").replace("</code>", "`")
    t = re.sub(r'<a href="([^"]*)">(.*?)</a>',
               lambda m: "[" + m.group(2) + "](" + m.group(1) + ")", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    return t.strip()


def sanitize_name(s):
    out = []
    for ch in s:
        out.append("-" if ch in ILLEGAL else ch)
    s = "".join(out).strip(" .-")
    s = re.sub(r"\s+", " ", s)
    if len(s) > 60:
        s = s[:60].rstrip(" -")
    return s or "讲"


def get_main(text):
    m = re.search(r'<main class="col-main">(.*?)</main>', text, re.S)
    return m.group(1) if m else text


def get_title(main):
    m = re.search(r"<h1>(.*?)</h1>", main, re.S)
    h1 = md_inline(m.group(1)) if m else ""
    return re.sub(r"^第\s*\d+\s*讲\s*(?:[·•∙]\s*)?", "", h1).strip()


def get_abstract(main):
    m = re.search(r'<div class="abstract">(.*?)</div>', main, re.S)
    if not m:
        return ""
    s = re.sub(r"^<b>\s*[^<]*[：:]\s*</b>", "", m.group(1), count=1, flags=re.S)
    return md_inline(s)


def get_qas(main):
    """md2qa 折叠卡页：每个 <details class="qa"> 一组问答。"""
    qas = []
    for m in re.finditer(r'<details class="qa">\s*<summary>(.*?)</summary>(.*?)</details>',
                         main, re.S):
        q = md_inline(m.group(1))
        body = m.group(2)
        lab = re.search(r"<b>\s*答[：:]\s*</b>", body)
        if lab:
            body = body[lab.end():]
        a = md_inline(body)
        if q:
            qas.append((q, a))
    return qas


def get_chapters(main):
    """章节导航页：<li><b>时间</b> 标题</li> + <li><span>简介</span></li> 成对出现。"""
    m = re.search(r"<h2>\s*章节导航\s*</h2>\s*<ul>(.*?)</ul>", main, re.S)
    if not m:
        return []
    chapters = []
    cur = None
    for li in re.findall(r'<li(?: [^>]*)?>(.*?)</li>', m.group(1), re.S):
        c = li.strip()
        tm = re.match(r"<b>(.*?)</b>(.*)", c, re.S)
        if tm:
            if cur:
                chapters.append(cur)
            cur = [md_inline(tm.group(1)), md_inline(tm.group(2)), ""]
        else:
            sp = re.search(r"<span[^>]*>(.*?)</span>", c, re.S)
            desc = md_inline(sp.group(1)) if sp else md_inline(c)
            if cur:
                cur[2] = desc
    if cur:
        chapters.append(cur)
    return chapters


def table_to_md(tbl):
    rows = []
    for tr in re.finditer(r"<tr>(.*?)</tr>", tbl, re.S):
        cells = [md_inline(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr.group(1), re.S)]
        rows.append(cells)
    if not rows:
        return ""
    n = max(len(r) for r in rows)
    for r in rows:
        r += [""] * (n - len(r))
    lines = ["| " + " | ".join(rows[0]) + " |",
             "|" + "|".join(["---"] * n) + "|"]
    for r in rows[1:]:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def blocks_to_md(region):
    """把一段 html（h2/h3/表格/tip）转成 md，用于多余内容兜底和 yuedu 精析速表。"""
    parts = []
    pat = re.compile(
        r'<h2><a id="showcase"></a>(.*?)</h2>'
        r'|<h3>(.*?)</h3>'
        r'|<table[^>]*>(.*?)</table>'
        r'|<p class="tip"[^>]*>(.*?)</p>'
        r'|<p>(.*?)</p>', re.S)
    for m in pat.finditer(region):
        if m.group(1) is not None:
            parts.append("## " + md_inline(m.group(1)))
        elif m.group(2) is not None:
            parts.append("### " + md_inline(m.group(2)))
        elif m.group(3) is not None:
            parts.append(table_to_md(m.group(3)))
        elif m.group(4) is not None:
            parts.append(md_inline(m.group(4)))
        else:
            parts.append(md_inline(m.group(5)))
    return "\n\n".join(parts)


def leftovers(main):
    """去掉已知结构后的残留（用于检查是否有遗漏内容）。"""
    s = main
    s = re.sub(r"<h1>.*?</h1>", "", s, flags=re.S)
    s = re.sub(r'<div class="abstract">.*?</div>', "", s, flags=re.S)
    s = re.sub(r'<details class="qa">.*?</details>', "", s, flags=re.S)
    s = re.sub(r"<h2>[^<]*</h2>", "", s)
    s = re.sub(r"<ul>.*?</ul>", "", s, flags=re.S)
    s = re.sub(r"<p style=\"color:#6b7280[^>]*>.*?</p>", "", s, flags=re.S)
    return s.strip()


def qa_md(q, a):
    marker = ""
    if "？" not in q and "发言人" not in q:
        marker = "发言人："   # md2qa 只把含全角？或"发言人"的段识别为问答，英文问句靠此标记兜底
    return "**" + q + "**" + marker + " " + a


def parse_yuedu(main):
    intro = re.search(r"<blockquote>\s*<p>(.*?)</p>\s*</blockquote>", main, re.S)
    if intro:
        intro_txt = re.sub(r"^<b>\s*[^<]*[：:]\s*</b>", "", intro.group(1), count=1, flags=re.S)
        intro_txt = md_inline(intro_txt)
    else:
        intro_txt = ""
    seg = main.split("逐题详解", 1)
    detail_seg = seg[1] if len(seg) > 1 else ""
    qas = []
    for m in re.finditer(
            r'<h2><a id="q\d+"></a>(?:Q\d+\.\s*)?(.*?)</h2>\s*<p class="qakey">(.*?)</p>',
            detail_seg, re.S):
        qas.append((md_inline(m.group(1)), md_inline(m.group(2))))
    show = ""
    if len(seg) > 1:
        pre = seg[0]
        ov = re.search(r'<h2><a id="overview">', pre)
        if ov:
            end = pre.find("</table>", ov.end())
            if end != -1:
                show = blocks_to_md(pre[end + len("</table>"):])
    return intro_txt, qas, show


def build_md(main, title):
    abstract = get_abstract(main)
    is_yuedu = "逐题详解" in main
    lines = ["# " + title]
    if is_yuedu:
        intro_txt, qas, show = parse_yuedu(main)
        body = intro_txt or abstract
        if body:
            lines += ["", body]
        if qas:
            for q, a in qas:
                lines += ["", qa_md(q, a)]
        if show:
            lines += ["", show]
    else:
        qas = get_qas(main)
        chapters = get_chapters(main)
        if abstract:
            lines += ["", abstract]
        if chapters:
            lines += ["", "## 章节导航"]
            for ts, ctitle, desc in chapters:
                s = "**" + ts + " " + ctitle + "**"
                if desc:
                    s += " " + desc
                lines += ["", s]
        if qas:
            lines += ["", "## 问答精要"]
            for q, a in qas:
                lines += ["", qa_md(q, a)]
        extra = leftovers(main)
        if extra:
            emd = blocks_to_md(extra)
            if emd:
                lines += ["", emd]
    return "\n".join(lines).strip() + "\n"


def expected_qas(main, kind):
    if kind == "yuedu":
        return len(re.findall(r'<h2><a id="q\d+"></a>', main))
    if kind == "details":
        return len(re.findall(r'<details class="qa">', main))
    return 0


def main():
    os.makedirs(OUTROOT, exist_ok=True)
    total = 0
    for cname, sub in COURSES:
        d = os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            print("跳过不存在目录:", d)
            continue
        files = sorted(f for f in os.listdir(d) if re.match(r"qa-\d+\.html$", f))
        outdir = os.path.join(OUTROOT, cname)
        os.makedirs(outdir, exist_ok=True)
        for fn in files:
            num = int(re.search(r"\d+", fn).group())
            path = os.path.join(d, fn)
            text = open(path, encoding="utf-8").read()
            main_html = get_main(text)
            title = get_title(main_html)
            kind = "yuedu" if "逐题详解" in main_html else (
                "details" if '<details class="qa"' in main_html else "plain")
            md_text = build_md(main_html, title)
            safe = sanitize_name(title)
            fname = "第%02d讲-%s.md" % (num, safe) if safe else "第%02d讲.md" % num
            outf = os.path.join(outdir, fname)
            open(outf, "w", encoding="utf-8").write(md_text)
            exp = expected_qas(main_html, kind)
            nq = len(re.findall(r"^(\*\*.*?\*\*)(.*)$", md_text, re.M))
            nq_pairs = len(get_qas(main_html)) if kind == "details" else (
                len(re.findall(r'<h2><a id="q\d+"></a>', main_html)) if kind == "yuedu" else len(get_chapters(main_html)))
            print("%s/%-28s 问答=%2d(html:%2d)%s" % (
                cname, fname, nq_pairs, exp,
                "  残留标签!" if left_tags(md_text) else ""))
            total += 1
    print("共生成 %d 个 md -> %s" % (total, OUTROOT))


def left_tags(md_text):
    return re.search(r"<(b|strong|a|code|p|h[1-6]|table|td|th|tr|div|span|img|li|ul|details|summary|blockquote)", md_text)


if __name__ == "__main__":
    main()