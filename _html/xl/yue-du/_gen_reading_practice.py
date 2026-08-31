# -*- coding: utf-8 -*-
# Generate yue-du reading practice pages (no emoji, 3-column layout, Ctrl+K search).
import io, os, re

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "practice")
os.makedirs(OUT, exist_ok=True)

# ---------- shared CSS ----------
CSS = """
*{box-sizing:border-box}
html,body{margin:0;padding:0;min-height:100%;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;color:#1f2328;background:#fff}
a{color:#2c5cdc;text-decoration:none}
a:hover{text-decoration:underline}
.topbar{position:fixed;top:0;left:0;right:0;height:56px;display:flex;align-items:center;padding:0 24px;border-bottom:1px solid #e5e7eb;background:#fff;z-index:10}
.logo{font-weight:800;font-size:20px;letter-spacing:-.5px;color:#111}
.logo span{color:#6b7280;font-weight:500}
.topbar-right{margin-left:auto;display:flex;gap:16px;align-items:center;position:relative}
.topbar-right input{border:1px solid #d1d5db;border-radius:6px;padding:6px 10px;font-size:13px;width:240px;background:#f9fafb}
.topbar-right input:focus{outline:none;border-color:#2c5cdc;background:#fff;box-shadow:0 0 0 3px rgba(44,92,220,.12)}
#search-panel{position:absolute;top:44px;right:0;width:360px;max-height:70vh;overflow-y:auto;background:#fff;border:1px solid #e5e7eb;border-radius:8px;box-shadow:0 10px 25px rgba(0,0,0,.08);padding:8px 0;z-index:100;font-size:13px;display:none}
#search-panel.show{display:block}
#search-panel .sp-group{padding:8px 14px 4px;font-size:11px;color:#6b7280;text-transform:uppercase;font-weight:600;letter-spacing:.5px}
#search-panel ul{list-style:none;padding:0;margin:0}
#search-panel li a{display:block;padding:6px 14px;color:#374151;line-height:1.4;font-size:12.5px}
#search-panel li a:hover{background:#f3f4f6;color:#1d4ed8;text-decoration:none}
#search-panel .sp-empty{padding:24px;text-align:center;color:#9ca3af;font-size:12px}
mark.search-hl{background:#fff3a3;color:inherit;padding:0 2px;border-radius:2px}
.layout{display:flex;padding-top:56px;min-height:100vh}
.col-left{width:240px;flex-shrink:0;border-right:1px solid #e5e7eb;padding:20px 14px 40px;overflow-y:auto;height:calc(100vh - 56px);position:sticky;top:56px}
.col-left ul{list-style:none;padding:0;margin:0 0 16px}
.col-left li{margin:2px 0}
.col-left a{display:block;padding:6px 10px;border-radius:6px;font-size:13.5px;color:#374151;line-height:1.4}
.col-left a:hover{background:#f3f4f6;text-decoration:none}
.col-left a.active{background:#eff6ff;color:#1d4ed8;font-weight:600}
.col-left h3{font-size:11px;text-transform:uppercase;color:#6b7280;margin:18px 8px 8px;letter-spacing:.5px;font-weight:600}
.col-left .back{font-size:12.5px;color:#4b5563}
.col-main{flex:1;min-width:0;padding:40px 56px 80px;max-width:820px;margin:0 auto}
.col-main h1{font-size:32px;margin-top:0;border-bottom:1px solid #e5e7eb;padding-bottom:12px;line-height:1.3}
.col-main h2{font-size:23px;margin-top:40px;padding-top:16px;border-top:1px solid #f3f4f6}
.col-main p{line-height:1.75;color:#374151}
.block{background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;padding:16px 18px;margin:14px 0}
.block .q{font-weight:600;color:#111;margin-bottom:8px}
.block .q .no{color:#2c5cdc;margin-right:6px}
.block .audio{font-style:italic;color:#4b5563;border-left:3px solid #dbeafe;padding:4px 10px;margin:8px 0;background:#eff6ff;border-radius:0 6px 6px 0;font-size:14px}
.block .audio b{color:#0f172a}
.block .blank{display:inline-block;min-width:52px;border-bottom:2px solid #9ca3af;color:transparent}
.block .hint{color:#6b7280;font-size:13px;margin-top:6px}
.ans-toggle{margin-top:10px}
.ans-toggle summary{cursor:pointer;color:#1d4ed8;font-weight:600;font-size:13.5px;padding:6px 10px;background:#eff6ff;border-radius:6px;display:inline-block;user-select:none}
.ans-toggle summary:hover{background:#dbeafe}
.ans-body{margin-top:10px;padding:10px 14px;background:#fff;border:1px solid #e5e7eb;border-radius:8px;font-size:14px;line-height:1.7}
.ans-body .ans{color:#059669;font-weight:700}
.ans-body .why{color:#374151}
.col-right{width:220px;flex-shrink:0;border-left:1px solid #e5e7eb;padding:24px 18px;font-size:13px;height:calc(100vh - 56px);position:sticky;top:56px;overflow-y:auto}
.col-right h4{font-size:11px;text-transform:uppercase;color:#6b7280;margin:0 0 12px;letter-spacing:.5px;font-weight:600}
.col-right ul{list-style:none;padding:0;margin:0}
.col-right li{margin:6px 0}
.col-right a{color:#4b5563;line-height:1.45;font-size:12.5px}
.col-right a:hover{color:#1d4ed8}
@media (max-width:1100px){.col-right{display:none}}
@media (max-width:800px){.col-left{display:none}.col-main{padding:24px}}
"""

