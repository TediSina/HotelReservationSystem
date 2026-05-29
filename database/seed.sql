-- ============================================================================
-- TË DHËNA TESTUESE — Hotel "Adriatik"
-- ============================================================================
USE hotel_db;

-- Llojet e dhomave
INSERT INTO LlojiDhomes (emertimi, kapaciteti, cmim_baza, pershkrim) VALUES
('Single',     1, 4500.00,  'Dhomë teke me një shtrat dhe banjë private.'),
('Double',     2, 7000.00,  'Dhomë dyshe me shtrat matrimonial dhe pamje nga deti.'),
('Twin',       2, 7000.00,  'Dhomë me dy shtretër teke të ndarë.'),
('Suite',      3, 14000.00, 'Suit me dhomë gjumi, sallon dhe ballkon.'),
('Familjare',  4, 11000.00, 'Dhomë familjare me dy shtretër dyshe dhe banjë të madhe.');

-- Dhomat fizike
INSERT INTO Dhoma (numri, kati, lloji_id, status) VALUES
('101', 1, (SELECT lloji_id FROM LlojiDhomes WHERE emertimi='Single'),    'E_LIRE'),
('102', 1, (SELECT lloji_id FROM LlojiDhomes WHERE emertimi='Single'),    'E_LIRE'),
('103', 1, (SELECT lloji_id FROM LlojiDhomes WHERE emertimi='Double'),    'E_LIRE'),
('201', 2, (SELECT lloji_id FROM LlojiDhomes WHERE emertimi='Double'),    'E_LIRE'),
('202', 2, (SELECT lloji_id FROM LlojiDhomes WHERE emertimi='Twin'),      'E_LIRE'),
('203', 2, (SELECT lloji_id FROM LlojiDhomes WHERE emertimi='Familjare'), 'E_LIRE'),
('301', 3, (SELECT lloji_id FROM LlojiDhomes WHERE emertimi='Suite'),     'MIREMBAJTJE'),
('302', 3, (SELECT lloji_id FROM LlojiDhomes WHERE emertimi='Suite'),     'E_LIRE'),
('303', 3, (SELECT lloji_id FROM LlojiDhomes WHERE emertimi='Familjare'), 'E_LIRE');

-- Shërbimet ekstra
INSERT INTO Sherbim (emertimi, cmimi) VALUES
('Mëngjes',          800.00),
('Darkë',           1500.00),
('Mini-bar',         500.00),
('Spa',             2500.00),
('Parking',          400.00),
('Lavanderi',        600.00);

-- Klientët shembull
INSERT INTO Klienti (emer, mbiemer, dokument_id, telefon, email, kombesia) VALUES
('Arben',  'Hoxha',   'I12345678X', '+355692345678', 'arben.hoxha@example.com',   'Shqiptare'),
('Drita',  'Kola',    'J23456789Y', '+355684567890', 'drita.kola@example.com',    'Shqiptare'),
('Marco',  'Rossi',   'IT9876543',  '+390471123456', 'marco.rossi@example.it',    'Italiane'),
('Anna',   'Müller',  'DE5566778',  '+49301234567',  'anna.mueller@example.de',   'Gjermane'),
('Besnik', 'Krasniqi','K34567890Z', '+38344223344',  'besnik.krasniqi@example.com','Kosovare');
