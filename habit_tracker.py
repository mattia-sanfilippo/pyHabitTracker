from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import pandas as pd

from constants import PERIODICITY_DAILY, PERIODICITY_WEEKLY
from habit import Habit, CheckOff, Base


class HabitTracker:
    def __init__(self, session=None):
        if session:
            self.session = session
        else:
            self.engine = create_engine('sqlite:///habit_tracker.db')
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

    def add_habit(self, name, description, periodicity):
        habit = Habit(name=name, description=description, periodicity=periodicity)
        self.session.add(habit)
        self.session.commit()
        return habit

    def check_off_habit(self, habit_id, check_off_date=datetime.utcnow()):
        date = check_off_date.date()

        # Get the habit to determine its periodicity
        habit = self.session.get(Habit, habit_id)
        if not habit:
            raise ValueError(f"Habit with id {habit_id} does not exist.")

        periodicity = habit.periodicity

        if periodicity == PERIODICITY_DAILY:
            # Check if a check-off already exists for the day
            existing_check_off = (
                self.session.query(CheckOff)
                .filter_by(habit_id=habit_id)
                .filter(func.date(CheckOff.date_time) == date)
                .first()
            )

            if existing_check_off:
                raise ValueError("You can only check off once per day.")

            # If no check-off exists for the day, create a new check-off
            check_off = CheckOff(habit_id=habit_id, date_time=check_off_date)
            self.session.add(check_off)
            self.session.commit()
            return check_off

        elif periodicity == PERIODICITY_WEEKLY:
            # Check if there is any previous check-off for this habit
            last_check_off = (
                self.session.query(CheckOff.date_time)
                .filter_by(habit_id=habit_id)
                .order_by(CheckOff.date_time.desc())
                .first()
            )

            if last_check_off:
                # Calculate the difference in days from the last check-off
                days_since_last_check_off = (check_off_date.date() - last_check_off.date_time.date()).days

                # If the last check-off was within the last 7 days, raise an error
                if days_since_last_check_off < 7:
                    raise ValueError("You can only check off once every 7 days.")

            # No previous check-off exists, or it's been 7 days or more, create a new check-off
            check_off = CheckOff(habit_id=habit_id, date_time=check_off_date)
            self.session.add(check_off)
            self.session.commit()
            return check_off

    def get_habits(self):
        habits = self.session.query(Habit).all()
        return habits

    def get_habit(self, habit_id):
        habit = self.session.get(Habit, int(habit_id))
        return habit.name

    def get_last_check_off_for_habit(self, habit_id):
        check_off = (self.session.query(CheckOff)
                     .filter_by(habit_id=habit_id)
                     .order_by(CheckOff.date_time.desc())
                     .first())
        return check_off

    def get_all_check_offs(self):
        check_offs = self.session.query(CheckOff).all()
        return check_offs

    def get_longest_check_off_streak_for_habit(self, habit_id):
        # Get the habit to determine its periodicity
        habit = self.session.get(Habit, int(habit_id))
        if not habit:
            raise ValueError(f"Habit with id {habit_id} does not exist.")

        periodicity = habit.periodicity
        interval = 1 if periodicity == PERIODICITY_DAILY else 7

        # Query data
        check_offs = (
            self.session.query(CheckOff.date_time)
            .filter_by(habit_id=habit_id)
            .order_by(CheckOff.date_time.asc())
            .all()
        )

        if not check_offs:
            return 0  # No check-offs, no streak

        # Create a Pandas DataFrame with datetime objects
        data_frame = pd.DataFrame([pd.Timestamp(co.date_time) for co in check_offs], columns=["date"])

        # Drop duplicates (in case of multiple check-offs on the same day)
        data_frame = data_frame.drop_duplicates()

        # Calculate streaks considering the periodicity interval
        data_frame["gap"] = (data_frame["date"] - data_frame["date"].shift()).dt.days
        data_frame["streak"] = (data_frame["gap"] != interval).cumsum()

        # Calculate the length of each streak in days
        data_frame["streak_length"] = (
            data_frame.groupby("streak")["date"].transform(lambda x: (x.max() - x.min()).days + 1)
        )

        # Return the longest streak length in days
        return data_frame["streak_length"].max()

    def get_longest_streak_of_all_habits(self):
        # Fetch all distinct habit IDs
        habit_ids = [habit.id for habit in self.session.query(Habit).all()]

        longest_streak = 0
        habit_with_longest_streak = None

        for habit_id in habit_ids:
            # Get the longest streak for each habit
            streak = self.get_longest_check_off_streak_for_habit(habit_id)

            # Update the longest streak found
            if streak > longest_streak:
                longest_streak = streak
                habit_with_longest_streak = habit_id

        return longest_streak, habit_with_longest_streak

    def generate_example_data(self, predefined_habits, start_date, weeks=4):
        added_habits = []
        total_days = weeks * 7

        for predefined_habit in predefined_habits:
            habit = self.add_habit(
                name=predefined_habit["name"],
                description=predefined_habit["description"],
                periodicity=predefined_habit["periodicity"],
            )
            added_habits.append(habit)

        for habit in added_habits:
            periodicity = 1 if habit.periodicity == PERIODICITY_DAILY else 7
            current_date = start_date

            while current_date < start_date + timedelta(days=total_days):
                try:
                    self.session.begin_nested()
                    self.check_off_habit(habit.id, current_date)
                    self.session.commit()
                except ValueError:
                    self.session.rollback()

                current_date += timedelta(days=periodicity)

        return added_habits
