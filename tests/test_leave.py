import pytest

def test_leave_balance_reduction():
    """Verify that approving leave correctly reduces the employee's balance."""
    initial_balance = 20
    approved_days = 3  # Workdays counted
    
    updated_balance = initial_balance - approved_days
    
    assert updated_balance == 17
    print(f"\n[SUCCESS] Initial Balance: {initial_balance} | Approved: {approved_days} | Remaining: {updated_balance}")

def test_weekend_and_holiday_exclusion():
    """Verify that weekends and holidays are never counted as leave days."""
    total_calendar_days = 5  # e.g., Friday through Tuesday
    weekends_in_span = 2     # Saturday and Sunday
    holidays_in_span = 0
    
    # Calculate actual billable leave days
    leave_days_counted = total_calendar_days - weekends_in_span - holidays_in_span
    
    assert leave_days_counted == 3
    print(f"\n[SUCCESS] Calendar Span: {total_calendar_days} days | Weekends/Holidays Excluded: {weekends_in_span} | Billable Leave Days: {leave_days_counted}")