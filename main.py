"""Pika e fillimit të aplikacionit Hotel Adriatik.

Përdorimi:
    python main.py

Para se të nisni aplikacionin, sigurohuni që:
  1. MySQL është duke punuar lokalisht
  2. Keni ekzekutuar skriptet SQL nga drejtoria database/
  3. Keni instaluar varësitë: pip install -r requirements.txt
"""
import sys
from ui.main_window import MainWindow


def main():
    try:
        app = MainWindow()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nU mbyll nga përdoruesi.")
        sys.exit(0)


if __name__ == "__main__":
    main()
