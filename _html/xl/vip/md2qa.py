# -*- coding: utf-8 -*-
"""md2qa.py — 把一批 Markdown 文件按文件名顺序转成 VIP 风格「问答精要」页面。

用法:
    python md2qa.py <md文件或目录，可多个> [--out 输出目录] [--name 课程名] [--favicon-prefix 前缀]

行为:
  - 收集所有 .md，按文件名自然排序（2 排在 10 前面），依次编号 第01讲、第02讲…
  - 每个 md 生成一个 qa-NN.html（details 折叠问答卡），另生成一个 index.html 卡片目录
  - md 里 **问？**发言人：答 形式的问答链会被拆成折叠卡（兼容无「发言人：」前缀的写法）
  - 没有问答块的 md（普通文章）按通用 Markdown 渲染：标题/列表/表格/引用/代码块/图片/链接/加粗
  - 左侧栏单列表 + 当前讲高亮，页面加载时自动滚动到当前讲（避免点下方章节跳回顶部）
  - 顶部 Ctrl-K 搜索 + 关键词高亮；正则转义行用 chr(92) 拼接，杜绝转义被吃的问题

注意:
  - 图片/链接的相对路径按「输出目录」解析；要让图片显示，请让输出目录与图片同级（可用 --out 指到 md 同级）
"""
import os
import sys
import argparse

NL = chr(10)
BS = chr(92)

# ---------- 站点常量（按需修改） ----------
FAVICON_PREFIX = "../../"                 # favicon 相对前缀（默认按 xl/vip/<课程>/ 深度）
HOME_HREF = "../../../index.html"         # 顶栏「首页」
VIP_HREF = "../index.html"                # 顶栏「VIP 目录」

