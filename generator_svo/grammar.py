"""Deterministyczna gramatyka angielska dla zamkniętego słownika.

Moduł nie zależy od GUI. Nie ocenia sensu zdań ani nie analizuje dowolnego tekstu.
Wszystkie formy leksykalne są jawne: nie zgadujemy nieregularnej fleksji.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Verb:
    base: str
    translation: str
    third: str
    past: str
    participle: str
    progressive: str


_VERBS = (
    Verb("eat", "jeść", "eats", "ate", "eaten", "eating"),
    Verb("drink", "pić", "drinks", "drank", "drunk", "drinking"),
    Verb("read", "czytać", "reads", "read", "read", "reading"),
    Verb("write", "pisać", "writes", "wrote", "written", "writing"),
    Verb("watch", "oglądać", "watches", "watched", "watched", "watching"),
    Verb("buy", "kupować", "buys", "bought", "bought", "buying"),
    Verb("sell", "sprzedawać", "sells", "sold", "sold", "selling"),
    Verb("take", "brać", "takes", "took", "taken", "taking"),
    Verb("bring", "przynosić", "brings", "brought", "brought", "bringing"),
    Verb("make", "robić", "makes", "made", "made", "making"),
    Verb("build", "budować", "builds", "built", "built", "building"),
    Verb("open", "otwierać", "opens", "opened", "opened", "opening"),
    Verb("close", "zamykać", "closes", "closed", "closed", "closing"),
    Verb("clean", "czyścić", "cleans", "cleaned", "cleaned", "cleaning"),
    Verb("wash", "myć", "washes", "washed", "washed", "washing"),
    Verb("paint", "malować", "paints", "painted", "painted", "painting"),
    Verb("draw", "rysować", "draws", "drew", "drawn", "drawing"),
    Verb("carry", "nieść", "carries", "carried", "carried", "carrying"),
    Verb("push", "pchać", "pushes", "pushed", "pushed", "pushing"),
    Verb("pull", "ciągnąć", "pulls", "pulled", "pulled", "pulling"),
    Verb("kick", "kopać", "kicks", "kicked", "kicked", "kicking"),
    Verb("throw", "rzucać", "throws", "threw", "thrown", "throwing"),
    Verb("catch", "łapać", "catches", "caught", "caught", "catching"),
    Verb("choose", "wybierać", "chooses", "chose", "chosen", "choosing"),
    Verb("hold", "trzymać", "holds", "held", "held", "holding"),
    Verb("cut", "ciąć", "cuts", "cut", "cut", "cutting"),
    Verb("break", "łamać", "breaks", "broke", "broken", "breaking"),
    Verb("visit", "odwiedzać", "visits", "visited", "visited", "visiting"),
    Verb("repair", "naprawiać", "repairs", "repaired", "repaired", "repairing"),
    Verb("move", "przesuwać", "moves", "moved", "moved", "moving"),
)
VERBS = {verb.base: verb for verb in _VERBS}


@dataclass(frozen=True)
class Noun:
    singular: str
    plural: str
    translation: str
    vowel_sound: bool = False


_NOUNS = (
    Noun("student", "students", "student"),
    Noun("teacher", "teachers", "nauczyciel"),
    Noun("dog", "dogs", "pies"),
    Noun("cat", "cats", "kot"),
    Noun("glass", "glasses", "szklanka"),
    Noun("book", "books", "książka"),
    Noun("apple", "apples", "jabłko", True),
    Noun("orange", "oranges", "pomarańcza", True),
    Noun("umbrella", "umbrellas", "parasol", True),
    Noun("car", "cars", "samochód"),
    Noun("house", "houses", "dom"),
    Noun("robot", "robots", "robot"),
    Noun("child", "children", "dziecko"),
    Noun("person", "people", "osoba"),
    Noun("woman", "women", "kobieta"),
    Noun("man", "men", "mężczyzna"),
    Noun("mouse", "mice", "mysz"),
    Noun("box", "boxes", "pudełko"),
    Noun("city", "cities", "miasto"),
    Noun("sandwich", "sandwiches", "kanapka"),
    Noun("letter", "letters", "list"),
    Noun("picture", "pictures", "obrazek"),
    Noun("university", "universities", "uniwersytet"),
    Noun("hour", "hours", "godzina", True),
)
NOUNS = {noun.singular: noun for noun in _NOUNS}


@dataclass(frozen=True)
class Adjective:
    word: str
    translation: str
    vowel_sound: bool = False


_ADJECTIVES = (
    Adjective("small", "mały"),
    Adjective("big", "duży"),
    Adjective("red", "czerwony"),
    Adjective("blue", "niebieski"),
    Adjective("green", "zielony"),
    Adjective("old", "stary", True),
    Adjective("young", "młody"),
    Adjective("new", "nowy"),
    Adjective("happy", "szczęśliwy"),
    Adjective("angry", "zły / rozgniewany", True),
    Adjective("beautiful", "piękny"),
    Adjective("interesting", "interesujący", True),
    Adjective("expensive", "drogi", True),
    Adjective("empty", "pusty", True),
    Adjective("honest", "uczciwy", True),
    Adjective("useful", "użyteczny"),
)
ADJECTIVES = {adjective.word: adjective for adjective in _ADJECTIVES}

NUMBERS = {"singular": "Liczba pojedyncza", "plural": "Liczba mnoga"}
DETERMINERS = {
    "definite": "Określony · the",
    "indefinite": "Nieokreślony · a / an / some",
    "my": "Dzierżawczy · my",
    "your": "Dzierżawczy · your",
    "our": "Dzierżawczy · our",
    "their": "Dzierżawczy · their",
    "demonstrative": "Wskazujący · this / these",
}
MOODS = {"indicative": "Oznajmujący", "conditional": "Przypuszczający · would"}
TENSES = {
    "present_simple": "Present Simple",
    "past_simple": "Past Simple",
    "future_simple": "Future Simple",
    "present_continuous": "Present Continuous",
    "past_continuous": "Past Continuous",
    "future_continuous": "Future Continuous",
    "present_perfect": "Present Perfect",
    "past_perfect": "Past Perfect",
    "future_perfect": "Future Perfect",
    "conditional_simple": "Simple Conditional",
    "conditional_perfect": "Perfect Conditional",
}
MOOD_TENSES = {
    "indicative": tuple(key for key in TENSES if not key.startswith("conditional")),
    "conditional": ("conditional_simple", "conditional_perfect"),
}


def require_choice(value, choices, label):
    if value not in choices:
        raise ValueError(f"Nieprawidłowa wartość pola „{label}”: {value!r}.")


@dataclass(frozen=True)
class NounPhrase:
    noun: str = "student"
    number: str = "singular"
    determiner: str = "definite"
    adjective: str = ""

    def validate(self):
        require_choice(self.noun, NOUNS, "rzeczownik")
        require_choice(self.number, NUMBERS, "liczba")
        require_choice(self.determiner, DETERMINERS, "określnik")
        require_choice(self.adjective, ("", *ADJECTIVES), "przymiotnik")


@dataclass(frozen=True)
class Subject:
    kind: str = "noun"
    phrase: NounPhrase = field(default_factory=NounPhrase)
    person: int = 3
    number: str = "singular"
    gender: str = "she"

    def validate(self):
        require_choice(self.kind, ("noun", "pronoun"), "typ podmiotu")
        if self.kind == "noun":
            self.phrase.validate()
        else:
            require_choice(self.person, (1, 2, 3), "osoba")
            require_choice(self.number, NUMBERS, "liczba zaimka")
            require_choice(self.gender, ("he", "she", "it"), "zaimek 3. osoby")

    @property
    def agreement(self):
        return (3, self.phrase.number) if self.kind == "noun" else (self.person, self.number)


@dataclass(frozen=True)
class SentenceSpec:
    subject: Subject = field(default_factory=Subject)
    verb: str = "read"
    object: NounPhrase = field(default_factory=lambda: NounPhrase("book", adjective="interesting"))
    mood: str = "indicative"
    tense: str = "present_simple"
    negative: bool = False
    question: bool = False

    def validate(self):
        self.subject.validate()
        self.object.validate()
        require_choice(self.verb, VERBS, "czasownik")
        require_choice(self.mood, MOODS, "tryb")
        require_choice(self.tense, MOOD_TENSES[self.mood], "czas / konstrukcja")
        if type(self.negative) is not bool or type(self.question) is not bool:
            raise ValueError("Pytanie i przeczenie muszą mieć wartość logiczną.")


@dataclass(frozen=True)
class TreeNode:
    label: str
    text: str = ""
    children: tuple = ()


@dataclass(frozen=True)
class Sentence:
    text: str
    subject: str
    verb: str
    object: str
    tokens: tuple  # pary (funkcja składniowa, fragment zdania), w kolejności powierzchniowej
    tree: TreeNode
    explanations: tuple
    pattern: str
    construction: str


def noun_phrase_parts(phrase):
    phrase.validate()
    noun = NOUNS[phrase.noun]
    adjective = ADJECTIVES.get(phrase.adjective)
    if phrase.determiner == "definite":
        determiner = "the"
    elif phrase.determiner == "indefinite":
        vowel = adjective.vowel_sound if adjective else noun.vowel_sound
        determiner = "some" if phrase.number == "plural" else ("an" if vowel else "a")
    elif phrase.determiner == "demonstrative":
        determiner = "these" if phrase.number == "plural" else "this"
    else:
        determiner = phrase.determiner
    return determiner, phrase.adjective, noun.plural if phrase.number == "plural" else noun.singular


def noun_phrase_text(phrase):
    return " ".join(part for part in noun_phrase_parts(phrase) if part)


def subject_text(subject):
    subject.validate()
    if subject.kind == "noun":
        return noun_phrase_text(subject.phrase)
    if subject.person == 1:
        return "I" if subject.number == "singular" else "we"
    if subject.person == 2:
        return "you"
    return subject.gender if subject.number == "singular" else "they"


def _verb_chain(spec):
    """Zwraca (pierwszy operator, reszta orzeczenia); operator bywa pusty."""
    verb = VERBS[spec.verb]
    person, number = spec.subject.agreement
    third = person == 3 and number == "singular"
    present_be = "am" if person == 1 and number == "singular" else ("is" if third else "are")
    past_be = "was" if number == "singular" and person != 2 else "were"
    if spec.tense == "present_simple":
        if spec.question or spec.negative:
            return ("does" if third else "do"), verb.base
        return "", verb.third if third else verb.base
    if spec.tense == "past_simple":
        return ("did", verb.base) if spec.question or spec.negative else ("", verb.past)
    return {
        "future_simple": ("will", verb.base),
        "present_continuous": (present_be, verb.progressive),
        "past_continuous": (past_be, verb.progressive),
        "future_continuous": ("will", "be " + verb.progressive),
        "present_perfect": ("has" if third else "have", verb.participle),
        "past_perfect": ("had", verb.participle),
        "future_perfect": ("will", "have " + verb.participle),
        "conditional_simple": ("would", verb.base),
        "conditional_perfect": ("would", "have " + verb.participle),
    }[spec.tense]


def _np_tree(label, phrase):
    determiner, adjective, noun = noun_phrase_parts(phrase)
    children = [TreeNode("Det · określnik", determiner)]
    if adjective:
        children.append(TreeNode("Adj · przymiotnik", adjective))
    children.append(TreeNode("N · rzeczownik", noun))
    return TreeNode(label, noun_phrase_text(phrase), tuple(children))


def _explanations(spec, operator, remainder):
    person, number = spec.subject.agreement
    result = [
        f"Podmiot: {person}. osoba, {NUMBERS[number].lower()}. "
        "Osoba i liczba podmiotu sterują formą czasownika lub operatora.",
        f"{TENSES[spec.tense]}: " + (f"operator „{operator}” + „{remainder}”." if operator else f"forma „{remainder}”."),
    ]
    if spec.tense in ("present_simple", "past_simple") and (spec.question or spec.negative):
        result.append("Po do / does / did występuje podstawowa forma czasownika, bez -s i bez odmiany przeszłej.")
    if spec.question:
        result.append("Pytanie tak/nie: pierwszy operator poprzedza podmiot. Funkcje S, V i O pozostają te same, ale szyk to Aux–S–V–O.")
    else:
        result.append("Szyk zdania oznajmującego: S (podmiot) → V (orzeczenie) → O (dopełnienie).")
    if spec.negative:
        result.append("Przeczenie not stoi po pierwszym operatorze; w pytaniu bez skrótów stoi po podmiocie.")
    for label, phrase in (("Podmiot", spec.subject.phrase if spec.subject.kind == "noun" else None), ("Dopełnienie", spec.object)):
        if phrase is None:
            continue
        determiner, adjective, noun = noun_phrase_parts(phrase)
        if phrase.determiner == "indefinite":
            if phrase.number == "plural":
                result.append(f"{label}: some + liczba mnoga („{noun}”); a/an nie łączy się z liczbą mnogą.")
            else:
                result.append(f"{label}: „{determiner}” zależy od pierwszego dźwięku słowa „{adjective or noun}”, a nie od pierwszej litery.")
        if phrase.determiner == "demonstrative":
            result.append(f"{label}: określnik „{determiner}” jest zgodny z liczbą rzeczownika.")
    result.append("Przymiotnik stoi przed rzeczownikiem i nie odmienia się przez liczbę ani rodzaj: small dog / small dogs.")
    if spec.mood == "conditional":
        result.append("Would tworzy tu samodzielne zdanie z domyślnym warunkiem. Program nie dodaje zdania podrzędnego z if.")
    return tuple(result)


def generate(spec):
    """Generuje zdanie, strukturę i objaśnienia; odrzuca niedozwolone wybory."""
    spec.validate()
    subject = subject_text(spec.subject)
    obj = noun_phrase_text(spec.object)
    operator, remainder = _verb_chain(spec)
    negation = "not " if spec.negative else ""
    predicate = " ".join(part for part in (operator, negation.strip(), remainder) if part)
    if spec.question:
        tokens = [("V", operator), ("S", subject), ("V", negation + remainder), ("O", obj)]
    else:
        tokens = [("S", subject), ("V", predicate), ("O", obj)]
    first_role, first_text = tokens[0]
    tokens[0] = (first_role, first_text[0].upper() + first_text[1:])
    punctuation = "?" if spec.question else "."
    text = " ".join(value for _, value in tokens) + punctuation
    subject_tree = (
        _np_tree("S · NP · podmiot", spec.subject.phrase)
        if spec.subject.kind == "noun"
        else TreeNode("S · podmiot", subject, (TreeNode("Pron · zaimek osobowy", subject),))
    )
    verb_nodes = []
    if operator and not spec.question:
        verb_nodes.append(TreeNode("Aux · operator", operator))
    if spec.negative:
        verb_nodes.append(TreeNode("Neg · przeczenie", "not"))
    verb_nodes.append(TreeNode("V · czasownik / dalsza część orzeczenia", remainder))
    verb_nodes.append(_np_tree("O · NP · dopełnienie", spec.object))
    children = [subject_tree, TreeNode("VP · fraza czasownikowa", children=tuple(verb_nodes))]
    if spec.question:
        children.insert(0, TreeNode("Aux · operator przeniesiony przed podmiot", operator))
    tree = TreeNode("Zdanie pytające" if spec.question else "Zdanie oznajmujące", text, tuple(children))
    return Sentence(
        text, subject, predicate, obj, tuple(tokens), tree,
        _explanations(spec, operator, remainder),
        "Aux → S → V → O" if spec.question else "S → V → O",
        TENSES[spec.tense],
    )


def tree_as_text(node, depth=0):
    line = "  " * depth + node.label + (": " + node.text if node.text else "")
    return "\n".join([line, *(tree_as_text(child, depth + 1) for child in node.children)])


def export_text(sentence):
    return (
        f"GENERATOR SVO\n\n{sentence.text}\n\n"
        f"Konstrukcja: {sentence.construction}\nSzyk: {sentence.pattern}\n"
        f"S — podmiot: {sentence.subject}\nV — orzeczenie: {sentence.verb}\n"
        f"O — dopełnienie: {sentence.object}\n\nSTRUKTURA\n{tree_as_text(sentence.tree)}\n\n"
        "REGUŁY\n" + "\n".join(f"• {rule}" for rule in sentence.explanations) + "\n"
    )
