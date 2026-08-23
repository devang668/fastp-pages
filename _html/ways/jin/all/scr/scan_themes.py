import os, re, json
from collections import defaultdict

MD = r"C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich/公众号/_md"

# theme keyword buckets
themes = {
    "life_philosophy": ["人生", "哲学", "心态", "认知", "修行", "命运", "内心", "快乐", "意义", "自由", "道", "定力", "修行", "境界", "孤独", "生死", "欲望", "贪", "执"],
    "wealth": ["财富", "搞钱", "富有", "资产", "复利", "睡后收入", "财商", "钱", "被动收入", "现金流", "本金", "杠杆", "通胀", "保值", "阶级", "阶层"],
    "trading": ["股票", "交易", "持仓", "减仓", "加仓", "纳指", "标普", "止损", "抄底", "投资", "个股", "伯克希尔", "巴菲特", "估值", "仓位", "建仓", "清仓", "期权", "期货", "账户", "盈亏", "回撤", "分散", "集中", "美股", "A股", "大饼", "币", "黄金"],
    "expectation": ["预期", "验证", "判断", "预测", "兑现", "如我所料", "如期", "出乎", "打脸", "复盘", "总结", "当时说", "此前", "早就", "提醒", "应验", "证伪", "预判"],
}

files = sorted([f for f in os.listdir(MD) if f.lower().endswith(".md") and os.path.isfile(os.path.join(MD, f))])

stats = []
for f in files:
    text = open(os.path.join(MD, f), encoding="utf-8", errors="ignore").read()
    chars = len(text)
    base = os.path.splitext(f)[0]
    # match date prefix
    dm = re.match(r"^(\d{4}-\d{2}-\d{2})[_ ](.*)$", base)
    date = dm.group(1) if dm else ""
    title = dm.group(2) if dm else base
    counts = {}
    for th, kws in themes.items():
        c = sum(text.count(kw) for kw in kws)
        counts[th] = c
    total = sum(counts.values())
    stats.append({"file": f, "date": date, "title": title, "chars": chars, "counts": counts, "total": total})

# per-theme ranking
for th in themes:
    ranked = sorted([s for s in stats if s["counts"][th] > 0], key=lambda x: -x["counts"][th])
    print(f"\n===== THEME: {th}  (top 12 by hits) =====")
    for s in ranked[:12]:
        print(f"  {s['counts'][th]:4d}  {s['date']}  {s['title'][:40]}  ({s['chars']}字)")

# global: longest / highest total (most substantive)
print("\n===== TOP 15 by total keyword hits =====")
for s in sorted(stats, key=lambda x: -x["total"])[:15]:
    print(f"  {s['total']:4d}  {s['date']}  {s['title'][:42]}  chars={s['chars']}")

print(f"\nTotal _md files: {len(stats)}")
print(f"Total chars: {sum(s['chars'] for s in stats)}")