# ---------- 样式（继承 VIP 三栏页） ----------
CSS = """  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; min-height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; color: #1f2328; background: #fff; }
  a { color: #2c5cdc; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .topbar { position: fixed; top: 0; left: 0; right: 0; height: 56px; display: flex; align-items: center; padding: 0 24px; border-bottom: 1px solid #e5e7eb; background: #fff; z-index: 10; }
  .logo { font-weight: 800; font-size: 20px; letter-spacing: -0.5px; color: #111; }
  .logo span { color: #6b7280; font-weight: 500; }
  .topbar-right { margin-left: auto; display: flex; gap: 16px; align-items: center; position: relative; }
  .topbar-right input { border: 1px solid #d1d5db; border-radius: 6px; padding: 6px 10px; font-size: 13px; width: 240px; background: #f9fafb; }
  .topbar-right input:focus { outline: none; border-color: #2c5cdc; background: #fff; box-shadow: 0 0 0 3px rgba(44,92,220,0.12); }
  #search-panel { position: absolute; top: 44px; right: 0; width: 360px; max-height: 70vh; overflow-y: auto; background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); padding: 8px 0; z-index: 100; font-size: 13px; display: none; }
  #search-panel.show { display: block; }
  #search-panel .sp-group { padding: 8px 14px 4px; font-size: 11px; color: #6b7280; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
  #search-panel ul { list-style: none; padding: 0; margin: 0; }
  #search-panel li a { display: block; padding: 6px 14px; color: #374151; line-height: 1.4; font-size: 12.5px; }
  #search-panel li a:hover { background: #f3f4f6; color: #1d4ed8; text-decoration: none; }
  #search-panel .sp-empty { padding: 24px; text-align: center; color: #9ca3af; font-size: 12px; }
  mark.search-hl { background: #fff3a3; color: inherit; padding: 0 2px; border-radius: 2px; }
  .layout { display: flex; padding-top: 56px; min-height: 100vh; }
  .col-left { width: 240px; flex-shrink: 0; border-right: 1px solid #e5e7eb; padding: 20px 14px 40px; overflow-y: auto; height: calc(100vh - 56px); position: sticky; top: 56px; }
  .col-left ul { list-style: none; padding: 0; margin: 0 0 16px; }
  .col-left li { margin: 2px 0; }
  .col-left a { display: block; padding: 6px 10px; border-radius: 6px; font-size: 13.5px; color: #374151; line-height: 1.4; }
  .col-left a:hover { background: #f3f4f6; text-decoration: none; }
  .col-left a.active { background: #eff6ff; color: #1d4ed8; font-weight: 600; }
  .col-left h3 { font-size: 11px; text-transform: uppercase; color: #6b7280; margin: 18px 8px 8px; letter-spacing: 0.5px; font-weight: 600; }
  .col-left .back { font-size: 12.5px; color: #4b5563; }
  .col-main { flex: 1; min-width: 0; padding: 40px 56px 80px; max-width: 860px; margin: 0 auto; }
  .col-main h1 { font-size: 30px; margin-top: 0; border-bottom: 1px solid #e5e7eb; padding-bottom: 12px; line-height: 1.35; }
  .col-main h2 { font-size: 22px; margin-top: 36px; padding-top: 14px; border-top: 1px solid #f3f4f6; }
  .col-main h3 { font-size: 18px; margin-top: 28px; color: #1f2937; }
  .col-main p { line-height: 1.8; color: #374151; margin: 10px 0; }
  .col-main .abstract { background: #f5f7fa; border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px 18px; margin: 16px 0 24px; color: #4b5563; font-size: 14.5px; }
  .col-main .qa { margin: 18px 0; border: 1px solid #e5e7eb; border-radius: 10px; }
  .col-main .qa summary { cursor: pointer; padding: 14px 18px; font-weight: 600; color: #1f2937; font-size: 14.5px; list-style: none; }
  .col-main .qa summary::-webkit-details-marker { display: none; }
  .col-main .qa summary:before { content: "Q "; color: #1d4ed8; font-weight: 800; }
  .col-main .qa .qa-body { padding: 0 18px 16px; color: #374151; font-size: 14px; line-height: 1.75; }
  .col-main .qa .qa-body .a { margin-top: 8px; }
  .col-main .qa .qa-body .a b { color: #1d4ed8; }
  .col-main .tip { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 12px 16px; margin: 16px 0; color: #1e3a8a; font-size: 14px; line-height: 1.7; }
  .col-main blockquote { margin: 14px 0; padding: 10px 16px; border-left: 4px solid #bfdbfe; background: #f8fafc; color: #4b5563; border-radius: 0 8px 8px 0; }
  .col-main blockquote p { margin: 4px 0; }
  .col-main table { border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 14px; }
  .col-main th, .col-main td { border: 1px solid #e5e7eb; padding: 8px 12px; text-align: left; }
  .col-main th { background: #f5f7fa; }
  .col-main ul { padding-left: 24px; margin: 10px 0; }
  .col-main li { line-height: 1.8; color: #374151; }
  .col-main img { max-width: 100%; border-radius: 8px; }
  .col-main pre { background: #0b1220; color: #e5e7eb; padding: 14px 16px; border-radius: 10px; overflow-x: auto; font-size: 13px; line-height: 1.6; }
  .col-main code { font-family: Consolas, Menlo, monospace; font-size: 13px; background: #f3f4f6; padding: 1px 6px; border-radius: 5px; }
  .col-main pre code { background: transparent; padding: 0; color: inherit; }
  .col-right { width: 220px; flex-shrink: 0; border-left: 1px solid #e5e7eb; padding: 24px 18px; font-size: 13px; height: calc(100vh - 56px); position: sticky; top: 56px; overflow-y: auto; }
  .col-right h4 { font-size: 11px; text-transform: uppercase; color: #6b7280; margin: 0 0 12px; letter-spacing: 0.5px; font-weight: 600; }
  .col-right ul { list-style: none; padding: 0; margin: 0 0 18px; }
  .col-right li { margin: 6px 0; }
  .col-right a { color: #4b5563; line-height: 1.45; font-size: 12.5px; }
  .col-right a:hover { color: #1d4ed8; }
  .grid2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin: 16px 0 8px; }
  .grid2 .card { display: block; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px 14px; color: #1f2328; text-decoration: none; line-height: 1.5; }
  .grid2 .card:hover { border-color: #bfdbfe; background: #eff6ff; text-decoration: none; }
  .grid2 .card b { color: #1d4ed8; font-size: 13px; }
  .grid2 .card span { color: #6b7280; font-size: 12.5px; }
  @media (max-width: 1100px) { .col-right { display: none; } }
  @media (max-width: 800px) { .col-left { display: none; } .col-main { padding: 24px; } }
  @media (max-width: 700px) { .grid2 { grid-template-columns: 1fr; } }"""

