"""
SUSTAV ZA ŠIFRIRANJE - ENKRIPTIRANJE
Opis: Implementacija Caesar, Vigenère i kolumnarne transpozicije za enkriptiranje
"""

# Definiranje hrvatskog alfabeta s dodatnim znakovima
HR_ALFABET = "ABCČĆDĐEFGHIJKLMNOPRSŠTUVZŽ"


def caesar_enkript(text, shift, alphabet=HR_ALFABET):
    """
    Caesar šifra - enkriptiranje
    Svaki znak se pomiče za određeni broj pozicija unatrag u alfabetu
    """
    n = len(alphabet)  # Ukupan broj znakova u alfabetu

    # Koristimo generator expression za obradu svakog znaka
    return "".join(
        # Ako je znak u velikim slovima alfabeta
        alphabet[(alphabet.index(ch) - shift) % n] if ch in alphabet
        # Ako je znak u malim slovima alfabeta
        else alphabet.lower()[(alphabet.lower().index(ch) - shift) % n]
        if ch.lower() in alphabet.lower()
        # Ako znak nije u alfabetu (razmaci, interpunkcija), ostavi ga kako jest
        else ch
        for ch in text  # Prođi kroz svaki znak u tekstu
    )


def vigenere_enkript(text, password, key):
    """\
    Vigenère šifra - enkriptiranje
    Koristi ključ za kreiranje keyed alphabet-a i lozinku za šifriranje
    """
    # Osnovni hrvatski alfabet
    base = "ABCČĆDĐEFGHIJKLMNOPRSŠTUVZŽ"

    # Kreiranje keyed alphabet-a: ključ + osnovni alfabet (bez duplikata)
    # dict.fromkeys() čuva redoslijed i uklanja duplikate
    keyed = "".join(dict.fromkeys(key.upper() + base))

    n = len(keyed)  # Duljina keyed alphabet-a
    res = []  # Lista za rezultat
    p = 0  # Indeks za lozinku

    # Prođi kroz svaki znak u tekstu
    for ch in text:
        # Provjeri je li znak u keyed alphabet-u
        if ch.upper() in keyed:
            # Pronađi poziciju trenutnog znaka lozinke (redak u tablici)
            row = keyed.index(password[p % len(password)].upper())

            # Pronađi poziciju znaka teksta (stupac u tablici)
            col = keyed.index(ch.upper())

            # Enkriptiraj: (redak + stupac) mod n
            enc = keyed[(row + col) % n]

            # Zadrži originalnu veličinu slova
            res.append(enc.lower() if ch.islower() else enc)

            # Pomakni se na sljedeći znak lozinke
            p += 1
        else:
            # Ako znak nije u alfabetu, dodaj ga nepromijenjenog
            res.append(ch)

    return "".join(res)


def columnar_enkript(text, key):
    """
    Kolumnarna transpozicija - enkriptiranje
    Tekst se upisuje u matricu redak-po-redak, a čita stupac-po-stupac
    prema redoslijedu određenom ključem
    """
    cols = len(key)  # Broj stupaca = duljina ključa
    rows = (len(text) + cols - 1) // cols  # Broj redaka (zaokruženo naviše)

    # KORAK 1: Kreiranje prazne matrice
    grid = [['' for _ in range(cols)] for _ in range(rows)]

    # KORAK 2: Popunjavanje matrice redak-po-redak
    idx = 0
    for r in range(rows):  # Za svaki red
        for c in range(cols):  # Za svaki stupac
            if idx < len(text):  # Ako još ima znakova
                grid[r][c] = text[idx]
                idx += 1

    # KORAK 3: Određivanje redoslijeda stupaca
    # Svaka znamenka ključa govori koji će stupac biti na toj poziciji
    # Npr. ključ '24513' znači: 1.stupac=2, 2.stupac=4, 3.stupac=5, 4.stupac=1, 5.stupac=3
    order = [int(d) - 1 for d in key]  # Pretvaramo u 0-indeksirane pozicije

    # KORAK 4: Čitanje stupaca prema redoslijedu
    cipher = []
    for col in order:  # Za svaki stupac u određenom redoslijedu
        for row in range(rows):  # Čitaj sve redove tog stupca
            if grid[row][col]:  # Ako postoji znak (nije prazan)
                cipher.append(grid[row][col])

    return ''.join(cipher)


def main():
    """
    Glavna funkcija - korisničko sučelje za enkriptiranje
    """
    print("=== HRVATSKI SUSTAV ZA ŠIFRIRANJE ===\n")

    # Beskonačna petlja za meni
    while True:
        # Prikaz opcija
        print("Odaberite metodu:")
        print("1 – Caesar šifra")
        print("2 – Vigenère šifra")
        print("3 – Kolumnarna transpozicija")
        print("4 – Izlaz")

        choice = input("Odabir: ")

        if choice == "1":
            # CAESAR ŠIFRA
            t = input("Tekst: ")
            # Omogući korisniku da unese vlastiti alfabet ili koristi zadani
            a = input("Alfabet (ENTER=zadani): ") or HR_ALFABET
            s = int(input("Pomak: "))
            print("Šifrat:", caesar_enkript(t, s, a), "\n")

        elif choice == "2":
            # VIGENÈRE ŠIFRA
            t = input("Tekst: ")
            key = input("Ključ: ")  # Ključ za kreiranje keyed alphabet-a
            pwd = input("Lozinka: ")  # Lozinka za šifriranje
            print("Šifrat:", vigenere_enkript(t.upper(), pwd, key), "\n")

        elif choice == "3":
            # KOLUMNARNA TRANSPOZICIJA
            t = input("Tekst: ").replace(" ", "")  # Ukloni razmake
            k = input("Ključ: ")  # Numerički ključ (npr. '24513')
            print("Šifrat:", columnar_enkript(t.upper(), k), "\n")

        elif choice == "4":
            # Izlaz iz programa
            break

        else:
            print("Pogrešan odabir!")


# Pokretanje programa
if __name__ == "__main__":
    main()
