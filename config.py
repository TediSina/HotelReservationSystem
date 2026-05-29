"""Konfigurimi i lidhjes me bazën e të dhënave MySQL.

Ndryshoni vlerat e mëposhtme sipas instalimit tuaj lokal të MySQL.
Mund të përdorni gjithashtu variabla mjedisi (environment variables).
"""
import os

DB_CONFIG = {
    "host":     os.getenv("HOTEL_DB_HOST", "localhost"),
    "port":     int(os.getenv("HOTEL_DB_PORT", "3306")),
    "user":     os.getenv("HOTEL_DB_USER", "root"),
    "password": os.getenv("HOTEL_DB_PASS", ""),
    "database": os.getenv("HOTEL_DB_NAME", "hotel_db"),
    "charset":  "utf8mb4",
    "use_unicode": True,
    "autocommit": False,
}

APP_TITLE = "Hotel Adriatik — Sistemi i Rezervimeve"
APP_VERSION = "1.0.0"
TVSH_RATE = 0.20  # 20%