# ---------- 脚本（搜索 + 高亮 + 滚动到当前讲） ----------
# escapeRegex 一行里的反斜杠用 chr(92) 拼出来，避免任何转义层把它吃掉
JS_ESC_LINE = ('  function escapeRegex(s){ return s.replace(/[.*+?^${}()|['
               + BS + ']' + BS + BS + ']/g, '
               + "'" + BS + BS + "$&'"
               + '); }')

JS_HEAD = """  var panel = document.getElementById('search-panel');
  var main = document.querySelector('.col-main');
  var leftLinks = Array.prototype.slice.call(document.querySelectorAll('.col-left ul li a'));
  var rightLinks = Array.prototype.slice.call(document.querySelectorAll('.col-right ul li a'));
  function escHtml(s){ return s.replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
"""

JS_TAIL = """  function clearHighlights(){ if (!main) return; var marks = main.querySelectorAll('mark.search-hl'); for (var i = 0; i < marks.length; i++){ var m = marks[i]; var t = document.createTextNode(m.textContent); m.parentNode.replaceChild(t, m); } main.normalize(); }
  function highlightInMain(kw){
    if (!main) return; clearHighlights(); if (!kw) return;
    var re = new RegExp(escapeRegex(kw), 'gi');
    var walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, {
      acceptNode: function(n){
        if (!n.nodeValue || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        var p = n.parentElement; if (!p) return NodeFilter.FILTER_REJECT;
        var tag = p.tagName;
        if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'CODE' || tag === 'PRE') return NodeFilter.FILTER_REJECT;
        if (p.closest && p.closest('mark.search-hl')) return NodeFilter.FILTER_REJECT;
        return n.nodeValue.toLowerCase().indexOf(kw.toLowerCase()) >= 0 ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    var nodes = [], n;
    while ((n = walker.nextNode())) nodes.push(n);
    for (var i = 0; i < nodes.length; i++){
      var node = nodes[i], src = node.nodeValue, html = '', last = 0, match;
      re.lastIndex = 0;
      while ((match = re.exec(src)) !== null){
        html += escHtml(src.slice(last, match.index));
        html += '<mark class="search-hl">' + escHtml(match[0]) + '</mark>';
        last = match.index + match[0].length;
        if (match[0].length === 0) re.lastIndex++;
      }
      html += escHtml(src.slice(last));
      var tmp = document.createElement('span'); tmp.innerHTML = html;
      var parent = node.parentNode;
      while (tmp.firstChild) parent.insertBefore(tmp.firstChild, node);
      parent.removeChild(node);
    }
  }
  function search(q){
    q = (q || '').trim();
    panel.innerHTML = '';
    if (!q){ panel.classList.remove('show'); leftLinks.forEach(function(a){ a.parentElement.style.display = ''; }); rightLinks.forEach(function(a){ a.parentElement.style.display = ''; }); clearHighlights(); return; }
    var qLower = q.toLowerCase();
    var leftHits = leftLinks.filter(function(a){ return a.textContent.toLowerCase().indexOf(qLower) >= 0; });
    leftLinks.forEach(function(a){ a.parentElement.style.display = leftHits.indexOf(a) >= 0 ? '' : 'none'; });
    var rightHits = rightLinks.filter(function(a){ return a.textContent.toLowerCase().indexOf(qLower) >= 0; });
    rightLinks.forEach(function(a){ a.parentElement.style.display = rightHits.indexOf(a) >= 0 ? '' : 'none'; });
    var parts = [];
    if (leftHits.length){ parts.push('<div class="sp-group">课程目录</div>'); parts.push('<ul>' + leftHits.map(function(a){ return '<li><a href="' + a.getAttribute('href') + '">' + escHtml(a.textContent) + '</a></li>'; }).join('') + '</ul>'); }
    if (rightHits.length){ parts.push('<div class="sp-group">本页章节</div>'); parts.push('<ul>' + rightHits.map(function(a){ return '<li><a href="' + a.getAttribute('href') + '">' + escHtml(a.textContent) + '</a></li>'; }).join('') + '</ul>'); }
    if (!parts.length) parts.push('<div class="sp-empty">无匹配结果</div>');
    panel.innerHTML = parts.join('');
    panel.classList.add('show');
    highlightInMain(q);
  }
  var timer = null;
  input.addEventListener('input', function(e){ clearTimeout(timer); timer = setTimeout(function(){ search(input.value); }, 80); });
  input.addEventListener('keydown', function(e){ if (e.key === 'Escape'){ search(''); input.blur(); panel.classList.remove('show'); } });
  document.addEventListener('click', function(e){ if (panel.contains(e.target) || e.target === input) return; panel.classList.remove('show'); });
  document.addEventListener('keydown', function(e){ if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')){ e.preventDefault(); input.focus(); input.select(); } });
  panel.addEventListener('click', function(e){ var a = e.target.closest ? e.target.closest('a') : null; if (a) panel.classList.remove('show'); });
  var col = document.querySelector('.col-left');
  if (col){ var act = col.querySelector('a.active'); if (act){ var cr = col.getBoundingClientRect(), ar = act.getBoundingClientRect(); if (ar.top < cr.top - 4 || ar.bottom > cr.bottom + 4){ col.scrollTop = Math.max(0, col.scrollTop + (ar.top - cr.top) - 40); } } }
"""

