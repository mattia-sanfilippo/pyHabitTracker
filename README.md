# pyHabitTracker

Python CLI Application to track your habits.

## Installation

This application is built using Python 3.9.

### Dependencies

Install the following dependencies:

#### Python Fire

```shell
pip install fire
```

#### Pandas

```shell
pip install pandas
```

#### SqlAlchemy

```shell
pip install sqlalchemy
```

## How to use the CLI

### Create a new habit

```shell
python cli.py create_habit "HABIT NAME" "HABIT DESCRIPTION" 1
```

The third parameter is the periodicity. Type 1 for "Daily", type 2 for "Weekly".

### Lists all habits

```shell
python cli.py list_habits
```

### Check off habit

```shell
python cli.py check_off_habit HABIT_ID
```

### List all check offs

```shell
python cli.py get_all_check_offs
```

### Get last check off for a habit

```shell
python cli.py get_last_check_off_from_habit HABIT_ID
```

### Get longest streak of check offs for a habit

```shell
python cli.py get_longest_check_off_streak_for_habit HABIT_ID
```

### Get longest check-off streak of all habits

```shell
python cli.py get_longest_check_off_streak_of_all_habits
```

### Generate example data

```shell
python cli.py generate_example_data START_DATE NUMBER_OF_WEEKS
```

example:

```shell
python cli.py generate_example_data "2024-01-01" 10
```

will generate example data for 10 weeks starting from 2024-01-01.