JS = """
(function(){
  var input=document.getElementById('search-input');
  var panel=document.getElementById('search-panel');
  if(!input||!panel)return;
  var main=document.querySelector('.col-main');
  var rightLinks=Array.prototype.slice.call(document.querySelectorAll('.col-right ul li a'));
  function escHtml(s){return s.replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function escapeRegex(s){ return s.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'); }
  function clearHighlights(){if(!main)return;var marks=main.querySelectorAll('mark.search-hl');for(var i=0;i<marks.length;i++){var m=marks[i];var t=document.createTextNode(m.textContent);m.parentNode.replaceChild(t,m);}main.normalize();}
  function highlightInMain(kw){if(!main)return;clearHighlights();if(!kw)return;var re=new RegExp(escapeRegex(kw),'gi');var walker=document.createTreeWalker(main,NodeFilter.SHOW_TEXT,{acceptNode:function(n){if(!n.nodeValue||!n.nodeValue.trim())return NodeFilter.FILTER_REJECT;var p=n.parentElement;if(!p)return NodeFilter.FILTER_REJECT;var tag=p.tagName;if(tag==='SCRIPT'||tag==='STYLE'||tag==='CODE'||tag==='PRE')return NodeFilter.FILTER_REJECT;if(p.closest&&p.closest('mark.search-hl'))return NodeFilter.FILTER_REJECT;return n.nodeValue.toLowerCase().indexOf(kw.toLowerCase())>=0?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT;}});var nodes=[];var n;while((n=walker.nextNode()))nodes.push(n);for(var i=0;i<nodes.length;i++){var node=nodes[i];var src=node.nodeValue;var re2=new RegExp(escapeRegex(kw),'gi');var out='';var last=0;var m;while((m=re2.exec(src))!==null){out+=escHtml(src.slice(last,m.index));out+='<mark class="search-hl">'+escHtml(m[0])+'</mark>';last=m.index+m[0].length;if(m[0].length===0)re2.lastIndex++;}out+=escHtml(src.slice(last));var tmp=document.createElement('span');tmp.innerHTML=out;var parent=node.parentNode;while(tmp.firstChild)parent.insertBefore(tmp.firstChild,node);parent.removeChild(node);}}
  function doSearch(q){
    q=(q||'').trim();
    if(!q){panel.className='';panel.innerHTML='';clearHighlights();return;}
    var qLower=q.toLowerCase();
    var hits=rightLinks.filter(function(a){return a.textContent.toLowerCase().indexOf(qLower)>=0;});
    var parts=[];
    if(hits.length){parts.push('<div class="sp-group">本页小节</div>');parts.push('<ul>'+hits.map(function(a){return '<li><a href="'+a.getAttribute('href')+'">'+escHtml(a.textContent)+'</a></li>';}).join('')+'</ul>');}
    if(!parts.length)parts.push('<div class="sp-empty">无匹配结果</div>');
    panel.innerHTML=parts.join('');panel.className='show';highlightInMain(q);
  }
  var timer=null;
  input.addEventListener('input',function(e){clearTimeout(timer);timer=setTimeout(function(){doSearch(input.value);},80);});
  input.addEventListener('keydown',function(e){if(e.key==='Escape'){input.value='';doSearch('');input.blur();}});
  document.addEventListener('click',function(e){if(panel.contains(e.target)||e.target===input)return;panel.className='';});
  panel.addEventListener('click',function(e){var a=e.target.closest('a');if(a)panel.className='';});
  document.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&(e.key==='k'||e.key==='K')){e.preventDefault();input.focus();input.select();}});
})();
"""

def go(title, desc, sections, left_extra=""):
    """left_extra: extra <ul> before 返回 (e.g. 总入口链接)."""
    links = []
    for sid, label in sections:
        links.append('<li><a href="#%s">%s</a></li>' % (sid, label))
    right = '<h4>本页小节</h4><ul>' + ''.join(links) + '</ul>'
    left = '<ul><li><a href="#%s">%s</a></li>' % (sections[0][0], sections[0][1])
    for sid, label in sections[1:]:
        left += '<li><a href="#%s">%s</a></li>' % (sid, label)
    left += '</ul>'
    return left

def page(title, desc, sections_blocks, filename, left_html):
    """sections_blocks: list of (anchor, h2_text, blocks_html)"""
    main = '<h1>%s</h1>\n<p style="color:#6b7280;">%s</p>\n' % (title, desc)
    for anchor, h2text, blocks in sections_blocks:
        main += '<h2><a id="%s"></a>%s</h2>\n%s' % (anchor, h2text, blocks)
    right = '<h4>本页小节</h4><ul>'
    for anchor, h2text, _ in sections_blocks:
        right += '<li><a href="#%s">%s</a></li>' % (anchor, h2text)
    right += '</ul>'
    html = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="alternate icon" type="image/x-icon" href="../../favicon.ico">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s</title>
<style>%s</style>
</head>
<body>
<header class="topbar">
  <div class="logo">阅读考点自测<span> · 雅思阅读13讲配套</span></div>
  <div class="topbar-right">
    <a href="../../index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">首页</a>
    <a href="../qa-index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">课程目录</a>
    <input id="search-input" placeholder="搜索 Ctrl K" autocomplete="off">
    <div id="search-panel"></div>
  </div>
</header>
<div class="layout">
  <aside class="col-left">
%s
    <h3>返回</h3>
    <ul>
      <li><a class="back" href="index.html">返回练习总入口</a></li>
      <li><a class="back" href="../qa-index.html">返回课程目录</a></li>
      <li><a class="back" href="../../index.html">返回首页</a></li>
    </ul>
  </aside>
  <main class="col-main">
%s
  </main>
  <aside class="col-right">
%s
  </aside>
