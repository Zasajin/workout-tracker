"""
Tracker for workouts and exercise progressions
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime, date
import calendar

from wt25.database import WorkoutDB


class WorkoutTracker(toga.App):

    # construct and show the Toga application
    def startup(self):

        self.db = WorkoutDB("workouts.db")

        # setting current  day in calendar
        today = datetime.today()
        self.current_month = today.month
        self.current_year = today.year

        # main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.show_calendar_view()
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


    # build calendar grid for desired month and year
    def build_calendar(self) -> toga.Box:

        self.calendar_box.clear()

        workouts = self.db.get_all_workouts()
        workout_dates = set()

        # collect workout dates in currently selected month
        for workout in workouts:

            workout_date = datetime.strptime(workout['date'], "%Y-%m-%d").date()

            if workout_date.month == self.current_month and workout_date.year == self.current_year:

                workout_dates.add(workout_date.day)

        # header (weekdays)
        header_box = toga.Box(style=Pack(direction=ROW, padding=2))
        header_box.add(toga.Label("WK", style=Pack(width=40, padding=2, font_weight='bold')))

        for day_name in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:

            header_box.add(toga.Label(
                day_name,
                style=Pack(width=50, padding=2, text_align='center', font_weight='bold')
            ))
        self.calendar_box.add(header_box)

        cal = calendar.monthcalendar(self.current_year, self.current_month)

        for week in cal:

            week_box = toga.Box(style=Pack(direction=ROW, padding=2))

            first_day = next((d for d in week if d != 0), 1)
            week_date = date(self.current_year, self.current_month, first_day)
            week_number = week_date.isocalendar()[1]

            week_box.add(toga.Label(
                str(week_number),
                style=Pack(width=40, padding=2, text_align='center', color='#666')
            ))

            for day in week:

                if day == 0:

                    week_box.add(toga.Box(style=Pack(width=50, height=50, padding=2)))

                else:

                    has_workout = day in workout_dates
                    day_btn = toga.Button(
                        str(day),
                        on_press=lambda widget, d=day: self.day_clicked(d),
                        style=Pack(
                            width=50,
                            height=50,
                            padding=2,
                            background_color='#4caf50' if has_workout else '#f0f0f0',
                            color='white' if has_workout else 'black',
                        )
                    )
                    
                    week_box.add(day_btn)

            self.calendar_box.add(week_box)


    # scroll to the previous month and update calendar
    def prev_month(self, widget):

        if self.current_month == 1:
            
            self.current_month = 12
            self.current_year -= 1

        else:

            self.current_month -= 1

        self.update_calendar()


    # scroll to the next month and update calendar
    def next_month(self, widget):

        if self.current_month == 12:
            
            self.current_month = 1
            self.current_year += 1

        else:

            self.current_month += 1

        self.update_calendar()


    # update the calendar to show the right month
    def update_calendar(self):

        month_name = calendar.month_name[self.current_month]
        self.month_label.text = f"{month_name} {self.current_year}"
        self.build_calendar()


    # handles display of details of a clicked day in the calendar
    def day_clicked(self, day):

        clicked_date = date(self.current_year, self.current_month, day)
        self.show_day_details(clicked_date)

    
    # displays the workout detils for a specific selected day
    def show_day_details(self, selected_date):

        self.selected_date = selected_date

        # main container for details view
        detail_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
    
        # box for navigation tools
        header_box = toga.Box(style=Pack(direction=ROW, padding=5))

        # button to return to calendar grid
        back_btn = toga.Button(
            "Back",
            on_press=lambda widget: self.show_calendar_view(),
            style=Pack(width=80, padding=5)
        )

        # label displaying selected day
        date_label = toga.label(
            selected_date.strftime("%A, %B %d, %Y"),
            style=Pack(flrx=1, text_align='center', font_size=16, padding=5)
        )

        # TODO: add button to add workout for selected day
        create_workout_btn = toga.Button(
            "Add Workout",
            on_press=lambda widget: self.create_workout(selected_date)
        )

        # building header
        header_box.add(back_btn)
        header_box.add(date_label)
        header_box.add(create_workout_btn)

        # building whole scene
        detail_box.add(header_box)
        


    # builds and displays calendar view
    # uses build_navigation for nav buttons
    # uses build_calendar for calendar grid
    def show_calendar_view(self):

        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        nav_box = self.build_navigation()
        main_box.add(nav_box)

        self.calendar_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.build_calendar()
        main_box.add(self.calendar_box)

        self.main_window.content = main_box


    # TODO: logic for workout creation and 
    def create_workout(self, workout_date):

        # TODO: implement workout creation form and logic
        print(f"Creating workout for {workout_date}")


def main():

    return WorkoutTracker()
