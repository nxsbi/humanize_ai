"""Run with: python -m unittest discover tests"""

import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("scan", ROOT / "skills/humanize/scripts/scan.py")
scan = importlib.util.module_from_spec(spec)
sys.modules["scan"] = scan
spec.loader.exec_module(scan)


def ids(text: str) -> set[str]:
    return {f.pattern for f in scan.scan(text)}


class FlagsSlop(unittest.TestCase):
    def test_binary_reframe(self):
        self.assertIn("B1", ids("It's not a dashboard problem. It's a decision problem."))

    def test_negative_stack(self):
        self.assertIn("B2", ids("No setup. No cost. Just results."))

    def test_fake_qa(self):
        self.assertIn("B3", ids("The result? Pipeline doubled."))

    def test_colon_reveal(self):
        self.assertIn("B4", ids("The best part: it learns."))

    def test_fragment_stack(self):
        self.assertIn("B5", ids("You plan. You build. You ship."))

    def test_vocab_and_filler(self):
        found = ids("We leverage cutting-edge tools. It's worth noting that studies show gains.")
        self.assertTrue({"D1", "D2", "C4"} <= found)

    def test_hollow_analysis(self):
        self.assertIn("C2", ids("The launch adds search, highlighting the team's focus."))

    def test_em_dash_and_emoji_heading(self):
        found = {f.label for f in scan.scan("# \U0001F680 Launch\n\nFast — and cheap.")}
        self.assertTrue({"em dash", "emoji in heading"} <= found)

    def test_line_numbers(self):
        f = [x for x in scan.scan("First line here.\n\nThe best part: it learns.") if x.pattern == "B4"]
        self.assertEqual(f[0].line, 3)

    def test_en_dash_and_semicolon(self):
        found = {f.label for f in scan.scan("We ran it 2019–2021; it held up.")}
        self.assertTrue({"en dash", "semicolon"} <= found)

    def test_long_sentence(self):
        long = " ".join(["word"] * 21) + "."
        self.assertIn("long sentence", {f.label for f in scan.scan(long)})
        self.assertEqual(scan.scan(long, max_words=0), [])
        self.assertEqual(scan.scan(" ".join(["word"] * 20) + "."), [])


class LeavesCleanTextAlone(unittest.TestCase):
    def test_plain_prose(self):
        text = (
            "We moved month-end close from nine days to four by replacing three spreadsheet "
            "hand-offs with one dataset. Finance signs off on Tuesday now.\n\n"
            "The hard part was getting regional teams to agree on one chart of accounts. "
            "That took two months."
        )
        self.assertEqual(scan.scan(text), [])

    def test_semicolon_in_link_target_is_ignored(self):
        self.assertEqual(scan.scan("See [the guide](http://x.com/a;b) here."), [])

    def test_code_is_ignored(self):
        self.assertEqual(scan.scan("Run `leverage --robust` first.\n\n```\nutilize()\n```\n"), [])


if __name__ == "__main__":
    unittest.main()
