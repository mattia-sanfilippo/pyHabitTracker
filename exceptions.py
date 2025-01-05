class InvalidStartDateError(Exception):
    """
    Exception raised for errors in the input start date when generating example data.
    The start date should be at least n weeks before the current date because we are generating data from the past.
    """
    pass

class MultipleCheckOffError(Exception):
    """
    Exception raised for errors when trying to check off a habit multiple times in the same day.
    """
    pass

class HabitNotFoundError(Exception):
    """
    Exception raised for errors when a habit is not found.
    """
    pass
