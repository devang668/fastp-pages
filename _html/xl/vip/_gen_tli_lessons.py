# -*- coding: utf-8 -*-
"""Generate listening VIP lesson pages (lesson-NN.html) + QA pages (qa-NN.html)
from 听力.md (20 lectures: tl-1 .. tl-20, tl-6. has a dot). Style: xl
three-column + Ctrl-K search + favicon, no emoji. Same skeleton as the
speaking generator (_gen_speaking_lessons.py).
"""
import io
import os
import re

MD = r"C:/Users/Cheng/Downloads/听力.md"
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tli")

# ---------- read md and split sections ----------
with io.open(MD, encoding="utf-8") as f:
    lines = f.readlines()

heads = []  # (lineno, title)
for i, ln in enumerate(lines, 1):
    s = ln.strip()
    if s.startswith("##"):
        heads.append((i, s))

def section_text(key):
    """Return lines (including the ## header line) for a section key like tl-6."""
    for idx, (s, n) in enumerate(heads):
        if n.lstrip("#").strip() == key:
            e = heads[idx + 1][0] - 1 if idx + 1 < len(heads) else len(lines)
            return lines[s - 1:e]
    return None

LESSON_META = {
    1: ("tl-1", "第01讲 · 导学篇：考试形式与评分标准", "雅思听力四部分结构与难度、机考与纸笔考、目标分数设定、替换概念、语感大于语法、学习资源与刷题网站"),
    2: ("tl-2", "第02讲 · 听力三大核心能力", "听基本信息、识别否定词、理解转折关系三大能力讲解与训练"),
    3: ("tl-3", "第03讲 · 精听方法与分层练习", "精听是提升听力能力的关键，针对不同水平学生的分层练习方法"),
    4: ("tl-4", "第04讲 · Part One 场景与方法论", "问询类/介绍类场景区分、表格填空与笔记填空、读题与范围定位"),
    5: ("tl-5", "第05讲 · Part One 对话精听：爱尔兰家庭假期", "天气、活动、住宿与费用细节，雨天冲浪改租皮划艇"),
    6: ("tl-6.", "第06讲 · Part One 问询类与推荐类场景", "求职对话精听：大型企业、员工福利与折扣、团队合作与细节关注"),
    7: ("tl-7", "第07讲 · Part Two 结构与地图题", "Part Two 客观题结构（地图/单选/多选/配对）、地图题分类与解题"),
    8: ("tl-8", "第08讲 · 单选与多选解题策略", "筛选与排除错误选项，通过具体例子讲解多选和单选题策略"),
    9: ("tl-9", "第09讲 · 配对题：细节配对与分类配对", "两种配对类型的区别：细节配对找对应细节，分类配对按类归位"),
    10: ("tl-10", "第10讲 · 听力练习：开发项目反馈对话", "住宿类型包容性、合理价格设置、乡村短途可达性的讨论与精听"),
    11: ("tl-11", "第11讲 · 三篇听力综合练习", "读题、听题、复盘三步法，覆盖多种题型的综合听力练习"),
    12: ("tl-12", "第12讲 · 理解题目与核心信息", "面对难题聚焦核心信息、避免过度耗时，正确解读题目信息"),
    13: ("tl-13", "第13讲 · Part Three 配对题与流程图题", "事实配对与态度配对、流程图题的结构与解题方法"),
    14: ("tl-14", "第14讲 · 对话精听：学生表现与行为分析", "冷静下来、竞争态度、任务难度对学生表现与学习的影响"),
    15: ("tl-15", "第15讲 · 复盘技巧与重听方法", "高水平学生重听与对标选项，需改进学生朗读课文增强理解后再复盘"),
    16: ("tl-16", "第16讲 · Part Four 填空题要点", "Part Four 场景复杂、原文原词与单复数一致、拼写与词性预判"),
    17: ("tl-17", "第17讲 · 科学场景：植物学与动物学", "多选与填空题在植物学/动物学场景的解题策略"),
    18: ("tl-18", "第18讲 · Part Four 场景区分与模拟题", "人文社科场景与科学场景的区别，剑桥雅思模拟题实战"),
    19: ("tl-19", "第19讲 · 研究项目对话精听", "数据分析、整理与转录占 70-80% 时间，团队分工与研究流程"),
    20: ("tl-20", "第20讲 · 时间管理与选题策略", "有效管理考试时间与题目策略，避免在单选部分过度纠结"),
}

# ---------- html skeleton ----------
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

JS = """  var panel = document.getElementById('search-panel');
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
  panel.addEventListener('click', function(e){ var a = e.target.closest ? e.target.closest('a') : null; if (a) panel.classList.remove('show'); });"""


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
    parts.append('    <a href="tli-index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">听力目录</a>')
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


def left_html(active_num):
    out = []
    out.append('    <h3>听力课程</h3>')
    out.append("    <ul>")
    for num in range(1, 21):
        key, title, _ = LESSON_META[num]
        cls = ' class="active"' if num == active_num else ""
        out.append('      <li><a%s href="lesson-%02d.html">%s</a></li>' % (cls, num, title))
    out.append("    </ul>")
    out.append('    <h3>问答精要</h3>')
    out.append("    <ul>")
    for num in range(1, 21):
        out.append('      <li><a href="qa-%02d.html">第%02d讲 · 问答精要</a></li>' % (num, num))
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
    if active_num < 20:
        out.append('      <li><a href="lesson-%02d.html">下一讲 %02d</a></li>' % (active_num + 1, active_num + 1))
    out.append("    </ul>")
    return "\n".join(out)


def split_section(body):
    """body: lines including the ## header.
    Return (abstract_text, qa_pairs, transcript_paras).

    Listening md format: one paragraph containing many **问题**发言人：回答...
    blocks joined together. Q pairs are extracted by splitting that paragraph
    on the ** question markers.
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
        if p.startswith("**") and ("问" in p[:40] or "？" in p[:40]):
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
    html = page(title + " · 听力VIP", "听力 VIP", "· 第 %02d 讲" % num, left_html(num), "\n".join(main), right_html(num))
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
    html = page(title + " · 问答精要", "听力 VIP", "· 第 %02d 讲问答" % num, left_html(num), "\n".join(main), right_html(num))
    with io.open(os.path.join(OUTDIR, "qa-%02d.html" % num), "w", encoding="utf-8") as f:
        f.write(html)
    print("written qa-%02d (%d chars, %d Q pairs)" % (num, len(html), len(qa_pairs)))


for n in range(1, 21):
    render_transcript_page(n)
    render_qa_page(n)
print("ALL DONE")