import re, math, ssl, urllib.request, random
from collections import defaultdict, Counter
from itertools import permutations
from itertools import combinations





# Hrvatske frekvencije za chi-kvadrat test
HR_FREQ = {
    'A': 11.5, 'I': 10.04, 'O': 9.01, 'E': 8.43, 'N': 6.39, 'R': 5.47, 'J': 5.15,
    'S': 5.11, 'T': 4.47, 'U': 4.33, 'K': 3.85, 'L': 3.55, 'V': 3.54, 'D': 3.20,
    'P': 3.00, 'M': 2.95, 'Z': 1.69, 'G': 1.63, 'B': 1.54, 'C': 1.12, 'H': 1.04,
    'Č': 0.92, 'Š': 0.73, 'Ć': 0.49, 'Ž': 0.47, 'F': 0.31, 'Đ': 0.20,
    'Y': 0.05, 'W': 0.04, 'X': 0.02, 'Q': 0.01
}

HR_BIGRAMS = {
    'JE': 2.7, 'NA': 1.5, 'RA': 1.5, 'ST': 1.0, 'AN': 1.0, 'NI': 1.0,
    'KO': 1.0, 'OS': 1.0, 'TI': 1.0, 'IJ': 1.0, 'NO': 1.0, 'EN': 1.0, 'PR': 1.0
}

HR_TRIGRAMS = {
    'IJE': 0.6, 'STA': 0.4, 'OST': 0.4, 'JED': 0.4, 'KOJ': 0.4, 'OJE': 0.4, 'JEN': 0.4
}

# Top 100 najčešćih hrvatskih riječi
HR_COMMON_WORDS = [
    'JE', 'DA', 'NE', 'SE', 'I', 'U', 'TO', 'SAM', 'STO', 'NA', 'TI', 'ZA', 'MI', 'SI',
    'LI', 'JA', 'SU', 'ALI', 'NIJE', 'S', 'SAMO', 'GA', 'ME', 'OD', 'A', 'BI', 'OVO',
    'KAKO', 'TE', 'CE', 'O', 'DOBRO', 'AKO', 'SMO', 'SA', 'SVE', 'KAO', 'CU', 'BITI',
    'TAKO', 'ZNAM', 'STE', 'NISAM', 'OVDJE', 'BIO', 'MOGU', 'PA', 'ZASTO', 'ON', 'JOS',
    'REDU', 'ZASTO', 'NESTO', 'BILO', 'VAS', 'KOJI', 'KAD', 'ZNASM', 'IH', 'MISLIM',
    'IZ', 'GDJE', 'IMA', 'VAM', 'ILI', 'SADA', 'MOJ', 'VISE', 'DO', 'ZAR', 'BIH',
    'MOZDA', 'REKAO', 'NAS', 'ONDA', 'MALO', 'CEMO', 'TAMO', 'ZELIM', 'HEJ', 'SAD',
    'CES', 'MOZES', 'BILA', 'IMAM', 'ONA', 'TU', 'JESI', 'VI', 'MOZE', 'NI', 'IDEMO',
    'NAM', 'SVI', 'TREBA', 'OH', 'RECI', 'NISI', 'MORAM', 'LJUDI', 'PO', 'ZBOG'
]

# Pragovi
CHI2_THRESHOLD = 37.652  # Standardni prag za hrvatski
IC_THRESHOLD = 0.058     # Prilagođeno za hrvatski
MAX_BRUTE = 50000        # Prag za brute force

def clean_text(text):
    """Uklanja ne-slova i pretvara u velika slova."""
    return re.sub(r'[^A-Za-z]', '', text).upper()


def caesar_shift(text, shift):
    """Pomakni svako slovo unatrag za 'shift' mjesta."""
    return ''.join(
        chr((ord(ch) - ord('A') - shift) % 26 + ord('A'))
        for ch in text
    )

def chi2_stat(text, freq_table=HR_FREQ):
    n = len(text)
    counts = Counter(text)
    chi2 = 0.0
    for ch, exp_pct in freq_table.items():
        exp = n * (exp_pct / 100)
        chi2 += (counts.get(ch,0) - exp)**2 / exp
    return chi2

