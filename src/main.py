import random
import copy
import csv

ROWS = 11      # Numarul de randuri al tablei de joc
COLS = 11      # Numarul de coloane al tablei de joc

COLORS = [1, 2, 3, 4]  # Culorile posibile pe tabla, reprezentate prin numere

GAMES = 100          # Numarul de jocuri care se vor simula
TARGET_SCORE = 10000 # Scorul tinta pe care dorim sa il atingem intr-un joc

# Puncte pentru diferite tipuri de formatiuni
SCORES = {
    "LINE3": 5,  # 3 elemente la rand/coloana
    "LINE4": 10, # 4 elemente la rand/coloana
    "LINE5": 50, # 5 elemente la rand/coloana
    "L": 20,     # Forma in L
    "T": 30      # Forma in T
}

# Tabla predefinita pentru teste deterministe
PREDEFINED_BOARD = [
    [1,2,3,4,1,2,3,4,1,2,3],
    [2,1,4,3,2,1,4,3,2,1,4],
    [3,2,1,2,2,4,1,2,3,4,1],
    [4,3,2,1,4,3,2,1,4,3,2],
    [1,2,3,4,1,2,3,4,1,2,3],
    [2,1,4,3,2,1,4,3,2,1,4],
    [3,4,1,2,3,4,4,2,3,4,1],
    [4,3,2,1,4,4,2,4,4,3,2],
    [1,2,3,4,1,2,3,4,1,2,3],
    [2,1,4,3,2,1,4,3,2,1,4],
    [3,4,1,2,3,2,1,2,3,4,1]
]

# Functie pentru a verifica daca o pozitie este in limitele tablei
def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS  # Returneaza True daca randul si coloana sunt valide

# Initializarea tablei de joc
def init_board(predefined=None):
    if predefined is not None:                 # Daca se primeste tabla predefinita
        return copy.deepcopy(predefined)       # Returnam o copie profunda pentru a nu modifica originalul
    return [[random.choice(COLORS)             # Generam o lista de liste cu culori aleatorii
             for _ in range(COLS)]
            for _ in range(ROWS)]

# Functie care gaseste toate formatiunile de tip LINE, T sau L
def find_formations(board):
    used = set()      # Set pentru a tine evidenta celulelor deja utilizate
    removals = set()  # Set pentru celulele care trebuie eliminate
    score = 0         # Puncte acumulate in aceasta etapa

    # Functie auxiliara pentru a marca celulele si a adauga puncte
    def take(cells, pts):
        nonlocal score                     # Folosim score din functia parinte
        s = set(cells)                     # Convertim lista de celule in set
        if not (s & used):                 # Daca nu s-au folosit deja
            used.update(s)                 # Adaugam celulele in setul used
            removals.update(s)             # Adaugam celulele in setul de eliminat
            score += pts                   # Adaugam punctele la scorul total

    # Detectarea liniilor orizontale
    for r in range(ROWS):                  # Pentru fiecare rand
        c = 0
        while c < COLS:                     # Parcurgem fiecare coloana
            v = board[r][c]                 # Valoarea curenta
            start = c                        # Pozitia de start pentru o posibila linie
            while c < COLS and board[r][c] == v and v != 0:  # Cat timp valorile sunt aceleasi
                c += 1                       # Extindem linia
            length = c - start               # Lungimea liniei consecutive
            if length >= 5:                  # Linie de 5
                take([(r, x) for x in range(start, start+5)], SCORES["LINE5"])
            elif length == 4:                # Linie de 4
                take([(r, x) for x in range(start, c)], SCORES["LINE4"])
            elif length == 3:                # Linie de 3
                take([(r, x) for x in range(start, c)], SCORES["LINE3"])
            if v == 0:                       # Daca celula e goala
                c += 1                       # Trecem peste

    # Detectarea liniilor verticale
    for c in range(COLS):                  # Pentru fiecare coloana
        r = 0
        while r < ROWS:                     # Parcurgem fiecare rand
            v = board[r][c]                 # Valoarea curenta
            start = r                        # Pozitia de start pentru o posibila linie
            while r < ROWS and board[r][c] == v and v != 0:  # Cat timp valorile sunt aceleasi
                r += 1                       # Extindem linia
            length = r - start               # Lungimea liniei consecutive
            if length >= 5:                  # Linie de 5
                take([(x, c) for x in range(start, start+5)], SCORES["LINE5"])
            elif length == 4:                # Linie de 4
                take([(x, c) for x in range(start, r)], SCORES["LINE4"])
            elif length == 3:                # Linie de 3
                take([(x, c) for x in range(start, r)], SCORES["LINE3"])
            if v == 0:                       # Daca celula e goala
                r += 1                       # Trecem peste

    # Detectarea formelor in T
    for r in range(ROWS):                  # Pentru fiecare rand
        for c in range(COLS):              # Pentru fiecare coloana
            v = board[r][c]                # Valoarea curenta
            if v == 0:                     # Daca e celula goala, sarim
                continue
            cells = [(r,c),(r-1,c),(r+1,c),(r,c-1),(r,c+1)]  # Pozitiile celulelor pentru T
            if all(in_bounds(x,y) and board[x][y]==v for x,y in cells):  # Daca toate sunt valide si egale
                take(cells, SCORES["T"])   # Adaugam puncte pentru T

    # Detectarea formelor in L
    L_SHAPES = [
        [(0,0),(1,0),(2,0),(2,1),(2,2)],  # L vertical, baza dreapta
        [(0,0),(0,1),(0,2),(1,0),(2,0)],  # L orizontal, baza jos
        [(0,2),(1,2),(2,2),(0,0),(0,1)],  # L vertical inversat
        [(2,0),(2,1),(2,2),(0,2),(1,2)]   # L orizontal inversat
    ]
    for r in range(ROWS):
        for c in range(COLS):
            v = board[r][c]                # Valoarea curenta
            if v == 0:                     # Daca celula e goala
                continue
            for shape in L_SHAPES:         # Pentru fiecare forma de L
                cells = [(r+dr, c+dc) for dr,dc in shape]   # Calculam pozitiile reale
                if all(in_bounds(x,y) and board[x][y]==v for x,y in cells):  # Daca toate celulele sunt valide
                    take(cells, SCORES["L"])   # Adaugam puncte pentru L

    return removals, score                 # Returnam celulele de eliminat si scorul total

