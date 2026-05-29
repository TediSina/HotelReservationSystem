-- ============================================================================
-- PAMJET (VIEWS), TRIGGERAT DHE PROCEDURAT E RUAJTURA
-- ============================================================================
USE hotel_db;

-- ----------------------------------------------------------------------------
-- VIEW: Detajet e plota të rezervimeve (për ekranin kryesor)
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS v_rezervime_detajuara;
CREATE VIEW v_rezervime_detajuara AS
SELECT
    r.rezervim_id,
    CONCAT(k.emer, ' ', k.mbiemer) AS klienti,
    k.dokument_id,
    d.numri                         AS nr_dhoma,
    ld.emertimi                     AS lloji,
    r.data_check_in,
    r.data_check_out,
    DATEDIFF(r.data_check_out, r.data_check_in) AS net,
    r.status,
    ld.cmim_baza,
    DATEDIFF(r.data_check_out, r.data_check_in) * ld.cmim_baza AS shuma_dhomes
FROM Rezervimi r
JOIN Klienti k       ON r.klient_id = k.klient_id
JOIN Dhoma   d       ON r.dhoma_id  = d.dhoma_id
JOIN LlojiDhomes ld  ON d.lloji_id  = ld.lloji_id;

-- ----------------------------------------------------------------------------
-- VIEW: Raporti i të ardhurave mujore
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS v_te_ardhurat_mujore;
CREATE VIEW v_te_ardhurat_mujore AS
SELECT
    DATE_FORMAT(f.data_leshimit, '%Y-%m') AS muaji,
    COUNT(*)                              AS nr_fatura,
    SUM(f.shuma_neto)                     AS neto_total,
    SUM(f.tvsh)                           AS tvsh_total,
    SUM(f.shuma_totale)                   AS shuma_totale
FROM Fatura f
WHERE f.status_pagese = 'E_PAGUAR'
GROUP BY DATE_FORMAT(f.data_leshimit, '%Y-%m');

-- ----------------------------------------------------------------------------
-- VIEW: Shfrytëzimi i dhomave (sa rezervime për dhomë)
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS v_shfrytezimi_dhomave;
CREATE VIEW v_shfrytezimi_dhomave AS
SELECT
    d.numri,
    ld.emertimi                AS lloji,
    COUNT(r.rezervim_id)       AS nr_rezervimesh,
    COALESCE(SUM(DATEDIFF(r.data_check_out, r.data_check_in)), 0) AS net_total
FROM Dhoma d
JOIN LlojiDhomes ld ON d.lloji_id = ld.lloji_id
LEFT JOIN Rezervimi r
       ON r.dhoma_id = d.dhoma_id
      AND r.status IN ('I_REGJISTRUAR','I_PERFUNDUAR')
GROUP BY d.dhoma_id, d.numri, ld.emertimi;

-- ============================================================================
-- TRIGGERAT
-- ============================================================================

DROP TRIGGER IF EXISTS trg_rezervim_check_overlap;
DELIMITER //
-- Parandalon mbivendosjen e rezervimeve për të njëjtën dhomë.
CREATE TRIGGER trg_rezervim_check_overlap
BEFORE INSERT ON Rezervimi
FOR EACH ROW
BEGIN
    DECLARE konflikt INT DEFAULT 0;
    SELECT COUNT(*) INTO konflikt
    FROM Rezervimi r
    WHERE r.dhoma_id = NEW.dhoma_id
      AND r.status IN ('I_REZERVUAR','I_REGJISTRUAR')
      AND NOT (NEW.data_check_out <= r.data_check_in
            OR NEW.data_check_in  >= r.data_check_out);
    IF konflikt > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Dhoma është e zënë në këtë periudhë.';
    END IF;
END//
DELIMITER ;

DROP TRIGGER IF EXISTS trg_rezervim_status_dhomes;
DELIMITER //
-- Përditëson statusin e dhomës sipas ndryshimit të rezervimit.
CREATE TRIGGER trg_rezervim_status_dhomes
AFTER UPDATE ON Rezervimi
FOR EACH ROW
BEGIN
    IF NEW.status = 'I_REGJISTRUAR' THEN
        UPDATE Dhoma SET status='E_ZENE' WHERE dhoma_id = NEW.dhoma_id;
    ELSEIF NEW.status IN ('I_PERFUNDUAR','I_ANULUAR') THEN
        UPDATE Dhoma SET status='E_LIRE' WHERE dhoma_id = NEW.dhoma_id;
    END IF;
END//
DELIMITER ;

-- ============================================================================
-- PROCEDURA E RUAJTUR: Gjenerimi automatik i faturës
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_gjenero_fature;
DELIMITER //
CREATE PROCEDURE sp_gjenero_fature(
    IN  p_rezervim_id   INT,
    IN  p_menyra_pagese VARCHAR(20),
    OUT p_fatura_id     INT
)
BEGIN
    DECLARE v_neto      DECIMAL(10,2);
    DECLARE v_tvsh      DECIMAL(10,2);
    DECLARE v_totale    DECIMAL(10,2);
    DECLARE v_net       INT;
    DECLARE v_cmim      DECIMAL(10,2);
    DECLARE v_sherbime  DECIMAL(10,2);
    DECLARE v_ekziston  INT;

    -- A ekziston tashmë një faturë për këtë rezervim?
    SELECT COUNT(*) INTO v_ekziston FROM Fatura WHERE rezervim_id = p_rezervim_id;
    IF v_ekziston > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Fatura për këtë rezervim ekziston tashmë.';
    END IF;

    -- Llogaritja e shumës së dhomës (netë × çmim baza i llojit)
    SELECT DATEDIFF(r.data_check_out, r.data_check_in), ld.cmim_baza
      INTO v_net, v_cmim
    FROM Rezervimi r
    JOIN Dhoma d        ON r.dhoma_id = d.dhoma_id
    JOIN LlojiDhomes ld ON d.lloji_id = ld.lloji_id
    WHERE r.rezervim_id = p_rezervim_id;

    -- Shërbimet ekstra
    SELECT COALESCE(SUM(s.cmimi * rs.sasia), 0) INTO v_sherbime
    FROM RezervimSherbim rs
    JOIN Sherbim s ON rs.sherbim_id = s.sherbim_id
    WHERE rs.rezervim_id = p_rezervim_id;

    SET v_neto   = (v_net * v_cmim) + v_sherbime;
    SET v_tvsh   = ROUND(v_neto * 0.20, 2);  -- TVSH 20%
    SET v_totale = v_neto + v_tvsh;

    INSERT INTO Fatura
        (rezervim_id, data_leshimit, shuma_neto, tvsh, shuma_totale, menyra_pagese)
        VALUES
        (p_rezervim_id, CURDATE(), v_neto, v_tvsh, v_totale, p_menyra_pagese);

    SET p_fatura_id = LAST_INSERT_ID();

    -- Përditëso statusin e rezervimit në I_PERFUNDUAR
    UPDATE Rezervimi SET status='I_PERFUNDUAR' WHERE rezervim_id = p_rezervim_id;
END//
DELIMITER ;
