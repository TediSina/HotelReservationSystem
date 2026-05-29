-- ============================================================================
-- SISTEMI I REZERVIMEVE NË HOTEL — SKEMA E BAZËS SË TË DHËNAVE
-- Forma përfundimtare: BCNF (Boyce-Codd Normal Form)
-- DBMS: MySQL 8.0+
-- ============================================================================
--
-- Hapat e normalizimit (versionet e ndërmjetme janë në dokument):
--   UNF   → Një tabelë e vetme e rrafshët me përsëritje dhe anomalitë.
--   1NF   → Eliminimi i grupeve të përsëritura, vlera atomike.
--   2NF   → Eliminimi i varësive të pjesshme nga çelësi i përbërë.
--   3NF   → Eliminimi i varësive tranzitive.
--   BCNF  → Çdo determinant është çelës kandidat (forma e mëposhtme).
--
-- Entitetet përfundimtare:
--   Klienti          — informacion identifikues mbi mysafirin
--   LlojiDhomes      — kategoria e dhomës (Single/Double/Suite/Familjare)
--   Dhoma            — dhoma fizike, me numër dhe kat
--   Rezervimi        — lidhja klient–dhomë për një periudhë
--   Sherbim          — shërbime opsionale (mëngjes, mini-bar, spa, etj.)
--   RezervimSherbim  — tabela e ndërmjetme (M:N) rezervim–shërbim
--   Fatura           — fatura e lëshuar për një rezervim (1:1 me Rezervimin)
-- ============================================================================

DROP DATABASE IF EXISTS hotel_db;
CREATE DATABASE hotel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hotel_db;

