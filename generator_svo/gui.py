"""Interfejs Tkinter. Uruchomienie: python -m generator_svo."""

import random
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .grammar import (
    ADJECTIVES, DETERMINERS, MOODS, MOOD_TENSES, NOUNS, NUMBERS, TENSES, VERBS,
    NounPhrase, SentenceSpec, Subject, export_text, generate,
)

BG = "#F3F5F8"
WHITE = "#FFFFFF"
INK = "#19283E"
MUTED = "#59697E"
LINE = "#DFE5EE"
ACCENT = "#087F73"
COLORS = {"S": "#2667BF", "V": "#7850B5", "O": "#AC591B"}
TINTS = {"S": "#EDF4FF", "V": "#F3EEFC", "O": "#FFF3E8"}


def label(parent, text="", *, size=10, bold=False, color=INK, bg=WHITE, **kwargs):
    return tk.Label(
        parent, text=text, font=("Segoe UI", -round(size * 1.4), "bold" if bold else "normal"),
        fg=color, bg=bg, anchor="w", **kwargs,
    )


class Choice:
    """Lista tylko do odczytu, mapująca etykiety na klucze modelu."""

    def __init__(self, parent, title, choices, default, on_change):
        self.frame = tk.Frame(parent, bg=WHITE)
        self.frame.pack(fill="x", pady=(0, 7))
        label(self.frame, title, size=9, color=MUTED).pack(fill="x", pady=(0, 3))
        self.variable = tk.StringVar()
        self.box = ttk.Combobox(self.frame, textvariable=self.variable, state="readonly", width=20)
        self.box.pack(fill="x")
        self.set_choices(choices, default)
        self.box.bind("<<ComboboxSelected>>", lambda _event: on_change())

    def set_choices(self, choices, selected=None):
        self.choices = dict(choices)
        self.reverse = {value: key for key, value in self.choices.items()}
        self.box.configure(values=list(self.choices.values()))
        self.set(selected if selected in self.choices else next(iter(self.choices)))

    def get(self):
        return self.reverse[self.variable.get()]

    def set(self, key):
        self.variable.set(self.choices[key])

    def enabled(self, enabled):
        self.box.configure(state="readonly" if enabled else "disabled")


class NounEditor:
    def __init__(self, parent, default, on_change):
        self.frame = tk.Frame(parent, bg=WHITE)
        self.noun = Choice(self.frame, "Rzeczownik", {
            key: f"{key} — {value.translation}" for key, value in NOUNS.items()
        }, default.noun, on_change)
        self.number = Choice(self.frame, "Liczba", NUMBERS, default.number, on_change)
        self.determiner = Choice(self.frame, "Określnik", DETERMINERS, default.determiner, on_change)
        self.adjective = Choice(self.frame, "Przymiotnik · opcjonalnie", {
            "": "Bez przymiotnika",
            **{key: f"{key} — {value.translation}" for key, value in ADJECTIVES.items()},
        }, default.adjective, on_change)

    def get(self):
        return NounPhrase(self.noun.get(), self.number.get(), self.determiner.get(), self.adjective.get())

    def set(self, phrase):
        self.noun.set(phrase.noun)
        self.number.set(phrase.number)
        self.determiner.set(phrase.determiner)
        self.adjective.set(phrase.adjective)


class GeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SVO Studio · generator zdań angielskich")
        width = min(1180, self.winfo_screenwidth() - 80)
        height = min(940, self.winfo_screenheight() - 90)
        self.geometry(f"{width}x{height}+30+25")
        self.minsize(900, 620)
        self.configure(bg=BG)
        self.option_add("*Font", ("Segoe UI", -14))
        self.option_add("*TCombobox*Listbox.font", ("Segoe UI", -14))
        self._pending = None
        self.sentence = None
        self._configure_styles()
        self._build_shell()
        self._build_header()
        self._build_editors()
        self._build_actions()
        self._build_result()
        self._build_footer()
        self.bind("<Control-Return>", lambda _event: self.refresh())
        self.bind("<Control-s>", lambda _event: self.save())
        self.refresh()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground="#F8FAFD", foreground=INK,
                        bordercolor=LINE, arrowcolor=MUTED, padding=5)
        style.map("TCombobox", fieldbackground=[("readonly", "#F8FAFD"), ("disabled", BG)],
                  foreground=[("disabled", "#8590A0")], selectbackground=[("readonly", "#F8FAFD")],
                  selectforeground=[("readonly", INK)])
        style.configure("TButton", font=("Segoe UI", -14), padding=(12, 7),
                        background=WHITE, foreground=INK, bordercolor=LINE)
        style.map("TButton", background=[("active", "#EAF0F5")])
        style.configure("Primary.TButton", background=ACCENT, foreground=WHITE,
                        bordercolor=ACCENT, font=("Segoe UI", -14, "bold"))
        style.map("Primary.TButton", background=[("active", "#06685F")])
        style.configure("TNotebook", background=WHITE, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", -14), padding=(14, 8),
                        background=BG, foreground=MUTED)
        style.map("TNotebook.Tab", background=[("selected", WHITE)], foreground=[("selected", INK)])
        style.configure("Treeview", font=("Segoe UI", -14), rowheight=28, background=WHITE,
                        fieldbackground=WHITE, foreground=INK, borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", -13, "bold"), background=BG)

    def _build_shell(self):
        viewport = tk.Frame(self, bg=BG)
        viewport.pack(side="top", fill="both", expand=True)
        self.canvas = tk.Canvas(viewport, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(viewport, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.page = tk.Frame(self.canvas, bg=BG, padx=22, pady=16)
        self.page_id = self.canvas.create_window((0, 0), window=self.page, anchor="nw")
        self.page.bind("<Configure>", lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(self.page_id, width=event.width))
        self.bind_all("<MouseWheel>", self._scroll)
        self.bind_all("<Button-4>", lambda _event: self.canvas.yview_scroll(-1, "units"))
        self.bind_all("<Button-5>", lambda _event: self.canvas.yview_scroll(1, "units"))
        self.bind_all("<FocusIn>", self._reveal_focus, add="+")

    def _scroll(self, event):
        if isinstance(event.widget, (ttk.Combobox, ttk.Treeview, tk.Text)):
            return
        self.canvas.yview_scroll(-int(event.delta / 120) if abs(event.delta) >= 120 else (-1 if event.delta > 0 else 1), "units")

    def _reveal_focus(self, event):
        """Przewiń do kontrolki także przy obsłudze wyłącznie klawiaturą."""
        widget = event.widget
        if widget.winfo_toplevel() is not self or widget is self or not str(widget).startswith(str(self.page) + "."):
            return
        top = widget.winfo_rooty() - self.page.winfo_rooty()
        bottom = top + widget.winfo_height()
        visible_top = self.canvas.canvasy(0)
        visible_bottom = visible_top + self.canvas.winfo_height()
        total = max(self.page.winfo_height(), 1)
        if top < visible_top:
            self.canvas.yview_moveto(max(0, top - 15) / total)
        elif bottom > visible_bottom:
            self.canvas.yview_moveto((bottom - self.canvas.winfo_height() + 15) / total)

    def _build_header(self):
        row = tk.Frame(self.page, bg=BG)
        row.pack(fill="x")
        label(row, "S V O", size=12, bold=True, color=WHITE, bg=ACCENT,
              padx=13, pady=8).pack(side="left")
        label(row, "STUDIO", size=11, bold=True, bg=BG, padx=10).pack(side="left")
        label(row, "ENGLISH  /  ANALIZA SKŁADNIOWA", size=9, color=MUTED, bg=BG).pack(side="right")
        label(self.page, "Zbuduj zdanie. Poznaj jego strukturę.", size=21, bold=True, bg=BG).pack(fill="x", pady=(12, 4))
        label(self.page, "Wybierz podmiot, czasownik i dopełnienie. Reguły gramatyczne połączą je w zdanie.",
              size=10, color=MUTED, bg=BG).pack(fill="x", pady=(0, 14))

    def _card(self, parent, column, role, title, subtitle):
        outer = tk.Frame(parent, bg=WHITE, highlightbackground=LINE, highlightthickness=1)
        outer.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 7, 0 if column == 2 else 7))
        tk.Frame(outer, bg=COLORS[role], height=4).pack(fill="x")
        card = tk.Frame(outer, bg=WHITE, padx=14, pady=11)
        card.pack(fill="both", expand=True)
        heading = tk.Frame(card, bg=WHITE)
        heading.pack(fill="x")
        label(heading, role, size=13, bold=True, color=COLORS[role], bg=TINTS[role],
              padx=10, pady=3).pack(side="left")
        label(heading, title, size=14, bold=True, padx=9).pack(side="left")
        subtitle_label = label(card, subtitle, size=9, color=MUTED, justify="left")
        subtitle_label.pack(fill="x", pady=(7, 10))
        card.bind("<Configure>", lambda event: subtitle_label.configure(wraplength=max(150, event.width - 28)))
        return card

    def _build_editors(self):
        row = tk.Frame(self.page, bg=BG)
        row.pack(fill="x")
        for column in range(3):
            row.columnconfigure(column, weight=1, uniform="editor")
        s_card = self._card(row, 0, "S", "Podmiot", "01   Kto lub co wykonuje czynność?")
        self.subject_kind = Choice(s_card, "Typ podmiotu", {
            "noun": "Fraza rzeczownikowa", "pronoun": "Zaimek osobowy",
        }, "noun", self.changed)
        self.subject_noun = NounEditor(s_card, NounPhrase(), self.changed)
        self.subject_noun.frame.pack(fill="x")
        self.pronoun_panel = tk.Frame(s_card, bg=WHITE)
        self.person = Choice(self.pronoun_panel, "Osoba", {
            1: "1. osoba · ja / my", 2: "2. osoba · ty / wy", 3: "3. osoba · on, ona, ono / oni",
        }, 3, self.changed)
        self.pronoun_number = Choice(self.pronoun_panel, "Liczba", NUMBERS, "singular", self.changed)
        self.gender = Choice(self.pronoun_panel, "Zaimek w 3. osobie liczby pojedynczej", {
            "he": "he — on", "she": "she — ona", "it": "it — ono / to",
        }, "she", self.changed)
        self.pronoun_hint = label(self.pronoun_panel, color=COLORS["S"], bg=TINTS["S"], padx=10, pady=9)
        self.pronoun_hint.pack(fill="x", pady=(3, 0))

        v_card = self._card(row, 1, "V", "Czasownik", "02   Co robi podmiot i kiedy?")
        self.verb = Choice(v_card, "Czasownik przechodni · 30 do wyboru", {
            key: f"{key} — {value.translation}" for key, value in VERBS.items()
        }, "read", self.changed)
        self.mood = Choice(v_card, "Tryb", MOODS, "indicative", self.changed)
        self.tense = Choice(v_card, "Czas / konstrukcja", {
            key: TENSES[key] for key in MOOD_TENSES["indicative"]
        }, "present_simple", self.changed)
        self.negative = Choice(v_card, "Czy dodać przeczenie?", {False: "Nie", True: "Tak · not"}, False, self.changed)
        self.question = Choice(v_card, "Czy zadać pytanie?", {False: "Nie · zdanie oznajmujące", True: "Tak · pytanie tak/nie"}, False, self.changed)

        o_card = self._card(row, 2, "O", "Dopełnienie", "03   Kogo lub czego dotyczy czynność?")
        label(o_card, "FRAZA RZECZOWNIKOWA", size=9, bold=True, color=COLORS["O"],
              bg=TINTS["O"], padx=9, pady=10).pack(fill="x", pady=(0, 15))
        self.object_noun = NounEditor(o_card, SentenceSpec().object, self.changed)
        self.object_noun.frame.pack(fill="x")

    def _build_actions(self):
        row = tk.Frame(self.page, bg=BG)
        row.pack(fill="x", pady=12)
        ttk.Button(row, text="Generuj zdanie  →", style="Primary.TButton", command=self.refresh).pack(side="left")
        ttk.Button(row, text="Losuj wybory", command=self.randomize).pack(side="left", padx=9)
        ttk.Button(row, text="Przykład początkowy", command=self.reset).pack(side="left")
        self.status = label(row, "Podgląd na żywo", size=9, color=MUTED, bg=BG)
        self.status.pack(side="right")

    def _build_result(self):
        # Wynik pozostaje na ekranie także wtedy, gdy użytkownik przewija formularz.
        panel = tk.Frame(self, bg=WHITE, highlightbackground=LINE, highlightthickness=1, padx=24, pady=10)
        panel.pack(side="bottom", fill="x")
        top = tk.Frame(panel, bg=WHITE)
        top.pack(fill="x")
        label(top, "TWOJE ZDANIE", size=9, bold=True, color=ACCENT).pack(side="left")
        self.meta = label(top, size=9, color=MUTED)
        self.meta.pack(side="right")
        self.output = tk.Text(panel, height=2, wrap="word", font=("Segoe UI", -28, "bold"),
                              bg=WHITE, fg=INK, relief="flat", borderwidth=0,
                              highlightthickness=0, padx=0, pady=5, cursor="arrow", takefocus=False)
        self.output.pack(fill="x")
        for role, color in COLORS.items():
            self.output.tag_configure(role, foreground=color)
        controls = tk.Frame(panel, bg=WHITE)
        controls.pack(fill="x")
        self.pattern = label(controls, size=10, bold=True, color=MUTED)
        self.pattern.pack(side="left")
        ttk.Button(controls, text="Zapisz .txt", command=self.save).pack(side="right")
        ttk.Button(controls, text="Kopiuj zdanie", command=self.copy).pack(side="right", padx=8)
        self.tabs = ttk.Notebook(self.page, height=175)
        self.tabs.pack(fill="both", expand=True)

        structure_tab = tk.Frame(self.tabs, bg=WHITE, pady=14)
        self.tabs.add(structure_tab, text="Elementy zdania")
        self.parts = {}
        for column, (role, title) in enumerate((("S", "Podmiot"), ("V", "Orzeczenie"), ("O", "Dopełnienie"))):
            structure_tab.columnconfigure(column, weight=1, uniform="parts")
            block = tk.Frame(structure_tab, bg=TINTS[role], padx=14, pady=12)
            block.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 5, 0 if column == 2 else 5))
            label(block, f"{role}   {title}", size=10, bold=True, color=COLORS[role], bg=TINTS[role]).pack(fill="x")
            value = label(block, size=13, bg=TINTS[role], justify="left", pady=9)
            value.pack(fill="x")
            block.bind("<Configure>", lambda event, item=value: item.configure(wraplength=max(90, event.width - 28)))
            self.parts[role] = value
        label(structure_tab, "Kolory wskazują funkcję fragmentu. Orzeczenie obejmuje też operatory i przeczenie.",
              size=9, color=MUTED).grid(row=1, column=0, columnspan=3, sticky="w", pady=(12, 0))

        tree_tab = tk.Frame(self.tabs, bg=WHITE)
        self.tabs.add(tree_tab, text="Drzewo składniowe")
        self.tree = ttk.Treeview(tree_tab, columns=("value",), selectmode="browse")
        self.tree.heading("#0", text="Składnik")
        self.tree.heading("value", text="Realizacja w zdaniu")
        self.tree.column("#0", width=420, minwidth=250)
        self.tree.column("value", width=450, minwidth=200)
        tree_scroll = ttk.Scrollbar(tree_tab, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        rule_tab = tk.Frame(self.tabs, bg=WHITE)
        self.tabs.add(rule_tab, text="Dlaczego poprawne?")
        self.rules = tk.Text(rule_tab, wrap="word", relief="flat", font=("Segoe UI", -14),
                             bg=WHITE, fg=INK, padx=8, pady=10, spacing3=9, cursor="arrow")
        rules_scroll = ttk.Scrollbar(rule_tab, command=self.rules.yview)
        self.rules.configure(yscrollcommand=rules_scroll.set)
        rules_scroll.pack(side="right", fill="y")
        self.rules.pack(fill="both", expand=True)

    def _build_footer(self):
        footer = tk.Frame(self.page, bg=BG)
        footer.pack(fill="x", pady=(13, 0))
        label(footer, "Poprawność gramatyczna w ramach słownika i reguł programu. Sens zdania może być dowolny.",
              size=9, color=MUTED, bg=BG).pack(side="left")
        ttk.Button(footer, text="Pomoc", command=self.help).pack(side="right")

    def changed(self):
        if self._pending is not None:
            self.after_cancel(self._pending)
        self._pending = self.after_idle(self.refresh)

    def _sync_controls(self):
        if self.subject_kind.get() == "noun":
            self.pronoun_panel.pack_forget()
            self.subject_noun.frame.pack(fill="x")
        else:
            self.subject_noun.frame.pack_forget()
            self.pronoun_panel.pack(fill="x")
        self.gender.enabled(self.person.get() == 3 and self.pronoun_number.get() == "singular")
        allowed = {key: TENSES[key] for key in MOOD_TENSES[self.mood.get()]}
        current = self.tense.get()
        if self.tense.choices != allowed:
            self.tense.set_choices(allowed, current)

    def get_spec(self):
        return SentenceSpec(
            subject=Subject(self.subject_kind.get(), self.subject_noun.get(), self.person.get(),
                            self.pronoun_number.get(), self.gender.get()),
            verb=self.verb.get(), object=self.object_noun.get(), mood=self.mood.get(),
            tense=self.tense.get(), negative=self.negative.get(), question=self.question.get(),
        )

    def refresh(self):
        if self._pending is not None:
            self.after_cancel(self._pending)
            self._pending = None
        self._sync_controls()
        try:
            self.sentence = generate(self.get_spec())
        except ValueError as error:
            self.sentence = None
            self.output.configure(state="normal")
            self.output.delete("1.0", "end")
            self.output.insert("end", "Sprawdź wybrane opcje.")
            self.output.configure(state="disabled")
            self.status.configure(text=str(error), fg="#B33B3B")
            return
        sentence = self.sentence
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        for index, (role, value) in enumerate(sentence.tokens):
            if index:
                self.output.insert("end", " ")
            self.output.insert("end", value, role)
        self.output.insert("end", "?" if self.question.get() else ".")
        self.output.configure(state="disabled")
        kind = "pytanie" if self.question.get() else "zdanie oznajmujące"
        if self.negative.get():
            kind += " · przeczenie"
        self.meta.configure(text=f"{sentence.construction}  /  {kind}")
        self.pattern.configure(text=sentence.pattern)
        for role, text in (("S", sentence.subject), ("V", sentence.verb), ("O", sentence.object)):
            self.parts[role].configure(text=text)
        self.pronoun_hint.configure(text=f"Wybrany podmiot: {sentence.subject}")
        self.tree.delete(*self.tree.get_children())
        self._insert_tree("", sentence.tree)
        self.rules.configure(state="normal")
        self.rules.delete("1.0", "end")
        self.rules.insert("end", "\n".join(f"• {rule}" for rule in sentence.explanations))
        self.rules.configure(state="disabled")
        self.status.configure(text="✓  Podgląd aktualny", fg=ACCENT)

    def _insert_tree(self, parent, node):
        item = self.tree.insert(parent, "end", text=node.label, values=(node.text,), open=True)
        for child in node.children:
            self._insert_tree(item, child)

    def apply_spec(self, spec):
        spec.validate()
        self.subject_kind.set(spec.subject.kind)
        self.subject_noun.set(spec.subject.phrase)
        self.person.set(spec.subject.person)
        self.pronoun_number.set(spec.subject.number)
        self.gender.set(spec.subject.gender)
        self.verb.set(spec.verb)
        self.mood.set(spec.mood)
        self._sync_controls()
        self.tense.set(spec.tense)
        self.negative.set(spec.negative)
        self.question.set(spec.question)
        self.object_noun.set(spec.object)
        self.refresh()

    def reset(self):
        self.apply_spec(SentenceSpec())

    def randomize(self):
        def phrase():
            return NounPhrase(random.choice(tuple(NOUNS)), random.choice(tuple(NUMBERS)),
                              random.choice(tuple(DETERMINERS)), random.choice(("", *ADJECTIVES)))
        mood = random.choice(tuple(MOODS))
        self.apply_spec(SentenceSpec(
            subject=Subject(random.choice(("noun", "pronoun")), phrase(), random.choice((1, 2, 3)),
                            random.choice(tuple(NUMBERS)), random.choice(("he", "she", "it"))),
            verb=random.choice(tuple(VERBS)), object=phrase(), mood=mood,
            tense=random.choice(MOOD_TENSES[mood]), negative=random.choice((False, True)),
            question=random.choice((False, True)),
        ))

    def copy(self):
        self.refresh()
        if self.sentence:
            self.clipboard_clear()
            self.clipboard_append(self.sentence.text)
            self.status.configure(text="✓  Skopiowano zdanie")

    def save(self):
        self.refresh()
        if not self.sentence:
            return
        path = filedialog.asksaveasfilename(parent=self, title="Zapisz zdanie i analizę", defaultextension=".txt",
                                          initialfile="zdanie_svo.txt", filetypes=[("Plik tekstowy", "*.txt")])
        if path:
            try:
                Path(path).write_text(export_text(self.sentence), encoding="utf-8")
            except OSError as error:
                messagebox.showerror("Nie udało się zapisać pliku", str(error), parent=self)
            else:
                self.status.configure(text="✓  Zapisano zdanie i analizę")

    def help(self):
        messagebox.showinfo(
            "Jak korzystać z SVO Studio",
            "1. Wybierz frazę rzeczownikową albo zaimek jako podmiot.\n"
            "2. Wybierz czasownik, tryb i czas / konstrukcję.\n"
            "3. Ustal, czy zdanie ma być przeczeniem lub pytaniem.\n"
            "4. Zbuduj dopełnienie, wybierając rzeczownik i jego określenia.\n"
            "5. Odczytaj zdanie, drzewo składniowe i zastosowane reguły.\n\n"
            "Podgląd aktualizuje się po każdej zmianie. Tab przechodzi między polami, "
            "strzałki zmieniają wybór. Ctrl+Enter generuje zdanie, Ctrl+S zapisuje analizę.\n\n"
            "Zakres: strona czynna, 30 czasowników przechodnich, 9 konstrukcji czasowych "
            "i 2 konstrukcje z would. Pytania mają szyk Aux–S–V–O. "
            "Przymiotniki angielskie są nieodmienne.\n\n"
            "Program nie ocenia znaczenia: The glass ate the dog. jest dozwolone. "
            "Nie jest parserem dowolnego tekstu.", parent=self,
        )


def main():
    app = GeneratorApp()
    app.mainloop()
