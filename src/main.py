import random
import copy
import csv

# ===================== CONFIG =====================
ROWS = 11
COLS = 11
COLORS = [1, 2, 3, 4]

GAMES = 10
TARGET_SCORE = 1000

SCORES = {
    "LINE3": 5,
    "LINE4": 10,
    "LINE5": 50,
    "L": 20,
    "T": 30
}

# ===================== PREDEFINED BOARD =====================
PREDEFINED_BOARD = [
    [1,2,3,4,1,2,3,4,1,2,3],
    [2,1,4,3,2,1,4,3,2,1,4],
    [3,4,1,2,3,4,1,2,3,4,1],
    [4,3,2,1,4,3,2,1,4,3,2],
    [1,2,3,4,1,2,3,4,1,2,3],
    [2,1,4,3,2,1,4,3,2,1,4],
    [3,4,1,2,3,4,1,2,3,4,1],
    [4,3,2,1,4,3,2,1,4,3,2],
    [1,2,3,4,1,2,3,4,1,2,3],
    [2,1,4,3,2,1,4,3,2,1,4],
    [3,4,1,2,3,4,1,2,3,4,1]
]

# ===================== UTIL =====================
def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS

# ===================== INIT =====================
def init_board(predefined=None):
    if predefined is not None:
        return copy.deepcopy(predefined)
    return [[random.choice(COLORS) for _ in range(COLS)] for _ in range(ROWS)]

# ===================== FORMATION DETECTION =====================
def find_formations(board):
    used = set()
    removals = set()
    score = 0

    def take(cells, pts):
        nonlocal score
        s = set(cells)
        if not (s & used):
            used.update(s)
            removals.update(s)
            score += pts

    # ---- lines ----
    for r in range(ROWS):
        c = 0
        while c < COLS:
            v = board[r][c]
            start = c
            while c < COLS and board[r][c] == v and v != 0:
                c += 1
            length = c - start
            if length >= 5:
                take([(r, x) for x in range(start, start+5)], SCORES["LINE5"])
            elif length == 4:
                take([(r, x) for x in range(start, c)], SCORES["LINE4"])
            elif length == 3:
                take([(r, x) for x in range(start, c)], SCORES["LINE3"])
            if v == 0:
                c += 1

    for c in range(COLS):
        r = 0
        while r < ROWS:
            v = board[r][c]
            start = r
            while r < ROWS and board[r][c] == v and v != 0:
                r += 1
            length = r - start
            if length >= 5:
                take([(x, c) for x in range(start, start+5)], SCORES["LINE5"])
            elif length == 4:
                take([(x, c) for x in range(start, r)], SCORES["LINE4"])
            elif length == 3:
                take([(x, c) for x in range(start, r)], SCORES["LINE3"])
            if v == 0:
                r += 1

    # ---- T ----
    for r in range(ROWS):
        for c in range(COLS):
            v = board[r][c]
            if v == 0:
                continue
            cells = [(r,c),(r-1,c),(r+1,c),(r,c-1),(r,c+1)]
            if all(in_bounds(x,y) and board[x][y]==v for x,y in cells):
                take(cells, SCORES["T"])

    # ---- L ----
    L_SHAPES = [
        [(0,0),(1,0),(2,0),(2,1),(2,2)],
        [(0,0),(0,1),(0,2),(1,0),(2,0)],
        [(0,2),(1,2),(2,2),(0,0),(0,1)],
        [(2,0),(2,1),(2,2),(0,2),(1,2)]
    ]

    for r in range(ROWS):
        for c in range(COLS):
            v = board[r][c]
            if v == 0:
                continue
            for shape in L_SHAPES:
                cells = [(r+dr, c+dc) for dr,dc in shape]
                if all(in_bounds(x,y) and board[x][y]==v for x,y in cells):
                    take(cells, SCORES["L"])

    return removals, score

# ===================== GRAVITY & REFILL =====================
def apply_gravity(board):
    for c in range(COLS):
        stack = [board[r][c] for r in range(ROWS) if board[r][c] != 0]
        for r in range(ROWS-1, -1, -1):
            board[r][c] = stack.pop() if stack else 0

def refill(board):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == 0:
                board[r][c] = random.choice(COLORS)

# ===================== CASCADES =====================
def resolve(board):
    total = 0
    cascades = 0
    while True:
        rem, pts = find_formations(board)
        if not rem:
            break
        for r,c in rem:
            board[r][c] = 0
        apply_gravity(board)
        refill(board)
        total += pts
        cascades += 1
    return total, cascades

# ===================== SWAPS =====================
def best_swap(board):
    best = 0
    best_board = None
    for r in range(ROWS):
        for c in range(COLS):
            for dr,dc in [(1,0),(0,1)]:
                nr,nc = r+dr, c+dc
                if not in_bounds(nr,nc):
                    continue
                b = copy.deepcopy(board)
                b[r][c], b[nr][nc] = b[nr][nc], b[r][c]
                gained,_ = resolve(copy.deepcopy(b))
                if gained > best:
                    best = gained
                    best_board = b
    return best, best_board

# ===================== GAME =====================
def play_game(predefined=None):
    board = init_board(predefined)
    points, cascades = resolve(board)

    swaps = 0
    moves_to_10000 = None

    while points < TARGET_SCORE:
        gained, new_board = best_swap(board)
        if gained == 0:
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

# ===================== RUN =====================
def run_simulation(use_predefined):
    results = []

    for i in range(GAMES):
        res = play_game(PREDEFINED_BOARD if use_predefined else None)
        res["game_id"] = i
        results.append(res)

        print(f"Game {i}: points={res['points']}, "
              f"reached_target={res['reached_target']}, "
              f"reason={res['stopping_reason']}")

    avg_points = sum(r["points"] for r in results) / GAMES
    avg_swaps = sum(r["swaps"] for r in results) / GAMES

    print("\n=== AVERAGES ===")
    print(f"avg_points = {avg_points:.2f}")
    print(f"avg_swaps  = {avg_swaps:.2f}")

    with open("results/rezultate.csv", "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "game_id","points","swaps","total_cascades",
                "reached_target","stopping_reason","moves_to_10000"
            ]
        )
        writer.writeheader()
        writer.writerows(results)

# ===================== ENTRY =====================
if __name__ == "__main__":
    choice = input("Use predefined board? (y/n): ").strip().lower()
    run_simulation(choice == "y")
