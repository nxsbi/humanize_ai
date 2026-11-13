---
name: voice-profile
description: Build a reusable written-voice profile from samples of someone's own writing. Later edits and drafts then sound like them instead of generic AI prose. Use when the user wants Claude to "learn my voice", "write like me", or capture a house style. Also use to create or update a voice-profile.md for the humanize skill.
metadata:
  short-description: Capture how a specific person writes
  version: "1.0.0"
---

# Voice profile

Generic "sound human" rules only get writing halfway. The other half is sounding like *this* person. This skill reads samples of someone's real writing and writes a short, concrete profile. The `humanize` skill, or any drafting task, can then follow it.

## Gather samples

Ask for 3 to 10 pieces the person wrote with little or no AI help. Ideally they span the formats the person cares about (emails, posts, docs). Around 1,500 words total is enough. More helps with rare traits. Accept pasted text or file paths.

Exclude text that was heavily AI-edited. It teaches the profile the very habits you are trying to remove. If the user is unsure about a sample, ask, or weight it lower.

If the user cannot supply samples, offer a short interview instead. Ask about their audience, formality, contractions, and words they love and hate. Ask for a sentence they wrote and are proud of. Build a lighter profile from that and mark it as interview-based.

## Analyze

Work from evidence in the samples. Do not flatter, and do not describe traits you cannot point to. Note:

1. **Sentence shape.** Typical length, how much it varies, use of fragments, run-ons, parentheticals, questions.
2. **Openings.** How pieces and paragraphs usually start (straight to the point, a story, a question, context).
3. **Endings.** How pieces end (an ask, a next step, a joke, just stop).
4. **Register.** Formality, contractions (yes/no, and how often), first person, second person, profanity, jargon level.
5. **Vocabulary.** Words and phrases they use often and that feel like theirs. Words they never use. Regional or industry spellings.
6. **Stance.** How directly they state opinions, how they hedge, how they disagree.
7. **Humor and warmth.** Type (dry, self-deprecating, none), and where it shows up.
8. **Formatting habits.** Bullets vs prose, headings, bold, emoji, punctuation quirks (dashes, ellipses, exclamation points, Oxford comma).
9. **Signature moves.** Two to five recurring things that make the writing recognizable.
10. **Their own AI-isms.** Patterns from the humanize library that this writer genuinely uses. These are allowed for them in moderation and should not be stripped.

## Write the profile

Save it as `voice-profile.md` in the current project unless the user names another path. If one already exists, read it, show what you would change, and update it instead of overwriting. Keep it under about 400 words so it stays usable as context. Use this shape:

```markdown
# Voice profile: <name or team>

_Built from: <n> samples (<formats>), <date>. Interview-based: yes/no._

## In one line
<A sentence a stranger could use to imitate this voice.>

## Do
- <specific, checkable instruction drawn from the samples>
- ...

## Don't
- <specific thing this writer avoids>
- ...

## Words
- Uses: <words and phrases>
- Avoids: <words and phrases>

## Shape
- Sentences: <length, variation, fragments>
- Openings: <pattern>
- Endings: <pattern>
- Formatting: <habits>
- Contractions: <yes / no / sometimes>

## Allowed exceptions to humanize rules
- <pattern id and why, e.g. "B5: uses one-line fragments for punchlines, sparingly">

## Example sentences (verbatim from samples)
- "<short quote>"
- "<short quote>"
```

Every **Do** and **Don't** line should be specific enough to check. "Write clearly" is useless. "Leads every email with the ask in the first sentence" is useful.

## Check before saving

- Each claim in the profile is supported by at least one sample.
- Nothing in the profile came from the humanize defaults rather than the samples.
- The example sentences are exact quotes.
- The profile is short enough to paste into a prompt.

Then tell the user where you saved it. `humanize` picks it up when they mention it or when it sits in the working folder.
