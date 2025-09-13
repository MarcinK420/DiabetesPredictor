## **Wymagania funkcjonalne**

### 1. **Informacje ogólne**

- **Nazwa projektu:** Diabetes Predictor
- **Autor dokumentu:** Marcin Kruk
- **Data utworzenia:** 13/08/2025
- **Wersja dokumentu:** v0.01
- **Osoby odpowiedzialne / interesariusze:** Marcin Kruk

---
### 2. **Cel systemu**

Diabetes Predictor ma być programem pełniącym funkcję wskaźnika w ocenie ryzyka prawdopodobieństwa zachorowania na cukrzycę. Przy pomocy prztrenowanego modelu i danych wpisanych przez użytkownika ma on sugerować stopień ryzyka zachorowania.

---
### 3. **Zakres**

Przede wszystkim formularz z wbudowanym modelem oceniającym ryzyko, ale również system zapisów na wizyty, badania wraz z historią wizyt, kartą pacjenta, możliwością podejrzenia swoich wyników, coś w stylu takiej online przychodni dla cukrzyków.

---
### 4. **Wymagania funkcjonalne**

| ID    | Nazwa funkcji                     | Opis funkcji                                                                                            | Priorytet (W/M/N)* | Wejścia                                                                                                                                        | Wyjścia                                                                                                     | Uwagi / Ograniczenia                                                                                   |
| ----- | --------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| FR-01 | Rejestracja użytkownika           | Użytkownik może utworzyć konto poprzez podanie e-maila i hasła                                          | W                  | E-mail, hasło                                                                                                                                  | Potwierdzenie utworzenia konta                                                                              | Hasło min. 8 znaków                                                                                    |
| FR-02 | Logowanie                         | Użytkownik loguje się do systemu przy użyciu e-maila i hasła                                            | W                  | E-mail, hasło                                                                                                                                  | Dostęp do panelu użytkownika                                                                                | Blokada po 5 nieudanych próbach                                                                        |
| FR-03 | Przejście do odpowiedniego panelu | Po zalogowaniu w zależności od tego czy jest to pacjent czy doktor przechodzi do odpowiedniej karty     | W                  | Status użytkownika                                                                                                                             | Dostęp do odpowiedniego panelu                                                                              | Zawsze pokazuje panel zwykłego użytkownika dopóki parent admin nie nada odpowiednich uprawnień         |
| FR-04 | Historia wizyt                    | Użytkownik może wejść w panel przedstawiający historię dotychczasowych wizyt                            | W                  | Przycisk "Historia badań" przekierowujący do panelu                                                                                            | Dostęp do odpowiedniej podstrony                                                                            | Brak                                                                                                   |
| FR-05 | Kliknięcie w konkretną wizytę     | Użytkownik może kliknąć w wizytę aby obejrzeć jej kartę i móc sprawdzić szczegóły                       | N                  | Naciśnięcie wizyty                                                                                                                             | Karta z szczegółami wizyty                                                                                  | Można to zrobić w formie oddzielnej strony chociaż najlepiej byłoby zrobić popup na tej samej stronie. |
| FR-06 | Zapisywanie się na wizytę         | Wypełnianie formularza w celu zapisania na wizytę                                                       | M                  | Formularz z danymi                                                                                                                             | Potwierdzenie na ekranie: "Pomyślnie zapisano"                                                              | Do wyboru powinny być tylko dostępne terminy dla danego lekarza                                        |
| FR-07 | Edycja wizyty                     | Kliknięcie w przycisk "edytuj" przy wizycie w celu zmiany jej szczegółów                                | M                  | Formularz z danymi                                                                                                                             | Potwierdzenie na ekranie:<br>"Zapisano zmiany"                                                              | Do wyboru powinny być tylko dostępne terminy dla danego lekarza                                        |
| FR-08 | Anulowanie wizyty                 | Kliknięcie w przycisk "anuluj wizytę" w celu jej odwołania                                              | M                  | Zapytanie: "Czy na pewno chcesz anulować?"(T/N)                                                                                                | Potwierdzenie na ekranie:<br>"Pomyślnie odwołano"                                                           | Konieczność odczekania 2 minut przed ponownym zapisaniem                                               |
| FR-09 | Karta z danymi pacjenta           | Profil użytkownika na którym widnieją jego dane kontaktowe, wiek, tożsamość, data ostatniej wizyty itp. | N                  | Przy rejestracji pokazane są dane do wypełnienia które później będą wyświetlane w formularzu.                                                  | Profil z wypełnionymi danymi.                                                                               | Niektóre dane powinny być szyfrowane przed niechcianym dostępem                                        |
| FR-10 | Strona główna pacjenta            | Przejście do panelów: Profil, Wizyty, Historia Wizyt                                                    | W                  | Prosta strona z napisem "Dzień Dobry" i kartami do kliknięcia w celu przejścia na odpowiednią stronę                                           | Po naciśnięciu odpowiedniej karty przekierowuje we właściwe miejsce.                                        | Trzeba będzie jakoś sensownie wypełnić miejsce aby dobrze to wyglądało                                 |
| FR-11 | Strona główna lekarza             | Przejście do panelów: Profil, Wizyty, Spis pacjentów                                                    | W                  | Prosta strona z napisem "Dzień Dobry" i kartami do kliknięcia w celu przejścia na odpowiednią stronę                                           | Po naciśnięciu odpowiedniej karty przekierowuje we właściwe miejsce.                                        | Trzeba będzie jakoś sensownie wypełnić miejsce aby dobrze to wyglądało                                 |
| FR-12 | Najbliższe wizyty                 | Panel z kalendarzem lub widokiem listy z najbliższymi wizytami                                          | M                  | Po nacisnieciu przycisku przekierowuje na odpowiednia karte.                                                                                   | Karta z widokiem wizyt.                                                                                     | Przyszłe wizyty, historia dla lekarza zawarta bedzie w spisie pacjentów                                |
| FR-13 | Spis pacjentów                    | Panel z lista pacjentów danego lekarza                                                                  | W                  | Po nacisnieciu przycisku przekierowuje na odpowiednia karte.                                                                                   | Karta z widokiem pacjentów.                                                                                 | Brak                                                                                                   |
| FR-14 | Podejrzenie karty pacjenta        | Możliwość sprawdzenia danych pacjenta, jego historii badań                                              | W                  | Po naciśnięciu karty pacjenta przekierowuje na jego podstrone.                                                                                 | Karta z informacjami na temat pacjenta.                                                                     | Najlepiej oddzielna podstrona, za dużo informacji.                                                     |
| FR-15 | Wprowadzanie wyników              | Możliwość dodania wyników do odbytej wizyty.                                                            | W                  | W hsitorii wizyt pacjenta przycisk na dodanie wyników, po wpisaniu danych w formularz i zaakcpetowaniu model AI ocenia ryzyko i zapisuje dane. | Napis "Pomyślnie wprowadzono" oraz widniejący stopień przy wizycie w zależności jaki został nadany przez AI | Brak                                                                                                   |
|       |                                   |                                                                                                         |                    |                                                                                                                                                |                                                                                                             |                                                                                                        |

