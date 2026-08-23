import os, re, json
from collections import defaultdict

MD = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich/公众号/_md"

themes = {
    "人生哲学": ["人生", "哲学", "心态", "认知", "修行", "命运", "内心", "快乐", "意义", "自由", "定力", "境界", "孤独", "生死", "欲望", "贪", "执", "孤独", "平静", "专注"],
    "财富理解": ["财富", "搞钱", "富有", "资产", "复利", "睡后收入", "财商", "钱", "被动收入", "现金流", "本金", "杠杆", "通胀", "保值", "阶级", "阶层", "阶层跃迁"],
    "股票交易": ["股票", "交易", "持仓", "减仓", "加仓", "纳指", "标普", "止损", "抄底", "投资", "个股", "伯克希尔", "巴菲特", "估值", "仓位", "建仓", "清仓", "期权", "账户", "盈亏", "回撤", "分散", "集中", "美股", "A股", "大饼", "黄金", "买入", "卖出"],
    "预期与验证": ["预期", "验证", "判断", "预测", "兑现", "如我所料", "如期", "出乎", "打脸", "复盘", "总结", "当时说", "此前", "早就", "提醒", "应验", "证伪", "预判", "没想到", "正如"],
}

files = sorted([f for f in os.listdir(MD) if f.lower().endswith(".md") and os.path.isfile(os.path.join(MD, f))])
data = {}
for f in files:
    text = open(os.path.join(MD, f), encoding="utf-8", errors="ignore").read()
    dm = re.match(r"^(\d{4}-\d{2}-\d{2})[_ ](.*)$", os.path.splitext(f)[0])
    data[f] = {"date": dm.group(1) if dm else "", "title": dm.group(2) if dm else os.path.splitext(f)[0], "text": text}

def theme_rank(th):
    scored = []
    for f, d in data.items():
        c = sum(d["text"].count(kw) for kw in themes[th])
        if c > 0:
            scored.append((c, f))
    scored.sort(reverse=True)
    return scored

def paragraphs(text):
    # split on blank lines, keep non-trivial
    ps = re.split(r"\n\s*\n", text)
    out = []
    for p in ps:
        p = p.strip()
        p = re.sub(r"\s+", " ", p)
        if len(p) >= 20:
            out.append(p)
    return out

digest = {}
for th, kws in themes.items():
    ranked = theme_rank(th)[:8]
    digest[th] = []
    for score, f in ranked:
        d = data[f]
        paras = paragraphs(d["text"])
        # rank paragraphs by number of theme kw hits
        ranked_paras = []
        for p in paras:
            c = sum(p.count(kw) for kw in kws)
            if c > 0:
                ranked_paras.append((c, p))
        ranked_paras.sort(reverse=True)
        top = [p for c, p in ranked_paras[:8]]
        digest[th].append({"file": f, "date": d["date"], "title": d["title"], "score": score, "paras": top})

# write digest to file
with open(os.path.join(os.path.dirname(MD), "..", "theme_digest.txt"), "w", encoding="utf-8") as fp:
    for th in themes:
        fp.write(f"\n\n########## 主题：{th} ##########\n")
        for item in digest[th]:
            fp.write(f"\n--- {item['date']}《{item['title']}》 (命中{item['score']}) ---\n")
            for p in item["paras"]:
                fp.write("· " + p[:400] + ("…" if len(p) > 400 else "") + "\n")

print("digest written. sizes by theme:")
for th in themes:
    n = sum(len(i["paras"]) for i in digest[th])
    print(f"  {th}: {n} paragraphs")
