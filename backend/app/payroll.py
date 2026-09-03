"""Calendar-day payroll arithmetic. No statutory or unrequested deductions."""

import calendar
import re
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


def month_bounds(month: str):
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise ValueError("Choose a month in YYYY-MM format")
    year, number = map(int, month.split("-"))
    if not 2000 <= year <= 2100:
        raise ValueError("Choose a year between 2000 and 2100")
    days = calendar.monthrange(year, number)[1]
    return date(year, number, 1), date(year, number, days), days


def calculate_payroll(month: str, salary: Decimal, absent_days: int, advance: Decimal):
    _, _, days = month_bounds(month)
    salary, advance = Decimal(str(salary)), Decimal(str(advance))
    if not salary.is_finite() or not advance.is_finite() or salary < 0 or advance < 0:
        raise ValueError("Salary and advance must be non-negative amounts")
    if isinstance(absent_days, bool) or not isinstance(absent_days, int) or not 0 <= absent_days <= days:
        raise ValueError("Absent days must be a whole number within the selected month")
    rate = salary / Decimal(days)
    payable_days = days - absent_days
    # Retain full rate precision until calculating the final rupee amount.
    gross = (rate * payable_days).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    net = (gross - advance).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "daysInMonth": days, "absentDays": absent_days, "payableDays": payable_days,
        "monthlySalary": str(salary.quantize(Decimal("0.01"))),
        "perDayRate": str(rate.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)),
        "payableAmount": str(gross), "advanceGiven": str(advance.quantize(Decimal("0.01"))),
        "netPayable": str(net),
    }
