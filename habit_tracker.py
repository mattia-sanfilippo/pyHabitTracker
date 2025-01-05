from datetime import datetime, timedelta
from sqlalchemy import create_engine, func, literal
from sqlalchemy.orm import sessionmaker
import pandas as pd
import logging
from typing import Optional, List, Tuple, Type

from constants import DATABASE_URL, PERIODICITY_DAILY, PERIODICITY_WEEKLY, WEEKLY_CHECK_OFF_LIMIT_DAYS
from exceptions import HabitNotFoundError, InvalidStartDateError, MultipleCheckOffError
from habit import Habit, CheckOff, Base

# Configure logging
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)


class HabitTracker:
    def __init__(self, session: Optional[sessionmaker] = None):
        if session:
            self.session = session
        else:
            self.engine = create_engine(DATABASE_URL)
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
            raise HabitNotFoundError(f"Habit with id {habit_id} does not exist.")
        return habit

    def _check_off_daily(self, habit_id: int, date: datetime.date, check_off_date: datetime) -> CheckOff:
        existing_check_off = (
            self.session.query(CheckOff)
            .filter_by(habit_id=habit_id)
            .filter(func.date(CheckOff.date_time) == literal(date))
            .first()
        )

        if existing_check_off:
            raise MultipleCheckOffError("You can only check off once per day.")

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
                raise MultipleCheckOffError("You can only check off once every 7 days.")

        check_off = CheckOff(habit_id=habit_id, date_time=check_off_date)
        self.session.add(check_off)
        self.session.commit()
        logger.info(f"Weekly check-off added: {check_off}")
        return check_off

    def get_habits(self) -> list[Type[Habit]]:
        return self.session.query(Habit).all()

    def get_habit(self, habit_id: int) -> Type[Habit]:
        habit: Type[Habit] = self._get_habit(habit_id)
        return habit
    
    def delete_habit(self, habit_id: int) -> None:
        habit = self._get_habit(habit_id)
        self.session.delete(habit)
        self.session.commit()
        logger.info(f"Habit deleted: {habit}")

    def delete_all_habits(self) -> None:
        habits = self.session.query(Habit).all()
        for habit in habits:
            self.session.delete(habit)
        self.session.commit()
        logger.info("All habits deleted.")

    def get_last_check_off_for_habit(self, habit_id: int) -> Optional[CheckOff]:
        return (
            self.session.query(CheckOff)
            .filter_by(habit_id=habit_id)
            .order_by(CheckOff.date_time.desc())
            .first()
        )
    
    def get_all_check_offs_for_habit(self, habit_id: int) -> list[Type[CheckOff]]:
        return self.session.query(CheckOff).filter_by(habit_id=habit_id).all()

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

        # start_date should be at least n weeks before the current date
        # because we are generating data from the past
        if start_date > datetime.utcnow() - timedelta(weeks=weeks):
            raise InvalidStartDateError(f"Start date should be in the past by at least {weeks} weeks.")        

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
