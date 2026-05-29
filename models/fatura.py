"""CRUD për tabelën Fatura — përdor proceduren e ruajtur sp_gjenero_fature."""
from db import Database


def listo() -> list[dict]:
    with Database.cursor() as cur:
        cur.execute(
            "SELECT f.*, CONCAT(k.emer,' ',k.mbiemer) AS klienti, d.numri AS nr_dhoma "
            "FROM Fatura f "
            "JOIN Rezervimi r ON f.rezervim_id = r.rezervim_id "
            "JOIN Klienti   k ON r.klient_id   = k.klient_id "
            "JOIN Dhoma     d ON r.dhoma_id    = d.dhoma_id "
            "ORDER BY f.data_leshimit DESC"
        )
        return cur.fetchall()


def gjej(fatura_id: int) -> dict | None:
    with Database.cursor() as cur:
        cur.execute(
            "SELECT f.*, CONCAT(k.emer,' ',k.mbiemer) AS klienti, "
            "k.dokument_id, d.numri AS nr_dhoma, ld.emertimi AS lloji, "
            "r.data_check_in, r.data_check_out, "
            "DATEDIFF(r.data_check_out, r.data_check_in) AS net "
            "FROM Fatura f "
            "JOIN Rezervimi r ON f.rezervim_id = r.rezervim_id "
            "JOIN Klienti   k ON r.klient_id   = k.klient_id "
            "JOIN Dhoma     d ON r.dhoma_id    = d.dhoma_id "
            "JOIN LlojiDhomes ld ON d.lloji_id = ld.lloji_id "
            "WHERE f.fatura_id = %s",
            (fatura_id,),
        )
        return cur.fetchone()


def gjej_per_rezervim(rezervim_id: int) -> dict | None:
    with Database.cursor() as cur:
        cur.execute("SELECT * FROM Fatura WHERE rezervim_id = %s", (rezervim_id,))
        return cur.fetchone()


def gjenero_per_rezervim(rezervim_id: int, menyra_pagese: str = 'CASH') -> int:
    """Thërret proceduren e ruajtur sp_gjenero_fature dhe kthen fatura_id-në."""
    conn = Database.get_connection()
    cur = conn.cursor()
    try:
        result_args = cur.callproc('sp_gjenero_fature', (rezervim_id, menyra_pagese, 0))
        fatura_id = result_args[2]
        conn.commit()
        return int(fatura_id)
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def ndrysho_status_pageses(fatura_id: int, status_i_ri: str) -> None:
    with Database.cursor() as cur:
        cur.execute(
            "UPDATE Fatura SET status_pagese = %s WHERE fatura_id = %s",
            (status_i_ri, fatura_id),
        )


def te_ardhurat_mujore() -> list[dict]:
    with Database.cursor() as cur:
        cur.execute("SELECT * FROM v_te_ardhurat_mujore ORDER BY muaji DESC")
        return cur.fetchall()


def shfrytezimi_dhomave() -> list[dict]:
    with Database.cursor() as cur:
        cur.execute("SELECT * FROM v_shfrytezimi_dhomave ORDER BY nr_rezervimesh DESC")
        return cur.fetchall()
