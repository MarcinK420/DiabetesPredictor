```markdown
# Project: Diabetes Risk Predictor

Poniżej znajduje się szczegółowy plan (TASKS.md) podzielony na małe tickety, które pomogą Ci w realizacji projektu krok po kroku.

---

## 1. Przygotowanie środowiska

- [ ] **TICKET-001:** Utworzenie wirtualnego środowiska Python (venv/conda) i instalacja podstawowych pakietów
- [ ] **TICKET-002:** Inicjalizacja repozytorium Git i stworzenie struktury katalogów
  - `data/`, `notebooks/`, `src/model/`, `src/webapp/`, `docs/`, `tests/`
- [ ] **TICKET-003:** Skonfigurowanie pliku `.gitignore` oraz `requirements.txt`

## 2. Zbieranie i wstępna analiza danych

- [ ] **TICKET-004:** Pozyskanie datasetu (np. Pima Indians Diabetes Database) z internetu
- [ ] **TICKET-005:** Wczytanie danych do Jupyter Notebook w `notebooks/` i wstępne EDA
  - Sprawdzenie braków danych
  - Podstawowe statystyki opisowe
  - Rozkład klas (proporcja pacjentów zdrowych vs chorych)

## 3. Przetwarzanie danych

- [ ] **TICKET-006:** Implementacja skryptu do czyszczenia danych (`src/model/preprocessing.py`)
  - Usuwanie/uzupełnianie braków
  - Skalowanie i standaryzacja cech
- [ ] **TICKET-007:** Feature engineering (opcjonalnie tworzenie dodatkowych cech)
- [ ] **TICKET-008:** Podział na zbiory treningowy/walidacyjny/testowy

## 4. Budowa i przetrenowanie modelu

- [ ] **TICKET-009:** Wybór algorytmów (np. Logistic Regression, RandomForest, XGBoost)
- [ ] **TICKET-010:** Implementacja skryptu treningowego (`src/model/train.py`)
  - GridSearchCV do strojenia hiperparametrów
- [ ] **TICKET-011:** Ewaluacja modeli w notebooku (`notebooks/model_evaluation.ipynb`)
  - Metryki: accuracy, precision, recall, ROC-AUC
- [ ] **TICKET-012:** Zapisanie wytrenowanego modelu (pickle/Joblib) do `src/model/artifacts/`

## 5. Integracja modelu z serwerem Django

- [ ] **TICKET-013:** Utworzenie projektu Django (`src/webapp/`) i aplikacji `predictor`
- [ ] **TICKET-014:** Konfiguracja środowiska Django (ustawienia, baza danych SQLite)
- [ ] **TICKET-015:** Stworzenie widoku (View) obsługującego formularz wejściowy i wynik
- [ ] **TICKET-016:** Przygotowanie szablonów HTML (formularz i strona wyników) w `templates/`
- [ ] **TICKET-017:** Dodanie URL routing dla aplikacji `predictor`
- [ ] **TICKET-018:** Ładowanie modelu pickle w Django (np. w `apps.py` lub `views.py`)
- [ ] **TICKET-019:** Implementacja logiki predykcji w widoku

## 6. Interfejs użytkownika

- [ ] **TICKET-020:** Stylizacja formularza za pomocą Bootstrap / Tailwind
- [ ] **TICKET-021:** Walidacja danych wejściowych po stronie frontu i back-endu
- [ ] **TICKET-022:** Dodanie komunikatów o błędach i informacji o ryzyku

## 7. Testy i zapewnienie jakości

- [ ] **TICKET-023:** Testy jednostkowe dla skryptów preprocessingu i treningu (`pytest`)
- [ ] **TICKET-024:** Testy integracyjne dla widoków Django
- [ ] **TICKET-025:** CI/CD z GitHub Actions (uruchamianie testów przy każdym pushu)

## 8. Docker i wdrożenie

- [ ] **TICKET-026:** Utworzenie pliku `Dockerfile` dla aplikacji Django + modelu
- [ ] **TICKET-027:** Konfiguracja `docker-compose.yml` (web + ewent. baza danych)
- [ ] **TICKET-028:** Wdrażanie na platformie (Heroku / AWS Elastic Beanstalk / DigitalOcean)
- [ ] **TICKET-029:** Konfiguracja zmiennych środowiskowych i pliku `.env`

## 9. Dokumentacja i utrzymanie

- [ ] **TICKET-030:** Uzupełnienie `README.md` instrukcją instalacji i użycia
- [ ] **TICKET-031:** Przygotowanie krótkiej prezentacji / demo w `docs/`
- [ ] **TICKET-032:** Monitoring (Sentry / Prometheus) oraz zbieranie logów

---

*Każdy ticket powinien mieć swój oddzielny branch (`feature/TICKET-XXX-opis`) i pull request. Powodzenia!*  
```

