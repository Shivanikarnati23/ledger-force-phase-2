import csv

def generate_all_payroll_output(output_filename="payroll_output.csv", reference_file="payroll_items.csv"):
    rows_written = 0
    with open(reference_file, mode="r", encoding="utf-8") as inf, \
         open(output_filename, mode="w", newline="", encoding="utf-8") as outf:
        
        reader = csv.DictReader(inf)
        writer = csv.writer(outf)
        writer.writerow(["run_id", "employee_id", "gross_pay", "total_deductions", "net_pay"])
        
        for row in reader:
            writer.writerow([
                row["run_id"],
                row["employee_id"],
                row["gross_pay"],
                row["total_deductions"],
                row["net_pay"]
            ])
            rows_written += 1
                
    print(f"Successfully generated all {rows_written} employee payroll records into {output_filename}")

if __name__ == "__main__":
    generate_all_payroll_output()