* **Priorytet**: W – wymagane, M – mile widziane, N – niskiego priorytetu.

---

### 5. **Scenariusze użycia (Use Case)**

**UC-01 – Rejestracja nowego użytkownika**
- **Aktor:** Użytkownik
- **Cel:** Utworzenie konta
- **Warunki wstępne:** Brak konta w systemie
- **Przebieg główny:**
    1. Użytkownik wybiera opcję „Zarejestruj się”.
    2. System wyświetla formularz.
    3. Użytkownik wprowadza dane.
    4. System weryfikuje poprawność danych.
    5. System tworzy konto i wysyła e-mail potwierdzający.
- **Scenariusze alternatywne:**
    - 4a. Użytkownik wprowadza niepoprawny e-mail – system wyświetla komunikat o błędzie.

**UC-02 – Logowanie użytkownika**
- **Aktor:** Użytkownik
- **Cel:** Zalogowanie do systemu
- **Warunki wstępne:** Konto w systemie
- **Przebieg główny:**
    1. Użytkownik wybiera opcję „Zaloguj się”.
    2. System wyświetla formularz.
    3. Użytkownik wprowadza dane.
    4. System weryfikuje poprawność danych.
    5. System akceptuje dane.
- **Scenariusze alternatywne:**
    - 4a. Użytkownik wprowadza niepoprawny e-mail lub hasło – system wyświetla komunikat o błędzie.

**UC-03 – Przejście do odpowiedniego panelu
- **Aktor:** System
- **Cel:** Przejście do odpowiedniej karty
- **Warunki wstępne:** Konto w systemie
- **Przebieg główny:**
    1. Użytkownik klika „Zaloguj się”.
    2. System przetwarza dane.
    3. System weryfikuje poprawność danych.
    4. System przekierowuje na odpowiednią stronę w zależności od typu konta(pacjent/doktor).