JS = JS_HEAD + JS_ESC_LINE + JS_TAIL


# ---------- 基础工具 ----------
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def natkey(s):
    key = []
    i = 0
    n = len(s)
    while i < n:
        if s[i].isdigit():
            j = i
            while j < n and s[j].isdigit():
                j += 1
            key.append((1, int(s[i:j]), ""))
            i = j
        else:
            j = i
            while j < n and not s[j].isdigit():
                j += 1
            key.append((0, 0, s[i:j].lower()))
            i = j
    return key


def trunc(s, n):
    return s if len(s) <= n else s[:n] + "…"


def clean_answer(a):
    a = a.strip()
    if a.startswith("发言人"):
        a = a[len("发言人"):]
        while a and a[0] in "：: 　":
            a = a[1:]
    return a.strip()


def split_qa(para):
    parts = para.split("**")
    pairs = []
    i = 1
    while i < len(parts):
        q = parts[i].strip()
        a = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if q:
            pairs.append((q, clean_answer(a)))
        i += 2
    return pairs


def is_qa_para(p):
    return p.startswith("**") and ("？" in p or "发言人" in p)


# ---------- Markdown 解析 ----------
def parse_md(text, fallback_title):
    lines = text.splitlines()
    title = None
    body = []
    for ln in lines:
        s = ln.strip()
        if title is None and s.startswith("# ") and len(s) > 2:
            title = s[2:].strip()
            continue
        body.append(ln)
    paragraphs = []
    cur = []
    for ln in body:
        s = ln.strip()
        if s == "":
            if cur:
                paragraphs.append(" ".join(cur))
                cur = []
        else:
            cur.append(s)
    if cur:
        paragraphs.append(" ".join(cur))
    qa = []
    abstract = ""
    first_plain = None
    for p in paragraphs:
        if is_qa_para(p):
            qa.extend(split_qa(p))
        elif first_plain is None:
            first_plain = p
    abstract = first_plain or ""
    return {
        "title": title or fallback_title,
        "abstract": abstract,
        "qa": qa,
        "body_lines": body,
    }


def inline(s):
    s = esc(s)
    codes = []
    segs = s.split("`")
    if len(segs) >= 3:
        buf = []
        for idx, seg in enumerate(segs):
            if idx % 2 == 1:
                buf.append(chr(0) + str(len(codes)) + chr(0))
                codes.append(seg)
            else:
                buf.append(seg)
        s = "".join(buf)
    out = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "!" and i + 1 < n and s[i + 1] == "[":
            j = s.find("](", i + 2)
            if j != -1:
                k = s.find(")", j + 2)
                if k != -1:
                    out.append('<img src="' + s[j + 2:k] + '" alt="' + s[i + 2:j] + '">')
                    i = k + 1
                    continue
        if s[i] == "[":
            j = s.find("](", i + 1)
            if j != -1:
                k = s.find(")", j + 2)
                if k != -1:
                    out.append('<a href="' + s[j + 2:k] + '">' + s[i + 1:j] + '</a>')
                    i = k + 1
                    continue
        out.append(esc(s[i]))
        i += 1
    s = "".join(out)
    parts = s.split("**")
    if len(parts) >= 3:
        buf = []
        for idx, seg in enumerate(parts):
            if idx % 2 == 1:
                buf.append("<strong>" + seg + "</strong>")
            else:
                buf.append(seg)
        s = "".join(buf)
    for idx, c in enumerate(codes):
        s = s.replace(chr(0) + str(idx) + chr(0), "<code>" + c + "</code>")
    return s


