# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Lawmap: kontrola stanu aktów w ELI i generowanie schematu oraz wersji tekstowej.

    uv run lawmap.py sprawdz    # pobiera status aktów z API ELI Sejmu do stan.json
    uv run lawmap.py generuj    # tworzy lawmap.mmd i lawmap.md z lawmap.yaml i stan.json
    uv run lawmap.py            # oba kroki

Źródłem danych jest wyłącznie lawmap.yaml. Pliki lawmap.mmd, lawmap.md i stan.json są generowane.
"""

import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
ELI_API = "https://api.sejm.gov.pl/eli/acts/"
TYPY_RELACJI = {
    "zrodlo": "jest źródłem dla",
    "transpozycja": "jest transponowana przez",
    "implementacja": "jest wdrażane przez",
    "delegacja": "upoważnia do wydania",
    "zmienia": "zmienia",
    "odwolanie": "odwołuje się do",
    "norma": "przywołuje normę",
    "zastapiony_przez": "został zastąpiony przez",
}
# Odwrotne opisy relacji w wersji tekstowej („Ustawa X: transponuje dyrektywę Y”).
TYPY_RELACJI_ODWROTNE = {
    "zrodlo": "wynika z",
    "transpozycja": "transponuje",
    "implementacja": "wdraża",
    "delegacja": "wydane na podstawie",
    "zmienia": "zmieniany przez",
    "odwolanie": "przywoływany przez",
    "norma": "przywoływana przez",
    "zastapiony_przez": "zastępuje",
}
ETYKIETY_MERMAID = {
    "transpozycja": "transpozycja",
    "implementacja": "implementacja",
    "delegacja": "delegacja",
    "zmienia": "zmienia",
    "odwolanie": "odwołanie",
    "norma": "norma techniczna",
    "zastapiony_przez": "zastąpiony przez",
}
KLASY = {
    "konstytucja": "pl_konstytucja",
    "umowa_miedzynarodowa": "ue",
    "traktat_ue": "ue",
    "dyrektywa_ue": "ue",
    "rozporzadzenie_ue": "ue",
    "ustawa": "pl_ustawa",
    "rozporzadzenie": "pl_rozporzadzenie",
    "dokument_urzedowy": "pl_rozporzadzenie",
    "norma": "standard",
    "wytyczne": "standard",
}


def wczytaj() -> dict:
    dane = yaml.safe_load((ROOT / "lawmap.yaml").read_text(encoding="utf-8"))
    ids = [akt["id"] for akt in dane["akty"]]
    powtorzone = {i for i in ids if ids.count(i) > 1}
    if powtorzone:
        sys.exit(f"Powtórzone identyfikatory aktów: {sorted(powtorzone)}")
    poziomy = {p["id"] for p in dane["poziomy"]}
    for akt in dane["akty"]:
        if akt["poziom"] not in poziomy:
            sys.exit(f"{akt['id']}: nieznany poziom {akt['poziom']}")
    for rel in dane["relacje"]:
        for koniec in (rel["z"], rel["do"]):
            if koniec not in ids:
                sys.exit(f"Relacja {rel}: nieznany akt {koniec}")
        if rel["typ"] not in TYPY_RELACJI:
            sys.exit(f"Relacja {rel}: nieznany typ")
    return dane


def wczytaj_stan() -> dict:
    plik = ROOT / "stan.json"
    return json.loads(plik.read_text(encoding="utf-8")) if plik.exists() else {}


def link(akt: dict) -> str | None:
    # Portal ELI zamiast ISAP: identyfikator ISAP starszych aktów zawiera numer dziennika,
    # którego nie da się wyprowadzić z identyfikatora ELI.
    if akt.get("eli"):
        return f"https://eli.gov.pl/eli/{akt['eli']}/ogl"
    if akt.get("celex"):
        return f"https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:{akt['celex']}"
    return akt.get("url")


def tytul(akt: dict, stan: dict) -> str:
    return stan.get(akt["id"], {}).get("tytul") or akt.get("tytul") or akt["skrot"]


def obowiazuje(akt: dict, stan: dict) -> bool | None:
    return stan.get(akt["id"], {}).get("obowiazuje")


def sprawdz() -> int:
    dane = wczytaj()
    stary = wczytaj_stan()
    stan, zmiany = {}, []
    for akt in dane["akty"]:
        if not akt.get("eli"):
            continue
        try:
            with urllib.request.urlopen(ELI_API + akt["eli"], timeout=30) as odp:
                eli = json.load(odp)
        except (urllib.error.URLError, TimeoutError) as blad:
            print(f"BŁĄD  {akt['id']:<22} {akt['eli']}: {blad}")
            if akt["id"] in stary:
                stan[akt["id"]] = stary[akt["id"]]
            continue
        wpis = {
            "eli": akt["eli"],
            "tytul": " ".join(eli["title"].split()).rstrip("."),
            "status": eli.get("status"),
            "obowiazuje": eli.get("inForce") == "IN_FORCE",
            "uchylony_od": eli.get("repealDate"),
            "sprawdzono": date.today().isoformat(),
        }
        stan[akt["id"]] = wpis
        poprzedni = stary.get(akt["id"], {})
        if poprzedni and poprzedni.get("status") != wpis["status"]:
            zmiany.append(f"{akt['id']}: {poprzedni.get('status')} -> {wpis['status']}")
        znak = "OK   " if wpis["obowiazuje"] else "UWAGA"
        print(f"{znak} {akt['id']:<22} {akt['eli']:<14} {wpis['status']}")

    (ROOT / "stan.json").write_text(
        json.dumps(stan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    nieobowiazujace = [k for k, v in stan.items() if not v["obowiazuje"]]
    print(f"\nSprawdzono {len(stan)} aktów, nie obowiązuje: {len(nieobowiazujace)}.")
    for zmiana in zmiany:
        print(f"ZMIANA STATUSU: {zmiana}")
    return 0


def mermaid(dane: dict, stan: dict) -> str:
    meta = dane["meta"]
    linie = [
        "---",
        f"title: '{meta['tytul']}'",
        f"author: '{meta['autor']}'",
        f"description: '{' '.join(meta['opis'].split())}'",
        "---",
        "%% Plik generowany z lawmap.yaml (uv run lawmap.py generuj). Nie edytuj ręcznie.",
        "",
        "graph TD",
        "    classDef ue fill:#003399,color:#fff,stroke:#000,stroke-width:2px;",
        "    classDef pl_konstytucja fill:#D22730,color:#fff,stroke:#000,stroke-width:4px;",
        "    classDef pl_ustawa fill:#fff,color:#000,stroke:#D22730,stroke-width:2px;",
        "    classDef pl_rozporzadzenie fill:#fff,color:#000,stroke:#D22730,"
        "stroke-width:1px,stroke-dasharray: 5 5;",
        "    classDef standard fill:#f2f2f2,color:#000,stroke:#000,stroke-width:1px;",
        "    classDef nieobowiazujacy fill:#e5e5e5,color:#555,stroke:#555,"
        "stroke-width:1px,stroke-dasharray: 2 2;",
        "",
    ]
    for poziom in dane["poziomy"]:
        linie.append(f'    subgraph {poziom["id"]}_grupa ["{poziom["nazwa"]}"]')
        for akt in dane["akty"]:
            if akt["poziom"] == poziom["id"]:
                etykieta = akt["skrot"]
                if obowiazuje(akt, stan) is False:
                    etykieta += " (nie obowiązuje)"
                linie.append(f'        {akt["id"]}["{etykieta}"]')
        linie.append("    end")
    linie.append("")
    for rel in dane["relacje"]:
        etykieta = ETYKIETY_MERMAID.get(rel["typ"])
        strzalka = f' --"{etykieta}"--> ' if etykieta else " --> "
        linie.append(f"    {rel['z']}{strzalka}{rel['do']}")
    linie.append("")
    for akt in dane["akty"]:
        klasa = "nieobowiazujacy" if obowiazuje(akt, stan) is False else KLASY[akt["typ"]]
        linie.append(f"    class {akt['id']} {klasa}")
    linie.append("")
    for akt in dane["akty"]:
        if url := link(akt):
            opis = tytul(akt, stan).replace('"', "'")
            linie.append(f'    click {akt["id"]} "{url}" "{opis}"')
    return "\n".join(linie) + "\n"


def tekst(dane: dict, stan: dict) -> str:
    akty = {akt["id"]: akt for akt in dane["akty"]}
    sprawdzono = max((v["sprawdzono"] for v in stan.values()), default=None)
    linie = [
        "---",
        "lang: pl",
        "---",
        "",
        f"# {dane['meta']['tytul']}",
        "",
        "Tekstowa wersja schematu z pliku `lawmap.mmd`. Plik jest generowany z `lawmap.yaml`"
        " (`uv run lawmap.py generuj`), nie edytuj go ręcznie.",
        "",
    ]
    if sprawdzono:
        linie += [f"Status aktów polskich sprawdzony w ELI: {sprawdzono}.", ""]
    for poziom in dane["poziomy"]:
        linie += [f"## {poziom['nazwa']}", ""]
        for akt in (a for a in dane["akty"] if a["poziom"] == poziom["id"]):
            url = link(akt)
            naglowek = f"[{akt['skrot']}]({url})" if url else akt["skrot"]
            linie += [f"### {naglowek}", ""]
            if tytul(akt, stan) != akt["skrot"]:
                linie += [tytul(akt, stan) + ".", ""]
            wpis = stan.get(akt["id"])
            if wpis:
                status = wpis["status"]
                if wpis.get("uchylony_od"):
                    status += f" od {wpis['uchylony_od']}"
                if not wpis["obowiazuje"]:
                    status = f"**Nie obowiązuje** ({status})"
                linie += [f"Status: {status}. ELI: {akt['eli']}.", ""]
            for pole in ("opis", "uwagi"):
                if akt.get(pole):
                    prefiks = "Uwaga: " if pole == "uwagi" else ""
                    linie += [prefiks + " ".join(akt[pole].split()), ""]
            powiazania = [
                f"{TYPY_RELACJI[r['typ']]}: {akty[r['do']]['skrot']}"
                for r in dane["relacje"]
                if r["z"] == akt["id"]
            ] + [
                f"{TYPY_RELACJI_ODWROTNE[r['typ']]}: {akty[r['z']]['skrot']}"
                for r in dane["relacje"]
                if r["do"] == akt["id"]
            ]
            if powiazania:
                linie += ["Powiązania:", ""] + [f"* {p}" for p in powiazania] + [""]
    return "\n".join(linie)


def generuj() -> int:
    dane, stan = wczytaj(), wczytaj_stan()
    (ROOT / "lawmap.mmd").write_text(mermaid(dane, stan), encoding="utf-8")
    (ROOT / "lawmap.md").write_text(tekst(dane, stan), encoding="utf-8")
    print(f"Zapisano lawmap.mmd i lawmap.md ({len(dane['akty'])} aktów, "
          f"{len(dane['relacje'])} relacji).")
    return 0


if __name__ == "__main__":
    polecenie = sys.argv[1] if len(sys.argv) > 1 else "wszystko"
    if polecenie == "sprawdz":
        sys.exit(sprawdz())
    if polecenie == "generuj":
        sys.exit(generuj())
    if polecenie == "wszystko":
        sys.exit(sprawdz() or generuj())
    sys.exit(__doc__)
