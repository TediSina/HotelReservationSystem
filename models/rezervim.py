"""CRUD për tabelën Rezervimi (përdor view-n v_rezervime_detajuara)."""
from db import Database


def listo(status_filter: str = None) -> list[dict]:
    with Database.cursor() as cur:
        if status_filter and status_filter != 'TË GJITHA':
            cur.execute(
                "SELECT * FROM v_rezervime_detajuara WHERE status = %s "
                "ORDER BY data_check_in DESC",
                (status_filter,),
            )
        else:
            cur.execute(
                "SELECT * FROM v_rezervime_detajuara ORDER BY data_check_in DESC"
            )
        return cur.fetchall()


def gjej(rezervim_id: int) -> dict | None:
    with Database.cursor() as cur:
        cur.execute(
            "SELECT * FROM v_rezervime_detajuara WHERE rezervim_id = %s",
            (rezervim_id,),
        )
        return cur.fetchone()


def shto(klient_id, dhoma_id, check_in, check_out, status='I_REZERVUAR') -> int:
    """Triggeri trg_rezervim_check_overlap parandalon mbivendosjet."""
    with Database.cursor() as cur:
        cur.execute(
            "INSERT INTO Rezervimi (klient_id, dhoma_id, data_check_in, "
            "data_check_out, status) VALUES (%s, %s, %s, %s, %s)",
            (klient_id, dhoma_id, check_in, check_out, status),
        )
        return cur.lastrowid


def ndrysho_status(rezervim_id: int, status_i_ri: str) -> None:
    with Database.cursor() as cur:
        cur.execute(
            "UPDATE Rezervimi SET status = %s WHERE rezervim_id = %s",
            (status_i_ri, rezervim_id),
        )


def fshij(rezervim_id: int) -> None:
    with Database.cursor() as cur:
        cur.execute("DELETE FROM Rezervimi WHERE rezervim_id = %s", (rezervim_id,))


def shto_sherbim(rezervim_id, sherbim_id, sasia=1) -> None:
    with Database.cursor() as cur:
        cur.execute(
            "INSERT INTO RezervimSherbim (rezervim_id, sherbim_id, sasia) "
            "VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE sasia = sasia + VALUES(sasia)",
            (rezervim_id, sherbim_id, sasia),
        )


def listo_sherbimet(rezervim_id: int) -> list[dict]:
    with Database.cursor() as cur:
        cur.execute(
            "SELECT rs.*, s.emertimi, s.cmimi "
            "FROM RezervimSherbim rs JOIN Sherbim s ON rs.sherbim_id = s.sherbim_id "
            "WHERE rs.rezervim_id = %s",
            (rezervim_id,),
        )
        return cur.fetchall()
