# -*- coding: utf-8 -*-
"""Safety guard for the VIP subject index pages.

These index pages are HAND-MAINTAINED (their grid-card descriptions,
intro/CTA copy, and right-column nav are hand-written editorial content
that is NOT derivable from the *_lessons.py LESSON_META tables — the
card blurbs mix title-fragments and trimmed descriptions with no single
rule). An earlier version of this script generated PLACEHOLDER versions
of these pages ("板块待更新" + generic "第NN讲 · 问答精要" sidebars).
Running that version now would CLOBBER the hand-maintained rich pages
and lose that editorial content.

So this script is now a NO-OVERWRITE safety valve: if a target index
page already exists, it is left untouched and a SKIP message is
printed. Nothing is destroyed by re-running this script.

To change an index page, edit the .html directly. The descriptive
sidebar titles are kept in sync with _gen_{wrt,tli,speaking}_lessons.py
LESSON_META by the patch step that already ran; if you rename a lesson
there, also update the matching index page's sidebar by hand (or re-run
the patch script that lives in the conversation that produced it).
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# (relative_path, what it is) — every one is hand-maintained.
TARGETS = [
    ("writing/writing-index.html", "redirect -> writing-lessons-index.html"),
    ("writing/writing-lessons-index.html", "writing lessons grid (17 讲)"),
    ("writing/writing-qa-index.html", "writing QA grid (17 讲)"),
    ("tli/tli-index.html", "listening landing + lesson/QA grids (20 讲)"),
    ("speaking/speaking-index.html", "speaking landing (16 讲)"),
    ("yuedu/yuedu-index.html", "reading landing"),
]

def main():
    skipped = 0
    missing = 0
    for rel, what in TARGETS:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            print("SKIP (hand-maintained, left untouched): %s  [%s]" % (rel, what))
            skipped += 1
        else:
            print("MISSING (not auto-created — hand-maintained, no template): %s" % rel)
            missing += 1
    print("---")
    print("skipped %d, missing %d. No files were written or overwritten." % (skipped, missing))
    print("These index pages are hand-maintained; edit the .html files directly.")

if __name__ == "__main__":
    main()
