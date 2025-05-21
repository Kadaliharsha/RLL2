from db_config import get_connection
from service import ServiceUsageDB
import re
import datetime
import csv
import os

import mysql.connector
from mysql.connector import IntegrityError, Error

class Bill:
    def __init__(self, bill_id, patient_id, billing_date=None):
        self.bill_id = bill_id
        self.patient_id = patient_id
        self.billing_date = billing_date or datetime.date.today().strftime("%Y-%m-%d")

    def add(self):
        # Data validation
        if not self.bill_id or not isinstance(self.bill_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.bill_id):
            print("Invalid Bill ID. It must be alphanumeric (no spaces or special characters).")
            return

        if not self.patient_id or not isinstance(self.patient_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.patient_id):
            print("Invalid Patient ID. It must be alphanumeric (no spaces or special characters).")
            return

        try:
            datetime.datetime.strptime(self.billing_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid Billing Date. Use YYYY-MM-DD format.")
            return

        # Fetch all services used by this patient from temp_service_usage
        services = ServiceUsageDB.get_services_for_patient(self.patient_id)
        print("DEBUG: Services fetched from temp_service_usage:", services)
        if not services:
            print("No services to bill for this patient.")
            return

        # Calculate total amount
        total_amount = sum(float(s[2]) for s in services)  # s[2] is cost

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Check patient exists
            cursor.execute("SELECT 1 FROM patients WHERE patient_id=%s", (self.patient_id,))
            if cursor.fetchone() is None:
                print("Patient ID does not exist.")
                return

            # Insert bill
            sql = "INSERT INTO billing (bill_id, patient_id, total_amount, billing_date) VALUES (%s, %s, %s, %s)"
            try:
                cursor.execute(sql, (self.bill_id, self.patient_id, total_amount, self.billing_date))
            except IntegrityError:
                print(f"Error: Duplicate Bill ID '{self.bill_id}'. Please use a unique ID.")
                return

            # Insert service details into billed_services
            for s in services:
                try:
                    cursor.execute(
                        "INSERT INTO billed_services (bill_id, patient_id, service_id, service_name, cost) VALUES (%s, %s, %s, %s, %s)",
                        (self.bill_id, self.patient_id, s[0], s[1], s[2])
                    )
                except IntegrityError:
                    print(f"Error: Duplicate service entry for bill {self.bill_id} and service {s[0]}. Skipping.")
            conn.commit()
            print(f"Bill added successfully. Total amount: {total_amount}")
            print("Billed services recorded.")
        except Error as e:
            print("Database error while adding bill:", e)
        except Exception as e:
            print("Unexpected error while adding bill:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

        # Clear temp service usage for this patient
        try:
            ServiceUsageDB.clear_services_for_patient(self.patient_id)
        except Exception as e:
            print("Error clearing temp service usage:", e)


    def update(self):
        # Data validation (same as add)
        if not self.bill_id or not isinstance(self.bill_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.bill_id):
            print("Invalid Bill ID. It must be alphanumeric (no spaces or special characters).")
            return

        if not self.patient_id or not isinstance(self.patient_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.patient_id):
            print("Invalid Patient ID. It must be alphanumeric (no spaces or special characters).")
            return

        try:
            datetime.datetime.strptime(self.billing_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid Billing Date. Use YYYY-MM-DD format.")
            return

        # Fetch all services used by this patient from temp_service_usage
        services = ServiceUsageDB.get_services_for_patient(self.patient_id)
        if not services:
            print("No services to bill for this patient.")
            return

        # Calculate total amount
        total_amount = sum(float(s[2]) for s in services)  # s[2] is cost

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Check patient exists
            cursor.execute("SELECT 1 FROM patients WHERE patient_id=%s", (self.patient_id,))
            if cursor.fetchone() is None:
                print("Patient ID does not exist.")
                return

            # Update bill
            sql = "UPDATE billing SET patient_id=%s, total_amount=%s, billing_date=%s WHERE bill_id=%s"
            cursor.execute(sql, (self.patient_id, total_amount, self.billing_date, self.bill_id))
            conn.commit()
            if cursor.rowcount == 0:
                print("Bill ID not found.")
            else:
                print("Bill updated successfully. Total amount:", total_amount)
        except Error as e:
            print("Database error while updating bill:", e)
        except Exception as e:
            print("Unexpected error while updating bill:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

        # Clear temp service usage for this patient
        try:
            ServiceUsageDB.clear_services_for_patient(self.patient_id)
        except Exception as e:
            print("Error clearing temp service usage:", e)

    @staticmethod
    def delete(bill_id):
        if not bill_id or not isinstance(bill_id, str) or not re.match(r'^[A-Za-z0-9]+$', bill_id):
            print("Invalid Bill ID. It must be alphanumeric (no spaces or special characters).")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM billing WHERE bill_id=%s"
            cursor.execute(sql, (bill_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print("Bill ID not found.")
            else:
                print("Bill deleted successfully.")
        except Error as e:
            print("Database error while deleting bill:", e)
        except Exception as e:
            print("Unexpected error while deleting bill:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def view():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM billing")
            rows = cursor.fetchall()
            print("ID | Patient ID | Total Amount | Billing Date")
            for row in rows:
                print(" | ".join(str(x) for x in row))
        except Error as e:
            print("Database error while viewing bills:", e)
        except Exception as e:
            print("Unexpected error while viewing bills:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()


    def generate_invoice(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. Fetch patient details
            cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (self.patient_id,))
            patient = cursor.fetchone()

            # 2. Fetch doctor and latest appointment details
            cursor.execute("""
                SELECT a.date, d.name AS doctor_name, d.specialization, a.consulting_charge
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.patient_id = %s
                ORDER BY a.date DESC LIMIT 1
            """, (self.patient_id,))
            appt = cursor.fetchone()

            # 3. Fetch services used from billed_services
            cursor.execute("""
                SELECT s.service_name, bs.cost
                FROM billed_services bs
                JOIN services s ON bs.service_id = s.service_id
                WHERE bs.bill_id = %s
            """, (self.bill_id,))
            services = cursor.fetchall()

            # 4. Prepare invoice content
            lines = []
            lines.append("="*60)
            lines.append("                        HOSPITAL INVOICE")
            lines.append("="*60)
            lines.append(f"Bill No.    : {self.bill_id:<15}   Date: {self.billing_date}")
            lines.append(f"Patient ID  : {self.patient_id:<15}   Name: {patient['name'] if patient else 'N/A'}")
            lines.append("-"*60)
            if appt:
                lines.append(f"Doctor      : {appt['doctor_name']} ({appt['specialization']})")
                lines.append(f"Consultation Charge: ₹{float(appt['consulting_charge']):,.2f}")
            else:
                lines.append("Doctor      : N/A")
                lines.append("Consultation Charge: ₹0.00")
                
            lines.append("-"*60)
            lines.append(f"{'Service Name':30} {'Amount':>15}")
            lines.append("-"*60)

            service_total = 0
            if services:
                for s in services:
                    # If you have quantity and unit price, use them; else just cost
                    lines.append(f"{s['service_name'][:30]:30} {float(s['cost']):>15,.2f}")
                    service_total += float(s['cost'])
            else:
                lines.append(f"{'No services billed.':<57}")

            lines.append("-"*60)
            lines.append(f"{'Service Total':>47} : ₹{service_total:,.2f}")
            consulting_charge = float(appt['consulting_charge']) if appt else 0.0
            lines.append(f"{'Consultation Charge':>47} : ₹{consulting_charge:,.2f}")
            lines.append("-"*60)
            total = service_total + consulting_charge
            lines.append(f"{'TOTAL AMOUNT DUE':>47} : ₹{total:,.2f}")
            lines.append("="*60)
            lines.append("Payment due within 30 days. For queries, call (123) 456-7890")
            lines.append("="*60)
            lines.append("        Thank you for choosing our Hospital!")
            lines.append("="*60)
            
            # 5. Ensure output/invoices directory exists
            output_dir = os.path.join("output", "invoices")
            os.makedirs(output_dir, exist_ok=True)

            # 6. Write to file
            filename = os.path.join(output_dir, f"bill_{self.patient_id}.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write('\n'.join(lines))
            print(f"Invoice generated and saved as {filename}")

        except Error as e:
            print("Database error while generating invoice:", e)
        except Exception as e:
            print("Unexpected error while generating invoice:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def export_billing_summary_to_csv(filename="billing_summary.csv"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT bill_id, patient_id, total_amount, billing_date FROM billing")
            rows = cursor.fetchall()
            if not rows:
                print("No billing records to export.")
                return
            with open(filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Bill ID", "Patient ID", "Total Amount", "Billing Date"])
                for row in rows:
                    writer.writerow(row)
            print(f"Billing summary exported to {filename}")
        except Exception as e:
            print("Error exporting billing summary:", e)
        finally:
            cursor.close()
            conn.close()

def compute_total_billing(patient_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Sum service costs
        cursor.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM temp_service_usage WHERE patient_id=%s",
            (patient_id,)
        )
        service_total = cursor.fetchone()[0] or 0

        # Sum consulting charges
        cursor.execute(
            "SELECT COALESCE(SUM(consulting_charge), 0) FROM appointments WHERE patient_id=%s",
            (patient_id,)
        )
        consulting_total = cursor.fetchone()[0] or 0

        total_billing = service_total + consulting_total
        print(f"Service Total: {service_total}")
        print(f"Consulting Total: {consulting_total}")
        print(f"Total Billing: {total_billing}")
        return total_billing
    except Error as e:
        print("Database error while computing total billing:", e)
        return None
    except Exception as e:
        print("Unexpected error while computing total billing:", e)
        return None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def generate_next_bill_id():
    from db_config import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bill_id FROM billing WHERE bill_id REGEXP '^B[0-9]+$'")
    bill_ids = cursor.fetchall()
    cursor.close()
    conn.close()
    # Extract numeric part and find max
    max_num = 0
    for (bill_id,) in bill_ids:
        try:
            num = int(bill_id[1:])  # skip 'B'
            if num > max_num:
                max_num = num
        except:
            continue
    return f'B{max_num+1:03d}'  # e.g., B301 if max was 300
