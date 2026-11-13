#!/usr/bin/env python3
"""Flag common AI-writing patterns in a text file or stdin.

Usage:
    python scan.py draft.md
    cat draft.md | python scan.py
    python scan.py draft.md --json
    python scan.py draft.md --fail-on 1     # exit 1 if 1+ findings (for CI)

Standard library only. Findings are leads for a human or model editor,
not verdicts: the scanner cannot judge voice, genre, or intent, and it
misses patterns that have been reworded.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict

# --------------------------------------------------------------------------
# Rules: (pattern id, label, regex). Pattern ids match references/patterns.md.
# --------------------------------------------------------------------------

def _words(*phrases: str) -> str:
    return r"\b(?:" + "|".join(phrases) + r")\b"


PHRASE_RULES: list[tuple[str, str, str]] = [
    ("A1", "secret-insight framing", _words(
        r"what nobody tells you", r"nobody(?:'s| is) talking about", r"no one(?:'s| is) talking about",
        r"(?:the )?part (?:most|everyone|nobody) (?:people )?(?:miss(?:es)?|skip|gets? wrong)",
        r"what (?:most|everyone) (?:people )?gets? wrong", r"here'?s what (?:most|everyone|nobody)",
    )),
    ("A2", "tee-up / announcement", _words(
        r"here'?s the kicker", r"here'?s where it gets (?:interesting|crazy|wild)",
        r"here'?s the part that", r"here'?s what i mean", r"which brings me to",
        r"let me explain", r"let me zoom out", r"i want to be (?:specific|precise|clear)",
    )),
    ("A3", "throat-clearing / staged candor", _words(
        r"here'?s the thing", r"let me be clear", r"i'?ll be honest", r"let'?s be real",
        r"the uncomfortable truth", r"picture this", r"imagine a world",
    ) + r"|(?m:^\s*honestly\?)"),
    ("A4", "generic scene-setting", _words(
        r"in today'?s (?:fast-paced |rapidly changing |digital )*(?:world|landscape|era|age)",
        r"as ai continues to", r"in an era of", r"in the age of", r"whether you'?re an? .{3,40}? or an?",
    )),
    ("A5", "assistant residue", _words(
        r"great question", r"i hope this helps", r"as an ai(?: language model)?",
        r"let me know if you(?:'d| would) like", r"here(?:'s| is) a comprehensive",
        r"certainly!", r"absolutely!",
    )),
    ("C1", "importance label", _words(
        r"pivotal moment", r"stands? as a testament", r"a testament to", r"plays? a (?:crucial|vital|key|pivotal) role",
        r"this distinction matters", r"the key takeaway", r"matters more than (?:it sounds|you(?:'d)? think)",
        r"solidif(?:y|ies) its position",
    )),
    ("C2", "hollow -ing analysis", r"(?:,|\u2014|\u2013| -)\s*(?:highlighting|underscoring|reflecting|showcasing|emphasizing|demonstrating)\s+(?:the|its|their|a|an|how)\b"),
    ("C3", "reaction narration", _words(
        r"let that sink in", r"read that again", r"that'?s unheard of", r"that just doesn'?t happen",
        r"that'?s the whole (?:game|move|thing)", r"and that'?s when it clicked",
    )),
    ("C4", "vague authority", _words(
        r"experts (?:agree|say|believe)", r"studies (?:show|suggest|have shown)", r"research shows",
        r"industry reports (?:suggest|show)", r"it'?s widely (?:recognized|known|accepted)", r"widely regarded as",
        r"many (?:argue|believe|say)",
    )),
    ("C5", "hedge stacking", _words(
        r"(?:may|might|could) potentially", r"could arguably", r"somewhat (?:arguably|potentially)",
    )),
    ("C6", "sales / transformation language", _words(
        r"unlock (?:your|the) (?:full )?potential", r"supercharge", r"take (?:your|it) .{0,20}?to the next level",
        r"unleash", r"end-to-end solution",
    )),
    ("D1", "stock AI vocabulary", _words(
        r"delv(?:e|es|ed|ing)", r"tapestry", r"realm", r"beacon", r"testament", r"paramount",
        r"multifaceted", r"meticulous(?:ly)?", r"intricate", r"transformative", r"revolutionary",
        r"game[- ]changer", r"paradigm shift", r"cutting[- ]edge", r"ever[- ]evolving", r"seamless(?:ly)?",
        r"holistic", r"synerg(?:y|ies)", r"leverag(?:e|es|ed|ing)", r"utiliz(?:e|es|ed|ing)",
        r"facilitat(?:e|es|ed|ing)", r"foster(?:s|ed|ing)?", r"empower(?:s|ed|ing)?", r"streamlin(?:e|es|ed|ing)",
        r"elevat(?:e|es|ed|ing)", r"embark(?:s|ed|ing)?", r"harness(?:es|ed|ing)?", r"spearhead(?:s|ed|ing)?",
        r"bolster(?:s|ed|ing)?", r"move the needle", r"deep dive", r"dive deep",
        r"this changes everything", r"this is huge",
    )),
    ("D2", "filler phrase", _words(
        r"it'?s worth noting", r"it'?s important to note", r"needless to say", r"at the end of the day",
        r"when it comes to", r"at its core", r"the reality is", r"the truth is", r"the fact of the matter",
        r"in terms of", r"with regard to", r"in order to", r"due to the fact that", r"going forward",
        r"moving forward", r"in this article", r"let'?s dive in", r"let'?s explore", r"without further ado",
    )),
    ("D4", "inflated verb", _words(
        r"serves as", r"acts as a", r"functions as", r"has the ability to", r"made a decision",
        r"conducted an analysis",
    )),
    ("E2", "recap ending", r"(?m:^\s*(?:in conclusion|to sum up|in summary|ultimately|overall),)"),
    ("E3", "engagement bait", _words(
        r"what do you think\?", r"drop a comment", r"agree or disagree\?", r"follow for more",
        r"let me know in the comments",
    )),
]

STRUCTURE_RULES: list[tuple[str, str, str]] = [
    # "It's not X. It's Y." / "It's not X, it's Y." / "isn't X, it's Y"
    ("B1", "binary reframe",
     r"\b(?:it|this|that)(?:'s| is)? ?(?:not|n't|isn'?t)\s+(?:just\s+|about\s+)?[^.!?\n]{1,60}?[.,;]\s*(?:it|this|that)(?:'s| is)\b"),
    ("B1", "binary reframe",
     r"\bthe (?:question|problem|issue|point) (?:isn'?t|is not)\b[^.!?\n]{1,60}?[.,;]\s*(?:it'?s|it is)\b"),
    ("B1", "binary reframe",
     r"\byou don'?t have an? [^.!?\n]{1,40}? problem\b"),
    # "Not a X. Not a Y." / "No X. No Y."
    ("B2", "negative stack", r"(?m:(?:^|(?<=[.!?] ))(?:Not|No) [^.!?\n]{1,40}[.,] +(?:Not|No) [^.!?\n]{1,40}[.,])"),
    ("B2", "negative stack", r"\bNo [^.!?\n]{1,30}\. No [^.!?\n]{1,30}\. Just\b"),
    # "The result? Pipeline doubled."
    ("B3", "fake question-and-answer", r"(?m:(?:^|(?<=[.!] ))(?:The|Our|My|Your|And the) [A-Za-z ]{1,30}\? +[A-Z][^.?!\n]{0,80}[.!])"),
    ("B3", "fake question-and-answer", _words(r"what if i told you", r"think about it:", r"plot twist:")),
    # "The best part: it learns."
    ("B4", "colon reveal", r"(?m:(?:^|(?<=[.!?] ))(?:The|My|Our|Your) [a-z][a-z ]{1,30}: [a-z][^.\n]{1,60}\.)"),
    # "That's it. That's the whole thing."
    ("B5", "dramatic fragment stack", r"(?m:(?:^|(?<=[.!?] ))(?:[A-Z][\w']*(?: [\w']+){0,3}[.!](?: +|$)){3,})"),
    ("B9", "range construction", r"\bfrom (?:startups|strategy|small businesses|beginners|ideation|concept) to (?:enterprises?|execution|large|experts|launch|reality)\b"),
    ("E1", "fake-profound kicker", _words(r"the future (?:isn'?t|is not) coming", r"is the new oil", r"in the end, it'?s all about")),
]


@dataclass
class Finding:
    line: int
    pattern: str
    label: str
    excerpt: str


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _excerpt(match_text: str, limit: int = 90) -> str:
    s = " ".join(match_text.split())
    return s if len(s) <= limit else s[: limit - 1] + "…"


def _strip_code(text: str) -> str:
    """Blank out fenced and inline code so identifiers aren't flagged. Keeps line numbers."""
    def blank(m: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"```.*?```", blank, text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", blank, text)
    return text


def scan(text: str) -> list[Finding]:
    clean = _strip_code(text)
    findings: list[Finding] = []
    seen: set[tuple[int, str, str]] = set()

    for pid, label, rx in PHRASE_RULES + STRUCTURE_RULES:
        flags = re.IGNORECASE if pid not in {"B2", "B3", "B4"} else 0
        for m in re.finditer(rx, clean, flags):
            line = _line_of(clean, m.start())
            ex = _excerpt(text[m.start(): m.end()])
            key = (line, pid, "" if pid.startswith("B") else ex.lower())
            if key in seen:
                continue
            seen.add(key)
            findings.append(Finding(line, pid, label, ex))

    # Formatting checks
    for i, raw in enumerate(clean.splitlines(), start=1):
        dashes = raw.count("—") + len(re.findall(r"\s--\s", raw))
        if dashes:
            findings.append(Finding(i, "F", "em dash", f"{dashes} em dash(es)"))
        if re.match(r"^\s*#{1,6}\s.*[\U0001F300-\U0001FAFF☀-➿]", raw):
            findings.append(Finding(i, "F", "emoji in heading", _excerpt(raw)))
        bolds = re.findall(r"(?<!^)(?<![-*] )\*\*[^*\n]+\*\*", raw.strip())
        if len(bolds) >= 2:
            findings.append(Finding(i, "F", "decorative bold", f"{len(bolds)} bold spans in one line"))

    findings.sort(key=lambda f: (f.line, f.pattern))
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", nargs="?", help="text or markdown file (default: stdin)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--fail-on", type=int, default=0, metavar="N",
                    help="exit with status 1 when there are N or more findings (0 = never)")
    args = ap.parse_args(argv)

    # Windows consoles often default to a legacy code page; never crash on emoji.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")

    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = sys.stdin.read()

    findings = scan(text)

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2, ensure_ascii=False))
    elif not findings:
        print("No listed patterns found. That is not proof the text is clean; read it.")
    else:
        width = len(str(findings[-1].line))
        for f in findings:
            print(f"L{f.line:<{width}}  {f.pattern:<3} {f.label:<30} {f.excerpt}")
        counts: dict[str, int] = {}
        for f in findings:
            counts[f.label] = counts.get(f.label, 0) + 1
        summary = ", ".join(f"{k} x{v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
        print(f"\n{len(findings)} finding(s): {summary}")

    return 1 if args.fail_on and len(findings) >= args.fail_on else 0


if __name__ == "__main__":
    sys.exit(main())
