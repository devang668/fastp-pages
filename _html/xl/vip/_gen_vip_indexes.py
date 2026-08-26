# -*- coding: utf-8 -*-
"""Regenerate the 4 corrupted VIP subject index pages (speaking/tli/writing/yuedu).
Style base: xl/tingli/tl-index.html (3-column + Ctrl-K search + favicon, no emoji).
"""
import io
import re
import os

ROOT = os.path.dirname(os.path.abspath(__file__))  # .../xl/vip

# ---------- shared CSS (same as tl-index / knowledge) ----------
CSS = """  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; color: #1f2328; background: #fff; }
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
  .col-main h1 { font-size: 32px; margin-top: 0; border-bottom: 1px solid #e5e7eb; padding-bottom: 12px; line-height: 1.3; }
  .col-main p { line-height: 1.75; color: #374151; }
  .cta { margin-top: 24px; padding: 18px 20px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; }
  .cta strong { color: #1d4ed8; font-size: 15px; }
  .cta p { color: #374151; margin: 8px 0 12px; font-size: 14px; }
  .cta a { display: inline-block; background: #1d4ed8; color: #fff; padding: 9px 18px; border-radius: 8px; font-weight: 600; text-decoration: none; }
  .cta a.ghost { margin-left: 10px; border: 1px solid #1d4ed8; color: #1d4ed8; background: #fff; }
  .col-right { width: 220px; flex-shrink: 0; border-left: 1px solid #e5e7eb; padding: 24px 18px; font-size: 13px; height: calc(100vh - 56px); position: sticky; top: 56px; overflow-y: auto; }
  .col-right h4 { font-size: 11px; text-transform: uppercase; color: #6b7280; margin: 0 0 12px; letter-spacing: 0.5px; font-weight: 600; }
  .col-right ul { list-style: none; padding: 0; margin: 0; }
  .col-right li { margin: 6px 0; }
  .col-right a { color: #4b5563; line-height: 1.45; font-size: 12.5px; }
  .col-right a:hover { color: #1d4ed8; }
  .col-right .empty { color: #9ca3af; font-size: 12px; }
  @media (max-width: 1100px) { .col-right { display: none; } }
  @media (max-width: 800px) { .col-left { display: none; } .col-main { padding: 24px; } }"""

JS = """  var panel = document.getElementById('search-panel');
  if (!input || !panel) return;
  var main = document.querySelector('.col-main');
  var leftLinks = Array.prototype.slice.call(document.querySelectorAll('.col-left ul li a'));
  var rightLinks = Array.prototype.slice.call(document.querySelectorAll('.col-right ul li a'));
  function escHtml(s){ return s.replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function escapeRegex(s){ return s.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'); }
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
})();"""


