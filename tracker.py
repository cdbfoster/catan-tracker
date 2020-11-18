from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import re

command_pattern = re.compile("^([a-z]?)\\s?(\\d{1,2}|[^\\s]+)?(?:\\s(\\d{1,2}))?$")

rolls = []
players = []

probability = {
    2:  1 / 36,
    3:  2 / 36,
    4:  3 / 36,
    5:  4 / 36,
    6:  5 / 36,
    7:  6 / 36,
    8:  5 / 36,
    9:  4 / 36,
    10: 3 / 36,
    11: 2 / 36,
    12: 1 / 36,
}

roll_counts = {n: 0 for n in probability.keys()}


class Player:
    def __init__(self, name):
        self.name = name
        self.owed = 0
        self.received = 0
        self.robbed = 0
        self.holdings = []
        self.robbed_holdings = []
        self.blessedness = []

    def calculate_roll(self, roll):
        robbed_holdings = self.robbed_holdings.copy()

        received = 0
        robbed = 0

        for h in self.holdings:
            if h == roll:
                if h in robbed_holdings:
                    robbed_holdings.remove(h)
                    robbed += 1
                else:
                    received += 1

        return (received, robbed)


def roll(number, *_):
    if number is None:
        return

    number = int(number)
    if number < 2 or number > 12:
        return

    global rolls
    global players
    global probability
    global roll_counts

    rolls.append(number)
    roll_counts[number] += 1

    for p in players:
        for h in p.holdings:
            p.owed += probability[h]

        received, robbed = p.calculate_roll(number)
        p.received += received
        p.robbed += robbed

        p.blessedness.append(p.received / p.owed if p.owed > 0 else 0.0)


def add_player(name, *_):
    if name is None:
        return

    global rolls
    if len(rolls) > 0:
        print("Can't add players to a game that's already started.")
        return

    global players
    players.append(Player(name))


def add_holding(name, number, *_):
    if name is None or number is None:
        return

    number = int(number)
    if number < 2 or number > 12:
        return

    global players
    player = {p.name: p for p in players}.get(name)
    if player is None:
        return

    player.holdings.append(number)


def move_robber(name, number, *_):
    global players

    if name is None and number is None:
        for p in players:
            p.robbed_holdings = []
        return
    elif name is None or number is None:
        return

    number = int(number)
    if number < 2 or number > 12:
        return

    player = {p.name: p for p in players}.get(name)
    if player is None:
        return

    player.robbed_holdings.append(number)


def clear_game(*_):
    with open("game", "w") as _:
        pass

    global rolls
    global players
    global roll_counts

    rolls = []
    players = []

    roll_counts = {n: 0 for n in probability.keys()}


def undo(*_):
    entries = [line for line in open("game")][:-1]

    clear_game()
    play_entries(entries, record=True)


def display_help(*_):
    print("""
Available Commands:
  <number>            - Record a roll.
  p <player>          - Adds <player> to the game.
  a <player> <number> - Give <player> a holding of <number>.
  r                   - Clear the robber's holdings.
  r <player> <number> - Prevent <player>'s <number> holding from receiving resources.
  u                   - Undo last successful command.
  c                   - Reset the game. (Can't be undone)
  q                   - Quit. (Progress is saved)
  h                   - Display this help text.
""")


def quit(*_):
    exit()


def play_entries(entries, record=False):
    global command_pattern
    global commands
    global dont_record_commands
    for entry in entries:
        match = command_pattern.search(entry.strip())
        if entry.strip() == "" or match is None:
            continue

        command, *parameters = match.groups()
        if command not in commands:
            continue
        elif record and command not in dont_record_commands:
            with open("game", "a") as f:
                f.write(entry.strip() + "\n")

        commands[command](*parameters)


def update_view(figure, axes):
    global drawers

    for drawer in drawers:
        drawer(figure, axes)

    plt.draw()


