"""Pika e fillimit të aplikacionit Hotel Adriatik.

Përdorimi:
    python main.py

Para se të nisni aplikacionin, sigurohuni që:
  1. MySQL është duke punuar lokalisht
  2. Keni ekzekutuar skriptet SQL nga drejtoria database/
  3. Keni instaluar varësitë: pip install -r requirements.txt
"""
import ctypes
import sys
from ui.main_window import MainWindow


def _set_windows_app_id():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "HotelAdriatik.ReservationSystem.1"
        )
    except Exception:
        pass


def main():
    try:
        _set_windows_app_id()
        app = MainWindow()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nU mbyll nga përdoruesi.")
        sys.exit(0)


if __name__ == "__main__":
    main()
