# Rebuild VIP speaking QA pages into a visible-table model.
# Parses each existing qa-NN.html (recovering the real Q&A content) and
# re-renders: always-visible "问答速览" table + per-question cards with
# bolded English vocabulary. No content is fabricated; abstract-only
# lessons are kept honest (no fake Q&A).

import re, os, glob

SPEAK = os.path.dirname(os.path.abspath(__file__))

def read(f):
    with open(f, encoding='utf-8') as fh:
        return fh.read()

def decode_entities(t):
    return (t.replace('&quot;', '"').replace('&amp;', '&')
             .replace('&lt;', '<').replace('&gt;', '>')
             .replace('&#39;', "'"))

def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))

def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)

def plain(a):
    return decode_entities(strip_tags(a)).strip()

def bold_vocab(text):
    # text is already HTML-escaped; bold Latin runs (len>=3) not inside tags.
    parts = re.split(r'(<[^>]+>)', text)
    out = []
    for p in parts:
        if p.startswith('<'):
            out.append(p)
        else:
            p = re.sub(r'(?<![\w&])([A-Za-z][A-Za-z' + "'" + r'-]{2,})(?![\w&])',
                       r'<b>\1</b>', p)
            out.append(p)
    return ''.join(out)

def core_answer(a):
    # first sentence, truncated, plain text
    pt = plain(a)
    m = re.split(r'[。！？.!?]', pt)
    first = m[0].strip() if m else pt
    if len(first) > 60:
        first = first[:60] + '…'
    return first

def clean_answer_html(a):
    a = re.sub(r'^<p[^>]*>', '', a)
    a = re.sub(r'</p>\s*$', '', a)
    a = re.sub(r'^(\s*<b>\s*答[:：]\s*</b>\s*|\s*答[:：]\s*)', '', a)
    return a.strip()

def parse_blob_qa(body, q0):
    # format: 发言人 问：Q 发言人答：A 发言人 问：Q2 发言人答：A2 ...
    body = re.sub(r'</?p[^>]*>', '', body)
    body = re.sub(r'<b>\s*答[:：]\s*</b>', '', body)
    text = decode_entities(strip_tags(body)).strip()
    text = re.sub(r'^答[:：]\s*', '', text)
    segs = text.split('发言人 问：')
    a1 = re.sub(r'^答[:：]\s*', '', segs[0]).strip()
    pairs = [(q0, a1)]
    for seg in segs[1:]:
        q, _, a = seg.partition('发言人答：')
        q = q.strip()
        a = a.strip()
        if q or a:
            pairs.append((q, a))
    return pairs

def parse_blob_colon(body, q0):
    # format: A0 Q1 发言人： A1 Q2 发言人： A2 Q3 ... (chained)
    # Every 发言人： follows a question, so treat it as a block separator.
    # After split, block[i] = [A_i + Q_{i+1}]; Q_{i+1} is the LAST sentence
    # (ends with ？/?), A_i is everything before that question.
    body = re.sub(r'</?p[^>]*>', '', body)
    body = re.sub(r'<b>\s*答[:：]\s*</b>', '', body)
    text = decode_entities(strip_tags(body)).strip()
    text = re.sub(r'^答[:：]\s*', '', text)
    if not text:
        return [(q0, '')] if q0 else []
    blocks = text.split('发言人：')
    def split_aq(block):
        # question = last sentence ending in ？/?; answer = text before it
        idx = block.rfind('？')
        if idx < 0:
            idx = block.rfind('?')
        if idx < 0:
            return block.strip(), ''
        # find question start: walk back to the previous sentence boundary.
        # Boundaries include ASCII . ! and Chinese 。！ plus newline, but NOT
        # ?/？ (those mark question ENDS) so consecutive questions still split.
        j = idx
        while j > 0 and block[j - 1] not in '。！.!':
            j -= 1
        a = block[:j].strip()
        q = block[j:idx + 1].strip()
        return a, q
    A, Qn = [], []
    for blk in blocks:
        a, q = split_aq(blk)
        A.append(a)
        Qn.append(q)
    # A[0] answers Q0 (summary); for k>=1, Qn[k-1] (question of block k-1)
    # is answered by A[k] (answer of block k).
    pairs = [(q0, A[0])] if (q0 or A[0]) else []
    for k in range(1, len(A)):
        q = Qn[k - 1]
        a = A[k]
        if q or a:
            pairs.append((q, a))
    return pairs

def trim_qa(s):
    # drop a single stray quote char at either end (from embedded examples)
    s = s.strip()
    for ch in ('"', '\u201c', '\u201d', '\u2018', '\u2019'):
        if s.startswith(ch):
            s = s[1:].strip()
        if s.endswith(ch):
            s = s[:-1].strip()
    return s

def parse_pairs(h):
    details = re.findall(r'<details class="qa">(.*?)</details>', h, re.S)
    if not details:
        return []  # abstract-only lesson, no Q&A
    parsed = []
    for d in details:
        summ = re.search(r'<summary>(.*?)</summary>', d, re.S)
        bm = re.search(r'class="qa-body">(.*)</div>', d, re.S)
        q = plain(summ.group(1)) if summ else ''
        q = re.sub(r'^问[:：]\s*', '', q).strip()
        a = bm.group(1) if bm else ''
        parsed.append((q, a))
    # multi-block: one clean block per question
    if len(parsed) >= 2:
        return [tuple(trim_qa(x) for x in p)
                for p in [(q, clean_answer_html(a)) for q, a in parsed if q or a.strip()]]
    # single block: blob in one of two chained formats
    q0, a0 = parsed[0]
    if not a0.strip():
        return [(trim_qa(q0), '')] if q0 else []
    if '发言人 问' in a0:
        return [(trim_qa(q), trim_qa(a)) for q, a in parse_blob_qa(a0, q0)]
    if '发言人' in a0:
        return [(trim_qa(q), trim_qa(a)) for q, a in parse_blob_colon(a0, q0)]
    return [(trim_qa(q0), trim_qa(clean_answer_html(a0)))]

