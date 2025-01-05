class InvalidStartDateError(Exception):
    """
    Exception raised for errors in the input start date when generating example data.
    The start date should be at least n weeks before the current date because we are generating data from the past.
    """
    pass