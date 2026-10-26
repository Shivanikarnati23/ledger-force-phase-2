import pandas as pd

# Load your attendance dataset
df = pd.read_csv('attendance.csv')

# Pick 3 employee IDs (make sure they exist in your file)
selected_employees = ['EMP-0002', 'EMP-0004', 'EMP-0006'] # Change these if needed

# Filter and calculate monthly summary
filtered_df = df[df['employee_id'].isin(selected_employees)]

# Group by employee and aggregate status/hours
summary = filtered_df.groupby('employee_id').agg(
    present_days=('status', lambda x: (x == 'PRESENT').sum()),
    lop_days=('status', lambda x: (x == 'LOP').sum()),
    total_overtime=('overtime_hours', 'sum')
).reset_index()

print("--- AUTOMATED ATTENDANCE SUMMARY FOR YOUR TABLE ---")
print(summary)