def page(title, logo_text, logo_sub, desc, left_html, main_html, right_items, out_rel, favicon_rel="../../favicon.svg"):
    rel = os.path.join(ROOT, out_rel)
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append('<html lang="zh">')
    lines.append("<head>")
    lines.append('<meta charset="UTF-8">')
    lines.append('  <link rel="icon" type="image/svg+xml" href="' + favicon_rel + '">')
    lines.append('  <link rel="alternate icon" type="image/x-icon" href="../../favicon.ico">')
    lines.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    lines.append("<title>" + title + "</title>")
    lines.append("<style>")
    lines.append(CSS)
    lines.append("</style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append('<header class="topbar">')
    lines.append('  <div class="logo">' + logo_text + '<span> ' + logo_sub + '</span></div>')
    lines.append('  <div class="topbar-right">')
    lines.append('    <a href="../../index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">首页</a>')
    lines.append('    <a href="../index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">VIP 目录</a>')
    lines.append('    <input id="search-input" placeholder="搜索 Ctrl K" autocomplete="off">')
    lines.append('    <div id="search-panel"></div>')
    lines.append('  </div>')
    lines.append("</header>")
    lines.append('<div class="layout">')
    lines.append('  <aside class="col-left">')
    lines.append(left_html)
    lines.append("  </aside>")
    lines.append('  <main class="col-main">')
    lines.append(main_html)
    lines.append("  </main>")
    lines.append('  <aside class="col-right">')
    lines.append("    <h4>本页内容</h4>")
    lines.append("    <ul>")
    for it in right_items:
        lines.append('      <li><a href="' + it[0] + '">' + it[1] + "</a></li>")
    lines.append("    </ul>")
    lines.append("  </aside>")
    lines.append("</div>")
    lines.append("<script>")
    lines.append("(function(){")
    lines.append("  var input = document.getElementById('search-input');")
    lines.append(JS)
    lines.append("</script>")
    lines.append("</body>")
    lines.append("</html>")
    html = "\n".join(lines) + "\n"
    with io.open(rel, "w", encoding="utf-8") as f:
        f.write(html)
    print("written", rel, len(html))


LECTURES = [
    ("speaking/lesson-01.html", "第01讲 · 导学课：口语考试流程与评分标准"),
    ("speaking/lesson-02.html", "第02讲 · 口语三大基本能力与基础"),
    ("speaking/lesson-03.html", "第03讲 · 句子结构与时态语态"),
    ("speaking/lesson-04.html", "第04讲 · Part One 综合练习与拓展"),
    ("speaking/lesson-05.html", "第05讲 · 发音练习与九大原因素材"),
    ("speaking/lesson-06.html", "第06讲 · Part Two 素材与串题方法"),
    ("speaking/lesson-07.html", "第07讲 · 喜欢的东西：串题素材"),
    ("speaking/lesson-08.html", "第08讲 · 成功人物素材"),
    ("speaking/lesson-09.html", "第09讲 · 活动描述与家庭聚会素材"),
    ("speaking/lesson-10.html", "第10讲 · 地点类素材与旅游话题"),
    ("speaking/lesson-11.html", "第11讲 · 物品类素材：礼物/家居/衣物"),
    ("speaking/lesson-12.html", "第12讲 · 节日与有意义的一天"),
    ("speaking/lesson-13.html", "第13讲 · 目标 6.5 以下备考策略"),
    ("speaking/lesson-14.html", "第14讲 · Part Three 答题思路链"),
    ("speaking/lesson-15.html", "第15讲 · Part Three 解决类话题"),
    ("speaking/lesson-16.html", "第16讲 · 实践与题库串讲总结"),
]


def speaking_left():
    parts = []
    parts.append('    <h3>口语课程</h3>')
    parts.append("    <ul>")
    for href, t in LECTURES:
        parts.append('      <li><a href="' + href + '">' + t + "</a></li>")
    parts.append("    </ul>")
    parts.append('    <h3>问答精要</h3>')
    parts.append("    <ul>")
    for i in range(1, 17):
        parts.append('      <li><a href="qa-%02d.html">第%02d讲 · 问答精要</a></li>' % (i, i))
    parts.append("    </ul>")
    parts.append('    <h3>返回</h3>')
    parts.append("    <ul>")
    parts.append('      <li><a class="back" href="../index.html">VIP 总目录</a></li>')
    parts.append("    </ul>")
    return "\n".join(parts)


def generic_left(subject_cn, subject_en, items):
    parts = []
    parts.append('    <h3>' + subject_cn + "课程</h3>")
    parts.append("    <ul>")
    for href, t in items:
        parts.append('      <li><a href="' + href + '">' + t + "</a></li>")
    parts.append("    </ul>")
    parts.append('    <h3>返回</h3>')
    parts.append("    <ul>")
    parts.append('      <li><a class="back" href="../index.html">VIP 总目录</a></li>')
    parts.append("    </ul>")
    return "\n".join(parts)


def main_block(h1, intro, cta_title, cta_desc, cta_href, cta_label, ghost=False):
    parts = []
    parts.append("    <h1>" + h1 + "</h1>")
    parts.append("    " + intro)
    parts.append('    <div class="cta">')
    parts.append("      <strong>" + cta_title + "</strong>")
    parts.append("      <p>" + cta_desc + "</p>")
    parts.append('      <a href="' + cta_href + '">' + cta_label + "</a>")
    if ghost:
        parts.append('      <a class="ghost" href="' + ghost[0] + '">' + ghost[1] + "</a>")
    parts.append("    </div>")
    return "\n".join(parts)


# ---------- speaking ----------
sp_left = speaking_left()
sp_main = main_block(
    "雅思口语 VIP 精讲",
    "<p>付费口语冲刺课程逐字稿。点击左侧课程开始学习；每讲配套「问答精要」页，把整讲考点压缩成速查问答。</p>",
    "口语课程 16 讲已就绪",
    "导学课讲考试流程与评分标准，中间各讲拆解 Part One / Part Two / Part Three 素材与串题方法，第 16 讲做实践与题库串讲总结。",
    "lesson-01.html",
    "从第 1 讲开始",
    ghost=("qa-01.html", "先看问答精要"),
)
right_items = [("lesson-01.html", "第 01 讲"), ("lesson-16.html", "第 16 讲"), ("qa-01.html", "问答精要")]
page("口语 VIP 精讲 · 雅思口语16讲", "口语 VIP", "· 16讲", "", sp_left, sp_main, right_items, "speaking/speaking-index.html")

# ---------- tli (listening) ----------
tli_items = [
    ("../../tingli/tl-index.html", "听力课程目录（8 讲）"),
    ("../../tingli/knowledge.html", "听力全面知识清单"),
    ("../../tingli/practice/index.html", "听力考点自测"),
]
tli_left = generic_left("听力", "Listening", tli_items)
tli_main = main_block(
    "雅思听力 VIP 精讲",
    "<p>付费听力课程逐字稿。左侧目录随每一讲文稿的生成自动更新。</p>",
    "听力板块待更新",
    "把这一讲的文稿发给我（直接粘贴文字或丢 .md 文件），即可生成精讲页与问答精要页并加入左侧目录。",
    "../index.html",
    "返回 VIP 总目录",
)
page("听力 VIP 精讲", "听力 VIP", "· 付费精修", "", tli_left, tli_main, [], "tli/tli-index.html")

# ---------- writing ----------
wr_items = [
    ("../index.html", "第01讲 · 待更新（文稿到位后生成）"),
]
wr_left = generic_left("写作", "Writing", wr_items)
wr_main = main_block(
    "雅思写作 VIP 精讲",
    "<p>付费写作课程逐字稿。左侧目录随每一讲文稿的生成自动更新。</p>",
    "写作板块待更新",
    "把这一讲的文稿发给我（直接粘贴文字或丢 .md 文件），即可生成精讲页与问答精要页并加入左侧目录。",
    "../index.html",
    "返回 VIP 总目录",
)
page("写作 VIP 精讲", "写作 VIP", "· 付费精修", "", wr_left, wr_main, [], "writing/writing-index.html")

# ---------- yuedu (reading) ----------
yd_items = [
    ("../../yue-du/qa-index.html", "阅读问答精要（13 讲）"),
    ("../../yue-du/practice/index.html", "阅读考点自测"),
]
yd_left = generic_left("阅读", "Reading", yd_items)
yd_main = main_block(
    "雅思阅读 VIP 精讲",
    "<p>付费阅读课程逐字稿。左侧目录随每一讲文稿的生成自动更新。</p>",
    "阅读板块待更新",
    "把这一讲的文稿发给我（直接粘贴文字或丢 .md 文件），即可生成精讲页与问答精要页并加入左侧目录。",
    "../index.html",
    "返回 VIP 总目录",
)
page("阅读 VIP 精讲", "阅读 VIP", "· 付费精修", "", yd_left, yd_main, [], "yuedu/yuedu-index.html")

print("ALL DONE")