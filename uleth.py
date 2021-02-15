from typing import Optional, List
import subprocess
import os
import sqlite3
import time

import typer

from connection import Connection
from typo import omissions, repetitions, swaps
from keystore import Keystore

app = typer.Typer()

BATCH_SIZE = 15


@app.command()
def new(name: str, filepath: str):
    """
    Creates a new uleth instance for a locked keystore.
    This will delete an existing entry with the same name.
    """
    connection = Connection(name, new=True)
    connection.create(filepath)


@app.command()
def entry(name: str, typos: bool = False):
    """
    Begins a manual password loading session for the named keystore.
    Automatically loads all 1-swap, 1-omission, and 1-addition passwords as well.
    """
    connection = Connection(name)

    try:
        print("Manually enter passwords. Ctrl+C to end session.")
        while True:
            raw = input("> ")
            if typos:
                passwords = [raw] + omissions(raw) + repetitions(raw) + swaps(raw)
            else:
                passwords = [raw]
            new = connection.load(list(set(passwords)))
            print(f"Loaded {new} unique passwords.")
    except KeyboardInterrupt:
        print("\nSession ended")


@app.command()
def load(name: str, filepath: str, typos: bool = False):
    """
    Load a newline-separated password file for the named keystore.
    Automatically loads all 1-swap, 1-omission, and 1-addition passwords as well.
    """
    connection = Connection(name)

    with open(filepath, "r") as f:
        raw_passwords = f.read().split("\n")
    passwords: List[str] = []
    for raw in raw_passwords:
        if typos:
            passwords += [raw] + omissions(raw) + repetitions(raw) + swaps(raw)
        else:
            passwords += [raw]
    new = connection.load(list(set(passwords)))
    print(f"Loaded {new} unique passwords.")


@app.command()
def clean(name: str):
    """
    Removes all untried passwords from the named keystore.
    """
    connection = Connection(name)
    amount = connection.remove_untried()
    print(f"Removed {amount} untried passwords.")


@app.command()
def ls(name: str, all: bool = False):
    """
    Lists all passwords that have been attempted for the named keystore.
    If the --all flag is used, also lists passwords that are loaded but not yet attempted.
    """
    connection = Connection(name)
    rows = connection.get()
    passwords = ""
    for row in rows:
        passwords += row[1] + "\n"
    print(passwords[:-1])


@app.command()
def stats(name: str):
    """
    Provides statistics such as single-password check time, 
    loaded passwords, attempted passwords for a keystore.
    """
    connection = Connection(name)
    keystore = Keystore(connection.get_keystore())
    rows = connection.get()
    loaded = len(rows)
    attempted = sum(1 for row in rows if row[2])
    timing = keystore.check_time_multi()

    success = None
    for row in rows:
        if row[3]:
            success = row[1]

    print(
        f"""
        Unique loaded: {loaded}
        Attempted: {attempted}
        Time per check: {str(timing)} seconds
        Success: {success if success else "Not yet"}
        """
    )


@app.command()
def run(name: str):
    """
    Begin attempting to unlock the keystore using loaded passwords.
    """
    connection = Connection(name)
    keystore = Keystore(connection.get_keystore())

    print("Attempting passwords. Ctrl+C to end session")
    try:

        while True:

            rows = connection.get_untried()
            indices = [row[0] for row in rows]
            passwords = [row[1] for row in rows]
            current_indices = []
            current_passwords = []

            tried = 0
            while len(rows) != 0:
                start_time = time.time()

                for _ in range(BATCH_SIZE):
                    current_indices.append(indices.pop())
                    current_passwords.append(passwords.pop())

                successes = keystore.check_multi(current_passwords)
                connection.update(current_indices, successes)

                for i, success in enumerate(successes):
                    if success:
                        print(f"SUCCESS: {current_passwords[i]}")
                        exit()
                    else:
                        print(f"tried {current_passwords[i]}")

                tried += BATCH_SIZE
                current_passwords = []
                current_indices = []

                end_time = time.time()

                profile = (end_time - start_time) / BATCH_SIZE
                remaining = len(rows) - tried
                hours = (profile * remaining) / (60.0 * 60.0)
                print(f"{remaining} passwords remaining.")
                print(f"{profile} seconds per password.")
                print(f"{hours} hours remaining.\n")

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nSession ended")


if __name__ == "__main__":
    app()
