# humanize_ai

Skills that make AI-assisted writing sound like the person who is supposed to have written it.

Most "humanizer" prompts remove the obvious tells ("delve", "It's not X, it's Y", the closing aphorism) and then hand back prose that sounds like nobody in particular. These skills remove the tells and keep the writer's vocabulary, rhythm, humor, and rough edges. If you give them samples of your own writing, they learn your voice and follow it.

## What's in the box

| Skill | What it does |
| --- | --- |
| [`humanize`](skills/humanize/SKILL.md) | Edits a draft, audits it without rewriting, or writes a new one. Checks 35+ patterns in six groups and adjusts for the genre (email, LinkedIn, docs, reports, resumes, web copy). |
| [`voice-profile`](skills/voice-profile/SKILL.md) | Reads samples of your writing and saves a short `voice-profile.md` that `humanize` follows. |
| [`scan.py`](skills/humanize/scripts/scan.py) | A standard-library Python scanner that flags patterns with line numbers. Works on its own, in CI, or as a first pass for the skill. |

## Install

**Any agent that supports skills** (Claude Code, Codex, Cursor, and others), using the open skills installer:

```sh
npx skills add nxsbi/humanize_ai --skill humanize --global --yes
npx skills add nxsbi/humanize_ai --skill voice-profile --global --yes
```

**Claude Code plugin:**

```text
/plugin marketplace add nxsbi/humanize_ai
/plugin install humanize-ai@humanize-ai
```

Plugin skills are namespaced, so they show up as `/humanize-ai:humanize` and `/humanize-ai:voice-profile`. Use the `npx` install if you want the shorter `/humanize`.

**Manual:** copy `skills/humanize` and `skills/voice-profile` into `~/.claude/skills/` (or your agent's skills folder).

Or just ask your agent: `Install the humanize and voice-profile skills from https://github.com/nxsbi/humanize_ai`.

## Use it

**Edit a draft.** You get the edited draft back with a short list of what changed and why.

```text
/humanize
<paste draft>
```

**Loosen it up.** The default pass is light: it fixes patterns and leaves the rest. If the draft is clean but stiff, ask for a rewrite. It keeps every fact and changes the delivery: it opens with why instead of a definition, splits stuffed sentences, and moves what the reader cares about forward.

```text
/humanize rewrite this so it sounds like me talking:
<paste draft>
```

**Audit without rewriting.** Each finding names the pattern, quotes the line, and suggests a fix. It never guesses whether AI wrote the text, because nobody can tell reliably and named patterns are something you can check yourself.

```text
/humanize audit this, don't rewrite:
<paste draft>
```

**Write something new.**

```text
/humanize draft a LinkedIn post from these notes:
<paste notes>
```

**Teach it your voice.** Paste three to ten things you wrote yourself (emails, posts, docs). It saves `voice-profile.md`, and `humanize` uses it whenever the file is in your working folder or you point to it.

```text
/voice-profile
<paste samples or file paths>
```

**Scan from the command line.**

```sh
python skills/humanize/scripts/scan.py draft.md
cat draft.md | python skills/humanize/scripts/scan.py --json
python skills/humanize/scripts/scan.py draft.md --fail-on 5   # exit 1 at 5+ findings
```

Sample output:

```text
L5   B1  binary reframe                 It's not a dashboard problem. It's
L7   B2  negative stack                 No setup. No cost.
L9   B3  fake question-and-answer       The result? Pipeline doubled.
L11  C4  vague authority                Studies show
L15  E1  fake-profound kicker           the future isn't coming
```

The scanner finds phrases and sentence shapes. It can't judge voice or context, and it misses reworded versions of the same move, so treat its output as a list of places to look.

## Before and after

| Before | After |
| --- | --- |
| **LinkedIn post.** Here's the thing nobody tells you about dashboards. It's not a tools problem. It's a trust problem. When finance stopped double-checking our numbers, meetings got 20 minutes shorter. Let that sink in. | Our dashboards had a trust problem. When finance stopped double-checking our numbers, meetings got 20 minutes shorter. |
| **Email.** I hope this email finds you well! I just wanted to circle back on the proposal. It's worth noting that we're keen to move forward. Please don't hesitate to reach out if you have any questions. | Are you ready to sign off on the proposal? We'd like to move forward, so let me know if anything is holding it up. |
| **Website.** No setup. No code. Just insights. Our cutting-edge platform empowers teams to unlock the full potential of their data. | Connect your data and get reports without writing code or setting anything up. *[Add one concrete result, such as how long the first report takes.]* |
| **Report.** Studies show that automation may potentially reduce errors. The new process was rolled out in Q3, highlighting the team's commitment to quality. | Automation may reduce errors *[source needed: which study, and what did it find?]*. The team rolled out the new process in Q3. |
| **Launch post (rewrite).** I built Ledgerly, an open-source tool for small finance teams that automates bank reconciliation and flags mismatches, and most tools in this space are expensive and hard to set up. | I couldn't find a reconciliation tool that was affordable and easy to set up, so I built Ledgerly. It matches bank transactions automatically and flags anything that doesn't line up. It's open source and made for small finance teams. |

Nothing gets invented. When a draft is missing a number or a source, the edit flags it for you to fill in. [`examples.md`](skills/humanize/references/examples.md) lists which pattern each change fixes.

## What it catches

The full library is in [`patterns.md`](skills/humanize/references/patterns.md). The short version:

- **Framing:** "What nobody tells you", "Here's the kicker", "Let's be real", "In today's fast-paced world", leftover chat-assistant lines like "I hope this helps".
- **Structure:** "It's not X, it's Y", "No setup. No cost. Just results.", "The result? Growth.", "The best part: it learns.", stacked fragments, reflexive triads, both-sides hedging.
- **Claims:** "a pivotal moment", "...highlighting its commitment to", "Let that sink in", "Studies show", stacked hedges, "unlock your potential".
- **Vocabulary:** delve, tapestry, leverage, seamless, synergy, filler phrases, empty adverbs, "serves as" where "is" works, rotating synonyms for one thing.
- **Endings:** the closing aphorism, the recap paragraph, "Drop a comment below".
- **Formatting:** em dashes as the default connector, emoji headings, scattered bold, bullets and headings that should be prose.

[`contexts.md`](skills/humanize/references/contexts.md) changes the rules by genre. A README should be uniform and imperative. A LinkedIn post can use one-line paragraphs. A research paper keeps its hedges. A resume never gets an invented metric.

## Repository layout

```text
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
skills/humanize/SKILL.md
skills/humanize/references/patterns.md
skills/humanize/references/contexts.md
skills/humanize/references/checklist.md
skills/humanize/references/examples.md
skills/humanize/scripts/scan.py
skills/voice-profile/SKILL.md
tests/test_scan.py
```

## Development

```sh
python -m unittest discover tests
claude plugin validate .
```

To add a pattern, document it in `patterns.md` with an ID, examples, and a fix. Add it to `checklist.md`, add a regex to `scan.py` if it can be caught at the phrase level, and add a test with an example it should flag and one it should leave alone.

## Credits

This project builds on two MIT-licensed skills: Peter Yang's [No AI Slop](https://github.com/petergyang/no-ai-slop) and Nate Herk's [Human Speak](https://github.com/nateherkai/human-speak). Their pattern lists and editing workflows shaped this one. The wording, genre guidance, scanner, and voice-profile skill are new. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

MIT. See [LICENSE](LICENSE).
