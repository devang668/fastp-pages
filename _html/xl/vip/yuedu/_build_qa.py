# -*- coding: utf-8 -*-
# Build yuedu (Reading VIP) QA pages from the source markdown.
# Output: xl/vip/yuedu/qa-01..qa-22.html + yuedu-index.html
# Model: qa-tl-08.html (always-visible key-info tables + bold answers) with VIP chrome.
import os, re, io

SRC = r"D:\a.create\_MY_GIT_lib\FINISH\fastp-pages\_html\xl\vip\vip-md\vip阅读22节 (1).md"
OUT = r"D:\a.create\_MY_GIT_lib\FINISH\fastp-pages\_html\xl\vip\yuedu"
os.makedirs(OUT, exist_ok=True)

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def md_inline(s):
    # escape first, then **x** -> <b>x</b>
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s

# ---- parse source ----
raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")

lessons = []  # list of dict: num, raw_block
cur = None
for ln in lines:
    m = re.match(r"^##\s*reading-?-?(\d+)\s*$", ln.strip())
    if m:
        if cur: lessons.append(cur)
        cur = {"num": int(m.group(1)), "lines": []}
    elif cur is not None:
        cur["lines"].append(ln)
if cur: lessons.append(cur)

lessons.sort(key=lambda x: x["num"])

def split_qa(block_text):
    # block_text: everything before transcript
    # split on ** -> segments; odd = question, even (prefixed 发言人：) = answer
    parts = block_text.split("**")
    intro = parts[0] if parts else ""
    qa = []
    i = 1
    while i + 1 < len(parts):
        q = parts[i].strip()
        a = parts[i + 1]
        a = re.sub(r"^发言人：", "", a.strip())
        if q and a:
            qa.append((q, a))
        i += 2
    return intro.strip(), qa

def subtitle_from(intro):
    if not intro:
        return "雅思阅读"
    s = intro.strip()
    # strip generic leading openers (common in these transcripts)
    for opener in ["在本次教学对话中，", "在本次讨论中，", "在这次讲解中，", "在这次讨论中，",
                  "在一段讨论中，", "在准备考试时，", "针对雅思阅读考试，", "老师在讲解",
                  "本次课程专注于", "本次课程重点讲解了", "今天的课程专注于", "老师在本次课程中强调了",
                  "老师介绍了", "范老师介绍了", "范老师强调了", "三老师比喻道，", "针对",
                  "在这次雅思阅读课程介绍中，", "在这次教学对话中", "本次课程", "今天的课程"]:
        if s.startswith(opener):
            s = s[len(opener):]
            break
    m = re.search(r"[。！？；，,]", s)
    sub = s[:m.start()] if m else s
    sub = sub.strip()
    if len(sub) > 18:
        sub = sub[:18]
    if len(sub) < 4:
        sub = intro[:18]
    return sub

def core_answer(a):
    a0 = re.split(r"[。！？；\n]", a)[0].strip()
    a0 = re.sub(r"^发言人：", "", a0)
    if len(a0) > 84:
        a0 = a0[:84] + "…"
    return a0

pages = []
for L in lessons:
    num = L["num"]
    # collect pre-transcript text
    pre = []
    for ln in L["lines"]:
        t = ln.strip()
        if not t:
            continue
        if t.lower().startswith("hello") or t.startswith("各位同学大家好") or t.startswith("你好"):
            break
        pre.append(t)
    block = "\n".join(pre)
    intro, qa = split_qa(block)
    sub = subtitle_from(intro)
    pages.append({"num": num, "sub": sub, "intro": intro, "qa": qa})