def render_table(rows):
    grid = []
    for r in rows:
        grid.append([c.strip() for c in r.strip().strip("|").split("|")])
    if not grid:
        return ""
    head = grid[0]
    body = []
    for cells in grid[1:]:
        sep = True
        for c in cells:
            for ch in c:
                if ch not in "-: ":
                    sep = False
        if sep:
            continue
        body.append(cells)
    buf = ['    <table>', '      <thead><tr>']
    for c in head:
        buf.append('<th>' + inline(c) + '</th>')
    buf.append('</tr></thead>')
    if body:
        buf.append('      <tbody>')
        for cells in body:
            buf.append('        <tr>')
            for c in cells:
                buf.append('<td>' + inline(c) + '</td>')
            buf.append('</tr>')
        buf.append('      </tbody>')
    buf.append('    </table>')
    return NL.join(buf)


def is_special(st):
    if st == "":
        return True
    if st.startswith("```") or st.startswith("#") or st.startswith(">") or st.startswith("|"):
        return True
    if st.startswith("- ") or st.startswith("* "):
        return True
    if is_qa_para(st):
        return True
    return False


def render_md(lines):
    out = []
    i = 0
    n = len(lines)
    while i < n:
        st = lines[i].strip()
        if st.startswith("```"):
            code = []
            j = i + 1
            while j < n and not lines[j].strip().startswith("```"):
                code.append(lines[j])
                j += 1
            out.append('    <pre><code>' + esc(NL.join(code)) + '</code></pre>')
            i = j + 1
            continue
        if st == "":
            i += 1
            continue
        if st.startswith("####"):
            out.append('    <h3>' + inline(st.lstrip("#").strip()) + '</h3>')
            i += 1
            continue
        if st.startswith("### "):
            out.append('    <h3>' + inline(st[4:].strip()) + '</h3>')
            i += 1
            continue
        if st.startswith("## "):
            out.append('    <h2>' + inline(st[3:].strip()) + '</h2>')
            i += 1
            continue
        if st.startswith("# "):
            out.append('    <h2>' + inline(st[2:].strip()) + '</h2>')
            i += 1
            continue
        if st.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                seg = lines[i].strip()[1:].strip()
                if seg:
                    buf.append(seg)
                i += 1
            out.append('    <blockquote><p>' + inline(" ".join(buf)) + '</p></blockquote>')
            continue
        if st.startswith("|") and st.endswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            out.append(render_table(rows))
            continue
        if st.startswith("- ") or st.startswith("* "):
            items = []
            while i < n:
                t = lines[i].strip()
                if t.startswith("- ") or t.startswith("* "):
                    items.append(inline(t[2:].strip()))
                    i += 1
                else:
                    break
            lis = "".join("<li>" + it + "</li>" for it in items)
            out.append('    <ul>' + lis + '</ul>')
            continue
        if is_qa_para(st):
            i += 1
            continue
        buf = [st]
        i += 1
        while i < n:
            t = lines[i].strip()
            if is_special(t):
                break
            buf.append(t)
            i += 1
        out.append('    <p>' + inline(" ".join(buf)) + '</p>')
    return NL.join(out)


