import os, re, json

WT = r'C:/Users/Cheng/Downloads/zsq-ob/raw/08-madao-sun/.claude/worktrees/nifty-stonebraker-d0b96e/raw/books/gzh-jin_rich'
MD = os.path.join(WT, '公众号', '_md')

# collect dated md files
files = []
for f in os.listdir(MD):
    if f.lower().endswith('.md') and os.path.isfile(os.path.join(MD, f)):
        m = re.match(r'^(\d{4}-\d{2}-\d{2})[_\s].*', f)
        if m:
            files.append((m.group(1), f))
files.sort()

# split into sentences (zh)
def sentences(text):
    text = re.sub(r'\s+', ' ', text)
    parts = re.split(r'(?<=[。！？!?；;\n])', text)
    return [p.strip() for p in parts if len(p.strip()) >= 6]

# prediction / operation markers
PRED = ['预判','预测','预感','大概率','认为是','认为会','会涨','会跌','看到','目标位','第一目标','第二目标',
        '防守位','防守点','支撑位','压力位','见顶','见底','触底','抄底','逃顶','减仓','加仓','建仓','买入','卖出',
        '止损','止盈','看多','看空','看平','震荡','突破','跌破','站上','等待','布局','左侧','右侧','逢低','逢高',
        '重仓','轻仓','仓位','机会','风险','顶部','底部','拐点','反转','背离','钝化','背离','背离']
# validation / mea-culpa markers
VALID = ['验证','如期','应验','兑现','果然','正如','如我所料','如预期','判断正确','判断错误','打脸','认错','认输',
         '止损','被套','解套','获利','盈利','亏损','达标','不及预期','超预期','实现了','应验了','对了','错了',
         '打脸','成功','失败','正确','错误','准确','不准确','精准','不精准','蒙对','蒙错','侥幸','失误','反思','总结']

date_re = re.compile(r'\b(1[0-9]{3,4}|[2-9]\d{3,4}|1\d{4}|2\d{4})\b')  # crude number catch
num_re = re.compile(r'\d{3,5}(?:\.\d+)?')  # price/level numbers

pred_out = []
valid_out = []
for date, fn in files:
    path = os.path.join(MD, fn)
    try:
        txt = open(path, encoding='utf-8').read()
    except Exception as e:
        continue
    # skip if it's mostly a reader comment dump? keep all
    for s in sentences(txt):
        has_pred = any(k in s for k in PRED)
        has_valid = any(k in s for k in VALID)
        if has_pred:
            nums = num_re.findall(s)
            pred_out.append({'date': date, 'file': fn, 'sent': s, 'nums': nums})
        elif has_valid:
            nums = num_re.findall(s)
            valid_out.append({'date': date, 'file': fn, 'sent': s, 'nums': nums})

# dedupe near-identical sentences (keep first by sent)
def dedupe(lst):
    seen = set(); out=[]
    for x in lst:
        key = x['sent'][:40]
        if key in seen: continue
        seen.add(key); out.append(x)
    return out

pred_out = dedupe(pred_out)
valid_out = dedupe(valid_out)

with open(os.path.join(WT, 'extract_pred.txt'), 'w', encoding='utf-8') as fp:
    fp.write(f"# 预判/操作陈述抽取 ({len(pred_out)} 条)\n")
    for x in pred_out:
        fp.write(f"[{x['date']}] {x['file']}\n  {x['sent']}\n  nums={x['nums']}\n\n")

with open(os.path.join(WT, 'extract_valid.txt'), 'w', encoding='utf-8') as fp:
    fp.write(f"# 验证/认错陈述抽取 ({len(valid_out)} 条)\n")
    for x in valid_out:
        fp.write(f"[{x['date']}] {x['file']}\n  {x['sent']}\n  nums={x['nums']}\n\n")

print("pred:", len(pred_out), "valid:", len(valid_out))
