# application that tracks how much time you spend on your pc and what you are doing

import sqlite3
from pathlib import Path
from time import sleep
import win32api
import argparse
import pandas as pd

# GLOBAL_CONFIG
DATABASE_NAME = "timings.db"
# TRACKED_PROGRAMS = ["slack", "discord", "steam", "firefox", "chrome"] # could be a bit too complicated to do
# create database Path object
p = Path.home().absolute()
# DB_PATH = p / "Desktop" / DATABASE_NAME
DB_PATH = Path(".") / DATABASE_NAME
TIME_BETWEEN_RECORDINGS = 3 # time between db recording

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

def record_user_status(db_path: Path, user_status: bool):
    """ Record if the user is on the pc or not."""

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""INSERT INTO usage (date, user_present) VALUES (DATETIME('now'), ?)""", (int(user_status),))
    con.commit()
    con.close()

def export_excel_file(db_path, start_date=None, end_date=None):

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # if no start and end dates are given in gui, then select the max and min as dates
    if start_date is None:
        # returns a tuple, so need a ,
        start_date, = cur.execute("""SELECT MIN(date) FROM usage""").fetchone()
    if end_date is None:
        end_date, = cur.execute("""SELECT MAX(date) FROM usage""").fetchone()

    # read in df from sql database between the two selected dates
    df = pd.read_sql("SELECT * FROM usage WHERE date BETWEEN DATETIME(?) AND DATETIME(?);", con, index_col="id", params=(start_date, end_date), parse_dates={"date":{"infer_datetime_format":True}})

    daily_data_to_plot = []
    dates = df["date"].map(lambda t: t.date()).unique()

    # iterate over dates in dataframe to find the time spent on pc each day
    for date in dates:

        # create a smaller dataframe for each date
        df_date_subset = df[df["date"].dt.date == date].copy()
        df_date_subset["date_offset"] = df_date_subset["date"].shift()
        df_date_subset["time_present"] = df_date_subset["date"] - df_date_subset["date_offset"]

        # split the dataframe into user present and user absent
        time_user_present = df_date_subset[df_date_subset["user_present"] == 1]["time_present"].dt.seconds.sum()
        time_user_absent = df_date_subset[df_date_subset["user_present"] == 0]["time_present"].dt.seconds.sum()

        print(time_user_present)
        print(time_user_absent)
        daily_data_to_plot.append((str(date), time_user_present, time_user_absent))


    print(daily_data_to_plot)

class User:

    def __init__(self):
        self.event = win32api.GetLastInputInfo()

    def check_status(self):
        current_event = win32api.GetLastInputInfo()

        # if self.event == current_event, then user is away, so we want to record False
        record_user_status(DB_PATH, not self.event == current_event)
        self.event = current_event

record = False

if __name__ == "__main__":

    make_database(DB_PATH)
    user = User()
    while record:
        sleep(TIME_BETWEEN_RECORDINGS)
        user.check_status()
    export_excel_file(DB_PATH)

    # else:
    #     make_database(DB_PATH)
    #     user = User()
    #     while True:
    #         sleep(TIME_BETWEEN_RECORDINGS)
    #         user.check_status()

# use pysimplegui or something like that for gui
# have option to start script and start recording db
# have option to select upper and lower dates (based on sql table) - sort sqlite table by dates and pick lowest and highest date
# once a lower and upper dates are selected, then make the excel spreadsheet and calculate stuff
# make a bar chart for each day, showing how much time the pc was on, as well as how much time the user was on the pc

# SELECT * FROM usage WHERE user_present = 1 AND


    # parser = argparse.ArgumentParser()
    # parser.add_argument("-xl", action="store_true")
    # args = parser.parse_args()

    # if args.xl is True and (database_exists(DB_PATH) is True):