---
name: humanize
description: Edit, audit, or draft writing so it reads like a specific person wrote it, removing recognizable AI phrasing and structural habits while keeping the writer's meaning and voice. Use when the user asks to humanize text, remove AI slop, make copy sound natural or less robotic, check whether a draft "sounds like AI", or invokes humanize.
metadata:
  short-description: Make AI-assisted writing sound like a real person
  version: "1.0.0"
---

# Humanize

Your job is to make writing sound like one particular person with something real to say. Strip out the canned moves that make AI-assisted text interchangeable, and do it without sanding the writer's voice into generic, polished prose.

The user's instructions win over anything in this skill. Respect the tone, format, length, and stylistic choices they ask for.

## Pick the mode

**Edit (default).** The user hands you a draft. Make the smallest set of changes that fixes it. Return the full edited draft, then a short **What changed** list. If they ask for "clean copy only", skip the list.

**Audit.** The user asks you to audit, scan, flag, check, or "is this AI?". Do not rewrite. For each problem, give the pattern name, the shortest quote that shows it, and a fix in a few words. Do not score the text and do not guess who or what wrote it. Detectors guess; named patterns are evidence the user can verify. If nothing on the list appears, say so. Never pad an audit to look thorough. Offer to edit afterward.

**Draft.** The user asks for new writing (a post, email, summary, page). Apply the same rules from the start. Match any voice sample, voice profile, or source notes they give you. Never invent facts, numbers, quotes, experiences, or opinions.

## Before you touch anything

1. Read [references/patterns.md](references/patterns.md), the full pattern library.
2. If the user gave you a voice profile or writing samples, or a `voice-profile.md` (made by the `voice-profile` skill) sits in the working folder, read it. The profile overrides the defaults in this skill where they conflict. If there is no profile, infer the voice from the draft itself.
3. Check [references/contexts.md](references/contexts.md) for the genre at hand (email, LinkedIn, technical doc, executive summary, resume, web copy). Genre changes what counts as a problem.
4. Read the whole draft before editing. Pin down:
   - the one thing the reader should understand, believe, or do afterward
   - the voice: vocabulary, sentence length, bluntness, humor, hedging, contractions, level of polish
   - the details that must survive: names, numbers, dates, examples, mechanisms, opinions

If there is no draft, ask for it. If audience or format is unclear and the answer would change the result, ask one short question: who reads this, and where? Otherwise proceed.

When a draft is long or you want a quick first pass, run the bundled scanner (in this skill's `scripts/` folder) if you can execute code:

```sh
python <skill-dir>/scripts/scan.py path/to/draft.md      # or pipe text on stdin
```

It flags phrase-level and structural patterns with line numbers. Treat its output as leads, not verdicts. It cannot judge voice or context, and it misses rephrased variants.

## How to edit

- **Keep the meaning.** Do not add claims, and do not make the writer sound surer than the source.
- **Keep the voice.** Distinctive words, humor, bluntness, admissions, fragments, tangents, and rough edges stay when they look deliberate.
- **Smallest effective edit.** Fix the slop, errors, repetition, and tangles. Leave strong sentences alone, even if they are not how you would write them. The writer should recognize the result as theirs.
- **Get to the point.** Cut generic warm-up. Keep a personal aside or story when it adds context, tension, or character.
- **Concrete beats abstract.** Names, numbers, dates, mechanisms, and examples beat words like "efficiency", "impact", and "value". If the draft has the specific fact, surface it. If it does not, do not make one up. Flag it.
- **Portability test.** If a sentence could be pasted unchanged into a piece about a different company, product, or person, it is filler. Cut it or tie it to this subject.
- **Show, do not label.** Let facts and consequences carry the weight. Delete commentary that tells the reader something is important, surprising, or obvious.
- **Plain verbs, active voice.** "Decided", not "made a decision". "Can", not "has the ability to". "Is", not "serves as", when "is" is clearer. People do things; abstractions do not "emerge" or "drive".
- **Repeat the right word.** If it is the agent, keep calling it the agent. Do not rotate synonyms for variety.
- **Untangle without flattening.** Split sentences that are genuinely hard to follow. Keep long spoken sentences, fragments, and shifts in pace when they are clear and sound like the writer.
- **Structure stays unless it hurts.** If you reorganize, say why in **What changed**.
- **Punctuation.** No em dashes by default (use a period, comma, colon, or parentheses). No emojis unless asked for or native to the voice.

## Finish

Run the final check in [references/checklist.md](references/checklist.md) against your output. Fix every failure, then check again.

Check shapes, not just words. Rewording "It's not X, it's Y" into "X isn't the point; Y is" leaves the same move in place. Rewrite the underlying thought as a direct claim.

Output format:

- **Edit:** the full edited draft, then **What changed** (3 to 7 bullets, each naming the pattern and the fix). Mention anything you flagged but could not fix, such as a claim that needs a source.
- **Audit:** a list of findings (pattern, quote, fix), then one line offering to edit.
- **Draft:** the draft only, unless the user asked for notes.
