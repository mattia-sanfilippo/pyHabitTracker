# pyHabitTracker

Lightweight CLI application to track habits and check-offs.

- [pyHabitTracker](#pyhabittracker)
  - [Features](#features)
    - [Habits](#habits)
    - [Check-Off Management](#check-off-management)
    - [Streak Tracking](#streak-tracking)
    - [Example Data Generation](#example-data-generation)
  - [Installation](#installation)
    - [Dependencies](#dependencies)
  - [How to use the CLI](#how-to-use-the-cli)
    - [Create a new habit](#create-a-new-habit)
    - [Lists all habits](#lists-all-habits)
    - [Check off habit](#check-off-habit)
    - [Delete habit and related check offs](#delete-habit-and-related-check-offs)
    - [Delete all habits and related check offs](#delete-all-habits-and-related-check-offs)
    - [List all check offs](#list-all-check-offs)
    - [List all check offs for a habit](#list-all-check-offs-for-a-habit)
    - [Get last check off for a habit](#get-last-check-off-for-a-habit)
    - [Get longest streak of check offs for a habit](#get-longest-streak-of-check-offs-for-a-habit)
    - [Get longest check-off streak of all habits](#get-longest-check-off-streak-of-all-habits)
    - [Generate example data](#generate-example-data)
  - [Testing](#testing)

## Features

### Habits

- **Create a New Habit**: Users can create new habits by specifying a name, description, and periodicity (daily or weekly).
- **List All Habits**: Users can list all the habits they have created.
- **Delete Habit**: Users can delete a specific habit and all its related check-offs.
- **Delete All Habits**: Users can delete all habits and their related check-offs.

### Check-Off Management

- **Check Off Habit**: Users can mark a habit as completed for a specific day or week.
- **List All Check-Offs**: Users can list all check-offs for all habits.
- **List Check-Offs for a Habit**: Users can list all check-offs for a specific habit.
- **Get Last Check-Off for a Habit**: Users can retrieve the last check-off date for a specific habit.

### Streak Tracking

- **Get Longest Check-Off Streak for a Habit**: Users can find the longest streak of consecutive check-offs for a specific habit.
- **Get Longest Check-Off Streak of All Habits**: Users can find the longest streak of consecutive check-offs across all habits.

### Example Data Generation

- **Generate Example Data**: Users can generate example data for predefined habits starting from a specific date for a given number of weeks.

## Installation

This application is built using Python 3.9.

### Dependencies

The dependencies are listed in the `requirements.txt` file. You can install them using the following command:

```shell
pip install -r requirements.txt
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

### Delete habit and related check offs

```shell
python cli.py delete_habit HABIT_ID
```

### Delete all habits and related check offs

```shell
python cli.py delete_all_habits
```

### List all check offs

```shell
python cli.py get_all_check_offs
```

### List all check offs for a habit

```shell
python cli.py get_all_check_offs_for_habit HABIT_ID
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

## Testing

To run the tests for this application, follow these steps:

1. **Install Dependencies**: Ensure all dependencies are installed. You can use the following command:

    ```shell
    pip install -r requirements.txt
    ```

2. **Run Tests**: Use the `pytest` framework to run the tests. Execute the following command in the root directory of the project:

    ```shell
    pytest
    ```

3. **Check Test Coverage**: To check the test coverage, you can use the `coverage` package. First, install it if you haven't already:

    ```shell
    pip install coverage
    ```

    Then, run the tests with coverage:

    ```shell
    coverage run -m pytest
    ```

    Finally, generate the coverage report:

    ```shell
    coverage report -m
    ```
