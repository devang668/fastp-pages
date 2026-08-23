import os, re, json
from collections import defaultdict

WT = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich"
MAPFILE = os.path.join(WT, "jin-jiancheng", "jinjiancheng_articles_map.json")
with open(MAPFILE, encoding="utf-8") as f:
    master = json.load(f)
master_titles=[e.get("title","").strip() for e in master]

nomatch = [
"在底层互掐中产内卷富人联姻现象非常普遍的时代我很佩服两种人穷不丧志富不躺平但这不意味.html",
"币圈又是血流成河的惨烈走势大饼跌至94万美元支撑位二饼跌至3050美元最大的平台饼跌至9.html",
"我又阳了这段时间更新不确定知会一声不过现这波症状小了很多大家做好防护产业助农项目也走过了4.html",
"昨晚八点买了大饼BTC的多头加了杠杆这种没办法得随时盯着看情况随时决定要不要抛所以今天.html",
"最近一期的广子应读者要求那期保险收益我还是和过往一样都捐赠给腾讯公益中那些更需要的人.html",
"美股暴跌纳指下跌229标普500下跌166科技股领跌伯克希尔和强生这类避险股上涨礼.html",
"美股继续上涨强势得一塌糊涂n随着这段时间个股的涨跌不同我持仓的情况有些变化最大的账户进取.html",
"过去20小时对币圈的有些人来说堪称煎熬惊魂USDX暴雷事发突然投资者只能连夜抢着赎回能.html",
"这些天筹备去欧洲旅行的事基本上不会有更新新来的读者可以看看历史文章我做了一些集合比如投资心.html",
]

for f in nomatch:
    base=os.path.splitext(f)[0]
    # candidate prefixes: before first 'nn' or single 'n' run, also try a few cut points
    prefixes=[]
    m=re.search(r"nn", base)
    if m: prefixes.append(base[:m.start()])
    # single n boundaries (look for ' n' or 'n ' or just first lone n)
    for cut in [p for p in range(1,len(base)) if base[p]=="n" and base[p-1]!="n"]:
        prefixes.append(base[:cut])
    prefixes = list(dict.fromkeys(prefixes))
    hits=[]
    for pre in prefixes:
        for t in master_titles:
            if t.startswith(pre) or pre.startswith(t):
                hits.append(t)
        if hits: break
    print(f"\n* {base[:38]}...")
    if hits:
        for h in hits[:3]: print(f"   HIT: {h}")
    else:
        print("   NO HIT in master map")