def draw_player_blessedness(figure, axes):
    global rolls

    blessedness = [[1.0] + x for x in [[p.blessedness[i] for p in players] for i in range(len(rolls))]]
    mins = [min(x) for x in blessedness]
    scales = [y if y > 0 else 1.0 for y in [max(x) - min(x) for x in blessedness]]

    data = [[(blessedness[i][j] - mins[i]) / scales[i] for i in range(len(rolls))] for j in range(len(players) + 1)]

    a = axes["player_blessedness"]
    a.clear()
    a.set_title("Player Blessedness")
    a.tick_params(
        axis='y',
        which='both',
        left=False,
        labelleft=False,
    )
    a.plot(range(len(rolls)), data[0], color="black", label="Baseline: 1.00")
    for i, p in enumerate(players):
        a.plot(range(len(rolls)), data[i + 1], label=f"{p.name}: {p.blessedness[-1] if len(p.blessedness) > 0 else 0.0:.2f}")
    a.legend(loc="lower left")


def draw_roll_counts(figure, axes):
    global roll_counts

    a = axes["roll_counts"]
    a.clear()
    a.set_title("Roll Counts")
    a.set_yticks(range(max(roll_counts.values()) + 1))
    a.grid(axis="y", which="major", linewidth=0.3)
    a.bar(roll_counts.keys(), roll_counts.values())
    a.set_xticks(list(roll_counts.keys()))


def draw_number_blessedness(figure, axes):
    global probability
    global rolls
    global roll_counts

    a = axes["number_blessedness"]
    a.clear()
    a.set_title("Number Blessedness")
    a.axhline(1.0, color="black")
    a.bar(roll_counts.keys(), [x / (p * len(rolls)) if len(rolls) > 0 else 0.0 for x, p in zip(roll_counts.values(), probability.values())])
    a.set_xticks(list(roll_counts.keys()))
    a.grid(axis="y", which="major", linewidth=0.3)


def draw_resources_received(figure, axes):
    global players

    data = [p.received for p in players]
    most_received = max(data + [0])
    interval = max((most_received // 50 + 1) * 5, 1) if most_received >= 10 else 1

    a = axes["resources_received"]
    a.clear()
    a.set_title("Resources Received")
    a.bar(range(len(players)), data)
    a.set_yticks(range(0, (most_received // interval + 1) * interval + 1, interval))
    a.grid(axis="y", which="major", linewidth=0.3)
    a.set_xticks(range(len(players)))
    a.set_xticklabels([p.name for p in players])


def draw_resources_robbed(figure, axes):
    global players

    data = [p.robbed for p in players]

    a = axes["resources_robbed"]
    a.clear()
    a.set_title("Resources Robbed")
    a.bar(range(len(players)), data)
    a.set_yticks(range(max(data + [0]) + 1))
    a.grid(axis="y", which="major", linewidth=0.3)
    a.set_xticks(range(len(players)))
    a.set_xticklabels([p.name for p in players])


commands = {
    "": roll,
    "p": add_player,
    "a": add_holding,
    "r": move_robber,
    "c": clear_game,
    "u": undo,
    "h": display_help,
    "q": quit,
}
dont_record_commands = ["u", "h", "q"]

drawers = [
    draw_player_blessedness,
    draw_roll_counts,
    draw_number_blessedness,
    draw_resources_received,
    draw_resources_robbed,
]

if not os.path.exists("game"):
    with open("game", "w") as _:
        pass

play_entries([line for line in open("game")])

figure = plt.figure(figsize=(8, 8), constrained_layout=True)
grid = GridSpec(3, 2, figure=figure)
axes = {}
axes["player_blessedness"] = figure.add_subplot(grid[0, :])
axes["roll_counts"] = figure.add_subplot(grid[1, 0])
axes["number_blessedness"] = figure.add_subplot(grid[1, 1])
axes["resources_received"] = figure.add_subplot(grid[2, 0])
axes["resources_robbed"] = figure.add_subplot(grid[2, 1])
update_view(figure, axes)
figure.suptitle("Tracker of Divine Favor", fontsize=16)
plt.show(block=False)

while True:
    entry = input("Command (h for help): ")

    play_entries([entry], record=True)

    update_view(figure, axes)
