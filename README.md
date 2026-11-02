# SVO Studio — generator struktur składniowych

Aplikacja okienkowa w Pythonie do budowania angielskich zdań z podmiotu (S),
orzeczenia (V) i dopełnienia (O). Interfejs jest po polsku. Program działa
lokalnie, bez internetu, API, modeli językowych ani dodatkowych pakietów pip.

## Uruchomienie

Wymagania: **Python 3.10 lub nowszy z Tkinter** oraz środowisko graficzne.
Sprawdzono w Windows, Python 3.13.3 i Tk 8.6.

W folderze projektu uruchom:

```sh
python -m generator_svo
```

W Windows można też dwukrotnie kliknąć **`uruchom.pyw`**, jeśli rozszerzenie
`.pyw` jest powiązane z Pythonem. Przy problemie z uruchomieniem dwuklikiem
użyj powyższego polecenia, aby zobaczyć komunikat błędu.

Tkinter jest składnikiem standardowej instalacji Pythona dla Windows.
Można sprawdzić jego dostępność poleceniem `python -m tkinter`. W niektórych
dystrybucjach Linuksa trzeba doinstalować systemowy pakiet `python3-tk`.
Nie ma pliku `requirements.txt`, ponieważ aplikacja używa wyłącznie biblioteki standardowej.

## Przewodnik użytkownika

1. W panelu **S — Podmiot** wybierz frazę rzeczownikową lub zaimek osobowy.
   Dla frazy wybierz rzeczownik, liczbę, określnik i opcjonalny przymiotnik.
   Dla zaimka wybierz osobę i liczbę; w 3. osobie liczby pojedynczej wybierz
   również `he`, `she` albo `it`.
2. W panelu **V — Czasownik** wybierz jeden z 30 czasowników przechodnich,
   tryb i konstrukcję czasową. Odpowiedz „Tak” albo „Nie” na pytania
   o przeczenie i formę pytającą.
3. W panelu **O — Dopełnienie** zbuduj frazę rzeczownikową.
4. Zdanie aktualizuje się automatycznie i pozostaje widoczne u dołu okna.
   Przycisk **Generuj zdanie** dodatkowo odświeża wynik. Formularz i zakładki
   można przewijać, gdy nie mieszczą się w oknie.
5. Zakładka **Elementy zdania** pokazuje S, V i O. **Drzewo składniowe**
   przedstawia hierarchię składników, a **Dlaczego poprawne?** objaśnia
   zastosowane reguły.
6. **Losuj wybory** tworzy losową konfigurację zgodną z gramatyką programu.
   **Przykład początkowy** przywraca ustawienia domyślne.
7. **Kopiuj zdanie** kopiuje sam wynik. **Zapisz .txt** zapisuje zdanie,
   strukturę oraz objaśnienia w UTF-8.

Obsługa klawiaturą: `Tab` / `Shift+Tab` przechodzą między polami, strzałki
zmieniają wybór, `Ctrl+Enter` generuje wynik, a `Ctrl+S` zapisuje analizę.

## Zakres gramatyki

- Podmiot: fraza rzeczownikowa lub `I`, `you`, `he`, `she`, `it`, `we`, `they`.
  `You` jest dostępne w obu liczbach, z odpowiednią zgodą gramatyczną.
- Słownik: 30 czasowników przechodnich, 24 rzeczowniki policzalne i 16
  przymiotników. Podmiot i dopełnienie mogą występować w obu liczbach.
- Fraza rzeczownikowa: określnik + opcjonalny przymiotnik + rzeczownik.
  Określniki: `the`, automatyczne `a/an/some`, `my`, `your`, `our`, `their`
  oraz automatyczne `this/these`.
- Konstrukcje w trybie oznajmującym: Present, Past i Future w wariantach
  Simple, Continuous i Perfect — łącznie 9.
- Tryb przypuszczający: Simple Conditional (`would + bezokolicznik`)
  i Perfect Conditional (`would have + III forma`). Są to pojedyncze
  zdania z domyślnym warunkiem, bez automatycznie dopisywanego `if`.