def parse_file(path):
    h = read(path)
    title = re.search(r'<title>(.*?)</title>', h).group(1)
    h1 = re.search(r'<h1>(.*?)</h1>', h, re.S).group(1)
    abs_m = re.search(r'class="abstract">(.*?)</div>', h, re.S)
    abstract = plain(abs_m.group(1)) if abs_m else ''
    left = re.search(r'(<aside class="col-left">.*?</aside>)', h, re.S).group(1)
    right = re.search(r'(<aside class="col-right">.*?</aside>)', h, re.S).group(1)
    script = re.search(r'(<script>.*?</script>)', h, re.S).group(1)
    head = re.search(r'(<head>.*?</head>)', h, re.S).group(1)
    topbar = re.search(r'(<header class="topbar">.*?</header>)', h, re.S).group(1)
    pairs = parse_pairs(h)
    return dict(title=title, h1=h1, abstract=abstract, left=left,
                right=right, script=script, head=head, topbar=topbar,
                pairs=pairs)

EXTRA_CSS = """
  /* ---- rebuilt QA model ---- */
  .sec-title { font-size: 13px; color: #6b7280; font-weight: 700; letter-spacing: .6px; text-transform: uppercase; margin: 30px 0 8px; }
  .qa-table { width: 100%; border-collapse: collapse; margin: 16px 0 28px; font-size: 13.5px; }
  .qa-table th, .qa-table td { border: 1px solid #e5e7eb; padding: 9px 12px; text-align: left; vertical-align: top; }
  .qa-table th { background: #f5f7fa; color: #374151; font-weight: 700; }
  .qa-table tr:hover td { background: #fafbff; }
  .qa-table td.qnum { color: #1d4ed8; font-weight: 700; white-space: nowrap; width: 44px; text-align: center; }
  .qa-table td.qq { color: #111; }
  .qa-table td.qans { color: #374151; }
  .qcard { border: 1px solid #e5e7eb; border-left: 4px solid #1d4ed8; border-radius: 10px; padding: 14px 18px; margin: 16px 0; background: #fff; }
  .qcard h3 { margin: 0 0 8px; font-size: 16px; color: #111; line-height: 1.5; }
  .qcard h3 .qn { color: #1d4ed8; font-weight: 800; margin-right: 6px; }
  .qcard .a-body { color: #374151; font-size: 14px; line-height: 1.85; }
  .qcard .a-body b { color: #1d4ed8; }
  .qcard .a-body .lab { color: #1d4ed8; font-weight: 700; }
  .ov-note { background: #f5f7fa; border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px 18px; margin: 16px 0; color: #4b5563; font-size: 14px; line-height: 1.8; }
"""

def render_main(d):
    parts = []
    parts.append('<h1>%s</h1>' % d['h1'])
    parts.append('<div class="abstract"><b>本讲概要：</b>%s</div>' % esc(d['abstract']))
    pairs = d['pairs']
    if pairs:
        parts.append('<div class="sec-title">本讲问答速览</div>')
        parts.append('<table class="qa-table"><thead><tr>'
                     '<th style="width:44px;text-align:center;">#</th>'
                     '<th>问题</th><th>核心答案</th></tr></thead><tbody>')
        for i, (q, a) in enumerate(pairs, 1):
            parts.append('<tr><td class="qnum">%d</td>'
                         '<td class="qq">%s</td>'
                         '<td class="qans">%s</td></tr>'
                         % (i, esc(q), esc(core_answer(a))))
        parts.append('</tbody></table>')
        parts.append('<div class="sec-title">逐题详解</div>')
        for i, (q, a) in enumerate(pairs, 1):
            if '<b>' in a:
                abody = a  # keep existing bold terms
            else:
                abody = bold_vocab(esc(plain(a)))
            parts.append('<div class="qcard"><h3><span class="qn">Q%d.</span>%s</h3>'
                         '<div class="a-body"><span class="lab">答：</span>%s</div></div>'
                         % (i, esc(q), abody))
    else:
        parts.append('<div class="ov-note">本讲以精讲逐字稿为主，未单独拆出问答块。'
                     '建议结合左侧「精讲逐字稿」页学习。</div>')
        parts.append('<div class="sec-title">本讲概要</div>')
        parts.append('<div class="ov-note">%s</div>' % esc(d['abstract']))
    return '\n'.join(parts)

def render(d):
    head = d['head'].replace('</style>', EXTRA_CSS + '</style>')
    main = render_main(d)
    return ('<!DOCTYPE html>\n<html lang="zh">\n%s\n<body>\n%s\n'
            '<div class="layout">\n%s\n<main class="col-main">\n%s\n</main>\n%s\n'
            '</div>\n%s\n</body>\n</html>\n'
            % (head, d['topbar'], d['left'], main, d['right'], d['script']))

def main():
    files = sorted(glob.glob(os.path.join(SPEAK, 'qa-*.html')))
    for f in files:
        d = parse_file(f)
        out = render(d)
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(out)
        print('rebuilt', os.path.basename(f),
              '| pairs:', len(d['pairs']),
              '| title:', d['title'][:30])

if __name__ == '__main__':
    main()
