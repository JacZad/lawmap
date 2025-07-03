# Lawmap - Dostępność w polskim prawie

Projekt zawiera schemat ilustrujący hierarchię aktów prawnych dotyczących dostępności w polskim prawie. Schemat został stworzony przy użyciu [Mermaid](https://mermaid.js.org/) i jest dostępny w dwóch formatach:

*   `lawmap.mmd` - Plik źródłowy Mermaid, który definiuje schemat.
*   `lawmap.svg` - Wygenerowany plik SVG, będący graficzną reprezentacją schematu.

## Opis

Schemat przedstawia zależności między różnymi aktami prawnymi regulującymi kwestie dostępności w Polsce, w tym Konstytucją RP, umowami międzynarodowymi, dyrektywami UE, ustawami i rozporządzeniami.

## Technologie

*   [Mermaid](https://mermaid.js.org/) - język znaczników i narzędzie do generowania diagramów i schematów blokowych z tekstu.

## Pliki

*   `lawmap.mmd` - Plik źródłowy Mermaid zawierający definicję schematu. Można go edytować w dowolnym edytorze tekstowym i renderować za pomocą narzędzi Mermaid.
*   `lawmap.svg` - Plik SVG (Scalable Vector Graphics) zawierający graficzną reprezentację schematu. Można go wyświetlać w przeglądarkach internetowych i edytorach grafiki wektorowej.

## Jak wygenerować plik SVG

Plik SVG można wygenerować z pliku `lawmap.mmd` za pomocą narzędzi Mermaid. Na przykład, używając [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli):

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i lawmap.mmd -o lawmap.svg
```

Upewnij się, że masz zainstalowany [Node.js](https://nodejs.org/) i [npm](https://www.npmjs.com/) przed uruchomieniem powyższych poleceń.

## Wyświetlanie schematu

Tu możesz obejrzeć [wyrenderowany schemat w postaci graficznej.](https://github.com/JacZad/lawmap/blob/main/lawmap.mmd)

**Uwaga dla użytkowników czytników ekranu:** Wyrenderowany schemat SVG jest mało dostępny dla czytników ekranu. Już trochę pracują nad tym w Mermaid. Na ten moment proponuję korzystanie z pliku źródłowego, który jest czysto tekstowy i ma prostą strukturę.

## Zgłaszanie błędów i propozycje

Jeśli znajdziesz błędy w schemacie lub masz propozycje dodania kolejnych przepisów, proszę o zgłoszenie ich poprzez [Issues](https://github.com/jaczad/lawmap/issues). Będę wdzięczny za wszelkie uwagi i sugestie!

## Licencja

Ten projekt jest udostępniany na licencji [MIT](LICENSE).
