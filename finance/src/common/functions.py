import datetime
import calendar

def add_one_month(orig_date, months):
    # advance year and month by one month
    new_year = orig_date.year
    new_month = orig_date.month + months
    # note: in datetime.date, months go from 1 to 12
    if new_month > 12:
        new_year += 1
        new_month -= 12

    last_day_of_month = calendar.monthrange(new_year, new_month)[1]
    new_day = min(orig_date.day, last_day_of_month)

    return orig_date.replace(year=new_year, month=new_month, day=new_day)