def index_of_coincidence(text):
    """Izračunaj Index of Coincidence."""
    n = len(text)
    if n < 2:
        return 0.0
    freqs = Counter(text)
    num = sum(f*(f-1) for f in freqs.values())
    den = n*(n-1)
    return num / den

def detect_caesar(cipher):
    """
    Stroga detekcija Caesar šifre:
    ispisuje tablicu chi² i IC za svaki pomak, vraća prvi valjani.
    """
    txt = clean_text(cipher)
    print("Caesar test (shift | chi²     | IC     | prolazi?):")
    valid = None
    for shift in range(26):
        cand = caesar_shift(txt, shift)
        chi2 = chi2_stat(cand)
        ic = index_of_coincidence(cand)
        ok = (chi2 < CHI2_THRESHOLD and ic > IC_THRESHOLD)
        print(f"{shift:5} | {chi2:8.2f} | {ic:6.4f} | {'DA' if ok else 'NE'}")
        if ok and valid is None:
            valid = (shift, cand, chi2, ic)
    return valid  # ili None

def count_ngrams_positions(text, n=3):
    poz = defaultdict(list)
    for i in range(len(text)-n+1):
        gram = text[i:i+n]
        poz[gram].append(i)
    return {g:p for g,p in poz.items() if len(p)>1}

def distances(positions):
    """Svi parni razmaci za listu pozicija."""
    d = []
    for i in range(len(positions)):
        for j in range(i+1, len(positions)):
            d.append(positions[j] - positions[i])
    return d

def all_divisors(n):
    """Svi djelitelji broja n >1."""
    divs = set()
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            divs.add(i)
            divs.add(n//i)
    divs.add(n)
    return sorted(divs)

def find_vigenere_key_lengths(cipher, top_n=5, ngram_n=3):
    """
    Analiza ponovljenih n-grama:
    vraća top_n najčešćih djelitelja razmaka.
    """
    text = clean_text(cipher)
    ngram_pos = count_ngrams_positions(text, ngram_n)
    cnt = Counter()
    for pos in ngram_pos.values():
        for dist in distances(pos):
            for d in all_divisors(dist):
                cnt[d] += 1
    top = cnt.most_common(top_n)
    print("\nVigenère kandidati (duljina | učestalost):")
    for length, freq in top:
        print(f"{length:7} | {freq}")
    return [length for length,_ in top]

def decrypt_vigenere(cipher, key_len):
    """Dešifriraj Vigenère: dijeli u retke i Caesar po retku."""
    text = clean_text(cipher)
    rows = [text[i::key_len] for i in range(key_len)]
    shifts = [min(range(26), key=lambda s: chi2_stat(caesar_shift(r, s))) for r in rows]
    plain = []
    for i, ch in enumerate(text):
        r = i % key_len
        plain.append(caesar_shift(ch, shifts[r]))
    return ''.join(plain), shifts

def shifts_to_key(shifts):
    """
    Pretvara listu Caesar pomaka u Vigenère ključ.
    Pomak 0 → 'A', 1 → 'B', … 25 → 'Z'.
    """
    return ''.join(chr(ord('A') + s) for s in shifts)

def decrypt_transposition(cipher, key_order, rows, cols):
    text = re.sub(r'[^A-Za-z]', '', cipher).upper()
    total_chars = len(text)

    # 1. Izračunaj duljine segmenata za svaki stupac
    base = total_chars // cols
    extra = total_chars % cols
    segment_lengths = [base + 1 if i < extra else base for i in range(cols)]

    # 2. Podijeli ciphertext u segmente prema ključu
    segments = []
    start = 0
    for col_num in key_order:
        length = segment_lengths[col_num - 1]
        segments.append(text[start:start + length])
        start += length

    # 3. Napuni matricu po prirodnim stupcima
    matrix = [[''] * cols for _ in range(rows)]
    col_index = 0
    for col_num in sorted(key_order):  # Prolazimo po prirodnom redoslijedu stupaca
        segment = segments[key_order.index(col_num)]
        for row in range(len(segment)):
            matrix[row][col_num - 1] = segment[row]

    # 4. Pročitaj matricu red po red
    plain = []
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c]:
                plain.append(matrix[r][c])
    return ''.join(plain)






