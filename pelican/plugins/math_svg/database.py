from __future__ import annotations

import hashlib
from pathlib import Path
import sqlite3

from .settings import PelicanMathSettings


def hash_equation(equation: str) -> str:
    return hashlib.sha256(equation.encode()).hexdigest()


class Database:
    def __init__(self):
        path = Path(".cache") / "pelican-math-svg"
        path.mkdir(exist_ok=True, parents=True)
        self.connection = sqlite3.connect(path / "equations.db")
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS inline ("
            "  hash TEXT PRIMARY KEY CHECK (length(hash) == 64), "
            "  equation TEXT UNIQUE, "
            "  rendered TEXT, "
            "  settings TEXT"
            ")"
        )

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS display ("
            "  hash TEXT PRIMARY KEY CHECK (length(hash) == 64), "
            "  equation TEXT UNIQUE, "
            "  rendered TEXT, "
            "  settings TEXT"
            ")"
        )
        self.connection.commit()

    def add_equation(
        self,
        inline: bool,
        equation: str,
        settings: PelicanMathSettings,
        rendered: str | None = None,
    ):
        hash = hash_equation(equation)
        if inline:
            self.cursor.execute(
                "INSERT OR REPLACE INTO inline VALUES (?, ?, ?, ?)",
                (hash, equation, rendered, settings.serialize()),
            )
        else:
            self.cursor.execute(
                "INSERT OR REPLACE INTO display VALUES (?, ?, ?, ?)",
                (hash, equation, rendered, settings.serialize()),
            )
        self.connection.commit()

    def fetch_rendered_equation(
        self, inline: bool, equation: str
    ) -> tuple[str | None, str | None]:
        hash = hash_equation(equation)
        if inline:
            self.cursor.execute(
                "SELECT rendered, settings FROM inline WHERE hash = ?", (hash,)
            )
        else:
            self.cursor.execute(
                "SELECT rendered, settings FROM display WHERE hash = ?", (hash,)
            )
        entry = self.cursor.fetchone()
        self.connection.commit()
        if entry:
            return entry[0], entry[1]

        return None, None

    def fetch_missing_inline(self) -> list[str]:
        self.cursor.execute("SELECT equation FROM inline WHERE rendered IS NULL")
        return [entry[0] for entry in self.cursor.fetchall()]

    def fetch_missing_display(self) -> list[str]:
        self.cursor.execute("SELECT equation FROM display WHERE rendered IS NULL")
        return [entry[0] for entry in self.cursor.fetchall()]
