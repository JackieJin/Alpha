import calendar

def _end_of_month(cur_time):
    """
    Determine if the current day is at the end of the month.
    """
    cur_day = cur_time.day
    end_day = calendar.monthrange(cur_time.year, cur_time.month)[1]
    return cur_day == end_day