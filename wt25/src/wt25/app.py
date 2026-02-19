"""
Tracker for workouts and exercise progressions
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime, date, timedelta
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
        date_label = toga.Label(
            selected_date.strftime("%A, %B %d, %Y"),
            style=Pack(flex=1, text_align='center', font_size=16, padding=5)
        )

        prev_day_btn = toga.Button(
            "<",
            on_press=lambda widget: self.show_day_details(selected_date - timedelta(days=1)),
            style=Pack(width=50, padding=5)
        )

        next_day_btn = toga.Button(
            ">",
            on_press=lambda widget: self.show_day_details(selected_date + timedelta(days=1)),
            style=Pack(width=50, padding=5)
        )

        # building header
        header_box.add(back_btn)
        header_box.add(prev_day_btn)
        header_box.add(date_label)
        header_box.add(next_day_btn)

        # fetch workouts of selected day from db
        workouts = self.db.get_workouts_by_date(selected_date.strftime("%Y-%m-%d"))
        # box to list workouts of the day
        workout_list_box = toga.Box(style=Pack(direction=COLUMN, padding=5, flex=1))

        if workouts:

            for workout in workouts:

                workout_btn = toga.Button(
                    workout['name'],
                    on_press=lambda widget, w=workout: self.show_workout_detail(w),
                    style=Pack(width=300, padding=5)
                )

                # add button for workout into list box
                # enables concise overview and possibility to
                # expand to see details
                workout_list_box.add(workout_btn)

        else:

            none_label = toga.Label(
                "No workouts logged for this day yet.",
                style=Pack(padding=20, text_align='center')
            )

            # display message if no workouts logged for selected day
            workout_list_box.add(none_label)

        # button to add workout for selected day
        create_workout_btn = toga.Button(
            "Add Workout",
            on_press=lambda widget: self.create_workout(selected_date)
        )

        # building whole scene
        detail_box.add(header_box)
        detail_box.add(workout_list_box)
        detail_box.add(create_workout_btn)

        self.main_window.content = detail_box


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


    # workout creation form and logic for selected day 
    def create_workout(self, workout_date):

        # main display box
        form_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        header_label = toga.Label(
            f"New Workout - {workout_date.strftime('%d, %m, %Y')}",
            style=Pack(padding=10, font_size=16, font_weight='bold', text_align='center')
        )

        # input and display of workout name
        name_label = toga.Label("Workout Name:", style=Pack(padding=5))
        self.name_input = toga.TextInput(
            placeholder="e.g. Leg Day",
            style=Pack(padding=5, width=300)
        )

        # buttons to save/cancel workout creation
        button_box = toga.Box(style=Pack(direction=ROW, padding=10))
        cancel_btn = toga.Button(
            "Cancel",
            on_press=lambda widget: self.show_day_details(workout_date),
            style=Pack(padding=5, width=100)
        )
        save_btn = toga.Button(
            "Cancel",
            on_press=lambda widget: self.save_workout(workout_date),
            style=Pack(padding=5, width=100)
        )
        # build button box
        button_box.add(cancel_btn)
        button_box.add(save_btn)

        # build whole display
        form_box.add(header_label)
        form_box.add(name_label)
        form_box.add(self.name_input)
        form_box.add(button_box)

        self.main_window.content = form_box

    
    # saves workout to db
    def save_workout(self, workout_date):

        name = self.name_input.value.strip()

        if not name:

            self.main_window.error.dialog(
                "Error",
                "Workout name cannot be empty."
            )

            return

        self.db.add_workout(
            name = name,
            date = workout_date.strftime("%d-%m-%Y")
        )

        self.show_day_details(workout_date)


    # expands workout details when a workout button is clicked
    # shows button to add exercises to workout
    def show_workout_detail(self, workout):
        
        # workout details display
        detail_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # header with workout name, date and return button
        header_box = toga.Box(style=Pack(direction=ROW, padding=5))

        # return
        back_btn = toga.Button(
            "Back",
            on_press=lambda widget: self.show_day_details(self.selected_date),
            style=Pack(width=80, padding=5)
        )

        # workout name and date
        workout_label = toga.Label(
            f"{workout['name']} - {workout['date']}",
            style=Pack(flex=1, text_align='center', font_size=16,
            font_weight='bold', padding=5)
        )

        # build header
        header_box.add(back_btn)
        header_box.add(workout_label)

        # fetch exercises of workout
        exercises = self.db.get_workout_exercises(workout['id'])

        # display exercises and sets of workout
        exercises_box = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=1))

        if exercises:

            for exercise in exercises:

                # row for each exercise with name and delete button
                exercise_row = toga.Box(style=Pack(direction=ROW, padding=5))

                exercise_label = toga.Label(
                    exercise['exercise_name'],
                    style=Pack(padding=5, font_size=14, font_weight='bold')
                )

                delete_exercise_btn = toga.Button(
                    "X",
                    on_press=lambda w, ex=exercise: self.confirm_delete_exercise(workout, ex),
                    style=Pack(width=40, background_color='#d32f2f')
                )

                # build exercise row
                exercise_row.add(exercise_label)
                exercise_row.add(delete_exercise_btn)

                # add exercise row per exercise to exercises box
                exercises_box.add(exercise_row)

                if exercise['sets']:

                    for set_data in exercise['sets']:

                        set_label = toga.Label(
                            f" {set_data['reps']} reps x {set_data['weight']} kg",
                            style=Pack(padding_left=20, padding_top=2)
                        )
                        exercise_box.add(set_label)

            # no sets logged for exercise yet
            else:

                none_label = toga.Label(
                    " No sets logged yet. ",
                    style=Pack(padding_left=20, padding_top=2, color='#888')
                )
                exercise_box.add(none_label)

        # no exercises logged for workout yet
        else:

            no_exercise_label = toga.Label(
                    " No exercises logged yet. ",
                    style=Pack(padding_left=20, text_align='center')
                )
                exercise_box.add(no_exercise_label)

        # button for workout deletion
        delete_btn = toga.Button(
            "Delete Workout",
            on_press=lambda widget: self.confirm_delete_workout(workout),
            style=Pack(padding=10, background_color='#d32f2f')
        )

        # button to add exercise to workout
        add_exercise_btn = toga.Button(
            "Add Exercise",
            on_press=lambda widget: self.add_exercise(workout),
             style=Pack(padding=10)
        )

        # build whole display
        detail_box.add(header_box)
        detail_box.add(exercises_list_box)
        detail_box.add(delete_btn)
        detail_box.add(add_exercise_btn)

        self.main_window.content = detail_box


    # adding exercise to workout
    def add_exercise(self, workout):
        
        # main display
        form_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # header with selected workout name
        header_label = toga.Label(
            f"Add Exercise to {workout['name']}",
            style=Pack(padding=10, font_size=16, font_weight='bold')
        )

        # input to select existing or enter new exercise
        exercise_label = toga.Label(
            "Select Exercise:",
            style=Pack(padding=5)
        )

        # fetch existing exercises from db to display
        existing_exercises = self.db.get_all_exercises()

        exercise_items = [ex['name'] for ex in existing_exercises]
        exercise_items.append("--Add new exercise--")

        # display for existing exercises
        self.exercise_select = toga.Selection(
            items=exercise_items,
            on_change=lambda widget: self.toggle_new_exercise_input(widget),
            style=Pack(padding=5, width=300)
        )

        # input window for new exercise
        self.new_exercise_input = toga.TextInput(
            placeholder="Enter new exercise name",
            style=Pack(padding=5, width=300)
        )
        self.new_exercise_box = toga.Box(style=Pack(direction=COLUMN))

        # box for cancel and save buttons
        button_box = toga.Box(style=Pack(direction=ROW, padding=10))

        cancel_btn = toga.Button(
            "Cancel",
            on_press=lambda widget: self.show_workout_detail(workout),
            style=Pack(padding=5, width=100)
        )

        save_btn = toga.Button(
            "Save",
            on_press=lambda widget: self.save_exercise(workout),
            style=Pack(padding=5, width=100)
        )

        # build button box
        button_box.add(cancel_btn)
        button_box.add(save_btn)

        # build main display
        form_box.add(header_label)
        form_box.add(exercise_label)
        form_box.add(self.exercise_select)
        form_box.add(self.new_exercise_box)
        form_box.add(button_box)

        self.main_window.content = form_box


    # toggle input window for new exercises
    def toggle_new_exercise_input(self, widget):
        
        if widget.value == "--Add new exercise--":

            self.new_exercise_box.add(self.new_exercise_input)

        else:

            self.new_exercise_box.clear()


    # save exercise to workout in db
    def save_exercise(self, workout_id):
        
        selected = self.exercise_select.value

        if selected == "--Add new exercise--":

            new_name = self.new_exercise_input.value.strip()

            if not new_name:

                self.main_window.error.dialog(
                    "Error",
                    "Exercise name cannot be empty."
                )

                return

            exercise_id = self.db.add_new_exercise(new_name)

        else:

            all_exercises = self.db.get_all_exercises()
            exercise_id = next(ex['id'] for ex in all_exercises if ex['name'] == selected)

        workout_exercise_id = self.db.link_exercise_to_workout(workout['id'], exercise_id)

        self.add_sets(workout, workout_exercise_id)


    # add set to exercise form/logic
    def add_sets(self, workout, workout_exercise_id):
        
        # main display box
        form_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        header_label = toga.Label(
            "Add sets",
            style=Pack(padding=10, font_size=16, font_weight='bold')
        )

        # reps section for a set
        reps_label = toga.Label("Reps:", style=Pack(padding=5))

        self.reps_input = toga.NumberInput(
            min=0,
            max=999,
            step=1,
            style=Pack(padding=5, width=300)
        )

        # weight section for a set
        weight_label = toga.Label("Weight (kg):", style=Pack(padding=5))

        self.weight_input = toga.NumberInput(
            min=0,
            max=999,
            step=0.125,
            style=Pack(padding=5, width=300)
        )

        # display element for adding a set/finishing and returning to workout details
        button_box = toga.Box(style=Pack(direction=ROW, padding=10))

        # finish adding sets and return to workout details
        done_btn = toga.Button(
            "Done",
            on_press=lambda widget: self.show_workout_detail(workout),
            style=Pack(padding=5, width=100)
        )

        # add a set
        add_set_btn = toga.Button(
            "Add set",
            on_press=lambda widget: self.save_set(workout, workout_exercise_id),
            style=Pack(padding=5, width=100)
        )

        # build button box
        button_box.add(done_btn)
        button_box.add(add_set_btn)
            
        # added sets feedback
        self.sets_list_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # build main display
        form_box.add(header_label)
        form_box.add(reps_label)
        form_box.add(self.reps_input)
        form_box.add(weight_label)
        form_box.add(self.weight_input)
        form_box.add(button_box)
        form_box.add(self.sets_list_box)

        self.main_window.content = form_box


    # saves a set to db, allows multiple additions
    def save_set(self, workout, workout_exercise_id):

        reps = self.reps_input.value
        weight = self.weight_input.value

        if reps is None or weight is None:

            self.main_window.error.dialog(
                "Error",
                "Reps and weight must be provided."
            )
            
            return

        # save to db
        self.db.add_set(workout_exercise_id, int(reps), float(weight))

        # feedback for added set
        set_label = toga.Label(
            f"Added {int(reps)} reps x {float(weight)} kg",
            style=Pack(padding=5)
        )
        self.sets_list_box.add(set_label)

        # reset inputs for next set
        self.reps_input.value = None
        self.weight_input.value = None


    # delete workout confirmation dialog
    def confirm_delete_workout(self, workout):

        self.main_window.confirm_dialog(
            "Delete Workout",
            f"Delete '{workout['name']}' ('{workout['date']}') and all its exercises? This action cannot be undone.",
            on_result=lambda result: self.delete_workout(workout, result)
        )


    # workout deletion handling depending of final choice
    def delete_workout(self, workout, confirmed):

        if confirmed:

            self.db.delete_workout(workout['id'])
            self.show_day_details(workout['date'])


    # delete exercise from workout confirmation dialog
    def confirm_delete_exercise(self, workout_exercise_id):

        self.main_window.confirm_dialog(
            "Delete Exercise",
            f"Delete this exercise from the workout?",
            on_result=lambda result: self.delete_exercise(workout, exercise, result)
        )


    # exercise (from workout) deletion handling depending on final choice
    def delete_exercise(self, workout_exercise_id, confirmed):

        if confirmed:

            self.db.del_linked_exercise(exercise['workout_exercise_id'])
            self.show_workout_detail(workout)



def main():

    return WorkoutTracker()
