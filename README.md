# pyHabitTracker
Python CLI Application to track your habits.

## Installation
This application is built using Python 3.9.
### Dependencies
Install the following dependencies:

**Python Fire**
```shell
pip install fire
```
**Pandas**
```shell
pip install pandas
```

**SqlAlchemy**
```shell
pip install sqlalchemy
```


## How to use the CLI
**Create a new habit:**
```shell
python cli.py create_habit "HABIT NAME" "HABIT DESCRIPTION" 1
```

The third parameter is the periodicity. Type 1 for "Daily", type 2 for "Weekly".

**Lists all habits**
```shell
python cli.py list_habits
```

**Check off habit**
```shell
python cli.py check_off_habit HABIT_ID
```
