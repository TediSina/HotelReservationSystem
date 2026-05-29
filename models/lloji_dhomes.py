"""CRUD për tabelën LlojiDhomes."""
from db import Database


def listo() -> list[dict]:
    with Database.cursor() as cur:
        cur.execute("SELECT * FROM LlojiDhomes ORDER BY cmim_baza")
        return cur.fetchall()


def gjej(lloji_id: int) -> dict | None:
    with Database.cursor() as cur:
        cur.execute("SELECT * FROM LlojiDhomes WHERE lloji_id = %s", (lloji_id,))
        return cur.fetchone()


def shto(emertimi, kapaciteti, cmim_baza, pershkrim) -> int:
    with Database.cursor() as cur:
        cur.execute(
            "INSERT INTO LlojiDhomes (emertimi, kapaciteti, cmim_baza, pershkrim) "
            "VALUES (%s, %s, %s, %s)",
            (emertimi, kapaciteti, cmim_baza, pershkrim),
        )
        return cur.lastrowid


def perditeso(lloji_id, emertimi, kapaciteti, cmim_baza, pershkrim) -> None:
    with Database.cursor() as cur:
        cur.execute(
            "UPDATE LlojiDhomes SET emertimi=%s, kapaciteti=%s, "
            "cmim_baza=%s, pershkrim=%s WHERE lloji_id=%s",
            (emertimi, kapaciteti, cmim_baza, pershkrim, lloji_id),
        )


def fshij(lloji_id: int) -> None:
    with Database.cursor() as cur:
        cur.execute("DELETE FROM LlojiDhomes WHERE lloji_id = %s", (lloji_id,))
