"""CRUD për tabelën Dhoma."""
from db import Database


def listo(vetem_te_lira: bool = False) -> list[dict]:
    with Database.cursor() as cur:
        if vetem_te_lira:
            cur.execute(
                "SELECT d.*, ld.emertimi AS lloji, ld.cmim_baza, ld.kapaciteti "
                "FROM Dhoma d JOIN LlojiDhomes ld ON d.lloji_id = ld.lloji_id "
                "WHERE d.status = 'E_LIRE' ORDER BY d.numri"
            )
        else:
            cur.execute(
                "SELECT d.*, ld.emertimi AS lloji, ld.cmim_baza, ld.kapaciteti "
                "FROM Dhoma d JOIN LlojiDhomes ld ON d.lloji_id = ld.lloji_id "
                "ORDER BY d.numri"
            )
        return cur.fetchall()


def gjej_te_lira_per_periudhe(check_in, check_out) -> list[dict]:
    """Kthen dhomat e lira për periudhën e dhënë (nuk kanë rezervime aktive që mbivendosen)."""
    with Database.cursor() as cur:
        cur.execute(
            "SELECT d.*, ld.emertimi AS lloji, ld.cmim_baza, ld.kapaciteti "
            "FROM Dhoma d JOIN LlojiDhomes ld ON d.lloji_id = ld.lloji_id "
            "WHERE d.status <> 'MIREMBAJTJE' "
            "AND d.dhoma_id NOT IN ("
            "    SELECT r.dhoma_id FROM Rezervimi r "
            "    WHERE r.status IN ('I_REZERVUAR','I_REGJISTRUAR') "
            "    AND NOT (%s <= r.data_check_in OR %s >= r.data_check_out)"
            ") ORDER BY d.numri",
            (check_out, check_in),
        )
        return cur.fetchall()


def gjej(dhoma_id: int) -> dict | None:
    with Database.cursor() as cur:
        cur.execute(
            "SELECT d.*, ld.emertimi AS lloji, ld.cmim_baza "
            "FROM Dhoma d JOIN LlojiDhomes ld ON d.lloji_id = ld.lloji_id "
            "WHERE d.dhoma_id = %s",
            (dhoma_id,),
        )
        return cur.fetchone()


def shto(numri, kati, lloji_id, status='E_LIRE') -> int:
    with Database.cursor() as cur:
        cur.execute(
            "INSERT INTO Dhoma (numri, kati, lloji_id, status) "
            "VALUES (%s, %s, %s, %s)",
            (numri, kati, lloji_id, status),
        )
        return cur.lastrowid


def perditeso(dhoma_id, numri, kati, lloji_id, status) -> None:
    with Database.cursor() as cur:
        cur.execute(
            "UPDATE Dhoma SET numri=%s, kati=%s, lloji_id=%s, status=%s "
            "WHERE dhoma_id=%s",
            (numri, kati, lloji_id, status, dhoma_id),
        )


def fshij(dhoma_id: int) -> None:
    with Database.cursor() as cur:
        cur.execute("DELETE FROM Dhoma WHERE dhoma_id = %s", (dhoma_id,))
