import unittest
from dataclasses import replace
from itertools import product

from generator_svo.grammar import (
    ADJECTIVES, DETERMINERS, MOOD_TENSES, NOUNS, VERBS,
    NounPhrase, SentenceSpec, Subject, export_text, generate, noun_phrase_text,
)


class GrammarTests(unittest.TestCase):
    def setUp(self):
        self.base = SentenceSpec(
            subject=Subject(kind="pronoun", gender="she"), verb="eat", object=NounPhrase("apple"),
        )

    def test_all_constructions_against_examples(self):
        # Oczekiwane zdania są zapisane niezależnie od algorytmu generatora.
        cases = {
            "present_simple": ("She eats", "She does not eat", "Does she eat", "Does she not eat"),
            "past_simple": ("She ate", "She did not eat", "Did she eat", "Did she not eat"),
            "future_simple": ("She will eat", "She will not eat", "Will she eat", "Will she not eat"),
            "present_continuous": ("She is eating", "She is not eating", "Is she eating", "Is she not eating"),
            "past_continuous": ("She was eating", "She was not eating", "Was she eating", "Was she not eating"),
            "future_continuous": ("She will be eating", "She will not be eating", "Will she be eating", "Will she not be eating"),
            "present_perfect": ("She has eaten", "She has not eaten", "Has she eaten", "Has she not eaten"),
            "past_perfect": ("She had eaten", "She had not eaten", "Had she eaten", "Had she not eaten"),
            "future_perfect": ("She will have eaten", "She will not have eaten", "Will she have eaten", "Will she not have eaten"),
            "conditional_simple": ("She would eat", "She would not eat", "Would she eat", "Would she not eat"),
            "conditional_perfect": ("She would have eaten", "She would not have eaten", "Would she have eaten", "Would she not have eaten"),
        }
        for tense, expected_forms in cases.items():
            mood = "conditional" if tense.startswith("conditional") else "indicative"
            for (question, negative), expected in zip(product((False, True), repeat=2), expected_forms):
                with self.subTest(tense=tense, negative=negative, question=question):
                    spec = replace(self.base, tense=tense, mood=mood, question=question, negative=negative)
                    self.assertEqual(generate(spec).text, expected + " the apple" + ("?" if question else "."))

    def test_person_number_agreement(self):
        cases = (
            (1, "singular", "she", "I", "eat", "am", "was", "have", "Do I eat"),
            (2, "singular", "she", "You", "eat", "are", "were", "have", "Do you eat"),
            (3, "singular", "he", "He", "eats", "is", "was", "has", "Does he eat"),
            (3, "singular", "she", "She", "eats", "is", "was", "has", "Does she eat"),
            (3, "singular", "it", "It", "eats", "is", "was", "has", "Does it eat"),
            (1, "plural", "she", "We", "eat", "are", "were", "have", "Do we eat"),
            (2, "plural", "she", "You", "eat", "are", "were", "have", "Do you eat"),
            (3, "plural", "she", "They", "eat", "are", "were", "have", "Do they eat"),
        )
        for person, number, gender, pronoun, simple, present_be, past_be, perfect, question in cases:
            spec = replace(self.base, subject=Subject(kind="pronoun", person=person, number=number, gender=gender))
            expected = {
                "present_simple": f"{pronoun} {simple}",
                "present_continuous": f"{pronoun} {present_be} eating",
                "past_continuous": f"{pronoun} {past_be} eating",
                "present_perfect": f"{pronoun} {perfect} eaten",
            }
            for tense, prefix in expected.items():
                with self.subTest(person=person, number=number, gender=gender, tense=tense):
                    self.assertEqual(generate(replace(spec, tense=tense)).text, prefix + " the apple.")
            self.assertEqual(generate(replace(spec, question=True)).text, question + " the apple?")

    def test_noun_subject_agreement_and_irregular_plurals(self):
        for number, prefix in (("singular", "The child eats"), ("plural", "The children eat")):
            spec = replace(self.base, subject=Subject(phrase=NounPhrase("child", number=number)))
            self.assertEqual(generate(spec).text, prefix + " the apple.")
        for noun, plural in {"person": "people", "man": "men", "woman": "women", "mouse": "mice", "city": "cities", "box": "boxes"}.items():
            self.assertEqual(noun_phrase_text(NounPhrase(noun, "plural")), "the " + plural)

    def test_articles_follow_sound_of_next_word(self):
        cases = (
            ("apple", "", "an apple"), ("university", "", "a university"),
            ("hour", "", "an hour"), ("book", "useful", "a useful book"),
            ("student", "honest", "an honest student"), ("apple", "red", "a red apple"),
            ("dog", "old", "an old dog"), ("hour", "happy", "a happy hour"),
        )
        for noun, adjective, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(noun_phrase_text(NounPhrase(noun, determiner="indefinite", adjective=adjective)), expected)
        self.assertEqual(noun_phrase_text(NounPhrase("child", "plural", "indefinite", "happy")), "some happy children")
        self.assertEqual(noun_phrase_text(NounPhrase("mouse", "plural", "demonstrative", "small")), "these small mice")
        self.assertEqual(noun_phrase_text(NounPhrase("mouse", "singular", "demonstrative", "small")), "this small mouse")

    def test_all_30_verb_forms_against_lexical_expectations(self):
        # base, 3sg, past, participle, -ing
        expected = """
eat eats ate eaten eating
drink drinks drank drunk drinking
read reads read read reading
write writes wrote written writing
watch watches watched watched watching
buy buys bought bought buying
sell sells sold sold selling
take takes took taken taking
bring brings brought brought bringing
make makes made made making
build builds built built building
open opens opened opened opening
close closes closed closed closing
clean cleans cleaned cleaned cleaning
wash washes washed washed washing
paint paints painted painted painting
draw draws drew drawn drawing
carry carries carried carried carrying
push pushes pushed pushed pushing
pull pulls pulled pulled pulling
kick kicks kicked kicked kicking
throw throws threw thrown throwing
catch catches caught caught catching
choose chooses chose chosen choosing
hold holds held held holding
cut cuts cut cut cutting
break breaks broke broken breaking
visit visits visited visited visiting
repair repairs repaired repaired repairing
move moves moved moved moving
""".strip().splitlines()
        self.assertEqual(len(VERBS), 30)
        for line in expected:
            base, third, past, participle, progressive = line.split()
            for tense, phrase in (("present_simple", third), ("past_simple", past),
                                  ("present_perfect", "has " + participle), ("present_continuous", "is " + progressive)):
                with self.subTest(verb=base, tense=tense):
                    self.assertEqual(generate(replace(self.base, verb=base, tense=tense)).text, f"She {phrase} the apple.")
            self.assertEqual(generate(replace(self.base, verb=base, tense="past_simple", question=True)).text, f"Did she {base} the apple?")

    def test_grammar_does_not_filter_semantics(self):
        result = generate(SentenceSpec(subject=Subject(phrase=NounPhrase("glass")),
                                       verb="eat", object=NounPhrase("dog"), tense="past_simple"))
        self.assertEqual(result.text, "The glass ate the dog.")

    def test_invalid_specs_are_rejected(self):
        cases = (
            replace(self.base, verb="sleep"), replace(self.base, mood="imperative"),
            replace(self.base, tense="unknown"), replace(self.base, mood="conditional"),
            replace(self.base, tense="conditional_simple"), replace(self.base, negative="yes"),
            replace(self.base, question=1), replace(self.base, subject=Subject(kind="unknown")),
            replace(self.base, subject=Subject(kind="pronoun", person=4)),
            replace(self.base, subject=Subject(kind="pronoun", number="dual")),
            replace(self.base, subject=Subject(kind="pronoun", gender="her")),
            replace(self.base, object=NounPhrase("water")),
            replace(self.base, object=NounPhrase("dog", number="dual")),
            replace(self.base, object=NounPhrase("dog", determiner="a")),
            replace(self.base, object=NounPhrase("dog", adjective="sleeping")),
        )
        for spec in cases:
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                generate(spec)

    def test_tree_and_export_match_surface_order(self):
        sentence = generate(replace(self.base, question=True, negative=True))
        self.assertEqual([role for role, _ in sentence.tokens], ["V", "S", "V", "O"])
        self.assertEqual(" ".join(text for _, text in sentence.tokens) + "?", sentence.text)
        self.assertEqual(sentence.tree.children[0].text, "does")
        self.assertEqual(sentence.tree.children[1].text, "she")
        self.assertEqual(sentence.tree.children[2].children[0].text, "not")
        self.assertEqual(sentence.tree.children[2].children[-1].text, "the apple")
        report = export_text(sentence)
        for value in (sentence.text, sentence.subject, sentence.verb, sentence.object, "REGUŁY", "STRUKTURA"):
            self.assertIn(value, report)

    def test_all_noun_phrase_combinations(self):
        # 24 rzeczowniki × 2 liczby × 7 określników × 17 opcji przymiotnika = 5712.
        for noun, number, determiner, adjective in product(NOUNS, ("singular", "plural"), DETERMINERS, ("", *ADJECTIVES)):
            phrase = NounPhrase(noun, number, determiner, adjective)
            text = noun_phrase_text(phrase)
            self.assertEqual(text, text.strip())
            self.assertNotIn("  ", text)
            self.assertTrue(text.endswith(NOUNS[noun].plural if number == "plural" else noun))
            if number == "plural":
                self.assertNotIn(text.split()[0], ("a", "an", "this"))

    def test_complete_verb_matrix(self):
        # 30 czasowników × 8 wariantów zaimka × 11 konstrukcji × 4 formy = 10560.
        pronouns = [Subject(kind="pronoun", person=person, number=number, gender=gender)
                    for person, number, gender in (
                        (1, "singular", "she"), (2, "singular", "she"),
                        (3, "singular", "he"), (3, "singular", "she"), (3, "singular", "it"),
                        (1, "plural", "she"), (2, "plural", "she"), (3, "plural", "she"),
                    )]
        constructions = [(mood, tense) for mood, tenses in MOOD_TENSES.items() for tense in tenses]
        for verb, subject, (mood, tense), question, negative in product(VERBS, pronouns, constructions, (False, True), (False, True)):
            spec = replace(self.base, subject=subject, verb=verb, mood=mood, tense=tense, question=question, negative=negative)
            sentence = generate(spec)
            self.assertEqual(sentence.text[-1], "?" if question else ".")
            self.assertEqual(sentence.text[0], sentence.text[0].upper())
            self.assertNotIn("  ", sentence.text)
            self.assertEqual(sentence.verb.split().count("not"), int(negative))
            if question and tense in ("present_simple", "past_simple"):
                self.assertEqual(sentence.tokens[2][1], ("not " if negative else "") + verb)


if __name__ == "__main__":
    unittest.main()
