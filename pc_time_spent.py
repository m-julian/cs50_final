# application that tracks how much time you spend on your pc and what you are doing

from datetime import datetime
import sqlite3
from pathlib import Path

# GLOBAL_CONFIG

DATABASE_DIR = "."
DATABASE_NAME = "pc_time.db"
TRACKED_PROGRAMS = ["slack", "discord", "steam", "firefox", "chrome"]
CURRENT_DATE = datetime.today().strftime('%Y-%m-%d')

# create databases
p = Path(DATABASE_DIR)
p = p.absolute()
db_path = p / DATABASE_NAME

def check_database_present(db_path):

    if not db_path.exists():
        con = sqlite3.connect(DATABASE_NAME)
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS timings (id INTEGER PRIMARY_KEY, date TEXT)""")
        con.commit()
        con.close()

def record_pc_start():
    


if __name__ == "__main__":

    check_database_present(db_path)