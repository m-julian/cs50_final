from datetime import datetime, date
from pathlib import Path
import PyQt5
import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtChart
from PyQt5.QtCore import Qt
from qtpy import uic
from typing import Tuple, List

from config import DB_PATH, PROGRAM_NAME, PROGRAM_PATH

class Plotter(QtWidgets.QMainWindow):
    
    def __init__(self, parent, data: List[Tuple[date, int, int]]):
        
        super().__init__(parent=parent)
        
        self.data = data
        
        ui_path = Path(__file__).parent / "plotter.ui"
        uic.loadUi((str(ui_path)), self)
    
        self.plot_data()
        
        self.daily_push_button.clicked.connect(self.print_total_days)
        self.weekly_push_button.clicked.connect(self.print_total_weeks)
        self.monthly_push_button.clicked.connect(self.print_total_months)
    
    @property
    def dates(self) -> List[date]:
        """ Returns a list of dates that were passed in into the data"""
        return [i[0] for i in self.data]

    @property
    def dates_str(self) -> List[str]:
        return [str(i) for i in self.dates]

    @property
    def time_active(self) -> list:
        """ Returns a list containing the time (in seconds) a user was active on a certain date. """
        return [i[1] for i in self.data]
    
    @property
    def time_idle(self) -> list:
        """ Returns a list containing the time (in seconds) a user not active (PC sitting idle) in a certain date."""
        return [i[2] for i in self.data]
    
    @property
    def total_pc_time(self) -> list:
        """ Returns a list containing the total time (in seconds) the PC was turned on (does not count in sleep) on a certain date."""
        return [i+j for i,j in zip(self.time_active, self.time_idle)]

    @property
    def weeks(self) -> list:
        """ Returns a list of weeks for which data has been recorded."""
        return list(set([i.isocalendar()[1] for i in self.dates]))

    @property
    def months(self) -> list:
        """ Returns a list of months for which data has been recorded. """
        return list(set([i.month for i in self.dates]))

    @property
    def time_active_weeks(self) -> list:
        """ Returns a list of time active (in seconds) every week that has been recorded so far."""
        
        active_time_for_week = []
        
        for w in self.weeks:
            
            weekly_time = 0
            for idx, d in enumerate(self.dates):
                
                # if the date falls is in this week, then add together the time for that date
                if d.isocalendar()[1] == w:
                    weekly_time += self.time_active[idx]
            active_time_for_week.append(int(weekly_time))

        return active_time_for_week

    @property
    def time_idle_weeks(self) -> list:
        """ Returns a list of time idle (in seconds) every week that has been recorded so far."""
        
        idle_time_for_week = []
        
        for w in self.weeks:
            for idx, d in enumerate(self.dates):
                
                weekly_time = 0
                # if the date falls is in this week, then add together the time for that date
                if d.isocalendar()[1] == w:
                    weekly_time += self.time_idle[idx]
            idle_time_for_week.append(weekly_time)

        return idle_time_for_week

    @property
    def total_time_weeks(self) -> list:
        """ Returns a list of total time the PC has been on for every recorded week"""
        return [i+j for i,j in zip(self.time_active_weeks, self.time_idle_weeks)]

    @property
    def time_active_months(self) -> list:
        """ Returns a list of time active (in seconds) every month that has been recorded so far."""
        
        active_time_for_month = []
        
        for m in self.months:
            for idx, d in enumerate(self.dates):
                
                active_monthly = 0
                # if the date falls is in this month, then add together the time for that date
                if d.month == m:
                    active_monthly += self.time_active[idx]
            active_time_for_month.append(int(active_monthly))

        return active_time_for_month

    @property
    def time_idle_months(self) -> list:
        """ Returns a list of time idle (in seconds) every month that has been recorded so far."""
        
        idle_time_for_month = []
        
        print(self.dates)
        
        for m in self.months:
            for idx, d in enumerate(self.dates):
                
                idle_monthly = 0
                
                # if the date falls is in this month, then add together the time for that date
                if d.month == m:
                    idle_monthly += self.time_idle[idx]
            idle_time_for_month.append(int(idle_monthly))

        return idle_time_for_month

    @property
    def total_time_months(self) -> list:
        """ Returns a list of total time the PC has been on for every recorded week"""
        return [i+j for i,j in zip(self.time_active_months, self.time_idle_months)]

    def print_total_days(self):
        print(self.total_pc_time)

    def print_total_weeks(self):
        print(self.total_time_weeks)

    def print_total_months(self):
        print(self.time_idle_months)

    @property
    def percent_time_active(self) -> list:
        """ Returns a list containing the percent of the time the user was active on a certain date."""
        return [100 * (i/j) for i, j in zip(self.time_active, self.total_pc_time)]

    @property
    def percent_time_idle(self) -> list:
        """ Returns a list containing the percent of the time the user was not active (PC is idle) on a certain date."""
        return [100 * (i/j) for i, j in zip(self.time_idle, self.total_pc_time)]

    def plot_data(self):
        
        bar_series = QtChart.QBarSeries()
        active_set = QtChart.QBarSet("active")
        idle_set = QtChart.QBarSet("idle")
        
        active_set.append(self.percent_time_active)
        idle_set.append(self.percent_time_idle)
        
        bar_series.append(active_set)
        bar_series.append(idle_set)
        
        chart = QtChart.QChart()
        chart.addSeries(bar_series)
        chart.setTitle("Time spend on PC")

        x_axis = QtChart.QBarCategoryAxis()
        x_axis.append(self.dates_str)
        chart.addAxis(x_axis, Qt.AlignBottom)
        bar_series.attachAxis(x_axis)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        chart_view = QtChart.QChartView(chart)
        self.plotter_layout.addWidget(chart_view)