# ---- HTML template ----
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
  .col-main { flex: 1; min-width: 0; padding: 40px 56px 80px; max-width: 880px; margin: 0 auto; }
  .col-main h1 { font-size: 30px; margin-top: 0; border-bottom: 1px solid #e5e7eb; padding-bottom: 12px; line-height: 1.35; }
  .col-main h2 { font-size: 21px; margin-top: 34px; padding-top: 14px; border-top: 1px solid #f3f4f6; }
  .col-main h3 { font-size: 17px; margin-top: 24px; color: #1f2937; }
  .col-main p { line-height: 1.8; color: #374151; margin: 10px 0; }
  .col-main blockquote { border-left: 3px solid #dbeafe; background: #f8fafc; margin: 16px 0; padding: 12px 18px; color: #4b5563; border-radius: 0 6px 6px 0; font-size: 14.5px; line-height: 1.75; }
  .col-main blockquote p { margin: 0; }
  .col-main table { border-collapse: collapse; width: 100%; margin: 18px 0; font-size: 13.5px; }
  .col-main th, .col-main td { border: 1px solid #e5e7eb; padding: 9px 12px; text-align: left; vertical-align: top; }
  .col-main th { background: #f1f5f9; font-weight: 600; color: #1f2937; }
  .col-main tr:nth-child(even) td { background: #fcfcfd; }
  .col-main td b, .col-main td strong { color: #1d4ed8; }
  .col-main .qakey b { color: #1d4ed8; }
  .col-right { width: 230px; flex-shrink: 0; border-left: 1px solid #e5e7eb; padding: 24px 18px; font-size: 13px; height: calc(100vh - 56px); position: sticky; top: 56px; overflow-y: auto; }
  .col-right h4 { font-size: 11px; text-transform: uppercase; color: #6b7280; margin: 0 0 12px; letter-spacing: 0.5px; font-weight: 600; }
  .col-right ul { list-style: none; padding: 0; margin: 0; }
  .col-right li { margin: 6px 0; }
  .col-right a { color: #4b5563; line-height: 1.45; font-size: 12.5px; }
  .col-right a:hover { color: #1d4ed8; }
  @media (max-width: 1100px) { .col-right { display: none; } }
  @media (max-width: 800px) { .col-left { display: none; } .col-main { padding: 24px; } }
"""

# ---- curated showcase tables (qa-tl-08 style: real key info, always visible) ----
SHOWCASE = {}

SHOWCASE[1] = """
    <h2><a id="showcase"></a>本讲精析速表（题型 / 评分 / 方法）</h2>
    <h3>三篇文章与题型分布</h3>
    <table>
      <thead><tr><th>文章</th><th>主题 / 类型</th><th>题量</th><th>主要题型</th><th>目标正确率</th></tr></thead>
      <tbody>
        <tr><td><b>第一篇</b></td><td>科普文（自然 / 人文，如灭绝海龟、巨石阵）</td><td>13</td><td>填空 + 判断（纯细节题）</td><td><b>≥10 题</b>（无论目标分）</td></tr>
        <tr><td><b>第二篇</b></td><td>科普 or 议论文</td><td>13</td><td>匹配题：人物观点 / 句子结尾 / 信息 / 标题配对</td><td><b>≥10 题</b>（目标 6+ 必争）</td></tr>
        <tr><td><b>第三篇</b></td><td>议论文（含作者观点与论证）</td><td>13–14</td><td>单选 + 标题配对（高分必争地）</td><td>拿一半以上</td></tr>
      </tbody>
    </table>
    <h3>四大题型一览</h3>
    <table>
      <thead><tr><th>题型</th><th>特点与要点</th></tr></thead>
      <tbody>
        <tr><td><b>填空</b></td><td>细节题。含笔记 / 表格 / 句子 / 总结 / 图形填空；题干给的线索多少不同（图形填空有“小乱序”特点）。</td></tr>
        <tr><td><b>判断</b></td><td>科普文用 <b>TRUE/FALSE/NOT GIVEN</b>，议论文用 <b>YES/NO/NOT GIVEN</b>；题材不同但考点完全一致。</td></tr>
        <tr><td><b>选择</b></td><td>单选四选一；多选每选项正确即给 1 分（人性化，错一个选项不整题零分）。</td></tr>
        <tr><td><b>配对</b></td><td>人物观点 / 信息 / 标题 / 句子结尾配对；或偏细节定位，或偏段落理解。</td></tr>
      </tbody>
    </table>
    <h3>评分目标（60 分钟 / 40 题）</h3>
    <table>
      <thead><tr><th>目标分</th><th>第一篇</th><th>第二篇</th><th>第三篇</th><th>总容错</th></tr></thead>
      <tbody>
        <tr><td><b>7 分</b></td><td>11–12（错 1）</td><td>约 10（错 2–3）</td><td>8–9（对一半以上）</td><td>共错 ≤ 10</td></tr>
        <tr><td><b>8 分</b></td><td>全对</td><td>至多错 1</td><td>至多错 4</td><td>共错 ≤ 5</td></tr>
      </tbody>
    </table>
    <h3>快速阅读两招（灵活穿插）</h3>
    <table>
      <thead><tr><th>方法</th><th>含义</th><th>用法</th></tr></thead>
      <tbody>
        <tr><td><b>Scanning 扫读</b></td><td>像扫描仪一样找定位词</td><td>所有细节题先 scan 定位词，定位句就在附近</td></tr>
        <tr><td><b>Skimming 跳读</b></td><td>定位到句后精读该句</td><td>只读定位句，其余不相干内容跳过</td></tr>
      </tbody>
    </table>
    <p class="tip" style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:12px 16px;color:#1e3a8a;font-size:14px;line-height:1.7;">机考强推：文章与题目左右对照，避免纸笔考翻页遗忘定位词；系统自带 highlight（多色）可标关键词。初期先保正确率，熟练后再追速度。</p>
"""

SHOWCASE[5] = """
    <h2><a id="showcase"></a>本讲精析速表（真题带练）</h2>
    <h3>句子填空题 · 做题步骤</h3>
    <table>
      <thead><tr><th>步骤</th><th>要点</th></tr></thead>
      <tbody>
        <tr><td><b>读题</b></td><td>先看题目要求（单词数限制：one word / no more than two words）</td></tr>
        <tr><td><b>预测</b></td><td>猜空性：名词 / 形容词 / 复数名词提示词</td></tr>
        <tr><td><b>定位</b></td><td>用名词做范围定位 + 空前形容词 / 动词做精确定位</td></tr>
        <tr><td><b>找替换</b></td><td>锁定替换词：结构类（a of b、并列）/ 替换类（动、形、抽象→具体）/ 指向类</td></tr>
        <tr><td><b>检查</b></td><td>意思顺、符合字数要求</td></tr>
      </tbody>
    </table>
    <h3>句子填空带练（西红柿基因题 24–26）</h3>
    <table>
      <thead><tr><th>题号</th><th>答案</th><th>定位词</th><th>同义替换 / 考点</th><th>依据句</th></tr></thead>
      <tbody>
        <tr><td>24</td><td><b>flavor</b></td><td>mutation（范围）→ undesirable trait / less desirable trait（精确）</td><td>lost 是干扰；答案在 less desirable trait 之后</td><td>“Tomato... have lost much of their <b>flavor</b>”</td></tr>
        <tr><td>25</td><td><b>size</b></td><td>three times（数字信息）</td><td>triple = three times（三倍）</td><td>“triple the <b>size</b> of fruit”</td></tr>
        <tr><td>26</td><td><b>salt / tolerant</b></td><td>vitamin C（原词定位）</td><td>not badly affected = more tolerant（动词替换）</td><td>“more tolerant <b>salt</b>... rich in vitamin C”</td></tr>
      </tbody>
    </table>
    <h3>总结填空带练（罗马隧道 / 战船商船 6–13）</h3>
    <table>
      <thead><tr><th>题号</th><th>答案</th><th>定位词</th><th>替换 / 考点</th><th>依据句</th></tr></thead>
      <tbody>
        <tr><td>战船</td><td><b>lightweight</b></td><td>warship（范围）</td><td>并列结构 and move quickly ↔ very speedy</td><td>“warship was light and moved quickly”</td></tr>
        <tr><td>战船</td><td><b>bronze</b></td><td>battery ram（原词）</td><td>a of b 结构：battery ram of bronze</td><td>“battery ram of <b>bronze</b>”</td></tr>
        <tr><td>战船</td><td><b>levels</b></td><td>rower（原词）</td><td>抽象→具体：three ↔ top/middle/lower levels（复数提示）</td><td>“rowers in top, middle and lower <b>levels</b>”</td></tr>
        <tr><td>商船</td><td><b>who</b></td><td>merchant ship + broad</td><td>broad ↔ wider（形容词替换）</td><td>“merchant ship was <b>wider</b>”</td></tr>
        <tr><td>商船</td><td><b>music</b></td><td>协调划船节奏</td><td>修饰关系：乐器弹奏的 music 助人，非 instrument 本身</td><td>“music could be played... keep time”</td></tr>
        <tr><td>商船</td><td><b>tour boat</b></td><td>sheep... poor to shore</td><td>poor ↔ interpreted（动词替换）</td><td>“towed by a number of <b>tour boats</b>”</td></tr>
        <tr><td>体育馆</td><td><b>fortress</b></td><td>convert（=change to）</td><td>并列：再变 residential area</td><td>“converted to <b>fortress</b>, then village”</td></tr>
        <tr><td>体育馆</td><td><b>opera</b></td><td>verona / famous</td><td>stage ↔ acting；set = 地点</td><td>“famous as venue for <b>opera</b>”</td></tr>
        <tr><td>体育馆</td><td><b>salt</b></td><td>lucca / storage</td><td>storage ↔ depot（仓库）</td><td>“impressive example of a depot for <b>salt</b>”</td></tr>
        <tr><td>体育馆</td><td><b>shops</b></td><td>market square + homes</td><td>并列：homes and shops；residence = home</td><td>“market square with <b>shops</b> and homes”</td></tr>
      </tbody>
    </table>
    <h3>总结填空带练（记忆力实验 37–40，第三篇）</h3>
    <table>
      <thead><tr><th>题号</th><th>答案</th><th>定位词</th><th>替换 / 考点</th><th>依据句</th></tr></thead>
      <tbody>
        <tr><td>37</td><td><b>memory</b></td><td>test / memory</td><td>a of b：memory test</td><td>“test of his <b>memory</b>”</td></tr>
        <tr><td>38</td><td><b>numbers</b></td><td>forward and reverse order</td><td>in order ↔ forward；reverse ↔ backward</td><td>“recall a series of <b>numbers</b>”</td></tr>
        <tr><td>39</td><td><b>communication</b></td><td>unusual amount / connected</td><td>greater than average ↔ unusual amount（复数名词提示）</td><td>“more highly connected... <b>communication</b>”</td></tr>
        <tr><td>40</td><td><b>visual / image</b></td><td>deal with... input</td><td>deal with ↔ process；image ↔ visual</td><td>“visual network... process <b>images</b>”</td></tr>
      </tbody>
    </table>
    <p class="tip" style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:12px 16px;color:#1e3a8a;font-size:14px;line-height:1.7;">句子填空难点在“定位分散、每题单独定位”；总结填空定位相对密集、且可借其他句子帮忙。两者考点一致，真正拉开差距的是定位——学完平行阅读法后这类题会轻松很多。</p>
"""

def build_qa_page(p):
    nn = "%02d" % p["num"]
    title = "第%s讲 · %s · 问答精要" % (nn, p["sub"])
    left_items = "\n".join(
        '      <li><a%s href="qa-%02d.html">第%02d讲 · %s</a></li>' % (
            " class=\"active\"" if q["num"] == p["num"] else "",
            q["num"], q["num"], q["sub"]) for q in pages)
    # questions
    qblocks = []
    toc = []
    for idx, (q, a) in enumerate(p["qa"], 1):
        anchor = "q%d" % idx
        qhtml = md_inline(q)
        ahtml = md_inline(a)
        qblocks.append(
            '    <h2><a id="%s"></a>Q%d. %s</h2>\n    <p class="qakey">%s</p>' % (anchor, idx, qhtml, ahtml))
        toc.append('<li><a href="#%s">Q%d. %s</a></li>' % (anchor, idx, md_inline(q)))
    qhtml_all = "\n".join(qblocks)
    toc_all = "\n".join(toc)
    showcase_html = SHOWCASE.get(p["num"], "")
    # overview table (always visible key info)
    ov_rows = []
    for idx, (q, a) in enumerate(p["qa"], 1):
        ov_rows.append("      <tr><td><b>Q%d</b></td><td>%s</td><td>%s</td></tr>" % (
            idx, md_inline(q), md_inline(core_answer(a))))
    ov_all = "\n".join(ov_rows)
    intro_html = md_inline(p["intro"]) if p["intro"] else "本讲内容见下方问答。"

    html = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="alternate icon" type="image/x-icon" href="../../favicon.ico">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s</title>
<style>
%s</style>
</head>
<body>
<header class="topbar">
  <div class="logo">阅读 VIP<span> · 第 %s 讲问答</span></div>
  <div class="topbar-right">
    <a href="../../../index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">首页</a>
    <a href="../index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">VIP 目录</a>
    <a href="yuedu-index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">阅读目录</a>
    <input id="search-input" placeholder="搜索 Ctrl K" autocomplete="off">
    <div id="search-panel"></div>
  </div>
</header>
<div class="layout">
  <aside class="col-left">
    <h3>阅读问答（22 讲）</h3>
    <ul>
%s
    </ul>
    <h3>返回</h3>
    <ul>
      <li><a class="back" href="../index.html">VIP 总目录</a></li>
      <li><a class="back" href="../../../index.html">站点首页</a></li>
    </ul>
  </aside>
  <main class="col-main">
    <h1>第%s讲 · %s</h1>
    <blockquote><p><b>本讲定位：</b>%s</p></blockquote>
    <h2><a id="overview"></a>本讲问答速览（关键信息）</h2>
    <table>
      <thead><tr><th style="width:54px;">编号</th><th style="width:38%%;">问题</th><th>核心答案</th></tr></thead>
      <tbody>
%s
      </tbody>
    </table>
    %s
    <h2><a id="detail"></a>逐题详解</h2>
%s
  </main>
  <aside class="col-right">
    <h4>本页问答</h4>
    <ul>
%s
    </ul>
  </aside>
</div>
<script>
(function(){
  var input = document.getElementById('search-input');
  var panel = document.getElementById('search-panel');
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
    if (leftHits.length){ parts.push('<div class="sp-group">阅读问答</div>'); parts.push('<ul>' + leftHits.map(function(a){ return '<li><a href="' + a.getAttribute('href') + '">' + escHtml(a.textContent) + '</a></li>'; }).join('') + '</ul>'); }
    if (rightHits.length){ parts.push('<div class="sp-group">本页问答</div>'); parts.push('<ul>' + rightHits.map(function(a){ return '<li><a href="' + a.getAttribute('href') + '">' + escHtml(a.textContent) + '</a></li>'; }).join('') + '</ul>'); }
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
})();
</script>
</body>
</html>
""" % (title, CSS, nn, left_items, nn, md_inline(p["sub"]), intro_html, ov_all, showcase_html, qhtml_all, toc_all)
    with open(os.path.join(OUT, "qa-%s.html" % nn), "w", encoding="utf-8") as f:
        f.write(html)

def build_index():
    left_items = "\n".join(
        '      <li><a href="qa-%02d.html">第%02d讲 · %s</a></li>' % (q["num"], q["num"], q["sub"]) for q in pages)
    cards = "\n".join(
        '      <a class="card" href="qa-%02d.html"><h3>第%02d讲</h3><p>%s</p><span class="tag">问答精要</span></a>' % (q["num"], q["num"], q["sub"]) for q in pages)
    html = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="alternate icon" type="image/x-icon" href="../../favicon.ico">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>阅读 VIP · 问答精要 22 讲</title>
<style>
%s</style>
</head>
<body>
<header class="topbar">
  <div class="logo">阅读 VIP<span> · 22 讲问答</span></div>
  <div class="topbar-right">
    <a href="../../../index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">首页</a>
    <a href="../index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">VIP 目录</a>
    <input id="search-input" placeholder="搜索 Ctrl K" autocomplete="off">
    <div id="search-panel"></div>
  </div>
</header>
<div class="layout">
  <aside class="col-left">
    <h3>阅读问答（22 讲）</h3>
    <ul>
%s
    </ul>
    <h3>返回</h3>
    <ul>
      <li><a class="back" href="../index.html">VIP 总目录</a></li>
      <li><a class="back" href="../../../index.html">站点首页</a></li>
    </ul>
  </aside>
  <main class="col-main">
    <h1>雅思阅读 VIP · 问答精要（22 讲）</h1>
    <p>付费阅读冲刺课程的问答精要。每讲把整讲考点压缩成可速查的 Q&amp;A，并附「本讲问答速览」表格让关键信息一眼可见。点击左侧任一一讲开始查重点。</p>
    <div class="cards">
%s
    </div>
  </main>
  <aside class="col-right">
    <h4>说明</h4>
    <p class="empty">本区为付费课程内容，仅作个人学习笔记使用。每一讲由课程文稿生成「问答精要」页，配速览表与逐题详解。</p>
  </aside>
</div>
<script>
(function(){
  var input = document.getElementById('search-input');
  var panel = document.getElementById('search-panel');
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
    if (leftHits.length){ parts.push('<div class="sp-group">阅读问答</div>'); parts.push('<ul>' + leftHits.map(function(a){ return '<li><a href="' + a.getAttribute('href') + '">' + escHtml(a.textContent) + '</a></li>'; }).join('') + '</ul>'); }
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
})();
</script>
</body>
</html>
""" % (CSS, left_items, cards)
    with open(os.path.join(OUT, "yuedu-index.html"), "w", encoding="utf-8") as f:
        f.write(html)

for p in pages:
    build_qa_page(p)
build_index()

print("Generated %d QA pages + index." % len(pages))
for p in pages:
    print("qa-%02d  Q=%d  sub=%s" % (p["num"], len(p["qa"]), p["sub"]))
