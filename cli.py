from datetime import datetime

import fire

from constants import PERIODICITY_DAILY, PERIODICITY_WEEKLY
from habit_tracker import HabitTracker


class Cli:

    def __init__(self):
        self.habit_tracker = HabitTracker()

    def create_habit(self, name, description, periodicity):
        self.habit_tracker.add_habit(name=name, description=description, periodicity=periodicity)
        return self.habit_tracker.get_habits()

    def list_habits(self):
        return self.habit_tracker.get_habits()

    def habit_details(self, habit_id):
        return self.habit_tracker.get_habit(habit_id=habit_id)

    def check_off_habit(self, habit_id):
        try:
            self.habit_tracker.check_off_habit(habit_id=habit_id)
            print(f"Checked off for habit {habit_id}")
        except ValueError as e:
            print(e)

    def get_last_check_off_from_habit(self, habit_id):
        check_off = self.habit_tracker.get_last_check_off_for_habit(habit_id=habit_id)
        if check_off:
            return "Last check off was " + str(check_off.date_time)
        return "No check offs yet"

    def get_all_check_offs(self):
        return self.habit_tracker.get_all_check_offs()

    def get_longest_check_off_streak_for_habit(self, habit_id):
        return self.habit_tracker.get_longest_check_off_streak_for_habit(habit_id=habit_id)

    def get_longest_check_off_streak_of_all_habits(self):
        longest_streak, habit_id = self.habit_tracker.get_longest_streak_of_all_habits()

        print(f"The longest streak is {longest_streak} days for habit {habit_id}.")

    def generate_example_data(self, start_date, weeks=4):
        predefined_habits = [
            {"name": "Drink Water", "description": "Drink 2 liters of water", "periodicity": PERIODICITY_DAILY},
            {"name": "Exercise", "description": "Do 30 minutes of exercise", "periodicity": PERIODICITY_DAILY},
            {"name": "Read a Book", "description": "Read a book for 30 minutes", "periodicity": PERIODICITY_DAILY},
            {"name": "Meditate", "description": "Meditate for 10 minutes", "periodicity": PERIODICITY_DAILY},
            {"name": "Grocery Shopping", "description": "Do grocery shopping", "periodicity": PERIODICITY_WEEKLY},
        ]

        try:
            # check if date is valid
            parsed_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date {start_date}. Use format YYYY-MM-DD.")

        print(f"Generating data starting from {parsed_date} for {weeks} weeks...")

        return self.habit_tracker.generate_example_data(predefined_habits, parsed_date, weeks)


if __name__ == "__main__":
    fire.Fire(Cli)
