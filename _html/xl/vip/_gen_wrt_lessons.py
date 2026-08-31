# -*- coding: utf-8 -*-
"""Generate writing VIP lesson pages (lesson-NN.html) + QA pages (qa-NN.html)
from 作文8p9.md (17 lectures: 0w-1..0w-8, 1w-8..1w-16; note 0w-1..0w-8 use
names starting with 0w-, then 1w-8..1w-16 continue the numbering). Style: xl
three-column + Ctrl-K search + favicon, no emoji. Same skeleton as the
listening generator (_gen_tli_lessons.py), with writing-specific links.
"""
import io
import os
import re

MD = r"C:/Users/Cheng/Downloads/作文8p9.md"
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "writing")

# ---------- read md and split sections ----------
with io.open(MD, encoding="utf-8") as f:
    lines = f.readlines()

heads = []  # (lineno, title)
for i, ln in enumerate(lines, 1):
    s = ln.strip()
    if s.startswith("##"):
        heads.append((i, s))

def section_text(key):
    """Return lines (including the ## header line) for a section key like 0w-1."""
    for idx, (s, n) in enumerate(heads):
        if n.lstrip("#").strip() == key:
            e = heads[idx + 1][0] - 1 if idx + 1 < len(heads) else len(lines)
            return lines[s - 1:e]
    return None

LESSON_META = {
    1: ("0w-1", "第01讲 · 动态图表（小作文）总览", "动态图表考察形式、写作结构、步骤及技巧；含两幅以上动态图的处理"),
    2: ("0w-2", "第02讲 · 动态图主体段构建与趋势词汇", "识别与描述数据趋势，上升/下降/波动等丰富词汇在小作文主体段的运用"),
    3: ("0w-3", "第03讲 · 静态图表", "静态图表的写作方法与数据描述技巧"),
    4: ("0w-4", "第04讲 · 复杂静态图表：澳大利亚男女运动参与率", "开头段改写、分段组织与静态图数据呈现"),
    5: ("0w-5", "第05讲 · 双动态图题目", "标题分析、两图比较与文章组织"),
    6: ("0w-6", "第06讲 · 双镜图（双图）题目", "双图题复杂度剖析与两幅图的分析写作方法"),
    7: ("0w-7", "第07讲 · 流程图与地图", "数据类图表中的流程图与地图处理方法（低频但资源少）"),
    8: ("0w-8", "第08讲 · 地图题：选址比较与历史变迁", "地图题两类题型与固定结构讲解"),
    9: ("1w-8", "第09讲 · 大作文先导：考试概述与评分标准", "Task One/Task Two 结构、评分标准解读与常见错误分析"),
    10: ("1w-9", "第10讲 · 大作文的\"正确审美\"与常见错误", "准确回应题目、内容完整性、逻辑连贯与\"正确审美\""),
    11: ("1w-10", "第11讲 · 论述题型（优缺点/利弊讨论）", "评估特定行动利弊，两正一反或两反一正的写作结构"),
    12: ("1w-11", "第12讲 · 同意与否题型", "明确个人观点与立场确立，避免常见审题误区"),
    13: ("1w-12", "第13讲 · 双边论述题型", "讨论至少两个对立观点并明确个人立场"),
    14: ("1w-13", "第14讲 · 双边论述进阶（对立观点深入）", "双边论述的深入：对立观点拆解与个人立场结合"),
    15: ("1w-14", "第15讲 · 辩论：广泛科目 vs 有限科目", "多学科学习 vs 有限科目的双边辩论写作"),
    16: ("1w-15", "第16讲 · 报告类题型（原因-解决方案）", "社会现象原因分析与解决方案写作"),
    17: ("1w-16", "第17讲 · 混合类题型", "报告+观点混合题：现象原因与个人观点结合"),
}

