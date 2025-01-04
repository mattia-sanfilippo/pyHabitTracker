from datetime import datetime, timedelta
from sqlalchemy import create_engine, func, literal
from sqlalchemy.orm import sessionmaker, InstrumentedAttribute
import pandas as pd
import logging
from typing import Optional, List, Tuple, Type

from constants import PERIODICITY_DAILY, PERIODICITY_WEEKLY
from habit import Habit, CheckOff, Base

# Constants
WEEKLY_CHECK_OFF_LIMIT_DAYS = 7

# Configure logging
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)


class HabitTracker:
    def __init__(self, session: Optional[sessionmaker] = None):
        if session:
            self.session = session
        else:
            self.engine = create_engine('sqlite:///habit_tracker.db')
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

    def add_habit(self, name: str, description: str, periodicity: int) -> Habit:
        habit = Habit(name=name, description=description, periodicity=periodicity)
        self.session.add(habit)
        self.session.commit()
        logger.info(f"Habit added: {habit}")
        return habit

    def check_off_habit(self, habit_id: int, check_off_date: datetime = datetime.utcnow()) -> CheckOff:
        date = check_off_date.date()
        habit = self._get_habit(habit_id)
        periodicity = habit.periodicity

        if periodicity == PERIODICITY_DAILY:
            return self._check_off_daily(habit_id, date, check_off_date)
        elif periodicity == PERIODICITY_WEEKLY:
            return self._check_off_weekly(habit_id, check_off_date)

    def _get_habit(self, habit_id: int) -> Type[Habit]:
        habit = self.session.get(Habit, habit_id)
        if not habit:
            raise ValueError(f"Habit with id {habit_id} does not exist.")
        return habit

    def _check_off_daily(self, habit_id: int, date: datetime.date, check_off_date: datetime) -> CheckOff:
        existing_check_off = (
            self.session.query(CheckOff)
            .filter_by(habit_id=habit_id)
            .filter(func.date(CheckOff.date_time) == literal(date))
            .first()
        )

        if existing_check_off:
            raise ValueError("You can only check off once per day.")

        check_off = CheckOff(habit_id=habit_id, date_time=check_off_date)
        self.session.add(check_off)
        self.session.commit()
        logger.info(f"Daily check-off added: {check_off}")
        return check_off

    def _check_off_weekly(self, habit_id: int, check_off_date: datetime) -> CheckOff:
        last_check_off = (
            self.session.query(CheckOff.date_time)
            .filter_by(habit_id=habit_id)
            .order_by(CheckOff.date_time.desc())
            .first()
        )

        if last_check_off:
            days_since_last_check_off = (check_off_date.date() - last_check_off.date_time.date()).days
            if days_since_last_check_off < WEEKLY_CHECK_OFF_LIMIT_DAYS:
                raise ValueError("You can only check off once every 7 days.")

        check_off = CheckOff(habit_id=habit_id, date_time=check_off_date)
        self.session.add(check_off)
        self.session.commit()
        logger.info(f"Weekly check-off added: {check_off}")
        return check_off

    def get_habits(self) -> list[Type[Habit]]:
        return self.session.query(Habit).all()

    def get_habit(self, habit_id: int) -> str:
        habit: Type[Habit] = self._get_habit(habit_id)
        return str(habit.name)

    def get_last_check_off_for_habit(self, habit_id: int) -> Optional[CheckOff]:
        return (
            self.session.query(CheckOff)
            .filter_by(habit_id=habit_id)
            .order_by(CheckOff.date_time.desc())
            .first()
        )

    def get_all_check_offs(self) -> list[Type[CheckOff]]:
        return self.session.query(CheckOff).all()

    def get_longest_check_off_streak_for_habit(self, habit_id: int) -> int:
        habit = self._get_habit(habit_id)
        periodicity = habit.periodicity
        interval = 1 if periodicity == PERIODICITY_DAILY else 7

        check_offs = (
            self.session.query(CheckOff.date_time)
            .filter_by(habit_id=habit_id)
            .order_by(CheckOff.date_time.asc())
            .all()
        )

        if not check_offs:
            return 0

        data_frame = pd.DataFrame([pd.Timestamp(co.date_time) for co in check_offs], columns=["date"])
        data_frame = data_frame.drop_duplicates()
        data_frame["gap"] = (data_frame["date"] - data_frame["date"].shift()).dt.days
        data_frame["streak"] = (data_frame["gap"] != interval).cumsum()
        data_frame["streak_length"] = (
            data_frame.groupby("streak")["date"].transform(lambda x: (x.max() - x.min()).days + 1)
        )

        return data_frame["streak_length"].max()

    def get_longest_streak_of_all_habits(self) -> Tuple[int, Optional[int]]:
        habit_ids = [habit.id for habit in self.get_habits()]

        longest_streak = 0
        habit_with_longest_streak = None

        habit_id: int

        for habit_id in habit_ids:
            streak = self.get_longest_check_off_streak_for_habit(habit_id)
            if streak > longest_streak:
                longest_streak = streak
                habit_with_longest_streak = habit_id

        return longest_streak, habit_with_longest_streak

    def generate_example_data(self, predefined_habits: List[dict], start_date: datetime, weeks: int = 4) -> List[Habit]:
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
