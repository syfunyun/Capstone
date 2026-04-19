import requests
import json
import networkx as nx
import time
from collections import defaultdict

BASE_URL = "https://lichess.org"

# ---------------------------
# SETTINGS
# ---------------------------

PERF_TYPE = "blitz"
TOP_N = 10
GAMES_PER_PLAYER = 500     # pull recent games once per player
ALPHA = 1.0                # Bayesian smoothing
SLEEP_TIME = 1.0           # API politeness


# ---------------------------
# GET TOP PLAYERS
# ---------------------------

def get_top_players(perf_type="blitz", n=10):
    url = f"{BASE_URL}/player/top/{n}/{perf_type}"
    headers = {"Accept": "application/vnd.lichess.v3+json"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    users = r.json()["users"]
    players = [u["username"] for u in users]
    return players[:n]  # enforce strict top N


# ---------------------------
# FETCH RECENT GAMES
# ---------------------------

def fetch_games(player, perf_type="blitz", max_games=500):
    url = f"{BASE_URL}/api/games/user/{player}"
    headers = {"Accept": "application/x-ndjson"}

    params = {
        "max": max_games,
        "perfType": perf_type,
        "moves": False,
        "pgnInJson": True
    }

    while True:
        r = requests.get(url, headers=headers, params=params)

        if r.status_code == 429:
            print("Rate limited. Sleeping 5 seconds...")
            time.sleep(5)
            continue

        r.raise_for_status()
        break

    games = []
    for line in r.iter_lines():
        if line:
            games.append(json.loads(line))

    return games


# ---------------------------
# BUILD PAIRWISE RECORDS
# ---------------------------

def compute_pairwise_records(players):
    records = defaultdict(lambda: {"wins": 0, "draws": 0, "losses": 0})

    player_set = set(players)

    for player in players:
        print(f"Fetching games for {player}")
        games = fetch_games(player, PERF_TYPE, GAMES_PER_PLAYER)

        for game in games:
            players_data = game.get("players", {})
            winner = game.get("winner", None)

            white = players_data.get("white", {}).get("user", {}).get("name", "")
            black = players_data.get("black", {}).get("user", {}).get("name", "")

            if white not in player_set or black not in player_set:
                continue

            opponent = black if white == player else white

            key = tuple(sorted([player, opponent]))

            if winner is None:
                records[key]["draws"] += 1
            elif (winner == "white" and white == player) or \
                 (winner == "black" and black == player):
                records[key]["wins"] += 1
            else:
                records[key]["losses"] += 1

        time.sleep(SLEEP_TIME)

    return records


# ---------------------------
# BUILD GRAPH
# ---------------------------

def build_graph(players, records):
    G = nx.DiGraph()
    G.add_nodes_from(players)

    for (p1, p2), result in records.items():
        w = result["wins"]
        d = result["draws"]
        l = result["losses"]

        total = w + d + l
        if total == 0:
            continue

        # Probability p1 beats p2
        p = (w + 0.5 * d + ALPHA) / (total + 2 * ALPHA)

        G.add_edge(p1, p2, weight=p, games=total)
        G.add_edge(p2, p1, weight=1 - p, games=total)

    return G


# ---------------------------
# MAIN
# ---------------------------

if __name__ == "__main__":
    players = get_top_players(PERF_TYPE, TOP_N)
    print("Top players:", players)
    print("Total players:", len(players))

    records = compute_pairwise_records(players)

    G = build_graph(players, records)

    print("\nGraph summary:")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())

    for u, v, data in G.edges(data=True):
        print(f"{u} -> {v}: weight={data['weight']:.3f}, games={data['games']}")