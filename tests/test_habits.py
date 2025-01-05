from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from exceptions import InvalidStartDateError, MultipleCheckOffError
from habit import Habit, CheckOff
from habit_tracker import HabitTracker

class TestHabitTracker:
    def test_create_habit(self):
        """Test if a habit is created correctly."""
        mock_db_session = MagicMock()

        habit = Habit(name="Drink water", description="Drink 2 liters of water daily", periodicity=1)
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None

        mock_db_session.add(habit)
        mock_db_session.commit()

        mock_db_session.add.assert_called_once_with(habit)
        mock_db_session.commit.assert_called_once()

        assert habit.name == "Drink water"
        assert habit.description == "Drink 2 liters of water daily"
        assert habit.periodicity == 1


    def test_get_habit(self):
        """Test if a habit is retrieved correctly."""
        mock_db_session = MagicMock()

        habit = Habit(id=1, name="Drink water", description="Drink 2 liters of water daily", periodicity=1)
        mock_db_session.get.return_value = habit

        habit_tracker = HabitTracker(mock_db_session)
        habit = habit_tracker.get_habit(1)

        assert habit.id == 1
        assert habit.name == "Drink water"
        assert habit.description == "Drink 2 liters of water daily"
        assert habit.periodicity == 1

    def test_delete_habit(self):
        """Test if a habit is deleted correctly."""
        mock_db_session = MagicMock()

        habit = Habit(id=1, name="Drink water", description="Drink 2 liters of water daily", periodicity=1)
        mock_db_session.get.return_value = habit

        habit_tracker = HabitTracker(mock_db_session)
        habit_tracker.delete_habit(1)

        mock_db_session.delete.assert_called_once_with(habit)
        mock_db_session.commit.assert_called_once()

    def test_delete_all_habits(self):
        """Test if all habits are deleted correctly."""
        mock_db_session = MagicMock()

        habit1 = Habit(id=1, name="Drink water", description="Drink 2 liters of water daily", periodicity=1)
        habit2 = Habit(id=2, name="Buy groceries", description="Buy groceries", periodicity=2)

        mock_db_session.query.return_value.all.return_value = [habit1, habit2]

        habit_tracker = HabitTracker(mock_db_session)
        habit_tracker.delete_all_habits()

        mock_db_session.delete.assert_any_call(habit1)
        mock_db_session.delete.assert_any_call(habit2)
        mock_db_session.commit.assert_called_once()

    def test_check_off_habit(self):
        """Test if a habit is checked off correctly."""
        mock_db_session = MagicMock()

        habit = Habit(id=1, name="Drink water", description="Drink 2 liters of water daily", periodicity=1)
        mock_db_session.get.return_value = habit

        check_off_date = datetime(2024, 1, 1)
        mock_db_session.query.return_value.filter_by.return_value.filter.return_value.first.return_value = None

        habit_tracker = HabitTracker(mock_db_session)
        check_off = habit_tracker.check_off_habit(habit_id=1, check_off_date=check_off_date)

        assert check_off.habit_id == 1
        assert check_off.date_time == check_off_date

    def test_check_off_habit_twice(self):
        """Test if a ValueError is raised when a habit is checked off twice in a day."""
        mock_db_session = MagicMock()

        habit = Habit(id=1, name="Drink water", description="Drink 2 liters of water daily", periodicity=1)
        mock_db_session.get.return_value = habit

        check_off_date = datetime(2024, 1, 1)
        mock_db_session.query.return_value.filter_by.return_value.filter.return_value.first.return_value = CheckOff(habit_id=1, date_time=check_off_date)

        habit_tracker = HabitTracker(mock_db_session)

        with pytest.raises(MultipleCheckOffError):
            habit_tracker.check_off_habit(habit_id=1, check_off_date=check_off_date)

    def test_get_last_check_off_for_habit(self):
        """Test if the last check off for a habit is returned correctly."""
        mock_db_session = MagicMock()

        habit = Habit(id=1, name="Drink water", description="Drink 2 liters of water daily", periodicity=1)
        mock_db_session.get.return_value = habit

        mock_db_session.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = CheckOff(habit_id=1, date_time=datetime(2024, 1, 1))

        habit_tracker = HabitTracker(mock_db_session)
        check_off = habit_tracker.get_last_check_off_for_habit(1)

        assert check_off.habit_id == 1
        assert check_off.date_time == datetime(2024, 1, 1)

    def test_no_check_off_for_habit(self):
        """Test if None is returned when there are no check offs for a habit."""
        mock_db_session = MagicMock()

        habit = Habit(id=1, name="Drink water", description="Drink 2 liters of water daily", periodicity=1)
        mock_db_session.get.return_value = habit

        mock_db_session.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = None

        habit_tracker = HabitTracker(mock_db_session)
        check_off = habit_tracker.get_last_check_off_for_habit(1)

        assert check_off is None

    def test_get_all_check_offs(self):
        """Test if all check offs are returned correctly."""
        mock_db_session = MagicMock()

        habit1 = Habit(id=1, name="Drink water", description="Drink 2 liters of water daily", periodicity=1)
        habit2 = Habit(id=2, name="Buy groceries", description="Buy groceries", periodicity=2)

        mock_db_session.query.return_value.all.return_value = [
            CheckOff(habit_id=1, date_time=datetime(2024, 1, 1)),
            CheckOff(habit_id=1, date_time=datetime(2024, 1, 2)),
            CheckOff(habit_id=2, date_time=datetime(2024, 1, 1)),
            CheckOff(habit_id=2, date_time=datetime(2024, 1, 8)),
        ]

        habit_tracker = HabitTracker(mock_db_session)
        check_offs = habit_tracker.get_all_check_offs()

        assert len(check_offs) == 4

    def test_get_all_check_offs_for_habit(self):
        """Test if all check offs for a habit are returned correctly."""
        mock_db_session = MagicMock()

        habit = Habit(id=1, name="Drink water", description="Drink 2 liters of water daily", periodicity=1)
        mock_db_session.get.return_value = habit

        mock_db_session.query.return_value.filter_by.return_value.all.return_value = [
            CheckOff(habit_id=1, date_time=datetime(2024, 1, 1)),
            CheckOff(habit_id=1, date_time=datetime(2024, 1, 2)),
        ]

        habit_tracker = HabitTracker(mock_db_session)
        check_offs = habit_tracker.get_check_offs_for_habit(1)

        assert len(check_offs) == 2

    def test_get_longest_check_off_streak_for_habit_daily(self):
        """Test if the longest check off streak is calculated correctly for a habit with daily periodicity."""
        mock_session = MagicMock()

        habit = Habit(id=1, name="Drink Water", description="Drink 2 liters of water daily", periodicity=1)
        mock_session.get.return_value = habit

        mock_session.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [
            CheckOff(habit_id=1, date_time=datetime(2024, 1, 1)),
            CheckOff(habit_id=1, date_time=datetime(2024, 1, 2)),
            CheckOff(habit_id=1, date_time=datetime(2024, 1, 3)),
            CheckOff(habit_id=1, date_time=datetime(2024, 1, 5)),
        ]

        habit_tracker = HabitTracker(mock_session)
        streak = habit_tracker.get_longest_check_off_streak_for_habit(1)
        assert streak == 3


    def test_get_longest_check_off_streak_for_habit_weekly(self):
        """Test if the longest check off streak is calculated correctly for a habit with weekly periodicity."""
        mock_session = MagicMock()

        habit = Habit(id=2, name="Buy groceries", description="Buy groceries", periodicity=2)
        mock_session.get.return_value = habit

        mock_session.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [
            CheckOff(habit_id=2, date_time=datetime(2024, 1, 1)),
            CheckOff(habit_id=2, date_time=datetime(2024, 1, 8)),
            CheckOff(habit_id=2, date_time=datetime(2024, 1, 15)),
            CheckOff(habit_id=2, date_time=datetime(2024, 1, 22)),
            CheckOff(habit_id=2, date_time=datetime(2024, 2, 14)),
        ]

        habit_tracker = HabitTracker(mock_session)
        streak = habit_tracker.get_longest_check_off_streak_for_habit(2)

        assert streak == 22

    def test_get_longest_streak_of_all_habits(self):
        """Test if the longest check off streak of all habits is calculated correctly."""
        mock_session = MagicMock()

        habit1 = Habit(id=1, name="Drink Water", description="Drink 2 liters of water daily", periodicity=1)
        habit2 = Habit(id=2, name="Buy groceries", description="Buy groceries", periodicity=2)

        mock_session.query.return_value.all.return_value = [habit1, habit2]

        # Mock the filter_by method to return the check offs for each habit
        def mock_filter_by(habit_id):
            if habit_id == habit1.id:
                return MagicMock(order_by=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[
                    CheckOff(habit_id=1, date_time=datetime(2024, 1, 1)),
                    CheckOff(habit_id=1, date_time=datetime(2024, 1, 2)),
                    CheckOff(habit_id=1, date_time=datetime(2024, 1, 3)),
                    CheckOff(habit_id=1, date_time=datetime(2024, 1, 5)),
                ]))))
            elif habit_id == habit2.id:
                return MagicMock(order_by=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[
                    CheckOff(habit_id=2, date_time=datetime(2024, 1, 1)),
                    CheckOff(habit_id=2, date_time=datetime(2024, 1, 8)),
                    CheckOff(habit_id=2, date_time=datetime(2024, 1, 15)),
                    CheckOff(habit_id=2, date_time=datetime(2024, 1, 22)),
                    CheckOff(habit_id=2, date_time=datetime(2024, 2, 14)),
                ]))))

        mock_session.query.return_value.filter_by.side_effect = mock_filter_by


        habit_tracker = HabitTracker(mock_session)
        streak, habit_id = habit_tracker.get_longest_streak_of_all_habits()

        # The longest streak is 22 days for habit 2, because habit 2 has weekly periodicity
        # so the streak is calculated by multiplying the number of weeks by the number of days in a week
        assert streak == 22
        assert habit_id == 2


    def test_generate_example_data_with_invalid_date(self):
        """Test if an InvalidStartDateError exception is raised when the start date is invalid when generating example data."""
        mock_session = MagicMock()

        weeks = 4
        invalid_start_date = datetime.utcnow() - timedelta(weeks=weeks-2)

        predefined_habits = [
            {"name": "Drink Water", "description": "Drink 2 liters of water", "periodicity": 1}
        ]

        with pytest.raises(InvalidStartDateError) as e:
            habit_tracker = HabitTracker(mock_session)
            habit_tracker.generate_example_data(predefined_habits=predefined_habits, start_date=invalid_start_date, weeks=weeks)
