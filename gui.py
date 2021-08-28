import dearpygui.dearpygui as dpg
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sqlite3
from pathlib import Path
from enum import Enum

#########################################################
### Importabt variables and dates, do not change
#########################################################

DATABASE_NAME = "timings.db"
DB_PATH = Path(".") / DATABASE_NAME
con = sqlite3.connect(DB_PATH)
cur = con.cursor()

GUI_START_DATE = datetime(1900, 1, 1) # date that dearpygui counts from

DB_START_DATE, = cur.execute("""SELECT MIN(date) FROM usage""").fetchone()
DB_START_DATE = datetime.strptime(DB_START_DATE, "%Y-%m-%d %H:%M:%S")
DB_START_DATE_MONTH = DB_START_DATE.month
DB_START_DATE_DAY = DB_START_DATE.day

TODAY  = datetime.today()
TODAY_MONTH = TODAY.month  # integer corresponding to month
TODAY_DAY = TODAY.day  # integer corresponding to date of month

YEARS_PASSED_UNTIL_DB_START = (DB_START_DATE - GUI_START_DATE).days // 365 # years until database earliest date
YEARS_PASSED_UNTIL_TODAY = (TODAY - GUI_START_DATE).days // 365 # years passed since 1900 until today

#########################################################
### Keep track of variables in GUI
#########################################################

#########################################################
### GUI Callbacks
#########################################################

def check_dates_range(date: "datetime.datetime", sender: int):
    """
    Checks if the entered date is in the range of the earliest date entry in the database and today. If it is not, an error is displayed.

    :param date: The date which that was entered in the GUI calendar
    :param sender: A unique integer value assigned to each widget that is diplayed in the GUI
    """
    global DATE_PICKER_START_DATE
    global DATE_PICKER_END_DATE
    DATE_PICKER_START_DATE = DB_START_DATE
    DATE_PICKER_END_DATE = TODAY

    # this is for the start date
    if sender == 20:
        if date < DB_START_DATE:
            with dpg.window(popup=True):
                dpg.add_text("Date picked is before the earliest database entry. Using earliest date in database as start date. Choose another date")
        else:
            DATE_PICKER_START_DATE = date

    elif sender == 30:
        if date > TODAY:
            with dpg.window(popup=True):
                dpg.add_text("Date picked is after today. Using today's date as end date. Choose another date")

        else:
            DATE_PICKER_END_DATE = date

    if not DATE_PICKER_END_DATE > DATE_PICKER_START_DATE:
        with dpg.window(popup=True):
            dpg.add_text("End Date cannot be before Start Date. Choose other dates.")

def date_picker_callback(sender: int, data: dict):
    """ Callback function after user has clicked on a date in the calendar.
    
    :param sender: An interger value given to the object which sent the signal
    :param data: A dictionary containing the date information selected on the calendar in the GUI
    """

    month_day = data["month_day"]
    month = data["month"] + 1 # need to add one as months start at 0
    year = data["year"] # year since 1900
    current_year = (GUI_START_DATE + relativedelta(years=+year)).year # get current date relative to 1900

    date = datetime(current_year, month, month_day)

    check_dates_range(date, sender)

def make_plots(senter: int, data):

    check_dates_range(DATE_PICKER_START_DATE, 20)
    check_dates_range(DATE_PICKER_END_DATE, 30)

#########################################################
### GUI building
#########################################################

with dpg.window(label="Example Window", width=420, height=600):

    # dearpygui counts dates from 1900 because it use implot
    dpg.add_text("Pick a Start Date")
    dpg.add_date_picker(id=20, callback=date_picker_callback, default_value= {'month_day': DB_START_DATE_DAY, 'year': YEARS_PASSED_UNTIL_DB_START, 'month': DB_START_DATE_MONTH-1})
    dpg.add_text("Pick End Date")
    dpg.add_date_picker(id=30, callback=date_picker_callback, default_value= {'month_day': TODAY_DAY, 'year': YEARS_PASSED_UNTIL_TODAY, 'month': TODAY_MONTH-1})
    dpg.add_button(label="Make Plots", callback=make_plots)

dpg.setup_viewport()
dpg.set_viewport_width(420)
dpg.set_viewport_height(600)
dpg.start_dearpygui()



# current_date_from_1900 = then + relativedelta(days=+duration) # get current date relative to 1900
# duration = (db_first_date - then).days
# db_first_date_from_1990 = then + relativedelta(days=+duration) # get current date relative to 1900
# print(current_date_from_1900)
# print(db_first_date_from_1990)
# days_from_beginning_of_year = now - datetime.now().replace(month=1, day=1)
# print(days_from_beginning_of_year)
# current_date = datetime.now().replace(month=1, day=1) + relativedelta(days_from_beginning_of_year)
# print(current_date)