# Gravitatia: celulele non-zero cad in jos, golurile raman sus
def apply_gravity(board):
    for c in range(COLS):                    # Pentru fiecare coloana
        stack = [board[r][c] for r in range(ROWS) if board[r][c] != 0]  # Preluam celulele non-zero
        for r in range(ROWS-1, -1, -1):      # De jos in sus
            board[r][c] = stack.pop() if stack else 0  # Punem celula sau zero daca nu mai e nimic

# Reumple celulele goale
def refill(board, use_random=True):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == 0:              # Daca celula e goala
                board[r][c] = random.choice(COLORS) if use_random else 0  # Punem culoare aleatorie

# Rezolvarea tablei: elimina formatiuni si aplica gravitatia si refill-ul
def resolve(board, use_random=True):
    total = 0      # Scor total acumulat
    cascades = 0   # Numar de cascade
    while True:
        rem, pts = find_formations(board)   # Gasim formatiuni
        if not rem:                         # Daca nu mai exista formatiuni
            break
        for r,c in rem:
            board[r][c] = 0                 # Eliminam celulele
        apply_gravity(board)                 # Aplicam gravitatia
        refill(board, use_random)            # Reumplem golurile
        total += pts
        cascades += 1                        # Incrementam cascada
    return total, cascades

# Gaseste cea mai buna mutare posibila
def best_swap(board):
    best = 0
    best_board = None
    for r in range(ROWS):
        for c in range(COLS):
            for dr,dc in [(1,0),(0,1)]:    # Verificam doar mutari verticale sau orizontale
                nr,nc = r+dr, c+dc
                if not in_bounds(nr,nc):
                    continue
                b = copy.deepcopy(board)   # Copiem tabla pentru simulare
                b[r][c], b[nr][nc] = b[nr][nc], b[r][c]  # Facem swap
                gained,_ = resolve(copy.deepcopy(b))     # Calculam punctele obtinute
                if gained > best:          # Daca e mai bun decat anterior
                    best = gained
                    best_board = b
    return best, best_board

# Simuleaza un joc complet
def play_game(predefined=None, use_random=True):
    board = init_board(predefined)           # Initializam tabla
    points, cascades = resolve(board, use_random)  # Rezolvam formatiunile initiale
    swaps = 0
    moves_to_10000 = None
    while points < TARGET_SCORE:             # Cat timp nu am atins scorul tinta
        gained, new_board = best_swap(board)
        if gained == 0:                      # Daca nu mai exista mutari posibile
            break
        board = new_board
        points += gained
        swaps += 1
        if points >= TARGET_SCORE and moves_to_10000 is None:
            moves_to_10000 = swaps
    reached = points >= TARGET_SCORE
    reason = "REACHED_TARGET" if reached else "NO_MOVES"
    return {
        "points": points,
        "swaps": swaps,
        "total_cascades": cascades,
        "reached_target": reached,
        "stopping_reason": reason,
        "moves_to_10000": moves_to_10000 or ""
    }

# Ruleaza simularea pentru mai multe jocuri
def run_simulation(use_predefined):
    results = []
    for i in range(GAMES):
        res = play_game(PREDEFINED_BOARD if use_predefined else None,
                        use_random=not use_predefined)
        res["game_id"] = i+1
        results.append(res)
        print(f"Jocul {i+1}: puncte={res['points']}, "
              f"tinta atinsa={res['reached_target']}, "
              f"cauza={res['stopping_reason']}")
    avg_points = sum(r["points"] for r in results) / GAMES  # Media punctelor
    avg_swaps = sum(r["swaps"] for r in results) / GAMES     # Media swap-urilor
    print("\n\tStatistici finale")
    print(f"Media aritmetica a punctelor = {avg_points:.2f}")
    print(f"Media aritmetica a swap-urilor  = {avg_swaps:.2f}")
    with open("../results/rezultate.csv", "w", newline="") as f:  # Salvam rezultatele
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "game_id","points","swaps","total_cascades",
                "reached_target","stopping_reason","moves_to_10000"
            ]
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    choice = input("Folositi tabla predefinita? (da/nu): ").strip().lower()  # Intrebam utilizatorul
    run_simulation(choice == "da")  # Rulam simularea