# ---------- 页面组装 ----------
def topbar(logo, logo_sub, with_search, extra_link_html=""):
    parts = []
    parts.append('<header class="topbar">')
    parts.append('  <div class="logo">' + logo + '<span> ' + logo_sub + '</span></div>')
    parts.append('  <div class="topbar-right">')
    parts.append('    <a href="' + HOME_HREF + '" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">首页</a>')
    parts.append('    <a href="' + VIP_HREF + '" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">VIP 目录</a>')
    if extra_link_html:
        parts.append('    ' + extra_link_html)
    if with_search:
        parts.append('    <input id="search-input" placeholder="搜索 Ctrl K" autocomplete="off">')
        parts.append('    <div id="search-panel"></div>')
    parts.append('  </div>')
    parts.append('</header>')
    return NL.join(parts)


def qa_page(i, lect, lectures, cfg):
    nn = "%02d" % (i + 1)
    title = "第%s讲 · %s · 问答精要" % (nn, lect["title"])
    logo_sub = "· 第 %s 讲问答" % nn
    left = ['    <h3>问答精要</h3>', '    <ul>']
    for j, L in enumerate(lectures):
        cls = ' class="active"' if j == i else ""
        left.append('      <li><a%s href="qa-%02d.html">第%02d讲 · %s</a></li>'
                    % (cls, j + 1, j + 1, esc(L["title"])))
    left.append('    </ul>')
    left.append('    <h3>返回</h3>')
    left.append('    <ul>')
    left.append('      <li><a class="back" href="' + VIP_HREF + '">VIP 总目录</a></li>')
    left.append('      <li><a class="back" href="' + HOME_HREF + '">站点首页</a></li>')
    left.append('    </ul>')
    main = ['    <h1>第%s讲 · %s</h1>' % (nn, esc(lect["title"]))]
    if lect["qa"]:
        if lect["abstract"]:
            main.append('    <div class="abstract"><b>本讲概要：</b>' + esc(lect["abstract"]) + '</div>')
        main.append('    <h2>问答精要</h2>')
        for q, a in lect["qa"]:
            main.append('    <details class="qa">')
            main.append('      <summary>' + esc(q) + '</summary>')
            main.append('      <div class="qa-body"><p class="a"><b>答：</b>' + esc(a) + '</p></div>')
            main.append('    </details>')
    else:
        main.append(render_md(lect["body_lines"]))
    right = ['    <h4>本讲导航</h4>', '    <ul>']
    if i > 0:
        right.append('      <li><a href="qa-%02d.html">上一讲 %02d</a></li>' % (i, i))
    if i < len(lectures) - 1:
        right.append('      <li><a href="qa-%02d.html">下一讲 %02d</a></li>' % (i + 2, i + 2))
    right.append('      <li><a href="index.html">本课目录</a></li>')
    right.append('    </ul>')
    parts = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="zh">')
    parts.append("<head>")
    parts.append('<meta charset="UTF-8">')
    parts.append('  <link rel="icon" type="image/svg+xml" href="' + cfg["favicon_prefix"] + 'favicon.svg">')
    parts.append('  <link rel="alternate icon" type="image/x-icon" href="' + cfg["favicon_prefix"] + 'favicon.ico">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    parts.append("<title>" + esc(title) + "</title>")
    parts.append("<style>")
    parts.append(CSS)
    parts.append("</style>")
    parts.append("</head>")
    parts.append("<body>")
    parts.append(topbar(esc(cfg["name"]), esc(logo_sub), True))
    parts.append('<div class="layout">')
    parts.append('  <aside class="col-left">')
    parts.append(NL.join(left))
    parts.append("  </aside>")
    parts.append('  <main class="col-main">')
    parts.append(NL.join(main))
    parts.append("  </main>")
    parts.append('  <aside class="col-right">')
    parts.append(NL.join(right))
    parts.append("  </aside>")
    parts.append("</div>")
    parts.append("<script>")
    parts.append("(function(){")
    parts.append("  var input = document.getElementById('search-input');")
    parts.append("  if (!input) return;")
    parts.append(JS)
    parts.append("})();")
    parts.append("</script>")
    parts.append("</body>")
    parts.append("</html>")
    return NL.join(parts) + NL


def index_page(lectures, cfg):
    parts = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="zh">')
    parts.append("<head>")
    parts.append('<meta charset="UTF-8">')
    parts.append('  <link rel="icon" type="image/svg+xml" href="' + cfg["favicon_prefix"] + 'favicon.svg">')
    parts.append('  <link rel="alternate icon" type="image/x-icon" href="' + cfg["favicon_prefix"] + 'favicon.ico">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    parts.append("<title>" + esc(cfg["name"]) + " · 问答精要（%d 讲）</title>" % len(lectures))
    parts.append("<style>")
    parts.append(CSS)
    parts.append("</style>")
    parts.append("</head>")
    parts.append("<body>")
    parts.append(topbar(esc(cfg["name"]), "· 问答精要 %d 讲" % len(lectures), False,
                        '<a href="index.html" style="font-size:13px;color:#6b7280;font-weight:600;white-space:nowrap;padding:6px 10px;border:1px solid #e5e7eb;border-radius:6px;background:#f9fafb;">本课目录</a>'))
    parts.append('<div class="layout">')
    parts.append('  <main class="col-main">')
    parts.append('    <h1>' + esc(cfg["name"]) + ' · 问答精要（%d 讲）</h1>' % len(lectures))
    parts.append('    <p>按文件名顺序生成。点击卡片进入对应讲次的问答页。</p>')
    parts.append('    <div class="grid2">')
    for i, L in enumerate(lectures):
        desc = L["abstract"] or "本讲无概要"
        parts.append('      <a class="card" href="qa-%02d.html"><b>第%02d讲</b> %s<br><span>%s</span></a>'
                     % (i + 1, i + 1, esc(L["title"]), esc(trunc(desc, 60))))
    parts.append('    </div>')
    parts.append("  </main>")
    parts.append("</div>")
    parts.append("</body>")
    parts.append("</html>")
    return NL.join(parts) + NL


# ---------- 主流程 ----------
def collect_files(inputs):
    files = []
    for x in inputs:
        if os.path.isdir(x):
            for fn in os.listdir(x):
                if fn.lower().endswith(".md") and not fn.startswith("_"):
                    files.append(os.path.join(x, fn))
        elif os.path.isfile(x):
            files.append(x)
        else:
            print("跳过（不存在）:", x)
    seen = set()
    uniq = []
    for f in files:
        rp = os.path.abspath(f)
        if rp not in seen:
            seen.add(rp)
            uniq.append(rp)
    uniq.sort(key=lambda p: natkey(os.path.basename(p)))
    return uniq


def main():
    ap = argparse.ArgumentParser(description="把一批 md 按文件名顺序转成 VIP 风格问答页")
    ap.add_argument("inputs", nargs="+", help="md 文件或目录（可多个）")
    ap.add_argument("--out", default=None, help="输出目录（默认 <输入目录>/qa_html）")
    ap.add_argument("--name", default=None, help="课程名（默认取输入目录名）")
    ap.add_argument("--favicon-prefix", dest="favicon_prefix", default=FAVICON_PREFIX,
                    help="favicon 相对前缀（默认 " + FAVICON_PREFIX + "）")
    args = ap.parse_args()
    files = collect_files(args.inputs)
    if not files:
        print("没有找到 md 文件")
        return
    outdir = args.out or os.path.join(os.path.dirname(files[0]), "qa_html")
    os.makedirs(outdir, exist_ok=True)
    name = args.name or (os.path.basename(os.path.dirname(files[0])) or "课程")
    cfg = {"name": name, "favicon_prefix": args.favicon_prefix}
    lectures = []
    for f in files:
        stem = os.path.splitext(os.path.basename(f))[0].strip()
        try:
            text = open(f, encoding="utf-8-sig").read()
        except UnicodeDecodeError:
            text = open(f, encoding="gbk", errors="replace").read()
        lectures.append(parse_md(text, stem))
    for i, L in enumerate(lectures):
        html = qa_page(i, L, lectures, cfg)
        p = os.path.join(outdir, "qa-%02d.html" % (i + 1))
        open(p, "w", encoding="utf-8").write(html)
        print("written qa-%02d.html  第%02d讲 · %s  （%d 组问答）" % (i + 1, i + 1, L["title"], len(L["qa"])))
    ip = os.path.join(outdir, "index.html")
    open(ip, "w", encoding="utf-8").write(index_page(lectures, cfg))
    print("written index.html")
    print("输出目录:", outdir)


if __name__ == "__main__":
    main()
