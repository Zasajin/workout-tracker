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

        
    # Previous month button
    prev_btn = toga.Button(
        "<",
        on_press=self.prev_month,
        style=Pack(width=50, padding=5)
    )
    
    # Current month/year label
    month_name = calendar.month_name[self.current_month]
    self.month_label = toga.Label(
        f"{month_name} {self.current_year}",
        style=Pack(flex=1, text_align='center', font_size=16, padding=5)
    )
    
    # Next month button
    next_btn = toga.Button(
        ">",
        on_press=self.next_month,
        style=Pack(width=50, padding=5)
    )
    
    nav_box = toga.Box(style=Pack(direction=ROW, padding=5))
    nav_box.add(prev_btn)
    nav_box.add(self.month_label)
    nav_box.add(next_btn)
    
    return nav_box


# build calender grid for desired month and year
def build_calender(self) -> toga.Box:

    self.calendar_box.clear()

    workouts = self.db.get_all_workouts()
    workout_dates = set()

    # collect workout dates in currently selected month
    for workout in workouts:

        workout_date = datetime.strptime(workout['date'], "%Y-%m-%d").date()

        if workout_date.month == self.current_month and workout_date.year == self.current_year:

            workout_dates.add(workout_date.day)

    # header (weekdays)
    


def main():

    return WorkoutTracker()
