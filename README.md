# Lawmap - Dostępność w polskim prawie

Projekt zawiera schemat ilustrujący hierarchię aktów prawnych dotyczących dostępności w polskim prawie. Schemat został stworzony przy użyciu [Mermaid](https://mermaid.js.org/) i jest dostępny w dwóch formatach:

*   `lawmap.mmd` - Plik źródłowy Mermaid, który definiuje schemat.
*   `lawmap.svg` - Wygenerowany plik SVG, będący graficzną reprezentacją schematu.

## Opis

Schemat przedstawia zależności między różnymi aktami prawnymi regulującymi kwestie dostępności w Polsce, w tym Konstytucją RP, umowami międzynarodowymi, dyrektywami UE, ustawami i rozporządzeniami.

## Pliki

*   `lawmap.yaml` - **jedyne źródło danych**: akty, ich identyfikatory (ELI, CELEX), opisy i relacje. Zmiany wprowadzamy tylko tutaj.
*   `lawmap.py` - skrypt, który sprawdza status aktów w ELI i generuje pozostałe pliki.
*   `stan.json` - status polskich aktów pobrany z API ELI Sejmu (generowany).
*   `lawmap.mmd` - schemat Mermaid (generowany).
*   `lawmap.md` - **tekstowa wersja schematu**, z nagłówkami i listami, wygodna dla czytników ekranu (generowana).
*   `lawmap.svg` - graficzna wersja schematu.

## Aktualizacja

Potrzebny jest [uv](https://docs.astral.sh/uv/). Zależności (PyYAML) instaluje się same.

```bash
uv run lawmap.py            # sprawdza status w ELI i generuje lawmap.mmd oraz lawmap.md
uv run lawmap.py sprawdz    # tylko sprawdzenie statusu (stan.json)
uv run lawmap.py generuj    # tylko generowanie z lawmap.yaml i stan.json
npx -y @mermaid-js/mermaid-cli -i lawmap.mmd -o lawmap.svg
```

Skrypt oznacza akty, które według ELI nie obowiązują (szare pole i dopisek „nie obowiązuje”), i wypisuje zmiany statusu od poprzedniego sprawdzenia. Akty unijne (CELEX) i normy nie są sprawdzane automatycznie.

### Pola w `lawmap.yaml`

| Pole | Znaczenie |
|---|---|
| `id` | krótki identyfikator, używany w relacjach i w schemacie |
| `skrot` | nazwa wyświetlana w schemacie |
| `poziom` | `konstytucja`, `miedzynarodowe`, `ustawy`, `rozporzadzenia`, `normy` |
| `typ` | np. `ustawa`, `rozporzadzenie`, `dyrektywa_ue`, `norma`, `wytyczne` |
| `eli` | identyfikator ELI, np. `DU/2019/1696`; pełny tytuł i status pobiera skrypt |
| `celex` | identyfikator EUR-Lex aktów unijnych |
| `url`, `tytul` | dla dokumentów spoza ELI i EUR-Lex |
| `opis`, `uwagi` | krótkie objaśnienie i zastrzeżenia (np. wątpliwy stan prawny) |

Typy relacji: `zrodlo`, `transpozycja`, `implementacja`, `delegacja`, `zmienia`, `odwolanie`, `norma`, `zastapiony_przez`.

## Wyświetlanie schematu

Tu możesz obejrzeć [wyrenderowany schemat w postaci graficznej.](https://github.com/JacZad/lawmap/blob/main/lawmap.mmd)

Wyrenderowany schemat SVG jest mało dostępny dla czytników ekranu. Dlatego plik [lawmap.md](lawmap.md) zawiera tę samą treść w postaci tekstu: każdy akt ma nagłówek, status i listę powiązań w obu kierunkach.

## Zgłaszanie błędów i propozycje

Jeśli znajdziesz błędy w schemacie lub masz propozycje dodania kolejnych przepisów, proszę o zgłoszenie ich poprzez [Issues](https://github.com/jaczad/lawmap/issues). Będę wdzięczny za wszelkie uwagi i sugestie!

## Licencja

Ten projekt jest udostępniany na licencji [MIT](LICENSE).
    