- Każda konstrukcja dopuszcza twierdzenie, przeczenie, pytanie tak/nie
  i pytanie przeczące. Program używa pełnych form, np. `does not`.
- W pytaniu zmienia się szyk: **Aux–S–V–O**. Kolor V obejmuje zarówno
  operator na początku, jak i dalszą część orzeczenia. Drzewo pokazuje
  rzeczywistą kolejność składników.

W angielskim przymiotnik stoi przed rzeczownikiem i nie odmienia się przez
rodzaj ani liczbę. Program dobiera `a/an` na podstawie pierwszego dźwięku
najbliższego słowa: `an apple`, `a red apple`, `an honest student`,
`a useful book`, `an hour`, `a university`. W liczbie mnogiej używa `some`
w miejsce `a/an`. Reguły dotyczące przedimków:
[Cambridge Dictionary](https://dictionary.cambridge.org/grammar/british-grammar/the).

Pytania i przeczenia w Present/Past Simple używają `do/does/did` i formy
podstawowej czasownika. W pozostałych konstrukcjach pierwszy operator
przechodzi przed podmiot w pytaniu, a `not` jest odpowiednio wstawiane:
[British Council — Questions and negatives](https://learnenglish.britishcouncil.org/free-resources/grammar/english-grammar-reference/questions-negatives).

Przykłady:

```text
The student reads the interesting book.
She does not eat an apple.
Do the children carry these small boxes?
The glass ate the dog.
Would I not have written the letter?
```

Gwarancja dotyczy reguł składni i fleksji zaimplementowanych dla zamkniętego
słownika. Program nie ocenia sensu, kontekstu, naturalności wypowiedzi ani
odniesienia określników. Dlatego szklanka może „zjeść” psa. Nie jest to
parser tekstu wpisanego przez użytkownika. Zakres nie obejmuje strony
biernej, trybu rozkazującego, pytań szczegółowych, zdań złożonych,
rzeczowników niepoliczalnych ani zaimków w dopełnieniu.

## Kod i testy

- `generator_svo/grammar.py` — słownik, modele danych, walidacja, reguły,
  generowanie zdań, drzew i raportów tekstowych; niezależny od GUI.
- `generator_svo/gui.py` — interfejs Tkinter, kontrolki tylko do odczytu,
  blokowanie niedozwolonych połączeń trybu i konstrukcji.
- `uruchom.pyw` — start bez okna konsoli w Windows.
- `tests/test_grammar.py` — przypadki wzorcowe, błędne dane oraz macierze
  10 560 form czasownikowych i 5712 fraz rzeczownikowych.
- `tests/test_gui.py` — integracja kontrolek, aktualizacja wyniku,
  kopiowanie, eksport, losowanie i reset. Bez środowiska graficznego
  testy GUI są pomijane.
- `docs/SPRAWOZDANIE.md` — opis projektu i przewodnik do sprawozdania.
- `pjn.ipynb` — wcześniejsza część projektu: częstotliwości znaków i Huffman.

```sh
python -m unittest discover -s tests -v
```

Same testy silnika, np. na serwerze bez pulpitu:

```sh
python -m unittest discover -s tests -p test_grammar.py -v
```

## GitHub i udostępnienie

Adres skonfigurowanego repozytorium:
[KacperK461/przetwarzanie-jezyka](https://github.com/KacperK461/przetwarzanie-jezyka).
Dodane pliki muszą zostać zatwierdzone i wysłane do tego repozytorium,
zanim będą dostępne dla prowadzącego. Samo utworzenie ich lokalnie
nie publikuje zmian na GitHubie.

Po publikacji można pobrać repozytorium przez **Code → Download ZIP**,
rozpakować i uruchomić program zgodnie z instrukcją powyżej. Lokalna paczka
`release/svo-studio.zip` zawiera aplikację, testy i dokumentację. Paczka
wymaga Pythona z Tkinter; nie jest samodzielnym plikiem `.exe`.