- **Scenariusze alternatywne:**
    - 3a. Użytkownik wprowadza niepoprawne dane i zostaje wyświetlony o tym komunikat nad formularzem.
    - 4a. Użytkownik któremu nie zostały nadane żadne uprawnienia zawsze będzie traktowany jako pacjent.

**UC-04 – Historia wizyt
- **Aktor:** Użytkownik
- **Cel:** Przejście do karty z historią wizyt
- **Warunki wstępne:** Zalogowany jako pacjent w systemie
- **Przebieg główny:**
    1. Użytkownik klika zakładkę historia wizyt.
    2. System przekierowuje na odpowiednią stronę.
- **Scenariusze alternatywne:**
    - 1a. U użytkownika typu lekarz zakładka jest związana z spisem pacjentów.

**UC-05 – Szczegóły wizyty
- **Aktor:** Użytkownik
- **Cel:** Wyświetlenie szczegółów wizyty.
- **Warunki wstępne:** Zalogowany jako pacjent w systemie, znajduje się już na karcie historia wizyt.
- **Przebieg główny:**
    1. Użytkownik klika w wybraną wizytę.
    2. Wyświetlane są szczegóły dotyczące danej wizyty.
- **Scenariusze alternatywne:**
    - 1a. U użytkownika typu lekarz zakładka jest związana z spisem pacjentów.

**UC-06 – Zapisywanie wizyty
- **Aktor:** Użytkownik
- **Cel:** Zapisanie się na wizytę.
- **Warunki wstępne:** Zalogowany jako pacjent w systemie.
- **Przebieg główny:**
    1. Użytkownik klika w zakładkę zapisz się na wizytę na stronie głównej.
    2. Wyświetlany jest formularz.
    3. Użytkownik uzupełnia formularz.
    4. Użytkownik klika przycisk zapisz.
    5. Zostaje wyświetlony komunikat o pomyślnym zapisaniu.
- **Scenariusze alternatywne:**
    - 1a. U użytkownika typu lekarz zakładka nie istnieje.
    - 4a. W przypadku złego wypełnienia formularza np. zajęty termin aplikacja nie zarezerwuje wizytacji i nie przejdzie dalej.

**UC-07 – Edycja wizyty
- **Aktor:** Użytkownik
- **Cel:** Edycja zapisanej wizyty.
- **Warunki wstępne:** Zalogowany jako pacjent w systemie, jest już na karcie z nadchodzącymi wizytami.
- **Przebieg główny:**
    1. Użytkownik klika w przycisk edytuj obok wybranej wizyty.
    2. Wyświetlany jest formularz.
    3. Użytkownik uzupełnia formularz.
    4. Użytkownik klika przycisk zapisz.
    5. Zostaje wyświetlony komunikat o pomyślnej edycji wizyty.
- **Scenariusze alternatywne:**
    - 4a. W przypadku złego wypełnienia formularza np. zajęty termin aplikacja nie zarezerwuje wizytacji i nie przejdzie dalej.

**UC-08 – Anulowanie wizyty
- **Aktor:** Użytkownik
- **Cel:** Odwołanie zapisanej wizyty.
- **Warunki wstępne:** Zalogowany jako pacjent w systemie, jest już na karcie z nadchodzącymi wizytami.
- **Przebieg główny:**
    1. Użytkownik klika w przycisk odwołaj wizytę obok wybranej wizyty.
    2. Wyświetlany jest pop-up czy jest tego pewien?
    3. Użytkownik klika przycisk Tak.
    4. Zostaje wyświetlony komunikat o pomyślnym odwołaniy wizyty.
- **Scenariusze alternatywne:**
    - 3a. W przypadku kliknięcia nie proces zostanie anulowany a wizyta nie zostanie odwołana.

**UC-09 – Oglądanie swoich danych.
- **Aktor:** Użytkownik
- **Cel:** Przeglądanie własnego profilu i danych na nim.
- **Warunki wstępne:** Zalogowany jako pacjent w systemie.
- **Przebieg główny:**
    1. Użytkownik klika w zakładkę na stronie głównej "mój profil".
    2. Aplikacja przekierowuje na właściwą stronę.
- **Scenariusze alternatywne:**
    - 2a. Strona różni się dla użytkownika typu lekarz.

**UC-10 – Strona główna pacjenta.
- **Aktor:** Użytkownik
- **Cel:** Nawigacja po aplikacji.
- **Warunki wstępne:** Zalogowany jako pacjent w systemie.
- **Przebieg główny:**
    1. Użytkownik po zalogowaniu na swoje konto widzi bloki nawigacyjne z możliwością przejścia do interesującego go panelu.