def find_possible_dimensions(n, margin=3):
    """Svi djelitelji n i n±1..n±margin (za nepotpune pravokutnike)."""
    cand = set()
    for delta in range(-margin, margin+1):
        m = n + delta
        if m < 2:
            continue
        for d in range(2, int(m**0.5)+1):
            if m % d == 0:
                cand.add(d)
                cand.add(m//d)
    return sorted(cand)

def evaluate_croatian_text(text):
    """Manji rezultat = bolji tekst."""
    text = text.upper()
    # 1) bigram χ²
    expected = {"TH":1.52,"HE":1.28,"IN":0.94,"ER":0.94,"AN":0.82,"RE":0.68,
                "ND":0.63,"AT":0.59,"ON":0.57,"NT":0.56}
    n = len(text)-1
    if n <= 0: return 1e9
    obs = Counter(text[i:i+2] for i in range(n))
    chi2 = 0
    for bg,pct in expected.items():
        exp = n*(pct/100)
        chi2 += (obs.get(bg,0)-exp)**2/exp
    # 2) trigram bonus
    bonus = sum(text.count(t) for t in ("THE","AND","ING"))
    return chi2 - 5*bonus    # heuristička vaga


def decrypt_cols(ct, order, rows, cols):
    """
    Ispravka funkcije decrypt_cols za dešifriranje transpozicijske šifre.

    Parametri:
    ct: ciphertext (već očišćen)
    order: lista indeksa stupaca (0-based) koja predstavlja permutaciju stupaca
    rows: broj redaka u matrici
    cols: broj stupaca u matrici

    Ova funkcija replicira logiku originalne decrypt_transposition funkcije.
    """
    total = len(ct)

    # 1. Izračunaj duljine segmenata za svaki stupac
    base = total // cols
    extra = total % cols
    segment_lengths = [base + 1 if i < extra else base for i in range(cols)]

    # 2. Konvertiraj order u key_order (1-based)
    key_order = [x + 1 for x in order]

    # 3. Podijeli ciphertext u segmente prema key_order
    segments = []
    start = 0
    for col_num in key_order:
        length = segment_lengths[col_num - 1]
        segments.append(ct[start:start + length])
        start += length

    # 4. Popuni matricu - segment odgovara stupcu u key_order
    matrix = [[''] * cols for _ in range(rows)]

    # Za svaki stupac u prirodnom redoslijedu, pronađi odgovarajući segment
    for col_num in sorted(key_order):
        segment_index = key_order.index(col_num)
        segment = segments[segment_index]
        for row in range(len(segment)):
            if row < rows:
                matrix[row][col_num - 1] = segment[row]

    # 5. Čitaj matricu red po red
    plain = []
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c]:
                plain.append(matrix[r][c])

    return ''.join(plain)


