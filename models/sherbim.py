"""CRUD për tabelën Sherbim."""
from db import Database


def listo() -> list[dict]:
    with Database.cursor() as cur:
        cur.execute("SELECT * FROM Sherbim ORDER BY emertimi")
        return cur.fetchall()


def shto(emertimi, cmimi) -> int:
    with Database.cursor() as cur:
        cur.execute(
            "INSERT INTO Sherbim (emertimi, cmimi) VALUES (%s, %s)",
            (emertimi, cmimi),
        )
        return cur.lastrowid


def fshij(sherbim_id: int) -> None:
    with Database.cursor() as cur:
        cur.execute("DELETE FROM Sherbim WHERE sherbim_id = %s", (sherbim_id,))
