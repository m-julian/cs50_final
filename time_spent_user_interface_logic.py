# application that tracks how much time you spend on your pc and what you are doing

from datetime import datetime
import sqlite3
from pathlib import Path
import pandas as pd
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QMainWindow
from qtpy import uic
import sys
from config import DB_PATH, PROGRAM_NAME

class Gui(QMainWindow):

    def __init__(self):

        super().__init__()

        # Setup for ui
        ui_path = Path("time_spent_user_interface.ui")
        Ui_MainWindow, _ = uic.loadUiType(ui_path)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # callbacks for buttons
        self.ui.start_date_calendar.clicked.connect(self.update_start_date)
        self.ui.end_date_calendar.clicked.connect(self.update_end_date)
        self.ui.export_to_excel_button.clicked.connect(self.export_excel_file)
        # todo: check if background process is running before making this button available
        self.ui.start_recording_button.clicked.connect(self.start_recording_user_status)

        self.show()

    def update_start_date(self):

        self._current_start_date = self.ui.start_date_calendar.selectedDate().toPyDate()

    def update_end_date(self):

        self._current_end_date = self.ui.end_date_calendar.selectedDate().toPyDate()

    def start_recording_user_status(self):
        
        import psutil
        if (PROGRAM_NAME + ".exe") in [p.name() for p in psutil.process_iter()]:
            QtWidgets.QMessageBox.about(self, "WARNING", f"'{PROGRAM_NAME}' is already running on the system.")
        else:
            import subprocess
            exe_path = Path("output/PCUserUptime.exe")
            subprocess.Popen(f"start {str(exe_path)}", shell=True)

    def export_excel_file(self):
        """ Exports excel file and makes charts based on time spent on pc each day"""

        start_date = self.ui.start_date_calendar.selectedDate().toPyDate()
        end_date = self.ui.end_date_calendar.selectedDate().toPyDate()

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()

        first_date_in_db, = cur.execute("""SELECT MIN(date) FROM usage""").fetchone()
        last_date_in_db, = cur.execute("""SELECT MAX(date) FROM usage""").fetchone()
        first_date_in_db = datetime.fromisoformat(first_date_in_db)
        last_date_in_db = datetime.fromisoformat(last_date_in_db)

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


            daily_data_to_plot.append((str(date), time_user_present, time_user_absent))

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    ex = Gui()
    app.exec_()