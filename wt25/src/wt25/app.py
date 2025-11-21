"""
Tracker for workouts and exercise progressions
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime
import calendar

from wt25.database import WorkoutDB


class WorkoutTracker(toga.App):

    # construct and show the Toga application
    def startup(self):

        self.db = WorkoutDB("workouts.db")

        # setting current  day in calender
        today = datetime.today()
        self.current_month = today.month
        self.current_year = today.year

        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # month navigation
        nav_box = self.build_navigation()
        main_box.add(nav_box)

        # calender grid
        self.calendar_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.build_calender()
        main_box.add(self.calendar_box)

        # main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


# build month navigation bar
def build_navigation(self) -> toga.Box:


# build calender grid for desired month and year
def build_calender(self) -> toga.Box:


def main():

    return WorkoutTracker()
