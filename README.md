# Hotel Adriatik — Sistemi i Rezervimeve

Aplikacion desktop në **Python + MySQL** për menaxhimin e rezervimeve hoteliere.
Projekt për lëndën **Bazat e të Dhënave** — Maj 2026.

**Grupi:** Eros Habazaj • Alons Fejzo • Tedi Sina • Tea Sina • Riseld Logu

---

## Çfarë bën aplikacioni

- **Klientët** — regjistrim, kërkim, përditësim, fshirje
- **Dhomat & llojet** — inventar i plotë me kapacitet dhe çmim/natë
- **Rezervimet** — kontroll automatik i disponueshmërisë, parandalim i mbivendosjeve me trigger
- **Faturat** — gjenerim automatik me procedurë të ruajtur (netë × çmim + shërbime + TVSH 20%)
- **Shërbime ekstra** — mëngjes, mini-bar, spa, parking, etj. (lidhje M:N me rezervimin)
- **Raporte** — të ardhurat mujore, shfrytëzimi i dhomave (përdor SQL views)

---

## Struktura e projektit

```
HotelReservationSystem/
├── main.py                  # Pika e fillimit
├── config.py                # Konfigurimi i DB
├── db.py                    # Lidhja me MySQL
├── requirements.txt
├── database/
│   ├── schema.sql                  # Skema BCNF e plotë
│   ├── seed.sql                    # Të dhëna testuese
│   └── views_triggers_procs.sql    # Pamjet, triggerat & proceduria
├── models/                  # Shtresa e të dhënave (CRUD)
│   ├── klient.py
│   ├── lloji_dhomes.py
│   ├── dhoma.py
│   ├── rezervim.py
│   ├── sherbim.py
│   └── fatura.py
├── ui/                      # Ndërfaqja grafike (tkinter)
│   ├── main_window.py
│   ├── styles.py
│   ├── klient_tab.py
│   ├── dhoma_tab.py
│   ├── rezervim_tab.py
│   ├── fatura_tab.py
│   └── raporte_tab.py
└── assets/
    └── logo.png
```

---

## Instalimi & ekzekutimi

### 1. MySQL — krijo bazën

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
mysql -u root -p < database/views_triggers_procs.sql
```

### 2. Konfiguro lidhjen

Modifiko `config.py` ose përdor variabla mjedisi:

```bash
export HOTEL_DB_HOST=localhost
export HOTEL_DB_USER=root
export HOTEL_DB_PASS=fjalekalimi_yt
export HOTEL_DB_NAME=hotel_db
```

### 3. Instalo varësitë Python

```bash
pip install -r requirements.txt
```

### 4. Nis aplikacionin

```bash
python main.py
```

---

## Detaje teknike

### Normalizimi
Skema është e **normalizuar deri në BCNF**. Hapat e ndërmjetëm (UNF → 1NF → 2NF → 3NF → BCNF) janë dokumentuar në raportin e projektit (.docx).

### Triggerat
- `trg_rezervim_check_overlap` — parandalon mbivendosjet e rezervimeve
- `trg_rezervim_status_dhomes` — përditëson automatikisht statusin e dhomës

### Procedura e ruajtur
- `sp_gjenero_fature(rezervim_id, menyra_pagese)` — llogarit dhe lëshon faturën

### Views
- `v_rezervime_detajuara` — JOIN i të gjitha tabelave për listimin e rezervimeve
- `v_te_ardhurat_mujore` — agregim mujor i të ardhurave
- `v_shfrytezimi_dhomave` — nr. rezervimesh & netë për çdo dhomë

---

## Ndarja e detyrave

| Anëtari            | Roli                                         |
|--------------------|----------------------------------------------|
| Eros Habazaj       | Database Architect — ER, skema, DDL          |
| Alons Fejzo        | Triggera, procedura të ruajtura, views       |
| Tedi Sina          | Ndërfaqja Python/tkinter & integrim          |
| Tea Sina           | Pyetjet SQL & raportet                       |
| Riseld Logu        | Testim, dokumentim, prezantim                |
