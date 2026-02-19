import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Callable, Any, Literal, TypedDict

class WorkoutDB:


    # initialize database
    def __init__(self, db_path: "workouts.db"):

        self.db_path = db_path
        self._create_tables()


    # establish connection to db
    def _get_connection(self) -> sqlite3.Connection:

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        return conn


    # create necessary tables if not existent
    def _create_tables(self) -> None:

        conn = self._get_connection()
        cursor = conn.cursor()

        # create workouts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                name TEXT NOT NULL
            )
        ''')

        # create exercises master table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE COLLATE NOCASE
            )
        ''')

        # junction for exercise/workout linking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER NOT NULL,
                exercise_id INTEGER NOT NULL,
                FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE,
                FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
                )
        ''')

        # create sets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_exercise_id INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                weight REAL NOT NULL,
                FOREIGN KEY (workout_exercise_id) REFERENCES workout_exercises(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()


# -- Workout Methods --

    # queries all workouts from db to display in calendar view
    def get_all_workouts(self) -> list[dict[str, Any]]:

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM workouts ORDER BY date DESC')
        workouts = cursor.fetchall()

        conn.close()

        return [dict(row) for row in workouts]


    # queries workouts for specific date
    def get_workouts_by_date(self, date: str) -> list[dict[str, Any]]:

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, name, date
        FROM workouts
        WHERE date = ?
        ORDER BY id
        """, (date,))

        workouts = []
        
        for row in cursor.fetchall():

            workouts.append(dict(row))

        conn.close()

        return workouts

    
    # adds new workout to db, return id for exefcise linking
    def add_workout(self, name: str, date:str) -> int:

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO workouts (name, date)
        VALUES (?, ?)
        """, (name, date))
        
        workout_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return workout_id


    # delete a workout and all linked exercises/sets
    def delete_workout(self, workout_id: int) -> None:

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM workouts WHERE id = ?', (workout_id,))

        conn.commit()
        conn.close()

# -- Exercise Methods --

    # queries all exercises from db
    def get_all_exercises(self) -> list[dict[str, Any]]:

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, name FROM exercises ORDER BY name')
        exercises = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return exercises


    # adds new exercise to db, avoiding redundancys
    # case insensitivity achieved by COLLATE NOCASE in table creation
    def add_new_exercise(self, name: str) -> int:

        conn = self._get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute('INSERT INTO exercises (name) VALUES (?)', (name,))
            exercise_id = cursor.lastrowid
            conn.commit()
        
        except sqlite3.IntegrityError:

            cursor.execute('SELECT id FROM exercises WHERE name = ?', (name,))
            exercise_id = cursor.fetchone()[0]

        finally:

            conn.close()

        return exercise_id


    # delete exercise from a workout
    def del_linked_exercise(self, workout_exercise_id: int) -> None:

        conn = self._get_connection()
        cursor = conn. cursor()

        cursor.execute('DELETE FROM workout_exercises WHERE id = ?', (workout_exercise_id,))

        conn.commit()
        conn.close()

# -- Set Methods --

    # adds new set to db, linked to an exercise in a workout
    def add_set(self, workout_exercise_id: int, reps: int, weight: float) -> int:

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO sets (workout_exercise_id, reps, weight)
        VALUES (?, ?, ?)
        """, (workout_exercise_id, reps, weight))

        set_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return set_id

# -- Combi Methods --

    # queries exercises and sets for a given workout
    def get_workout_exercises(self, workout_id: int) -> list[dict[str, Any]]:

        conn = self._get_connection()
        cursor = conn.cursor()

        # query workout exercises
        cursor.execute("""
        SELECT
        w.id AS workout_exercise_id,
        e.id AS exercise_id,
        e.name AS exercise_name
        FROM workout_exercises w
        JOIN exercises e ON w.exercise_id = e.id
        WHERE we.workout_id = ?
        ORDER BY we.id
        """, (workout_id,))

        exercises = [dict(row) for row in cursor.fetchall()]

        # query details for each exercise
        for exercise in exercises:

            cursor.execute("""
            SELECT id, reps, weight
            FROM sets
            WHERE workout_exercise_id = ?
            ORDER BY id
            """, (exercise['workout_exercise_id'],))

            exercise['sets'] = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return exercises


    # links exercise to workout, returns workout_exercise_id
    def link_exercise_to_workout(self, workout_id: int, exercise_id: int) -> int:

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO workout_exercises (workout_id, exercise_id)
        VALUES (?, ?)
        """, (workout_id, exercise_id))

        workout_exercise_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return workout_exercise_id
