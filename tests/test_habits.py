from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from exceptions import InvalidStartDateError
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


    def test_habit_details(self):
        """Test if the habit details are returned correctly."""
        mock_db_session = MagicMock()

        habit_id = 1
        habit = Habit(id=1, name="Drink water", description="Drink 2 liters of water daily", periodicity=1)
        mock_db_session.get.return_value = habit

        habit_details = mock_db_session.get(Habit, habit_id)

        mock_db_session.get.assert_called_once_with(Habit, habit_id)

        assert habit_details.name == "Drink water"
        assert habit_details.description == "Drink 2 liters of water daily"
        assert habit_details.periodicity == 1


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
