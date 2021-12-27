from datetime import date
from pathlib import Path
from PyQt5 import QtWidgets, QtChart
from PyQt5.QtCore import Qt
from qtpy import uic
from typing import Tuple, List

class Plotter(QtWidgets.QMainWindow):
    def __init__(self, parent, title, data: List[Tuple[date, int, int]]):

        super().__init__(parent=parent)

        self.data = data
        self.title = title

        # load in UI
        ui_path = Path(__file__).parent / "TimingManager_plotter.ui"
        uic.loadUi((str(ui_path)), self)

        self.setWindowTitle(title)

        self.daily_push_button.clicked.connect(self.plot_data)
        self.weekly_push_button.clicked.connect(self.plot_data)
        self.monthly_push_button.clicked.connect(self.plot_data)

        # initialize plot
        self.plot_data()

    @property
    def dates(self) -> List[date]:
        """ Returns a list of dates that were passed in into the data"""
        return [i[0] for i in self.data]

    @property
    def dates_str(self) -> List[str]:
        return [str(i) for i in self.dates]

    @property
    def time_active(self) -> List[int]:
        """ Returns a list containing the time (in seconds) a user was active on a certain date. """
        return [i[1] for i in self.data]

    @property
    def time_idle(self) -> List[int]:
        """ Returns a list containing the time (in seconds) a user not active (PC sitting idle) in a certain date."""
        return [i[2] for i in self.data]

    @property
    def total_pc_time(self) -> List[int]:
        """ Returns a list containing the total time (in seconds) the PC was turned on (does not count in sleep) on a certain date."""
        return [i + j for i, j in zip(self.time_active, self.time_idle)]

    @property
    def weeks(self) -> List[int]:
        """ Returns a list of weeks for which data has been recorded."""
        return list(set([i.isocalendar()[1] for i in self.dates]))

    @property
    def weeks_str(self) -> List[str]:
        """ Returns a list of weeks as strfor which data has been recorded."""
        return list(set([str(i) for i in self.weeks]))

    @property
    def months(self) -> List[int]:
        """ Returns a list of months for which data has been recorded. """
        return list(set([i.month for i in self.dates]))

    @property
    def months_str(self) -> List[str]:
        """ Returns a list of weeks as strfor which data has been recorded."""
        return list(set([str(i) for i in self.months]))

    @property
    def time_active_weeks(self) -> List[int]:
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
    def time_idle_weeks(self) -> List[int]:
        """ Returns a list of time idle (in seconds) every week that has been recorded so far."""

        idle_time_for_week = []

        for w in self.weeks:
            idle_weekly = 0

            for idx, d in enumerate(self.dates):
                # if the date falls is in this week, then add together the time for that date
                if d.isocalendar()[1] == w:
                    idle_weekly += self.time_idle[idx]

            idle_time_for_week.append(int(idle_weekly))

        return idle_time_for_week

    @property
    def total_time_weeks(self) -> List[int]:
        """ Returns a list of total time the PC has been on for every recorded week"""
        return [i + j for i, j in zip(self.time_active_weeks, self.time_idle_weeks)]

    @property
    def time_active_months(self) -> List[int]:
        """ Returns a list of time active (in seconds) every month that has been recorded so far."""

        active_time_for_month = []

        for m in self.months:
            active_monthly = 0

            for idx, d in enumerate(self.dates):
                # if the date falls is in this month, then add together the time for that date
                if d.month == m:
                    active_monthly += self.time_active[idx]

            active_time_for_month.append(int(active_monthly))

        return active_time_for_month

    @property
    def time_idle_months(self) -> List[int]:
        """ Returns a list of time idle (in seconds) every month that has been recorded so far."""

        idle_time_for_month = []

        for m in self.months:
            idle_monthly = 0

            for idx, d in enumerate(self.dates):
                # if the date falls is in this month, then add together the time for that date
                if d.month == m:
                    idle_monthly += self.time_idle[idx]
            idle_time_for_month.append(int(idle_monthly))

        return idle_time_for_month

    @property
    def total_time_months(self) -> List[int]:
        """ Returns a list of total time the PC has been on for every recorded week"""
        return [i + j for i, j in zip(self.time_active_months, self.time_idle_months)]

    @property
    def percent_time_active_days(self) -> List[int]:
        """ Returns a list containing the percent of the time the user was active on a certain date."""
        return [100 * (i / j) for i, j in zip(self.time_active, self.total_pc_time)]

    @property
    def percent_time_idle_days(self) -> List[int]:
        """ Returns a list containing the percent of the time the user was not active (PC is idle) on a certain date."""
        return [100 * (i / j) for i, j in zip(self.time_idle, self.total_pc_time)]

    @property
    def percent_time_active_weeks(self) -> List[int]:
        """ Returns a list containing the percent of the time the user was active in a certain week"""
        return [
            100 * (i / j) for i, j in zip(self.time_active_weeks, self.total_time_weeks)
        ]

    @property
    def percent_time_idle_weeks(self) -> List[int]:
        """ Returns a list containing the percent of the time the user was not active (PC idle) in a certain week."""
        return [
            100 * (i / j) for i, j in zip(self.time_idle_weeks, self.total_time_weeks)
        ]

    @property
    def percent_time_active_months(self) -> List[int]:
        """ Returns a list containing the percent of the time the user was active in a certain month."""
        return [
            100 * (i / j) for i, j in zip(self.time_active_weeks, self.total_time_weeks)
        ]

    @property
    def percent_time_idle_months(self) -> List[int]:
        """ Returns a list containing the percent of the time the user was not active (PC idle) in a certain month."""
        return [
            100 * (i / j) for i, j in zip(self.time_idle_weeks, self.total_time_weeks)
        ]

    def update_plot(
        self,
        active_list: List[int],
        idle_list: List[int],
        total_list: List[int],
        x_axis_list: List[str],
    ):

        # remove any widgets that were in that layout previously, so that charts to not stack but refresh instead
        prev_child_widget = self.chart_widget.findChild(QtChart.QChartView)
        if prev_child_widget:
            self.plotter_layout.removeWidget(prev_child_widget)

        bar_series = QtChart.QBarSeries()
        active_set = QtChart.QBarSet("Active")
        idle_set = QtChart.QBarSet("Idle")
        total_set = QtChart.QBarSet("Total")

        # append data to each bar set
        active_set.append(active_list)
        idle_set.append(idle_list)
        total_set.append(total_list)
        bar_series.append(active_set)
        bar_series.append(idle_set)
        bar_series.append(total_set)

        chart = QtChart.QChart()
        chart.addSeries(bar_series)
        chart.setTitle("Time spend on PC")

        x_axis = QtChart.QBarCategoryAxis()
        x_axis.append(x_axis_list)
        chart.addAxis(x_axis, Qt.AlignBottom)
        bar_series.attachAxis(x_axis)

        y_axis = QtChart.QValueAxis()
        y_axis.setTitleText("Time (Minutes)")
        chart.addAxis(y_axis, Qt.AlignLeft)
        bar_series.attachAxis(y_axis)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QtChart.QChartView(chart)

        self.plotter_layout.addWidget(chart_view)

    def plot_data(self):
        """ Plots the chart with the required data"""
        
        min_in_hour = 60

        if self.sender().text() == "Weekly":
            active_list = [round(i / min_in_hour) for i in self.time_active_weeks]
            idle_list = [round(i / min_in_hour) for i in self.time_idle_weeks]
            total_list = [round(i / min_in_hour) for i in self.total_time_weeks]
            x_axis_list = self.weeks_str

        elif self.sender().text() == "Monthly":
            active_list = [round(i / min_in_hour) for i in self.time_active_months]
            idle_list = [round(i / min_in_hour) for i in self.time_idle_months]
            total_list = [round(i / min_in_hour) for i in self.total_time_months]
            x_axis_list = self.months_str

        # use else statement for Daily in order to plot that in the beginning as well
        else:
            active_list = [round(i / min_in_hour) for i in self.time_active]
            idle_list = [round(i / min_in_hour) for i in self.time_idle]
            total_list = [round(i / min_in_hour) for i in self.total_pc_time]
            x_axis_list = self.dates_str

        self.update_plot(active_list, idle_list, total_list, x_axis_list)
