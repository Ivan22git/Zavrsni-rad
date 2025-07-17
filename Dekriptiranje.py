# -*- coding: utf-8 -*-
"""
SUSTAV ZA DEKRIPTIRANJE
Opis: Implementacija Caesar, Vigenère i kolumnarne transpozicije za dekriptiranje
"""

# Definiranje hrvatskog alfabeta
HR_ALFABET = "ABCČĆDĐEFGHIJKLMNOPRSŠTUVZŽ12345&"


def caesar_dekript(cipher, shift, alphabet=HR_ALFABET):
    """
    Caesar šifra - DEKRIPTIRANJE
    Pomičemo se unaprijed za zadani broj pozicija
    """
    n = len(alphabet)
    return "".join(
        alphabet[(alphabet.index(ch) + shift) % n] if ch in alphabet
        else alphabet.lower()[(alphabet.lower().index(ch) + shift) % n]
        if ch.lower() in alphabet.lower() else ch
        for ch in cipher
    )


def vigenere_dekript(cipher, password, key):
    """
    Vigenère šifra - DEKRIPTIRANJE
    Inverzno: (stupac - redak) mod n
    """
    base = "ABCČĆDĐEFGHIJKLMNOPRSŠTUVZŽ"
    keyed = "".join(dict.fromkeys(key.upper() + base))
    n, res, p = len(keyed), [], 0
    for ch in cipher:
        if ch.upper() in keyed:
            row = keyed.index(password[p % len(password)].upper())
            col = keyed.index(ch.upper())
            dec = keyed[(col - row) % n]
            res.append(dec.lower() if ch.islower() else dec)
            p += 1
        else:
            res.append(ch)
    return "".join(res)


def columnar_dekript(cipher, key):
    """
    Kolumnarna transpozicija - DEKRIPTIRANJE
    Puni se stupac-po-stupac pa se čita redak-po-redak
    """
    cols = len(key)
    rows = (len(cipher) + cols - 1) // cols

    # KORAK 1: Konstruktiraj praznu matricu
    grid = [['' for _ in range(cols)] for _ in range(rows)]

    # KORAK 2: Odredi permutaciju stupaca (0-indeksirano)
    order = [int(d) - 1 for d in key]

    # KORAK 3: Broj znakova po stupcu (ne mora biti jednak za sve)
    col_heights = [rows] * cols
    extra = len(cipher) % cols
    if extra:
        # Zadnjih 'extra' stupaca imat će po jedan znak manje
        for i in range(cols - extra):
            col_heights[order[-(i + 1)]] -= 1

    # KORAK 4: Popuni stupce redom iz ključa
    idx = 0
    for col in order:
        h = col_heights[col]
        for r in range(h):
            grid[r][col] = cipher[idx]
            idx += 1

    # KORAK 5: Čitaj redak-po-redak za originalni tekst
    plaintext = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c]:
                plaintext.append(grid[r][c])
    return ''.join(plaintext)


def main():
    print("=== HRVATSKI SUSTAV ZA DEKRIPTIRANJE ===\n")
    while True:
        print("Odaberite metodu:")
        print("1 – Caesar šifra (DEK)")
        print("2 – Vigenère šifra (DEK)")
        print("3 – Kolumnarna transpozicija (DEK)")
        print("4 – Izlaz")
        choice = input("Odabir: ")
        if choice == "1":
            c = input("Šifrat: ")
            a = input("Alfabet (ENTER=zadani): ") or HR_ALFABET
            s = int(input("Pomak: "))
            print("Plaintext:", caesar_dekript(c, s, a), "\n")
        elif choice == "2":
            c = input("Šifrat: ")
            key = input("Ključ: ")
            pwd = input("Lozinka: ")
            print("Plaintext:", vigenere_dekript(c.upper(), pwd, key), "\n")
        elif choice == "3":
            c = input("Šifrat: ")
            k = input("Ključ: ")
            print("Plaintext:", columnar_dekript(c.upper(), k), "\n")
        elif choice == "4":
            break
        else:
            print("Pogrešan odabir!")


if __name__ == "__main__":
    main()