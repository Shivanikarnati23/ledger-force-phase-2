import csv
from decimal import Decimal

def verify_all_payroll(output_file="payroll_output.csv", reference_file="payroll_items.csv"):
    output_data = {}
    with open(output_file, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["run_id"], row["employee_id"])
            output_data[key] = {
                "gross_pay": Decimal(str(row["gross_pay"])),
                "total_deductions": Decimal(str(row["total_deductions"])),
                "net_pay": Decimal(str(row["net_pay"]))
            }
            
    ref_data = {}
    with open(reference_file, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["run_id"], row["employee_id"])
            ref_data[key] = {
                "gross_pay": Decimal(str(row["gross_pay"])),
                "total_deductions": Decimal(str(row["total_deductions"])),
                "net_pay": Decimal(str(row["net_pay"]))
            }

    matches = 0
    mismatches = 0
    total = len(output_data)

    print(f"Comparing {total} employee payroll records against {reference_file} for all runs...\n")

    for key, out_vals in output_data.items():
        if key not in ref_data:
            mismatches += 1
            continue
        ref_vals = ref_data[key]
        if (out_vals["gross_pay"] == ref_vals["gross_pay"] and
            out_vals["total_deductions"] == ref_vals["total_deductions"] and
            out_vals["net_pay"] == ref_vals["net_pay"]):
            matches += 1
        else:
            mismatches += 1

    print("\n--- Verification Summary ---")
    print(f"Total Checked: {total}")
    print(f"Exact Matches: {matches}")
    print(f"Mismatches: {mismatches}")
    if total > 0:
        accuracy = (matches / total) * 100
        print(f"Accuracy Score: {accuracy:.2f}%")

if __name__ == "__main__":
    verify_all_payroll()