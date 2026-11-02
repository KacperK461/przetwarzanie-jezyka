# Generator struktur składniowych SVO — część II projektu

## Cel

Celem projektu jest opracowanie programu z graficznym interfejsem,
który umożliwia użytkownikowi zbudowanie zdania poprawnego pod względem
składni i fleksji w wybranym fragmencie języka. Wybrano język angielski,
którego podstawowy szyk zdania oznajmującego to Subject–Verb–Object.
Interfejs prowadzi użytkownika przez wybór elementów zdania, a reguły
gramatyczne ustalają ich ostateczne formy.

Program nosi nazwę **SVO Studio**. Jest napisany w Pythonie z użyciem
standardowej biblioteki Tkinter. Działa lokalnie i nie wymaga połączenia
z internetem. Generowanie jest deterministyczne; losowanie zmienia
wyłącznie konfigurację wejściową.

## Realizacja wymagań

Podmiot można zbudować jako frazę rzeczownikową albo zaimek osobowy.
Dla zaimka ustala się osobę oraz liczbę, a w 3. osobie liczby pojedynczej
również wybór `he`, `she` lub `it`. W przypadku frazy rzeczownikowej
wybiera się rzeczownik, jego liczbę, określnik oraz opcjonalny przymiotnik.

Program udostępnia 30 czasowników przechodnich. Użytkownik wybiera tryb
oznajmujący lub przypuszczający i dostępną w nim konstrukcję czasową.
W trybie oznajmującym są to Present, Past i Future w odmianach Simple,
Continuous i Perfect. W trybie przypuszczającym dostępne są konstrukcje
`would + V` oraz `would have + V3`.

Dopełnienie jest frazą rzeczownikową. Użytkownik może dodać przeczenie
oraz przekształcić zdanie w pytanie tak/nie. Dobór odbywa się przez listy
tylko do odczytu, dlatego nie można wprowadzić nieznanego słowa ani
samodzielnie wpisać błędnej formy fleksyjnej.

Interfejs rozróżnia funkcje składniowe kolorami i oznaczeniami literowymi:
S — podmiot, V — orzeczenie, O — dopełnienie. Wynik jest stale widoczny
na dole okna. Użytkownik może zobaczyć podział na składniki, rozwinąć
drzewo składniowe oraz przeczytać uzasadnienie zastosowanych reguł.

## Model gramatyki

Uproszczony schemat zdania oznajmującego:

```text
Zdanie → Podmiot VP
VP → GrupaCzasownikowa Dopełnienie
Podmiot → Zaimek | NP
Dopełnienie → NP
NP → Określnik [Przymiotnik] Rzeczownik
```

Schemat jest uzupełniony cechami: osobą, liczbą, konstrukcją czasową,
trybem, przeczeniem i formą pytającą. Sama gramatyka bez tych cech
nie wystarczyłaby do zapewnienia zgodności, np. `she reads` i `they read`.

Słownik przechowuje jawne formy czasowników: podstawową, 3. osoby liczby
pojedynczej, przeszłą, imiesłów przeszły i formę `-ing`. Rzeczowniki mają
zapisaną liczbę pojedynczą i mnogą, w tym formy nieregularne.
Przykładowo: `eat/eats/ate/eaten/eating` oraz `child/children`.

Algorytm wykonuje następujące kroki:

1. Sprawdza, czy wszystkie wybory należą do słownika i dozwolonych kategorii.
2. Buduje podmiot i wyznacza osobę oraz liczbę do uzgodnienia z orzeczeniem.
3. Tworzy dopełnienie zgodnie z regułami frazy rzeczownikowej.
4. Wybiera formę czasownika i ewentualny operator, np. `does`, `is`, `has`.
5. Dodaje `not`, jeżeli wybrano przeczenie.
6. W pytaniu umieszcza pierwszy operator przed podmiotem.
7. Dodaje wielką literę i znak interpunkcyjny, tworzy drzewo i objaśnienia.

Przymiotniki angielskie pozostają nieodmienne. Program umieszcza je przed
rzeczownikiem. Wybór `a/an` zależy od pierwszego dźwięku następnego słowa;
dlatego poprawne są `an honest student` i `a useful book`. Dla liczby mnogiej
program zastępuje przedimek nieokreślony przez `some`, a `this` przez `these`.

W pytaniu podział na funkcje S, V, O zostaje zachowany, natomiast rzeczywisty
szyk to Aux–S–V–O. W pytaniu przeczącym używana jest pełna forma,
np. `Does she not eat the apple?`. Operator występuje przed podmiotem,
a `not` po nim. Drzewo w interfejsie odwzorowuje tę kolejność.

## Architektura

Moduł `generator_svo/grammar.py` zawiera słownik, niezmienne modele danych,
walidację i generator. Nie importuje Tkinter, więc można używać go osobno,
np. w notebooku albo w testach automatycznych.

