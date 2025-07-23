```markdown
# Info o projekcie Diabetes Risk Predictor

Poniższy plik możesz wkleić do czata, aby szybko przekazać kontekst aplikacji, nad którą pracujesz.

---

## 1. Nazwa projektu

**Diabetes Risk Predictor**

## 2. Cel aplikacji

Aplikacja webowa pozwalająca na ocenę ryzyka zachorowania na cukrzycę u pacjenta na podstawie wprowadzonego zestawu cech (wiek, BMI, poziom glukozy, itp.) i wytrenowanego modelu ML.

## 3. Główne komponenty

1. **Model predykcji (Python)**
   - Preprocessing danych
   - Trening modeli ML (Logistic Regression, RandomForest, XGBoost)
   - Zapis i ładowanie artefaktów (pickle/Joblib)
2. **Interfejs użytkownika (Django)**
   - Formularz wejściowy
   - Widok wyświetlający wynik ryzyka
   - Szablony HTML + CSS (Bootstrap/Tailwind)
3. **Testy**
   - Jednostkowe (pytest)
   - Integracyjne (Django TestCase)
4. **CI/CD**
   - GitHub Actions
   - Docker + docker-compose
   - Wdrożenie (Heroku/AWS/DigitalOcean)

## 4. Struktura repozytorium

```

├── data/                   # Surowe i przetworzone dane ├── notebooks/             # Notatniki Jupyter (EDA, ewaluacja) ├── src/ │   ├── model/             # Skrypty ML (preprocessing, train, infer) │   └── webapp/            # Projekt Django │       ├── predictor/     # Aplikacja Django │       └── ...            # Ustawienia, statyczne pliki, templates ├── tests/                 # Testy jednostkowe i integracyjne ├── docs/                  # Dokumentacja, prezentacje ├── Dockerfile             # Konfiguracja obrazu Docker ├── docker-compose.yml     # Kompozycja serwisów ├── requirements.txt       # Zależności Python ├── .gitignore └── README.md

````

## 5. Jak uruchomić lokalnie

1. Klon repozytorium:
   ```bash
   git clone <repo-url>
   cd <project-folder>
````

2. Stworzenie wirtualnego środowiska i instalacja zależności:
   ```bash
   python -m venv venv
   source venv/bin/activate  # lub `venv\\Scripts\\activate` na Windows
   pip install -r requirements.txt
   ```
3. Migracje bazy danych Django:
   ```bash
   cd src/webapp
   python manage.py migrate
   ```
4. Uruchomienie serwera deweloperskiego:
   ```bash
   python manage.py runserver
   ```

## 6. Kontakt

- **Autor**: [Twoje Imię]
- **Email**: [twoj.email@domena.com](mailto\:twoj.email@domena.com)
- **GitHub**: [https://github.com/twoj/u…](https://github.com/twoj/u…)

---

*Wklej ten plik przy potrzebie szybkiego przekazania kontekstu projektu.*

```
```
