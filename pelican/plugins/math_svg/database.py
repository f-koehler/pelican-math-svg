import hashlib
from pathlib import Path
import sqlite3
from typing import Optional


def hash_equation(equation: str) -> str:
    return hashlib.sha256(equation.encode()).hexdigest()


class Database:
    def __init__(self):
        path = Path(".cache") / "pelican-math-svg"
        path.mkdir(exist_ok=True, parents=True)
        self.connection = sqlite3.connect(path / "equations.db")
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS equations ("
            "  hash TEXT PRIMARY KEY CHECK (length(hash) == 64), "
            "  equation TEXT UNIQUE, "
            "  rendered TEXT"
            ")"
        )
        self.connection.commit()

    def contains_equation(self, equation: str) -> bool:
        hash = hash_equation(equation)
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM equations WHERE hash == ?)", hash
        )
        return self.cursor.fetchone() == 1

    def add_equation(self, equation: str, rendered: Optional[str] = None):
        hash = hash_equation(equation)
        self.cursor.execute(
            "INSERT OR REPLACE INTO equations VALUES (?, ?, ?)",
            (hash, equation, rendered),
        )
        self.connection.commit()

    def fetch_rendered_equation(self, equation: str) -> Optional[str]:
        hash = hash_equation(equation)
        self.cursor.execute("SELECT rendered FROM equations WHERE hash = ?", (hash,))
        entry = self.cursor.fetchone()
        self.connection.commit()
        if entry:
            return entry[0]

        return None

    def fetch_missing_equations(self) -> list[str]:
        self.cursor.execute("SELECT equation FROM equations WHERE rendered IS NULL")
        return [entry[0] for entry in self.cursor.fetchall()]
