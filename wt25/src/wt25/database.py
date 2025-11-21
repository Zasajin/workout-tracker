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

        # create exercises table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE
            )
        ''')

        # create sets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_id INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                weight REAL NOT NULL,
                FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()


# -- Workout Methods --


# -- Exercise Methods --


# -- Set Methods --


# -- Combi Methods --


            