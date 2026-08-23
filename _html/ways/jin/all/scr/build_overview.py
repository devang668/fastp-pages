#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a complete, self-contained overview index (all.html) for the
gzh-jin_rich/all_html article collection.

Reads every *.html in the target dir (excluding all.html / index.html),
parses [prefix]YYYY-MM-DD_title.html, and emits a single local HTML file
with: total count, year grouping, a live title search, and clickable
file:/// links to each article.

Re-run any time to refresh after adding/renaming files.
"""
import os, re, html, urllib.parse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
AH = os.path.join(HERE, "all_html")
OUT = os.path.join(AH, "all.html")

SKIP = {"all.html", "index.html"}

def parse_name(fn):
    base = fn[:-5]
    m = re.match(r'^(金渐成_|_html_)?(.*)$', base)
    prefix = m.group(1) or ""
    rest = m.group(2)
    dm = re.match(r'^(\d{4}-\d{2}-\d{2})_(.*)$', rest)
    if dm:
        return prefix, dm.group(1), dm.group(2)
    return prefix, None, rest

entries = []
for fn in os.listdir(AH):
    if not fn.endswith(".html"):
        continue
    if fn in SKIP:
        continue
    prefix, date, title = parse_name(fn)
    entries.append({
        "file": fn,
        "date": date,
        "title": title,
        "href": urllib.parse.quote(fn),  # safe for file:///
    })

# sort: dated first by date desc, undated at end (by title)
def sort_key(e):
    if e["date"]:
        return (0, e["date"], e["title"])
    return (1, "", e["title"])

entries.sort(key=sort_key, reverse=False)
# for dated we want newest first: reverse the date portion only
entries.sort(key=lambda e: (0 if e["date"] else 1, e["date"] or "", e["title"]), reverse=True)

# group by year
groups = {}
for e in entries:
    if e["date"]:
        y = e["date"][:4]
    else:
        y = "未标注日期"
    groups.setdefault(y, []).append(e)

years = sorted([y for y in groups if y != "未标注日期"], reverse=True)
if "未标注日期" in groups:
    years.append("未标注日期")

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def li(e):
    date_span = '<span class="d">%s</span>' % (e["date"] or "—") if e["date"] else '<span class="d und">无日期</span>'
    return ('<li data-title="%s"><a href="%s">%s<span class="t">%s</span></a></li>'
            % (html.escape(e["title"]), e["href"], date_span, html.escape(e["title"])))

sections = []
for y in years:
    items = groups[y]
    lis = "\n".join(li(e) for e in items)
    sections.append(
        '<section class="yr" data-year="%s">\n'
        '<h2>%s <span class="cnt">%d 篇</span></h2>\n'
        '<ul>\n%s\n</ul>\n</section>' % (html.escape(y), html.escape(y), len(items), lis)
    )

year_buttons = " ".join('<button class="yb" data-y="%s">%s</button>' % (html.escape(y), html.escape(y)) for y in years)

doc = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>金渐成文章总览</title>
<style>
  :root{ --red:#c0392b; --blue:#2980b9; --bg:#fafafa; --fg:#333; --mut:#888; }
  *{box-sizing:border-box;}
  body{font-family:'Microsoft YaHei','PingFang SC',sans-serif;max-width:960px;margin:0 auto;padding:24px 20px 80px;background:var(--bg);color:var(--fg);}
  h1{border-bottom:2px solid var(--red);padding-bottom:10px;font-size:24px;}
  .meta{color:var(--mut);font-size:14px;margin:6px 0 18px;}
  .bar{position:sticky;top:0;background:var(--bg);padding:10px 0;z-index:5;border-bottom:1px solid #eee;}
  #q{width:100%;padding:10px 12px;font-size:15px;border:1px solid #ccc;border-radius:8px;outline:none;}
  #q:focus{border-color:var(--blue);}
  .ybtns{margin-top:10px;display:flex;flex-wrap:wrap;gap:6px;}
  .yb{font-size:13px;padding:4px 10px;border:1px solid #ccc;background:#fff;border-radius:14px;cursor:pointer;color:var(--fg);}
  .yb:hover{border-color:var(--blue);color:var(--blue);}
  .yb.on{background:var(--blue);color:#fff;border-color:var(--blue);}
  h2{color:var(--red);margin-top:28px;border-left:4px solid var(--red);padding-left:10px;font-size:18px;}
  h2 .cnt{color:var(--mut);font-size:13px;font-weight:normal;margin-left:6px;}
  ul{list-style:none;padding:0;columns:2;column-gap:28px;}
  @media(max-width:640px){ ul{columns:1;} }
  li{margin:5px 0;break-inside:avoid;font-size:14px;line-height:1.5;}
  a{color:var(--blue);text-decoration:none;display:block;}
  a:hover{color:var(--red);}
  a:hover .t{text-decoration:underline;}
  .d{display:inline-block;min-width:74px;color:var(--mut);font-size:12px;font-variant-numeric:tabular-nums;}
  .d.und{color:#bbb;}
  .t{margin-left:6px;}
  .empty{color:var(--mut);padding:20px;text-align:center;}
</style>
</head>
<body>
<h1>金渐成 / 公众号文章总览</h1>
<div class="meta">共 <b>__TOTAL__</b> 篇文章 · 生成于 __NOW__ · 点击标题在本地打开</div>
<div class="bar">
  <input id="q" type="text" placeholder="搜索标题…" autofocus>
  <div class="ybtns">__YBTNS__ <button class="yb on" data-y="ALL">全部</button></div>
</div>
__SECTIONS__
<script>
(function(){
  var q=document.getElementById('q');
  var ybs=document.querySelectorAll('.yb');
  var curYear='ALL';
  function apply(){
    var kw=q.value.trim().toLowerCase();
    var secs=document.querySelectorAll('.yr');
    var shownTotal=0;
    secs.forEach(function(sec){
      var year=sec.getAttribute('data-year');
      var showSec = (curYear==='ALL'||curYear===year);
      var lis=sec.querySelectorAll('li');
      var n=0;
      lis.forEach(function(li){
        var t=li.getAttribute('data-title').toLowerCase();
        var ok = showSec && (kw==='' || t.indexOf(kw)>-1);
        li.style.display = ok ? '' : 'none';
        if(ok) n++;
      });
      sec.style.display = (n===0)?'none':'';
      shownTotal+=n;
    });
    var meta=document.querySelector('.meta');
    meta.innerHTML = '当前显示 <b>'+shownTotal+'</b> 篇' + (kw?'（搜索：'+q.value+'）':'') ;
  }
  q.addEventListener('input',apply);
  ybs.forEach(function(b){
    b.addEventListener('click',function(){
      curYear=b.getAttribute('data-y');
      ybs.forEach(function(x){x.classList.remove('on');});
      b.classList.add('on');
      apply();
    });
  });
})();
</script>
</body>
</html>
"""
doc = (doc
       .replace("__TOTAL__", str(len(entries)))
       .replace("__NOW__", now)
       .replace("__YBTNS__", year_buttons)
       .replace("__SECTIONS__", "\n".join(sections)))

with open(OUT, "w", encoding="utf-8") as f:
    f.write(doc)

print("wrote", OUT)
print("total articles:", len(entries))
print("years:", [(y, len(groups[y])) for y in years])
