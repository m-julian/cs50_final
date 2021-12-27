from pathlib import Path
import sqlite3
import win32api
from TimingManager_config import DB_PATH, TIME_BETWEEN_RECORDINGS
from time import sleep


def make_database(db_path: Path):
    """ Makes an SQLite database if one does not exist already."""

    if not db_path.exists():
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS usage (id INTEGER PRIMARY KEY, date TEXT, user_present INTEGER)"""
        )
        con.commit()
        con.close()


class User:
    """ Class used to record user status on the computer."""

    def __init__(self):
        self.event = win32api.GetLastInputInfo()

    def record_user_status(self, db_path: Path, user_status: bool):
        """ Record if the user is currently on the pc or not to the SQLite database."""

        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(
            """INSERT INTO usage (date, user_present) VALUES (DATETIME('now', 'localtime'), ?)""",
            (int(user_status),),
        )
        con.commit()
        con.close()

    def check_status_and_record(self):
        """ Gets the Windows current event and checks if the previous one is the same. If it is, the computer is idle, otherwise it is active (the user
        is actively using the computer)."""
        current_event = win32api.GetLastInputInfo()

        # if self.event == current_event, then user is away, so we want to record False
        self.record_user_status(DB_PATH, not self.event == current_event)
        self.event = current_event


def start_recording_user_status():
    """ Records the current user status and appends result to SQLite database."""

    make_database(DB_PATH)
    user = User()
    while True:
        sleep(TIME_BETWEEN_RECORDINGS)
        user.check_status_and_record()


start_recording_user_status()
