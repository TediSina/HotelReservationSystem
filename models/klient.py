"""CRUD për tabelën Klienti."""
from db import Database


def listo(filtro_emri: str = "") -> list[dict]:
    with Database.cursor() as cur:
        if filtro_emri:
            like = f"%{filtro_emri}%"
            cur.execute(
                "SELECT * FROM Klienti "
                "WHERE emer LIKE %s OR mbiemer LIKE %s OR dokument_id LIKE %s "
                "ORDER BY mbiemer, emer",
                (like, like, like),
            )
        else:
            cur.execute("SELECT * FROM Klienti ORDER BY mbiemer, emer")
        return cur.fetchall()


def gjej(klient_id: int) -> dict | None:
    with Database.cursor() as cur:
        cur.execute("SELECT * FROM Klienti WHERE klient_id = %s", (klient_id,))
        return cur.fetchone()


def shto(emer, mbiemer, dokument_id, telefon, email, kombesia) -> int:
    with Database.cursor() as cur:
        cur.execute(
            "INSERT INTO Klienti (emer, mbiemer, dokument_id, telefon, email, kombesia) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (emer, mbiemer, dokument_id, telefon, email, kombesia),
        )
        return cur.lastrowid


def perditeso(klient_id, emer, mbiemer, dokument_id, telefon, email, kombesia) -> None:
    with Database.cursor() as cur:
        cur.execute(
            "UPDATE Klienti SET emer=%s, mbiemer=%s, dokument_id=%s, "
            "telefon=%s, email=%s, kombesia=%s WHERE klient_id=%s",
            (emer, mbiemer, dokument_id, telefon, email, kombesia, klient_id),
        )


def fshij(klient_id: int) -> None:
    with Database.cursor() as cur:
        cur.execute("DELETE FROM Klienti WHERE klient_id = %s", (klient_id,))
