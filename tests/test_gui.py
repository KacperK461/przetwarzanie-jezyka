"""Test integracyjny kontrolek; wymaga środowiska graficznego i Tkinter."""

import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from generator_svo.grammar import MOOD_TENSES, SentenceSpec, Subject
from generator_svo.gui import GeneratorApp


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.app = GeneratorApp()
        except tk.TclError as error:
            raise unittest.SkipTest(f"Brak środowiska graficznego: {error}")
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.app.reset()

    def test_selection_event_updates_output(self):
        self.app.subject_noun.number.set("plural")
        self.app.subject_noun.number.box.event_generate("<<ComboboxSelected>>")
        self.app.update()
        self.assertEqual(self.app.sentence.text, "The students read the interesting book.")
        self.assertEqual(self.app.output.get("1.0", "end-1c"), self.app.sentence.text)

    def test_mood_limits_tense_choices(self):
        self.app.mood.set("conditional")
        self.app.mood.box.event_generate("<<ComboboxSelected>>")
        self.app.update()
        self.assertEqual(tuple(self.app.tense.choices), MOOD_TENSES["conditional"])
        self.assertEqual(self.app.sentence.text, "The student would read the interesting book.")
        self.app.mood.set("indicative")
        self.app.refresh()
        self.assertEqual(tuple(self.app.tense.choices), MOOD_TENSES["indicative"])
        self.assertEqual(self.app.tense.get(), "present_simple")

    def test_pronoun_gender_control_and_questions(self):
        self.app.apply_spec(SentenceSpec(subject=Subject(kind="pronoun", person=1), question=True,
                                        tense="present_continuous"))
        self.assertEqual(str(self.app.gender.box.cget("state")), "disabled")
        self.assertEqual(self.app.sentence.text, "Am I reading the interesting book?")
        self.app.person.set(3)
        self.app.refresh()
        self.assertEqual(str(self.app.gender.box.cget("state")), "readonly")
        self.assertEqual(self.app.sentence.text, "Is she reading the interesting book?")

    def test_copy_and_utf8_export(self):
        with patch.object(self.app, "clipboard_clear") as clear, patch.object(self.app, "clipboard_append") as append:
            self.app.copy()
            clear.assert_called_once()
            append.assert_called_once_with(self.app.sentence.text)
        with tempfile.TemporaryDirectory() as directory:
            destination = str(Path(directory) / "zdanie.txt")
            with patch("generator_svo.gui.filedialog.asksaveasfilename", return_value=destination):
                self.app.save()
            report = Path(destination).read_text(encoding="utf-8")
            self.assertIn(self.app.sentence.text, report)
            self.assertIn("REGUŁY", report)
            self.assertIn("dopełnienie", report)

    def test_randomize_and_reset(self):
        for _ in range(30):
            self.app.randomize()
            self.app.get_spec().validate()
            self.assertEqual(self.app.output.get("1.0", "end-1c"), self.app.sentence.text)
        self.app.reset()
        self.assertEqual(self.app.get_spec(), SentenceSpec())

    def test_all_selects_are_readonly_or_disabled(self):
        def walk(widget):
            for child in widget.winfo_children():
                if child.winfo_class() == "TCombobox":
                    self.assertIn(str(child.cget("state")), ("readonly", "disabled"))
                walk(child)
        walk(self.app)


if __name__ == "__main__":
    unittest.main()
