from datetime import datetime, date
import sqlite3
from pathlib import Path
import PyQt5
import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtChart
from PyQt5.QtCore import Qt
from pandas.core import series
from qtpy.QtWidgets import QMainWindow
from qtpy import uic
from qtpy.QtGui import QIcon
import sys
import psutil
from typing import Tuple, List

from config import DB_PATH, PROGRAM_NAME, PROGRAM_PATH

class Plotter(QtWidgets.QMainWindow):
    
    def __init__(self, parent, data: List[Tuple[date, int, int]]):
        
        super().__init__(parent=parent)
        
        self.data = data
        
        ui_path = Path(__file__).parent / "plotter.ui"
        uic.loadUi((str(ui_path)), self)
    
        self.plot_data()
    
    @property
    def dates(self) -> list:
        """ Returns a list of dates that were passed in into the data"""
        return [str(i[0]) for i in self.data]
    
    @property
    def time_active(self) -> list:
        return [i[1] for i in self.data]
    
    @property
    def time_idle(self) -> list:
        return [i[2] for i in self.data]
    
    def plot_data(self):
        
        bar_series = QtChart.QBarSeries()
        active_set = QtChart.QBarSet("active")
        idle_set = QtChart.QBarSet("idle")
        
        active_set.append(self.time_active)
        idle_set.append(self.time_idle)
        
        bar_series.append(active_set)
        bar_series.append(idle_set)
        
        chart = QtChart.QChart()
        chart.addSeries(bar_series)
        chart.setTitle("Time spend on PC")

        x_axis = QtChart.QBarCategoryAxis()
        x_axis.append(self.dates)
        chart.addAxis(x_axis, Qt.AlignBottom)
        bar_series.attachAxis(x_axis)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        chart_view = QtChart.QChartView(chart)
        self.plotter_layout.addWidget(chart_view)
