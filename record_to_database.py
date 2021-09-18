from pathlib import Path
import sqlite3
import win32api
from config import DB_PATH, TIME_BETWEEN_RECORDINGS
from time import sleep


def make_database(db_path: Path):

    if not db_path.exists():
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS usage (id INTEGER PRIMARY KEY, date TEXT, user_present INTEGER)""")
        con.commit()
        con.close()

def database_exists(db_path: Path):

    if not db_path.exists():
        return False
    return True

class User:

    def __init__(self):
        self.event = win32api.GetLastInputInfo()

    def record_user_status(self, db_path: Path, user_status: bool):
        """ Record if the user is on the pc or not."""

        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("""INSERT INTO usage (date, user_present) VALUES (DATETIME('now'), ?)""", (int(user_status),))
        con.commit()
        con.close()

    def check_status_and_record(self):
        current_event = win32api.GetLastInputInfo()

        # if self.event == current_event, then user is away, so we want to record False
        self.record_user_status(DB_PATH, not self.event == current_event)
        self.event = current_event


def start_recording_user_status():

    make_database(DB_PATH)
    user = User()
    while True:
        sleep(TIME_BETWEEN_RECORDINGS)
        user.check_status_and_record()


start_recording_user_status()