Moduł `generator_svo/gui.py` odpowiada za formularz, ograniczenia wyboru,
prezentację wyniku i eksport. Zmiana trybu odświeża dostępne konstrukcje,
a pola, które nie mają zastosowania do aktualnego podmiotu, są ukryte
lub wyłączone. GUI i silnik niezależnie ograniczają niepoprawne wejścia.

Drzewo jest budowane razem ze zdaniem z wybranej konfiguracji. Jest to
generator z prezentacją struktury, a nie parser dowolnych zdań angielskich.

## Przewodnik uruchomienia i obsługi

1. Zainstalować Python 3.10 lub nowszy z Tkinter.
2. Pobrać i rozpakować projekt. Wejść do folderu z plikiem `uruchom.pyw`.
3. W Windows uruchomić `uruchom.pyw` dwuklikiem lub wykonać
   `python -m generator_svo` w terminalu otwartym w tym folderze.
4. W panelu podmiotu wybrać „Zaimek osobowy”, 3. osobę, liczbę pojedynczą
   i `she`.
5. Wybrać czasownik `eat`, tryb oznajmujący i Present Simple. Pozostawić
   „Nie” przy pytaniu i przeczeniu.
6. W dopełnieniu wybrać `apple`, liczbę pojedynczą, określnik nieokreślony
   i brak przymiotnika. Wynikiem jest **She eats an apple.**
7. Włączyć przeczenie. Wynik: **She does not eat an apple.**
8. Wyłączyć przeczenie i włączyć pytanie. Wynik: **Does she eat an apple?**
9. Zajrzeć do zakładek „Drzewo składniowe” i „Dlaczego poprawne?”.
10. Użyć „Zapisz .txt”, aby zapisać wynik z analizą, lub „Kopiuj zdanie”,
    aby skopiować sam tekst. Przycisk „Przykład początkowy” resetuje formularz.

## Weryfikacja

Testy można uruchomić poleceniem:

```sh
python -m unittest discover -s tests -v
```

Zestaw obejmuje 16 testów: wzorcowe zdania, zgodę podmiotu z orzeczeniem,
formy nieregularne, przedimki zależne od wymowy, odrzucanie błędnych danych,
zgodność drzewa z wynikiem oraz integrację GUI. Testy macierzowe przechodzą
przez 10 560 kombinacji czasowników, zaimków, konstrukcji i form wypowiedzi
oraz 5712 fraz rzeczownikowych. Testy macierzowe sprawdzają spójność
i wybrane warunki poprawności; testy wzorcowe porównują pełne wyniki
z niezależnie zapisanymi oczekiwanymi zdaniami. Nie stanowi to dowodu
poprawności dla całego języka angielskiego.

Testy GUI wymagają środowiska graficznego. Weryfikują zdarzenia wyboru,
ograniczenia list, przełączanie pól zaimka, losowanie, reset i eksport.
Test kopiowania używa zastępczego schowka, aby nie nadpisywać schowka
użytkownika podczas uruchamiania zestawu testów.

## Ograniczenia

Program obejmuje zamknięty słownik i wybrany fragment gramatyki: proste
zdania w stronie czynnej, pojedynczy podmiot i pojedyncze dopełnienie.
Nie obejmuje zdań złożonych, trybu rozkazującego, strony biernej, pytań
szczegółowych ani rzeczowników niepoliczalnych. Nie sprawdza semantyki,
kontekstu ani naturalności użycia. Zdanie **The glass ate the dog.** jest
celowo dopuszczalne.

Wcześniejsza część projektu znajduje się w `pjn.ipynb` i dotyczy
częstotliwości znaków oraz kodowania Huffmana. Generator stanowi osobny
moduł i nie zależy od danych korpusowych używanych w notebooku.

## Repozytorium i program do pobrania

Repozytorium projektu:
[github.com/KacperK461/przetwarzanie-jezyka](https://github.com/KacperK461/przetwarzanie-jezyka).

Przed oddaniem sprawozdania trzeba wysłać nowe pliki do repozytorium
i sprawdzić ich dostępność dla prowadzącego. Po wysłaniu kod można pobrać
przez **Code → Download ZIP**. Lokalna paczka `release/svo-studio.zip`
zawiera źródła generatora, instrukcję i testy; wymaga zainstalowanego Pythona.

## Źródła reguł

- [Cambridge Dictionary — A/an and the](https://dictionary.cambridge.org/grammar/british-grammar/the):
  użycie przedimków, policzalność i wpływ wymowy.
- [British Council — Questions and negatives](https://learnenglish.britishcouncil.org/free-resources/grammar/english-grammar-reference/questions-negatives):
  operatory, pytania i przeczenia.
- [British Council — Present simple](https://learnenglishteens.britishcouncil.org/grammar/a1-a2-grammar/present-simple):
  zgodność osoby i liczby oraz końcówki 3. osoby.
- [British Council — Conditionals: third and mixed](https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2/conditionals-third-mixed):
  konstrukcja `would have` z imiesłowem przeszłym.