-- ----------------------------------------------------------------------------
-- KLIENTI
-- FD: klient_id → emer, mbiemer, dokument_id, telefon, email, kombesia
-- FD: dokument_id → klient_id  (dokument_id është çelës kandidat)
-- BCNF: të dy determinantët janë çelësa kandidatë. ✓
-- ----------------------------------------------------------------------------
CREATE TABLE Klienti (
    klient_id     INT AUTO_INCREMENT PRIMARY KEY,
    emer          VARCHAR(60)  NOT NULL,
    mbiemer       VARCHAR(60)  NOT NULL,
    dokument_id   VARCHAR(30)  NOT NULL UNIQUE,
    telefon       VARCHAR(30),
    email         VARCHAR(120),
    kombesia      VARCHAR(60)  DEFAULT 'Shqiptare',
    krijuar_me    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_klient_email CHECK (email IS NULL OR email LIKE '%@%.%')
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- LLOJI I DHOMËS
-- FD: lloji_id → emertimi, kapaciteti, cmim_baza, pershkrim
-- FD: emertimi → lloji_id  (emertimi është UNIQUE → çelës kandidat)
-- BCNF: të dy determinantët janë çelësa kandidatë. ✓
-- ----------------------------------------------------------------------------
CREATE TABLE LlojiDhomes (
    lloji_id      INT AUTO_INCREMENT PRIMARY KEY,
    emertimi      VARCHAR(40)    NOT NULL UNIQUE,
    kapaciteti    INT            NOT NULL,
    cmim_baza     DECIMAL(10, 2) NOT NULL,
    pershkrim     VARCHAR(255),
    CONSTRAINT chk_kapaciteti CHECK (kapaciteti BETWEEN 1 AND 10),
    CONSTRAINT chk_cmim_baza  CHECK (cmim_baza > 0)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- DHOMA
-- FD: dhoma_id → numri, kati, lloji_id, status
-- FD: numri    → dhoma_id  (numri është UNIQUE → çelës kandidat)
-- BCNF: të dy determinantët janë çelësa kandidatë. ✓
-- Vërejtje: lloji_id → cmim_baza, kapaciteti janë në LlojiDhomes (3NF i siguruar).
-- ----------------------------------------------------------------------------
CREATE TABLE Dhoma (
    dhoma_id      INT AUTO_INCREMENT PRIMARY KEY,
    numri         VARCHAR(10)    NOT NULL UNIQUE,
    kati          INT            NOT NULL,
    lloji_id      INT            NOT NULL,
    status        ENUM('E_LIRE', 'E_ZENE', 'MIREMBAJTJE') NOT NULL DEFAULT 'E_LIRE',
    CONSTRAINT fk_dhoma_lloji
        FOREIGN KEY (lloji_id) REFERENCES LlojiDhomes(lloji_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_kati CHECK (kati BETWEEN 0 AND 50)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- REZERVIMI
-- FD: rezervim_id → klient_id, dhoma_id, data_check_in, data_check_out, status
-- BCNF: çelësi primar është determinanti i vetëm. ✓
-- ----------------------------------------------------------------------------
CREATE TABLE Rezervimi (
    rezervim_id     INT AUTO_INCREMENT PRIMARY KEY,
    klient_id       INT  NOT NULL,
    dhoma_id        INT  NOT NULL,
    data_check_in   DATE NOT NULL,
    data_check_out  DATE NOT NULL,
    status          ENUM('I_REZERVUAR','I_REGJISTRUAR','I_PERFUNDUAR','I_ANULUAR')
                    NOT NULL DEFAULT 'I_REZERVUAR',
    krijuar_me      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rezervim_klient
        FOREIGN KEY (klient_id) REFERENCES Klienti(klient_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_rezervim_dhoma
        FOREIGN KEY (dhoma_id) REFERENCES Dhoma(dhoma_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_data_rezervim CHECK (data_check_out > data_check_in)
) ENGINE=InnoDB;

CREATE INDEX idx_rezervim_dates ON Rezervimi(data_check_in, data_check_out);
CREATE INDEX idx_rezervim_klient ON Rezervimi(klient_id);
CREATE INDEX idx_rezervim_dhoma ON Rezervimi(dhoma_id);

-- ----------------------------------------------------------------------------
-- SHËRBIMI (entitet i pavarur — çmime për shërbime ekstra)
-- FD: sherbim_id → emertimi, cmimi
-- ----------------------------------------------------------------------------
CREATE TABLE Sherbim (
    sherbim_id    INT AUTO_INCREMENT PRIMARY KEY,
    emertimi      VARCHAR(60)    NOT NULL UNIQUE,
    cmimi         DECIMAL(10, 2) NOT NULL,
    CONSTRAINT chk_sherbim_cmimi CHECK (cmimi >= 0)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- REZERVIM_SHERBIM (lidhja M:N midis Rezervimit dhe Shërbimit)
-- Çelës i përbërë (rezervim_id, sherbim_id).
-- FD: (rezervim_id, sherbim_id) → sasia
-- BCNF: çelësi primar i përbërë është determinanti i vetëm. ✓
-- ----------------------------------------------------------------------------
CREATE TABLE RezervimSherbim (
    rezervim_id   INT NOT NULL,
    sherbim_id    INT NOT NULL,
    sasia         INT NOT NULL DEFAULT 1,
    PRIMARY KEY (rezervim_id, sherbim_id),
    CONSTRAINT fk_rs_rezervim
        FOREIGN KEY (rezervim_id) REFERENCES Rezervimi(rezervim_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_rs_sherbim
        FOREIGN KEY (sherbim_id) REFERENCES Sherbim(sherbim_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_rs_sasia CHECK (sasia > 0)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- FATURA  (1:1 me Rezervimin — rezervim_id UNIQUE)
-- FD: fatura_id  → rezervim_id, data_leshimit, shuma_neto, tvsh, shuma_totale, ...
-- FD: rezervim_id → fatura_id  (çelës kandidat)
-- BCNF: të dy determinantët janë çelësa kandidatë. ✓
-- ----------------------------------------------------------------------------
CREATE TABLE Fatura (
    fatura_id        INT AUTO_INCREMENT PRIMARY KEY,
    rezervim_id      INT            NOT NULL UNIQUE,
    data_leshimit    DATE           NOT NULL,
    shuma_neto       DECIMAL(10, 2) NOT NULL,
    tvsh             DECIMAL(10, 2) NOT NULL,
    shuma_totale     DECIMAL(10, 2) NOT NULL,
    menyra_pagese    ENUM('CASH','KARTE','TRANSFER') NOT NULL DEFAULT 'CASH',
    status_pagese    ENUM('E_PAPAGUAR','E_PAGUAR','E_ANULUAR')
                     NOT NULL DEFAULT 'E_PAPAGUAR',
    CONSTRAINT fk_fatura_rezervim
        FOREIGN KEY (rezervim_id) REFERENCES Rezervimi(rezervim_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_fatura_shuma CHECK (shuma_neto >= 0 AND tvsh >= 0 AND shuma_totale >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_fatura_data ON Fatura(data_leshimit);