def break_transposition(cipher):
    """Ispravljena verzija break_transposition funkcije"""
    txt = clean_text(cipher)
    n = len(txt)
    best = {"score": 1e9}

    # Pronađi sve moguće dimenzije
    def find_possible_dims(n, margin=3):
        dims = set()
        for delta in range(-margin, margin + 1):
            m = n + delta
            if m < 2: continue
            for d in range(2, int(math.sqrt(m)) + 1):
                if m % d == 0:
                    dims.add((d, m // d))
                    dims.add((m // d, d))
        return sorted(dims)

    for rows, cols in find_possible_dims(n):
        if rows * cols < n: continue

        # Brute force za male brojeve stupaca
        if math.factorial(cols) <= MAX_BRUTE:
            for order in permutations(range(cols)):
                plain = decrypt_cols(txt, order, rows, cols)
                sc = evaluate_croatian_text(plain)
                if sc < best["score"]:
                    best = {"score": sc, "plain": plain, "rows": rows,
                            "cols": cols, "key": [o + 1 for o in order]}
        else:
            # Hill climbing za veće brojeve
            order = list(range(cols))
            random.shuffle(order)
            current_sc = evaluate_croatian_text(decrypt_cols(txt, order, rows, cols))

            improved = True
            while improved:
                improved = False
                for i in range(cols):
                    for j in range(i + 1, cols):
                        # Zamijeni pozicije
                        order[i], order[j] = order[j], order[i]
                        new_plain = decrypt_cols(txt, order, rows, cols)
                        sc = evaluate_croatian_text(new_plain)
                        if sc < current_sc:
                            current_sc = sc
                            improved = True
                        else:
                            # Vrati promjenu ako nije bolja
                            order[i], order[j] = order[j], order[i]

            if current_sc < best["score"]:
                best = {"score": current_sc,
                        "plain": decrypt_cols(txt, order, rows, cols),
                        "rows": rows, "cols": cols,
                        "key": [o + 1 for o in order]}

    return best


if __name__ == "__main__":
    cipher = input("Unesi ciphertext: ")

    # 1. Testiraj i prikaži Caesar
    print("=== TEST CAESAR ===")
    caesar_res = detect_caesar(cipher)
    if caesar_res:
        shift, text_caesar, chi2, ic = caesar_res
        print(f"\nCAESAR DETEKTIRAN: shift={shift}, chi²={chi2:.2f}, IC={ic:.4f}")
        print("Dešifrirani tekst (Caesar):", text_caesar)
    else:
        print("\nNije detektirana validna Caesar šifra.")

    # 2. Prikaži Vigenère kandidate
    print("\n=== TEST VIGENÈRE ===")
    candidates = find_vigenere_key_lengths(cipher, top_n=5)

    # 3. Dešifriraj i prikaži rezultate za svaki kandidat
    print("\n=== DEŠIFRIRANJE VIGENÈRE ZA TOP KANDIDATE ===")
    results = []
    for k in candidates:
        plain, shifts = decrypt_vigenere(cipher, k)
        chi2 = chi2_stat(plain)
        ic = index_of_coincidence(plain)
        print(f"\nKljuč duljine {k}: chi²={chi2:.2f}, IC={ic:.4f}, pomaci={shifts}")
        print("Tekst:", plain)
        results.append({'key_len': k, 'chi2': chi2, 'ic': ic, 'plain': plain, 'shifts': shifts})

    # 4. Odaberi najbolji Vigenère rezultat prema chi² i IC

    if not results:
        print("Nema Vigenère kandidata za dešifriranje; preskačem taj dio.")
    else:
        best = sorted(results, key=lambda r: (r['chi2'], -r['ic']))[0]
        print("\n=== NAJBOLJI VIGENÈRE REZULTAT ===")
        print(f"Duljina ključa: {best['key_len']}")
        print(f"chi² = {best['chi2']:.2f}, IC = {best['ic']:.4f}")
        print(f"Pomaci po retku: {best['shifts']}")
        print("\nDešifrirani tekst:\n", best['plain'])

    # 5. Rekonstruiraj i prikaži Vigenère ključ
        key = shifts_to_key(best['shifts'])
        print(f"\nOtkriveni Vigenère ključ: {key}")

    # 6) Transpozicija
    print("\n--- Transpozicija (3×5, ključ 24513) ---")
    trans_key = [2, 4, 5, 1, 3]
    pt_trans = decrypt_transposition(cipher, trans_key, rows=3, cols=5)
    print("Transpozicija dekriptirano:", pt_trans)

    # (6) Transpozicija – automatski

    print("\n=== AUTOMATSKA TRANSP. ANALIZA ===")
    res = break_transposition(cipher)
    if res["score"] < 1e9:
        print(f"Rows×Cols  : {res['rows']}×{res['cols']}")
        print(f"Ključ      : {res['key']}")
        print(f"Ocjena     : {res['score']:.2f}")
        print("Otvoreni tekst:\n", res['plain'])
    else:
        print("Nije pronađeno uvjerljivo rješenje.")