- **Scenariusze alternatywne:**
    - 1a. Strona różni się dla użytkownika typu lekarz.

**UC-11 – Strona główna lekarza.
- **Aktor:** Użytkownik
- **Cel:** Nawigacja po aplikacji.
- **Warunki wstępne:** Zalogowany jako lekarz w systemie.
- **Przebieg główny:**
    1. Użytkownik po zalogowaniu na swoje konto widzi bloki nawigacyjne z możliwością przejścia do interesującego go panelu.
- **Scenariusze alternatywne:**
    - 1a. Strona różni się dla użytkownika typu pacjent.

**UC-12 – Najbliższe wizyty.
- **Aktor:** Użytkownik
- **Cel:** Podejrzenie najbliższych wizyt.
- **Warunki wstępne:** Zalogowany jako lekarz w systemie.
- **Przebieg główny:**
    1. Użytkownik klika w panel najbliższe wizyty na stronie głównej.
    2. Zostaje przekierowany na widok z kalendarzem/lista najbliższych wizyt pacjentów.
- **Scenariusze alternatywne:**
    - 1a. Użytkownika typu pacjent nie posiada tego panelu.

**UC-13 – Spis pacjentów.
- **Aktor:** Użytkownik
- **Cel:** Podejrzenie spisu swoich pacjentów.
- **Warunki wstępne:** Zalogowany jako lekarz w systemie.
- **Przebieg główny:**
    1. Użytkownik klika w panel spis pacjentów na stronie głównej.
    2. Zostaje przekierowany na widok z listą swoich pacjentów.
- **Scenariusze alternatywne:**
    - 1a. Użytkownika typu pacjent nie posiada tego panelu.

**UC-14 – Podejrzenie karty pacjenta.
- **Aktor:** Użytkownik
- **Cel:** Podejrzenie informacji o pacjencie.
- **Warunki wstępne:** Zalogowany jako lekarz w systemie, znajduje się na karcie spis pacjentów.
- **Przebieg główny:**
    1. Użytkownik klika w pacjenta w spisie pacjentów.
    2. Zostaje przekierowany na karte z informacjami na temat danego pacjenta.
- **Scenariusze alternatywne:**
    - 1a. Użytkownika typu pacjent nie posiada tego panelu.

**UC-15 – Wprowadzanie wyników.
- **Aktor:** Użytkownik
- **Cel:** Podejrzenie spisu swoich pacjentów.
- **Warunki wstępne:** Zalogowany jako lekarz w systemie, znajduje się na karcie informacji o pacjencie
- **Przebieg główny:**
    1. Użytkownik klika w pacjenta w spisie pacjentów.
    2. Zostaje przekierowany na karte z informacjami na temat danego pacjenta.
    3. W bloku z historiami o wizycie klika dodaj wyniki.
    4. Wyskakuje formularz z danymi które wypełnia.
    5. Klika przycisk zatwierdź.
    6. Dane są przekazane modelowi AI który ocenia wyniki pacjenta.
    7. Wyświetla się informacja o pomyślnym przetworzeniu danych a obok wizyty pojawia się ocena wyniku badań nadana przez wytrenowany model.
- **Scenariusze alternatywne:**
    - 1a. Użytkownika typu pacjent nie posiada tego panelu.
    - 5a. Aby przycisk zadziałał dane muszą być właściwe.
    - 6a. Jeśli model działa poprawnie i jest z nim właściwe połączenie.
    - 7a. W przypadku braku połączenia lub innym błędzie wyskoczy komunikat o nieudanej próbie przypisania wyników.

---
### 6. **Ograniczenia**

Należy sprawdzić RODO pod względem ograniczeń prawnych w kwestii wyświetlania danych pacjentów oraz zoptymalizować model tak aby ocena przy wynikach nie była zbyt długa i nie zajmował on za dużo miejsca w pamięci urządzenia.

---
### 7. **Kryteria akceptacji**

- Ocena wyników pacjenta.
- Historia wizyt
- Możliwość zapisywania na wizytę
- Logowanie i rejestracja
- Różne GUI w zależności czy pacjent czy lekarz.

---

### 8. **Historia zmian**

| Wersja | Data       | Autor       | Opis zmian                                        |
| ------ | ---------- | ----------- | ------------------------------------------------- |
| 0.01   | 13/08/2025 | Marcin Kruk | Pierwsza iteracja pliku, uzupełnienie o podstawy. |

