from typing import List
import os
import sqlite3


class Connection:
    def __init__(self, name, new=False):
        self.name = name
        filename = f"{name}.db"

        if os.path.exists(filename) and new:
            os.remove(filename)

        if not os.path.exists(filename) and not new:
            print("No existing keystore with that name.")
            exit()

        self.connection = sqlite3.connect(filename)

    def create(self, keystore_filepath: str):
        with open(keystore_filepath, "r") as f:
            contents = f.read()

        cursor = self.connection.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS keystore (
                id integer PRIMARY KEY,
                name text NOT NULL,
                contents text NOT NULL
            );"""
        )
        print("Created keystore table.")

        cursor.execute(
            f"""INSERT INTO keystore(name,contents)
                VALUES(?,?);""",
            (self.name, contents),
        )
        print("Inserted keystore information.")

        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS passwords (
                id integer PRIMARY KEY,
                raw text NOT NULL,
                tried INTEGER NOT NULL,
                success INTEGER NOT NULL
            );"""
        )
        print("Created passwords table.")

        self.connection.commit()

    def remove_untried(self) -> int:
        cursor = self.connection.cursor()
        a = cursor.execute("SELECT COUNT(*) FROM passwords").fetchone()[0]
        cursor.execute("DELETE FROM passwords WHERE tried = ?", (0,))
        b = cursor.execute("SELECT COUNT(*) FROM passwords").fetchone()[0]
        self.connection.commit()
        return a - b

    def load(self, raws: List[str]) -> int:
        cursor = self.connection.cursor()

        # Do not load passwords which are already in the db
        cursor.execute("SELECT * FROM passwords")
        rows = cursor.fetchall()
        existing_raws = set([row[1] for row in rows])

        new = [raw for raw in raws if raw not in existing_raws]

        for raw in new:
            cursor.execute(
                f"""INSERT INTO passwords(raw, tried, success)
                    VALUES(?,?,?); """,
                (raw, 0, 0),
            )

        self.connection.commit()
        return len(new)

    def get_keystore(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM keystore")
        row = cursor.fetchall()[0]
        return row[2]

    def get(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM passwords")
        return cursor.fetchall()

    def get_untried(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM passwords WHERE tried = 0")
        return cursor.fetchall()

    def update(self, indices: List[str], successes: List[bool]):
        cursor = self.connection.cursor()

        for i in range(len(indices)):
            index = indices[i]
            success = successes[i]

            cursor.execute(
                f"""UPDATE passwords
                    SET tried = ?,
                        success = ?
                    WHERE id = ?""",
                (1, 1 if success else 0, index),
            )

        self.connection.commit()
