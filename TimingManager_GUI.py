""" application that tracks how much time you spend on your PC """
from datetime import datetime, date
import sqlite3
from pathlib import Path
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from PyQt5 import uic
from PyQt5.QtGui import QIcon
import sys
import psutil
from typing import Tuple, List
from TimingManager_plotter import Plotter
from TimingManager_config import DB_PATH, PROGRAM_NAME, PROGRAM_PATH


class Gui(QMainWindow):
    """TimingManager graphics user interface implementation."""

    def __init__(self):

        super().__init__()

        # Setup for ui
        ui_path = Path(__file__).parent / f"{PROGRAM_NAME}.ui"
        uic.loadUi(ui_path, self)

        self.setWindowTitle(PROGRAM_NAME)
        # https://icon-icons.com/icon/clock/30023 , from user https://icon-icons.com/users/ImFp7tvsz65dSnmg9s2G2/icon-sets/
        self.setWindowIcon(QIcon("clock.png"))

        # callbacks for buttons
        self.export_to_excel_button.clicked.connect(self.export_excel_file)
        # todo: check if background process is running before making this button available
        self.start_recording_button.clicked.connect(self.start_recording_user_status)
        self.stop_recording_button.clicked.connect(self.stop_recording_user_status)
        self.show_plotter_button.clicked.connect(self.plot_start_end_date)

        # make minimum and maximum dates for calendars based on what is available in database
        self.first_date_in_db_label.setText(
            "First Date in Database: " + str(self.first_and_last_date_from_db[0].date())
        )
        self.last_date_in_db_label.setText(
            "Last Date in Database: " + str(self.first_and_last_date_from_db[1].date())
        )

        self.start_date_calendar.setMinimumDate(self.first_and_last_date_from_db[0])
        self.start_date_calendar.setMaximumDate(self.first_and_last_date_from_db[1])
        self.end_date_calendar.setMinimumDate(self.first_and_last_date_from_db[0])
        self.end_date_calendar.setMaximumDate(self.first_and_last_date_from_db[1])

        self.show()

    @property
    def first_and_last_date_from_db(self) -> Tuple[datetime, datetime]:
        """Returns a tuple of the first and last datetime currently recorded in the SQLite database."""

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        (first_date_in_db,) = cur.execute("""SELECT MIN(date) FROM usage""").fetchone()
        (last_date_in_db,) = cur.execute("""SELECT MAX(date) FROM usage""").fetchone()

        first_date_in_db = datetime.fromisoformat(first_date_in_db)
        last_date_in_db = datetime.fromisoformat(last_date_in_db)

        return first_date_in_db, last_date_in_db

    @property
    def current_start_date(self) -> date:
        """Returns the date selected on the start data calendar."""
        return self.start_date_calendar.selectedDate().toPyDate()

    @property
    def current_end_date(self) -> date:
        """Returns the date selected on the end date calendar."""
        return self.end_date_calendar.selectedDate().toPyDate()

    def start_recording_user_status(self):
        """ Run the executable which creates the database and checks if user is present. This process only runs if no
        process with the same name is already running. Only works on Windows."""

        if sys.platform.startswith("win"):

            if (PROGRAM_NAME + ".exe") in [p.name() for p in psutil.process_iter()]:
                QtWidgets.QMessageBox.about(
                    self,
                    "WARNING",
                    f"'{PROGRAM_NAME}' is already running on the system.",
                )
            else:
                import subprocess

                subprocess.Popen(f"start {str(PROGRAM_PATH)}", shell=True)
                QtWidgets.QMessageBox.about(
                    self, "", f"'{PROGRAM_NAME}' started running."
                )

        else:
            QtWidgets.QMessageBox.about(
                self, "WARNING", f"{PROGRAM_NAME} is only compiled for Windows."
            )
            self.exit()

    def stop_recording_user_status(self):
        """ Checks if the process name already exists and kills it if it does. Only works on Windows."""

        process_killed = False

        if sys.platform.startswith("win"):

            for p in psutil.process_iter():
                if (PROGRAM_NAME + ".exe") == p.name():
                    p.kill()
                    process_killed = True

            if process_killed:
                QtWidgets.QMessageBox.about(self, "", f"'{PROGRAM_NAME}' stopped.")
            else:
                QtWidgets.QMessageBox.about(
                    self, "", f"'{PROGRAM_NAME}' was not running currently."
                )

        else:
            QtWidgets.QMessageBox.about(
                self, "", f"{PROGRAM_NAME} is only compiled for Windows."
            )
            self.exit()

    def read_database_into_df(self) -> pd.DataFrame:
        """ Reads SQLite database into a dataframe and returns that dataframe for further processing."""

        con = sqlite3.connect(DB_PATH)

        # read in df from sql database between the two selected dates. Need to convert date because it is stored as datetime
        df = pd.read_sql(
            "SELECT * FROM usage WHERE DATE(date) BETWEEN DATE(?) AND DATE(?);",
            con,
            index_col="id",
            params=(str(self.current_start_date), str(self.current_end_date)),
            parse_dates={"date": {"infer_datetime_format": True}},
        )

        return df

    def get_data_from_db(self) -> List[Tuple[date, int, int]]:
        """ Returns a list of tuples containing a date, how much time the user has actively used the pc on that date,
        and how much time the pc has stayed idle on that date."""

        df = self.read_database_into_df()

        daily_data_to_plot = []
        dates = df["date"].map(lambda t: t.date()).unique()

        # iterate over dates in dataframe to find the time spent on pc each day
        for date in dates:

            # create a smaller dataframe for each date
            df_date_subset = df[df["date"].dt.date == date].copy()
            df_date_subset["date_offset"] = df_date_subset["date"].shift()
            df_date_subset["time_present"] = (
                df_date_subset["date"] - df_date_subset["date_offset"]
            )

            # split the dataframe into user present and user absent
            seconds_user_present = int(
                df_date_subset[df_date_subset["user_present"] == 1][
                    "time_present"
                ].dt.seconds.sum()
            )
            seconds_user_absent = int(
                df_date_subset[df_date_subset["user_present"] == 0][
                    "time_present"
                ].dt.seconds.sum()
            )

            daily_data_to_plot.append((date, seconds_user_present, seconds_user_absent))

        return daily_data_to_plot

    def plot_start_end_date(self):
        """ Makes another window that displays the recorded information for the provided dates in a bar chart. If the end date is before
        the start date, then a message is displayed which tells the user to pick a different time frame."""

        # only plot if the dates make sense otherwise dispay error box
        if self.current_end_date >= self.current_start_date:

            data = self.get_data_from_db()
            title = f"Data Range: {self.current_start_date} to {self.current_end_date}"
            widget = Plotter(self, title, data)
            widget.show()

        else:
            QtWidgets.QMessageBox.about(
                self,
                "",
                "Start date cannot be above end date. Please select another date range.",
            )

    def export_excel_file(self):
        """ Exports excel file with database information for later analysis."""

        # only plot if the dates make sense otherwise dispay error box
        if self.current_end_date >= self.current_start_date:

            df = self.read_database_into_df()
            file_name, _ = QFileDialog.getSaveFileName(directory=str(Path.cwd()))
            file_name = Path(file_name)
            if file_name.suffix != ".xlsx":
                file_name = file_name.with_suffix(".xlsx")

            df.to_excel(file_name)

            QtWidgets.QMessageBox.about(
                self, "", f"Dataframe written to excel file: {file_name}",
            )

        else:
            QtWidgets.QMessageBox.about(
                self,
                "",
                "Start date cannot be above end date. Please select another date range.",
            )


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    ex = Gui()
    app.exec_()