# ---------- html skeleton (copied from _gen_tli_lessons.py) ----------
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
  .col-right { width: 220px; flex-shrink: 0; border-left: 1px solid #e5e7eb; padding: 24px 18px; font-size: 13px; height: calc(100vh - 56px); position: sticky; top: 56px; overflow-y: auto; }
  .col-right h4 { font-size: 11px; text-transform: uppercase; color: #6b7280; margin: 0 0 12px; letter-spacing: 0.5px; font-weight: 600; }
  .col-right ul { list-style: none; padding: 0; margin: 0 0 18px; }
  .col-right li { margin: 6px 0; }
  .col-right a { color: #4b5563; line-height: 1.45; font-size: 12.5px; }
  .col-right a:hover { color: #1d4ed8; }
  @media (max-width: 1100px) { .col-right { display: none; } }
  @media (max-width: 800px) { .col-left { display: none; } .col-main { padding: 24px; } }"""

JS = r"""  var panel = document.getElementById('search-panel');
  var main = document.querySelector('.col-main');
  var leftLinks = Array.prototype.slice.call(document.querySelectorAll('.col-left ul li a'));
  var rightLinks = Array.prototype.slice.call(document.querySelectorAll('.col-right ul li a'));
  function escHtml(s){ return s.replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function escapeRegex(s){ return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  function clearHighlights(){ if (!main) return; var marks = main.querySelectorAll('mark.search-hl'); for (var i = 0; i < marks.length; i++){ var m = marks[i]; var t = document.createTextNode(m.textContent); m.parentNode.replaceChild(t, m); } main.normalize(); }
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
  if (col){ var act = col.querySelector('a.active'); if (act){ var cr = col.getBoundingClientRect(), ar = act.getBoundingClientRect(); if (ar.top < cr.top - 4 || ar.bottom > cr.bottom + 4){ col.scrollTop = Math.max(0, col.scrollTop + (ar.top - cr.top) - 40); } } }"""


def page(title, logo, logo_sub, left_html, main_html, right_html):
    parts = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="zh">')
    parts.append("<head>")
    parts.append('<meta charset="UTF-8">')
    parts.append('  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">')
    parts.append('  <link rel="alternate icon" type="image/x-icon" href="../../favicon.ico">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    parts.append("<title>" + title + "</title>")
    parts.append("<style>")
    parts.append(CSS)
    parts.append("</style>")
    parts.append("</head>")
    parts.append("<body>")
    parts.append('<header class="topbar">')
    parts.append('  <div class="logo">' + logo + "<span> " + logo_sub + "</span></div>")
    parts.append('  <div class="topbar-right">')
    parts.append('    <a href="../../../index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">首页</a>')
    parts.append('    <a href="../index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">VIP 目录</a>')
    parts.append('    <a href="writing-index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">写作目录</a>')
    parts.append('    <input id="search-input" placeholder="搜索 Ctrl K" autocomplete="off">')
    parts.append('    <div id="search-panel"></div>')
    parts.append("  </div>")
    parts.append("</header>")
    parts.append('<div class="layout">')
    parts.append('  <aside class="col-left">')
    parts.append(left_html)
    parts.append("  </aside>")
    parts.append('  <main class="col-main">')
    parts.append(main_html)
    parts.append("  </main>")
    parts.append('  <aside class="col-right">')
    parts.append(right_html)
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
    return "\n".join(parts) + "\n"


def left_html(active_num, kind="lesson"):
    """kind: "lesson" -> only the transcript list; "qa" -> only the QA list.
    The left column must never show both, so the two page types cannot
    cross-jump from the sidebar."""
    out = []
    if kind == "qa":
        out.append('    <h3>问答精要</h3>')
        out.append("    <ul>")
        for num in range(1, 18):
            key, title, _ = LESSON_META[num]
            cls = ' class="active"' if num == active_num else ""
            out.append('      <li><a%s href="qa-%02d.html">%s</a></li>' % (cls, num, title))
        out.append("    </ul>")
    else:
        out.append('    <h3>写作课程</h3>')
        out.append("    <ul>")
        for num in range(1, 18):
            key, title, _ = LESSON_META[num]
            cls = ' class="active"' if num == active_num else ""
            out.append('      <li><a%s href="lesson-%02d.html">%s</a></li>' % (cls, num, title))
        out.append("    </ul>")
    out.append('    <h3>返回</h3>')
    out.append("    <ul>")
    out.append('      <li><a class="back" href="../index.html">VIP 总目录</a></li>')
    out.append('      <li><a class="back" href="../../../index.html">站点首页</a></li>')
    out.append("    </ul>")
    return "\n".join(out)


def right_html(active_num):
    out = []
    out.append("    <h4>本讲导航</h4>")
    out.append("    <ul>")
    out.append('      <li><a href="lesson-%02d.html">精讲逐字稿</a></li>' % active_num)
    out.append('      <li><a href="qa-%02d.html">问答精要</a></li>' % active_num)
    out.append("    </ul>")
    out.append("    <h4>上下讲</h4>")
    out.append("    <ul>")
    if active_num > 1:
        out.append('      <li><a href="lesson-%02d.html">上一讲 %02d</a></li>' % (active_num - 1, active_num - 1))
    if active_num < 17:
        out.append('      <li><a href="lesson-%02d.html">下一讲 %02d</a></li>' % (active_num + 1, active_num + 1))
    out.append("    </ul>")
    return "\n".join(out)


def split_section(body):
    """body: lines including the ## header.
    Return (abstract_text, qa_pairs, transcript_paras).

    Writing md format: same as listening — one paragraph containing many
    **问题**发言人：回答... blocks joined together.
    """
    text = "\n".join(body[1:])  # skip ## header
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    abstract = ""
    for cand in paras:
        if cand.startswith("**"):
            continue
        abstract = cand
        break
    qa_pairs = []
    transcript = []
    for p in paras:
        # A QA chain paragraph starts with ** and contains either a speaker
        # marker (发言人) or a question mark. Writing md questions can be long,
        # so do NOT limit the check to the first 40 chars.
        if p.startswith("**") and ("发言人" in p or "？" in p or "?" in p):
            qa_pairs.extend(split_qa_text(p))
        else:
            transcript.append(p)
    return abstract, qa_pairs, transcript


def split_qa_text(text):
    """Split a one-paragraph QA chain into (question, answer) pairs.
    Pattern: **问...**发言人：答...**问...**发言人：答... (repeats).
    Every **...** block is a question; answer runs to the next ** or end.
    """
    pairs = []
    marks = list(re.finditer(r"\*\*([^*]+?)\*\*", text))
    for i, m in enumerate(marks):
        q = m.group(1).strip()
        a_start = m.end()
        a_end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        a = text[a_start:a_end].strip()
        pairs.append((q, a))
    return pairs


def clean_bold(s):
    """Strip markdown bold markers and leading Q/A labels for display."""
    s = s.replace("**", "")
    s = re.sub(r"^发言人[：:]?\s*", "", s)
    return s.strip()


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def render_transcript_page(num):
    key, title, desc = LESSON_META[num]
    body = section_text(key)
    if not body:
        print("MISS section", key)
        return
    abstract, qa_pairs, transcript = split_section(body)
    main = []
    main.append("    <h1>" + title + "</h1>")
    main.append('    <div class="abstract"><b>本讲概要：</b>' + esc(abstract) + "</div>")
    if qa_pairs:
        main.append('    <div class="tip">本讲含 ' + str(len(qa_pairs)) + " 组问答精要，可到<a href=\"qa-%02d.html\">问答精要页</a>速查。</div>" % num)
    if transcript:
        main.append("    <h2>精讲逐字稿</h2>")
        for p in transcript:
            if p.startswith("**") and ("问" in p[:40] or "答" in p[:20]):
                continue
            main.append("    <p>" + esc(p) + "</p>")
    else:
        main.append('    <p>本讲以问答精要为主，逐字稿段落较少，请查看<a href="qa-%02d.html">问答精要页</a>。</p>' % num)
    html = page(title + " · 写作VIP", "写作 VIP", "· 第 %02d 讲" % num, left_html(num, "lesson"), "\n".join(main), right_html(num))
    with io.open(os.path.join(OUTDIR, "lesson-%02d.html" % num), "w", encoding="utf-8") as f:
        f.write(html)
    print("written lesson-%02d (%d chars)" % (num, len(html)))


def render_qa_page(num):
    key, title, desc = LESSON_META[num]
    body = section_text(key)
    if not body:
        return
    abstract, qa_pairs, transcript = split_section(body)
    main = []
    main.append("    <h1>" + title + "</h1>")
    main.append('    <div class="abstract"><b>本讲概要：</b>' + esc(abstract) + "</div>")
    if qa_pairs:
        main.append("    <h2>问答精要</h2>")
        for q, a in qa_pairs:
            qq = esc(clean_bold(q))
            aa = esc(clean_bold(a))
            main.append("    <details class=\"qa\">")
            main.append("      <summary>" + qq + "</summary>")
            main.append('      <div class="qa-body"><p class="a"><b>答：</b>' + aa + "</p></div>")
            main.append("    </details>")
    else:
        main.append('    <p>本讲没有独立的问答块，核心内容见<a href="lesson-%02d.html">精讲逐字稿页</a>。</p>' % num)
    html = page(title + " · 问答精要", "写作 VIP", "· 第 %02d 讲问答" % num, left_html(num, "qa"), "\n".join(main), right_html(num))
    with io.open(os.path.join(OUTDIR, "qa-%02d.html" % num), "w", encoding="utf-8") as f:
        f.write(html)
    print("written qa-%02d (%d chars, %d Q pairs)" % (num, len(html), len(qa_pairs)))


for n in range(1, 18):
    render_transcript_page(n)
    render_qa_page(n)
print("ALL DONE")