</div>
<script>%s</script>
</body>
</html>""" % (title, CSS, left_html, main, right, JS)
    with io.open(os.path.join(OUT, filename), "w", encoding="utf-8") as f:
        f.write(html)

def block(no, question, audio, hint, ans, why):
    parts = ['<div class="block">', '<div class="q"><span class="no">%s</span>%s</div>' % (no, question)]
    if audio:
        parts.append('<div class="audio">%s</div>' % audio)
    if hint:
        parts.append('<div class="hint">%s</div>' % hint)
    parts.append('<details class="ans-toggle"><summary>显示答案 + 考点</summary>')
    parts.append('<div class="ans-body"><span class="ans">答案：%s</span><div class="why">%s</div></div>' % (ans, why))
    parts.append('</details></div>')
    return ''.join(parts)

def sec(anchor, h2text, blocks_html):
    return (anchor, h2text, blocks_html)

NAV = """    <h3>自测板块</h3>
    <ul>
      <li><a href="fill.html">第02讲 填空：表格/笔记填空</a></li>
      <li><a href="tfng.html">第03/10讲 判断 TFNG vs YNNG</a></li>
      <li><a href="sentence.html">第04讲 句子填空 + 简答</a></li>
      <li><a href="flow.html">第05讲 流程图/图形填空</a></li>
      <li><a href="summary.html">第06讲 总结填空</a></li>
      <li><a href="person.html">第07讲 人物观点配对</a></li>
      <li><a href="ending.html">第08讲 句子结尾配对</a></li>
      <li><a href="info.html">第09讲 信息匹配</a></li>
      <li><a href="multi.html">第11讲 多选题</a></li>
      <li><a href="single.html">第12讲 单选题</a></li>
      <li><a href="parallel.html">第13讲 平行阅读法</a></li>
    </ul>"""

def left_nav(active):
    lis = [
        ('fill.html', '第02讲 填空：表格/笔记填空'),
        ('tfng.html', '第03/10讲 判断 TFNG vs YNNG'),
        ('sentence.html', '第04讲 句子填空 + 简答'),
        ('flow.html', '第05讲 流程图/图形填空'),
        ('summary.html', '第06讲 总结填空'),
        ('person.html', '第07讲 人物观点配对'),
        ('ending.html', '第08讲 句子结尾配对'),
        ('info.html', '第09讲 信息匹配'),
        ('multi.html', '第11讲 多选题'),
        ('single.html', '第12讲 单选题'),
        ('parallel.html', '第13讲 平行阅读法'),
    ]
    out = ['    <h3>自测板块</h3>', '    <ul>']
    for href, label in lis:
        cls = ' class="active"' if href == active else ''
        out.append('      <li><a href="%s"%s>%s</a></li>' % (href, cls, label))
    out.append('    </ul>')
    return '\n'.join(out)

# ================= 02 填空：表格/笔记 =================
blocks = []
blocks.append(block('Q1', '表格填空的四大共通原则，第一条是什么？',
  None, '提示：老师把填空原则归纳为四条。',
  '顺序出题（偶尔小乱序）',
  '填空几乎都按题号顺序出题；但考官偶尔会搞小乱序（先找到第4题再第3题）。往下找不到目标时往回读一读，多半是与上一题乱序了。'))
blocks.append(block('Q2', '"答案必须原文原词"是什么意思？',
  None, '提示：这是填空第二条原则。',
  '答案必须从原文原封不动抄回，不能按自己理解改写',
  '机考直接 Ctrl+C / Ctrl+V，纸笔照抄原文单词。任何改写都不算对。'))
blocks.append(block('Q3', '填空题高频五大考点，第一个是什么？',
  None, '提示：想想填空题通常挖什么坑。',
  '并列结构（A and B）',
  '题干 A and ____ ，回原文找 A，and 的替换词后面就是答案。'))
blocks.append(block('Q4', '伦敦地铁题：题干 "____ of London" 用什么知识点定位？',
  None, '提示：介词结构。',
  'a of b 结构（= b a）',
  '题干 X of London 对应原文可能把语序倒成 London of the city 或 X, London；抓住 of 两端的核心名词。'))
blocks.append(block('Q5', '填空题"读题→预测词性"有什么用？',
  None, '提示：做题前先看空。',
  '预测空格词性（名词/动词/形容词），大幅缩小答案范围',
  '看懂空前空后语法，判断要填名词还是动词/形容词；答案大概率落在那类词上。'))
blocks.append(block('Q6', '袋狼真题：问"袋狼住在哪"该填什么？',
  None, '提示：pouch 长在 belly 上，belly 长在妈妈身上。',
  'pouch（育儿袋）',
  '顺着"住在哪"的链条：pouch 是住处本身。问"妈妈身上有什么"才填 belly。定位要分清问的主体。'))

page('雅思阅读第02讲 填空：表格/笔记填空（考点自测）',
     '题目全部来自老师讲过的真实考点。先独立做题，再点"显示答案 + 考点"对照；做错的返回对应 <a href="../qa-02.html">问答精要</a> 复习。',
     [sec('sec1', '填空四大原则', ''.join(blocks[0:3])),
      sec('sec2', '高频考点实战', ''.join(blocks[3:6]))],
     'fill.html', left_nav('fill.html'))

# ================= 03/10 判断 =================
blocks = []
blocks.append(block('Q1', '判断题题干由哪三部分构成？',
  None, '提示：老师归纳为"三分法"。',
  '定位词 + 考点词 + 限定条件',
  '定位词找位置，考点词（most/all/never 等）是判断核心，限定条件（如时间）锁范围。'))
blocks.append(block('Q2', 'TFNG 和 YNNG 的区别是什么？',
  None, '提示：字母不一样，名字不一样。',
  'TFNG 用于事实陈述（读细节），YNNG 用于观点/作者主张',
  'True/False/Not Given 对应事实信息；Yes/No/Not Given 对应作者观点。先分清再动笔。'))
blocks.append(block('Q3', '"唯一考点"是什么意思？',
  None, '提示：判断题每句话只有一个判断核心。',
  '一句话只有一个可判断对错的点（考点词）',
  '把考点变成问题，回原文自问自答：支持=True/Yes，反驳=False/No，没提=Not Given。'))
blocks.append(block('Q4', '判断题六大高频考点，最常考的是哪类？',
  None, '提示：想想 most/all/only。',
  '绝对词类（most / all / only / never / always）',
  '绝对词最容易出 False：原文说 some 或 not all，选项说 all，直接 False。'))
blocks.append(block('Q5', '判断题三步法是什么？',
  None, '提示：先读题再回原文。',
  '读一道题 → 找定位词 → 把考点变问题回原文自问自答 → True/False/Not Given',
  '不跨段找定位（大多一段一题）；找到定位句后只看它，别乱猜。'))
blocks.append(block('Q6', '伦敦地铁真题：首日客流大于预测 → 选什么？',
  None, '提示：原文只说了实际运送 4 万人。',
  'Not Given',
  '原文没提预测人数，对比不存在，不能凭感觉说 True/False。'))

page('雅思阅读第03/10讲 判断 TFNG vs YNNG（考点自测）',
     '判断是阅读主力题型，先分清 TFNG / YNNG，再套用六大考点识别与三步法。做错的返回 <a href="../qa-03.html">问答精要</a> 或 <a href="../qa-10.html">考点速查</a> 复习。',
     [sec('sec1', '题型构成与区别', ''.join(blocks[0:3])),
      sec('sec2', '考点与三步法', ''.join(blocks[3:6]))],
     'tfng.html', left_nav('tfng.html'))

# ================= 04 句子填空+简答 =================
blocks = []
blocks.append(block('Q1', '句子填空和简答题的核心特点是什么？',
  None, '提示：答案在哪找？',
  '答案基本来自原文原词，且有固定考点（并列/介词/被动/动词替换）',
  '这两类本质同源：空格处多为名词短语，靠定位和同义替换锁定原文答案词。'))
blocks.append(block('Q2', '"no more than two words" 是不是答案必须两个单词？',
  None, '提示：注意"不超过"。',
  '不是，最多两个，可以是一个',
  '"NO MORE THAN TWO WORDS" 是上限不是必须；答案 1-2 词都行。'))
blocks.append(block('Q3', '简答题"飘着读"是什么时候用？',
  None, '提示：读不完时怎么办。',
  '题干关键词多、来不及细读时，用关键词在文中快速扫读定位',
  '飘着读 = 不逐句精读，只带定位词去原文扫，找到定位句再停。'))
blocks.append(block('Q4', 'Perkin 紫色染料真题：问"consult"（咨询）该找什么定位？',
  None, '提示：专有名词。',
  '人名（大写专有名词）',
  'consult 的同义替换是 ask advice；题干出现动作词，回去找大写人名，直接扫大写。'))
blocks.append(block('Q5', '句子填空防坑提示：题干限定词 immediately 对应原文什么？',
  None, '提示：同义替换。',
  'quickly / instant recognition',
  '限定词也会被替换；看到 immediately 别只等原词，等 quickly 这类替换词。'))

page('雅思阅读第04讲 句子填空 + 简答题（考点自测）',
     '句子填空与简答题是填空题第二专题，重点练"定位 + 词性预测 + 同义替换"。做错返回 <a href="../qa-04.html">问答精要</a>。',
     [sec('sec1', '题型特点与词数规则', ''.join(blocks[0:3])),
      sec('sec2', '定位与防坑', ''.join(blocks[3:5]))],
     'sentence.html', left_nav('sentence.html'))

# ================= 05 流程图/图形 =================
blocks = []
blocks.append(block('Q1', '流程图填空的性价比为什么高？',
  None, '提示：位置在哪？',
  '位置固定（通常在文章中部/局部），范围小，答案基本是原文词',
  '流程图对应文章一小段实验/环节描述，范围固定，好定位、好得分。'))
blocks.append(block('Q2', '"不拘一格定位法"是什么？',
  None, '提示：别死等原文原词。',
  '题干词可能被替换，用任意独特词（数字/大写/怪词）都能定位',
  '不必等题干原词；只要是独特的定位信号（如 1996、triangular），抓到一个就能切入。'))
blocks.append(block('Q3', '动词为什么是流程图填空的核心线索？',
  None, '提示：流程图连的是动作。',
  '动词串联实验步骤，答案多为步骤中的名词宾语',
  '看图上的动词（collect / measure / record），找到对应原文动词，宾语就是答案。'))
blocks.append(block('Q4', '图形填空和流程图填空的区别？',
  None, '提示：图形上有什么？',
  '图形填空图上标数字/部位名称，答案贴在图形部位旁；流程图按步骤顺序填空',
  '图形填空像"看图贴标签"，流程图像"串联步骤"。两者都按题号顺序出题。'))
blocks.append(block('Q5', '乌龟实验真题：答案受"最多2词"限制时，怎么取舍？',
  None, '提示：原文是 triangular graph paper。',
  '限定形容词 triangular + 核心名词 graph',
  '原文词组超过字数上限时，保留限定形容词 + 核心名词：triangular graph，别贪多。'))

page('雅思阅读第05讲 流程图/图形填空（考点自测）',
     '这两类题位置固定、范围小，练"不拘一格定位" + 动词线索。做错返回 <a href="../qa-05.html">问答精要</a>。',
     [sec('sec1', '题型特点', ''.join(blocks[0:2])),
      sec('sec2', '定位与取舍', ''.join(blocks[2:5]))],
     'flow.html', left_nav('flow.html'))

# ================= 06 总结填空 =================
blocks = []
blocks.append(block('Q1', '总结填空和带选项的总结填空关系？',
  None, '提示：一种题型两种形式。',
  '同一题型：不带选项=填原文词；带选项=从选项池选',
  '带选项时选项池提供单词，但答案仍要与原文对应，不能只靠选项猜。'))
blocks.append(block('Q2', '总结填空也顺序出题吗？小乱序多频繁？',
  None, '提示：老师强调的规律。',
  '大多顺序出题，偶有小乱序（约三分之一区间内乱序）',
  '总结填空整体顺序，但同一段内 2-3 题可能乱序；先粗定位整组题的段落区间。'))
blocks.append(block('Q3', '什么时候会出总结填空？',
  None, '提示：看文章结构。',
  '常出现在文章有总结性段落时（文末/实验结论处）',
  '作者对前文做概括的段落，就是总结填空的取材区。'))
blocks.append(block('Q4', '总结填空考察的核心能力？',
  None, '提示：一句原文和一句题干。',
  '识别"题干小句"与"原文长句"间的同义替换',
  '题干把原文长句压缩成短句，答案词常被替换；练同替敏感度。'))
blocks.append(block('Q5', '罗马造船真题：题干并列结构 A and ____ 怎么找答案？',
  None, '提示：回到原文找 A。',
  '回原文找 A，并列词（and / as well as）后面就是答案',
  '原文几乎必有 and 的平行结构，答案在并列词之后出现。'))

page('雅思阅读第06讲 总结填空（考点自测）',
     '总结填空是填空收官题型，练"顺序 + 同义替换 + 段落定位"。做错返回 <a href="../qa-06.html">问答精要</a>。',
     [sec('sec1', '题型规律', ''.join(blocks[0:3])),
      sec('sec2', '核心能力实战', ''.join(blocks[3:5]))],
     'summary.html', left_nav('summary.html'))

# ================= 07 人物观点配对 =================
blocks = []
blocks.append(block('Q1', '人物观点配对有顺序吗？什么按顺序出现？',
  None, '提示：人物还是选项？',
  '人物按文章出现顺序出现；选项（观点）不按顺序',
  '按人物第一次出现的顺序找；题干观点句在文中不一定按顺序对应。'))
blocks.append(block('Q2', '人物观点配对三步法？',
  None, '提示：先划人名。',
  '读题干划人名 → 回文找人物首次出现位置 → 读其观点句匹配选项',
  '人物观点紧贴引号/冒号；找到人物观点就对比选项，别通读全文。'))
blocks.append(block('Q3', 'AI 文章真题：3 人 6 题，选项平均分配吗？',
  None, '提示：6 题 3 选项。',
  '大概率平均分配（222）',
  '人物观点配对选项大多平均分配：6 题 3 选项约是 222。可用作检查手段，但别当唯一依据。'))
blocks.append(block('Q4', 'Stella 验证法是什么？',
  None, '提示：漏题时用。',
  '把已用段落标黄，中间没被用到的段落 = 漏题所在',
  '人物观点配对按人物分区块；中间空白段往往藏着没找到的题，回那里补。'))

page('雅思阅读第07讲 人物观点配对（考点自测）',
     '配对题最简单的一类，练"划人名 + 按出现顺序 + 平均分配检查"。做错返回 <a href="../qa-07.html">问答精要</a>。',
     [sec('sec1', '顺序与三步法', ''.join(blocks[0:2])),
      sec('sec2', '分配规律与验证', ''.join(blocks[2:4]))],
     'person.html', left_nav('person.html'))

# ================= 08 句子结尾配对 =================
blocks = []
blocks.append(block('Q1', '句子结尾配对最特殊的特点？',
  None, '提示：想一半答案和另一半。',
  '题干给句子前半句，选项是结尾半句；答案组合成完整句',
  '先读题干半句，再去文章找对应内容，选结尾选项。'))
blocks.append(block('Q2', '句子结尾配对三步法？',
  None, '提示：先看题干还是选项？',
  '读题干（找主干）→ 回原文定位 → 对比选项结尾',
  '题干主干 = 句子前半逻辑；回原文找到对应句后，看哪句与原文意思衔接最顺。'))
blocks.append(block('Q3', '同义替换三个层级？',
  None, '提示：词/短语/句子。',
  '词级（building↔construction）、短语级、句级（整句改写）',
  '三个层级都要练；句子结尾配对常考词级与短语级替换。'))
blocks.append(block('Q4', '为什么不能"过度揣测"？',
  None, '提示：答案要落地。',
  '选项必须与原文直接对应，不能凭脑补推逻辑',
  '过度揣测是配对题失分主因：选项和原文有直接对应才选，别加戏。'))
blocks.append(block('Q5', '创新心理学真题：题干原文词定位后，选什么？',
  None, '提示：construction ↔ building。',
  'building',
  'take over in construction → building，词级同义替换直接对应。'))

page('雅思阅读第08讲 句子结尾配对（考点自测）',
     '句子结尾配对练"题干半句 → 原文定位 → 结尾选项"。做错返回 <a href="../qa-08.html">问答精要</a>。',
     [sec('sec1', '题型特点与三步法', ''.join(blocks[0:2])),
      sec('sec2', '替换层级与防坑', ''.join(blocks[2:5]))],
     'ending.html', left_nav('ending.html'))

# ================= 09 信息匹配 =================
blocks = []
blocks.append(block('Q1', '信息匹配题（段落信息匹配）有什么特点？',
  None, '提示：题目数量 vs 段落。',
  '选项是段落字母，题干是信息点；大多乱序、可能 NB 重复使用',
  '把题干理解为"信息点"（不是原词），回文章按段落检索。'))
blocks.append(block('Q2', '以五题为界的策略是什么？',
  None, '提示：先读文章还是先读题。',
  '题目 > 5 道 → 先读文章逐段检索；题目 ≤ 5 道 → 先读题干再通读',
  '题少带题读省时间；题多先通读文章，边读边对照剩余题目。'))
blocks.append(block('Q3', '题干里的"功能词"有什么用？',
  None, '提示：example / problem。',
  '功能词提示要找的段落类型（含例子/问题/对比的段落）',
  '题干出现 a number of examples → 选段落必须真的有一串例子；单个例子不算。'))
blocks.append(block('Q4', '做题"法宝"是什么？',
  None, '提示：别只等原词。',
  '同词异义替换 + 段落主题扫描',
  '扫每段首句/主题句，对照题干信息点；关键词同段出现还可能是陷阱（同词≠同段）。'))
blocks.append(block('Q5', '西红柿真题：NB 表示什么？',
  None, '提示：注意题目开头说明。',
  'NB = 一个段落可能被选多次',
  '有 NB 时段落可重复选；C 段西红柿真题用两次就是实例。'))

page('雅思阅读第09讲 信息匹配（考点自测）',
     '信息匹配练"五届策略"与"功能词"识别，注意同词≠同段。做错返回 <a href="../qa-09.html">问答精要</a>。',
     [sec('sec1', '题型特点与策略', ''.join(blocks[0:2])),
      sec('sec2', '功能词与法宝', ''.join(blocks[2:5]))],
     'info.html', left_nav('info.html'))

# ================= 11 多选 =================
blocks = []
blocks.append(block('Q1', '多选分哪两类？',
  None, '提示：按题的位置。',
  '分散型（题干分散在全文）+ 密集型（集中在某一段）',
  '第一眼看题干关键词分布在哪些段落：全文各段 = 分散型；都在一段 = 密集型。'))
blocks.append(block('Q2', '分散型多选题怎么处理？',
  None, '提示：找题干关键词。',
  '按题干关键词分段定位，平行阅读读到该段就做',
  '分散型题干关键词分散，用平行阅读法：读到相关段落顺手做对应题。'))
blocks.append(block('Q3', '密集型多选题怎么处理？',
  None, '提示：题干指明段落。',
  '题干指明段落 → 平行阅读读到该段立即做，别等',
  '密集型关键词集中，读那段时一并解决多道多选题。'))
blocks.append(block('Q4', '现代 vs 古代体育馆真题：C 选项筛掉的原因？',
  None, '提示：原文说钢筋混凝土。',
  '选项说 made of less durable material，正好与"钢筋混凝土"相反',
  '选项与原文相反直接排除；选正确项要先看限定特征是否完全符合原文。'))

page('雅思阅读第11讲 多选题（考点自测）',
     '多选练"分散/密集型"判断与筛选。做错返回 <a href="../qa-11.html">问答精要</a>。',
     [sec('sec1', '两类与策略', ''.join(blocks[0:3])),
      sec('sec2', '真题筛选', ''.join(blocks[3:4]))],
     'multi.html', left_nav('multi.html'))

# ================= 12 单选 =================
blocks = []
blocks.append(block('Q1', '单选题分哪三类？占比各多少？',
  None, '提示：老师说的三类。',
  '细节型 + 推理型 + 功能型（趋势：功能型占比上升、细节型下降）',
  '三类占比随剑 11 → 剑 16/17 变化：功能型越来越多。'))
blocks.append(block('Q2', '推理题的"逻辑链"有什么禁忌？',
  None, '提示：中式长逻辑链。',
  '不能搭长逻辑链（好好学习→好大学→好工作→幸福不成立）',
  '雅思阅读推理链极短：A 和 C 不能隔着多层建立因果。选贴近原文一步推理的选项。'))
blocks.append(block('Q3', '功能型题目为什么必须放到最后做？',
  None, '提示：题目类型顺序。',
  '功能题通常问"作者为什么提这个例子/说明什么"，需要全文理解',
  '功能题依赖整篇主旨，先做细节题锁定分数，最后攻功能题。'))
blocks.append(block('Q4', '百万美元四重奏案例：例子说明作者的什么观点？',
  None, '提示：识别"例子→观点"。',
  '识别例子背后的观点句，而不是停在例子表面细节',
  '例子是论据，观点是论点；选项考的是"作者提它想说明什么"。'))

page('雅思阅读第12讲 单选题（考点自测）',
     '单选练三类区分与"短推理链"直觉。做错返回 <a href="../qa-12.html">问答精要</a>。',
     [sec('sec1', '三类题型', ''.join(blocks[0:2])),
      sec('sec2', '推理与功能题', ''.join(blocks[2:4]))],
     'single.html', left_nav('single.html'))

# ================= 13 平行阅读 =================
blocks = []
blocks.append(block('Q1', '平行阅读法解决什么问题？',
  None, '提示：时间与题型穿插。',
  '让一篇文章内的多种题型同步推进，避免来回翻文章浪费时间',
  '先扫题型标出各区段，边读边做，读一遍解决多类题。'))
blocks.append(block('Q2', '平行阅读第一步"切"是什么？',
  None, '提示：切什么。',
  '用题目标出各题型对应段落（切分文章）',
  '扫各题型关键词，把它们标到文章对应段落；知道哪段归哪个题型。'))
blocks.append(block('Q3', '第二步"读"的执行顺序？',
  None, '提示：先细节后什么。',
  '一段一停，先细节题后信息题；无 NB 时一段命中一题即跳',
  '读一段就做该段的细节题；信息匹配类无 NB 时一段只选一题，命中就停。'))
blocks.append(block('Q4', '哪些"该停就停"？',
  None, '提示：别过度读。',
  '无 NB 的信息匹配题，一段命中一题后停；不读剩余无关内容',
  '找不到信息也别硬读一整段，时间留给别的题型。'))
blocks.append(block('Q5', '剑 16 冰川文物真题：信息题 19（考古学家压力大）来自哪段？',
  None, '提示：under pressure。',
  'B 段',
  '冰川收缩 → 考古学家 under pressure → work quickly，对应 B 段 "race the clock"。'))

page('雅思阅读第13讲 平行阅读法（考点自测）',
     '平行阅读是高效做题的核心方法论，练"切 → 读 → 停"。做错返回 <a href="../qa-13.html">问答精要</a>。',
     [sec('sec1', '方法与切读', ''.join(blocks[0:2])),
      sec('sec2', '停读时机与真题', ''.join(blocks[2:5]))],
     'parallel.html', left_nav('parallel.html'))

# ================= index =================
index = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="alternate icon" type="image/x-icon" href="../../favicon.ico">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>阅读考点自测 · 雅思阅读13讲配套练习</title>
<style>
  * { box-sizing: border-box; }
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
  .col-main { flex: 1; min-width: 0; padding: 40px 56px 80px; max-width: 820px; margin: 0 auto; }
  .col-main h1 { font-size: 32px; margin-top: 0; border-bottom: 1px solid #e5e7eb; padding-bottom: 12px; line-height: 1.3; }
  .col-main p { line-height: 1.75; color: #374151; }
  .cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 24px; }
  .card { display: block; border: 1px solid #e5e7eb; border-radius: 10px; padding: 18px 20px; transition: all .15s; }
  .card:hover { border-color: #2c5cdc; box-shadow: 0 6px 20px rgba(44,92,220,.08); text-decoration: none; }
  .card h3 { margin: 0 0 6px; font-size: 17px; color: #111; }
  .card p { margin: 0; color: #6b7280; font-size: 13.5px; line-height: 1.6; }
  .card .tag { display: inline-block; margin-top: 12px; font-size: 12px; color: #2c5cdc; font-weight: 600; }
  .tip { background: #f8fafc; border-left: 3px solid #2c5cdc; border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 18px 0; color: #374151; font-size: 14px; line-height: 1.7; }
  .col-right { width: 220px; flex-shrink: 0; border-left: 1px solid #e5e7eb; padding: 24px 18px; font-size: 13px; height: calc(100vh - 56px); position: sticky; top: 56px; overflow-y: auto; }
  .col-right h4 { font-size: 11px; text-transform: uppercase; color: #6b7280; margin: 0 0 12px; letter-spacing: 0.5px; font-weight: 600; }
  .col-right p { color: #6b7280; line-height: 1.6; }
  .col-right .empty { color: #9ca3af; font-size: 12px; padding: 6px 0; }
  @media (max-width: 1100px) { .col-right { display: none; } }
  @media (max-width: 800px) { .col-left { display: none; } .col-main { padding: 24px; } .cards { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<header class="topbar">
  <div class="logo">阅读考点自测<span> · 雅思阅读13讲配套</span></div>
  <div class="topbar-right">
    <a href="../../index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">首页</a>
    <a href="../qa-index.html" style="font-size:13px;color:#2c5cdc;font-weight:600;white-space:nowrap;">课程目录</a>
    <input id="search-input" placeholder="搜索 Ctrl K" autocomplete="off">
    <div id="search-panel"></div>
  </div>
</header>
<div class="layout">
  <aside class="col-left">
    <h3>自测板块</h3>
    <ul>
      <li><a href="fill.html">第02讲 填空：表格/笔记填空</a></li>
      <li><a href="tfng.html">第03/10讲 判断 TFNG vs YNNG</a></li>
      <li><a href="sentence.html">第04讲 句子填空 + 简答</a></li>
      <li><a href="flow.html">第05讲 流程图/图形填空</a></li>
      <li><a href="summary.html">第06讲 总结填空</a></li>
      <li><a href="person.html">第07讲 人物观点配对</a></li>
      <li><a href="ending.html">第08讲 句子结尾配对</a></li>
      <li><a href="info.html">第09讲 信息匹配</a></li>
      <li><a href="multi.html">第11讲 多选题</a></li>
      <li><a href="single.html">第12讲 单选题</a></li>
      <li><a href="parallel.html">第13讲 平行阅读法</a></li>
    </ul>
    <h3>返回</h3>
    <ul>
      <li><a class="back" href="../qa-index.html">返回课程目录</a></li>
      <li><a class="back" href="../../index.html">返回首页</a></li>
    </ul>
  </aside>
  <main class="col-main">
    <h1>阅读考点自测</h1>
    <p>把 13 讲里每个核心考点拆成自测题。做题时先自己想答案，再展开「显示答案 + 考点」对照；做错的返回对应 <a href="../qa-index.html" style="color:#2c5cdc;">问答精要</a> 复习。</p>
    <div class="tip">使用方法：先独立做题，再对答案，不会的回去翻问答精要。每个板块末尾都有一题检验是否掌握对应方法。</div>
    <div class="cards">
      <a class="card" href="fill.html"><h3>填空：表格/笔记填空</h3><p>四大原则（顺序/原文原词/速度/考点）、五大考点、读题预测词性。</p><span class="tag">进入自测</span></a>
      <a class="card" href="tfng.html"><h3>判断 TFNG vs YNNG</h3><p>三分法、唯一考点、六大考点（绝对词）、三步法。</p><span class="tag">进入自测</span></a>
      <a class="card" href="sentence.html"><h3>句子填空 + 简答题</h3><p>词数上限、定位专用词、飘着读、立即/最终限定词同替。</p><span class="tag">进入自测</span></a>
      <a class="card" href="flow.html"><h3>流程图/图形填空</h3><p>位置固定性价比高、不拘一格定位、动词线索、两词取舍。</p><span class="tag">进入自测</span></a>
      <a class="card" href="summary.html"><h3>总结填空</h3><p>顺序 + 小乱序、总结段落取材、题干小句↔原文长句同替。</p><span class="tag">进入自测</span></a>
      <a class="card" href="person.html"><h3>人物观点配对</h3><p>人物按出现顺序、三步法、选项平均分配、Stella 验证法。</p><span class="tag">进入自测</span></a>
      <a class="card" href="ending.html"><h3>句子结尾配对</h3><p>题干半句 + 结尾选项、三步法、替换三层级、防过度揣测。</p><span class="tag">进入自测</span></a>
      <a class="card" href="info.html"><h3>信息匹配</h3><p>五题策略、功能词、同词≠同段、NB 重复使用。</p><span class="tag">进入自测</span></a>
      <a class="card" href="multi.html"><h3>多选题</h3><p>分散型/密集型、平行阅读顺带做、选项与原文相反排除。</p><span class="tag">进入自测</span></a>
      <a class="card" href="single.html"><h3>单选题</h3><p>细节/推理/功能三类、短推理链、功能题放最后。</p><span class="tag">进入自测</span></a>
      <a class="card" href="parallel.html"><h3>平行阅读法</h3><p>切（题型分段落）→ 读（一段一停）→ 停（无 NB 命中即跳）。</p><span class="tag">进入自测</span></a>
    </div>
  </main>
  <aside class="col-right">
    <h4>说明</h4>
    <p class="empty">自测题按 13 讲顺序组织，覆盖老师强调的全部核心考点。做错的题建议返回问答精要对应讲复习。</p>
  </aside>
</div>
<script>
(function(){
  var input = document.getElementById('search-input');
  var panel = document.getElementById('search-panel');
  if (!input || !panel) return;
  var main = document.querySelector('.col-main');
  var leftLinks = Array.prototype.slice.call(document.querySelectorAll('.col-left ul li a'));
  function escHtml(s){ return s.replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function escapeRegex(s){ return s.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'); }
  function clearHighlights(){ if (!main) return; var marks = main.querySelectorAll('mark.search-hl'); for (var i=0;i<marks.length;i++){ var m=marks[i]; var t=document.createTextNode(m.textContent); m.parentNode.replaceChild(t,m); } main.normalize(); }
  function highlightInMain(kw){
    if (!main) return; clearHighlights(); if (!kw) return;
    var re = new RegExp(escapeRegex(kw), 'gi');
    var walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, { acceptNode: function(n){
      if (!n.nodeValue || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      var p = n.parentElement; if (!p) return NodeFilter.FILTER_REJECT;
      var tag = p.tagName; if (tag==='SCRIPT'||tag==='STYLE'||tag==='CODE'||tag==='PRE') return NodeFilter.FILTER_REJECT;
      if (p.closest && p.closest('mark.search-hl')) return NodeFilter.FILTER_REJECT;
      return n.nodeValue.toLowerCase().indexOf(kw.toLowerCase())>=0 ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    }});
    var nodes=[]; var n; while((n=walker.nextNode())) nodes.push(n);
    for (var i=0;i<nodes.length;i++){ var node=nodes[i]; var src=node.nodeValue; var re2=new RegExp(escapeRegex(kw),'gi'); var out=''; var last=0; var m;
      while((m=re2.exec(src))!==null){ out+=escHtml(src.slice(last,m.index)); out+='<mark class="search-hl">'+escHtml(m[0])+'</mark>'; last=m.index+m[0].length; if(m[0].length===0) re2.lastIndex++; }
      out+=escHtml(src.slice(last)); var tmp=document.createElement('span'); tmp.innerHTML=out; var parent=node.parentNode;
      while(tmp.firstChild) parent.insertBefore(tmp.firstChild,node); parent.removeChild(node);
    }
  }
  function search(q){
    q=(q||'').trim(); panel.innerHTML='';
    if(!q){ panel.className=''; leftLinks.forEach(function(a){ a.parentElement.style.display=''; }); clearHighlights(); return; }
    var qLower=q.toLowerCase();
    var hits=leftLinks.filter(function(a){ return a.textContent.toLowerCase().indexOf(qLower)>=0; });
    leftLinks.forEach(function(a){ a.parentElement.style.display = hits.indexOf(a)>=0 ? '' : 'none'; });
    var parts=[];
    if(hits.length){ parts.push('<div class="sp-group">板块（'+hits.length+'）</div>'); parts.push('<ul>'+hits.map(function(a){ return '<li><a href="'+a.getAttribute('href')+'">'+escHtml(a.textContent)+'</a></li>'; }).join('')+'</ul>'); }
    if(!parts.length) parts.push('<div class="sp-empty">无匹配结果</div>');
    panel.innerHTML=parts.join(''); panel.className='show'; highlightInMain(q);
  }
  var timer=null;
  input.addEventListener('input', function(e){ clearTimeout(timer); timer=setTimeout(function(){ search(input.value); },80); });
  input.addEventListener('keydown', function(e){ if(e.key==='Escape'){ input.value=''; search(''); input.blur(); } });
  document.addEventListener('click', function(e){ if(panel.contains(e.target)||e.target===input) return; panel.className=''; });
  panel.addEventListener('click', function(e){ var a=e.target.closest('a'); if(a) panel.className=''; });
  document.addEventListener('keydown', function(e){ if((e.ctrlKey||e.metaKey)&&(e.key==='k'||e.key==='K')){ e.preventDefault(); input.focus(); input.select(); } });
})();
</script>
</body>
</html>"""
with io.open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(index)

print("generated:", sorted(os.listdir(OUT)))