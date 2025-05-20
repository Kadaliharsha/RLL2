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
            conn.commit()
            print(f"Bill added successfully. Total amount: {total_amount}")

            # Insert service details into billed_services
            for s in services:
                try:
                    cursor.execute(
                        "INSERT INTO billed_services (bill_id, service_id, service_name, cost) VALUES (%s, %s, %s, %s)",
                        (self.bill_id, s[0], s[1], s[2])
                    )
                except IntegrityError:
                    print(f"Error: Duplicate service entry for bill {self.bill_id} and service {s[0]}. Skipping.")
            conn.commit()
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
            # Fetch patient details
            cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (self.patient_id,))
            patient = cursor.fetchone()

            # Fetch doctor and appointment details
            cursor.execute("""
                SELECT a.date, d.name AS doctor_name, d.specialization, a.consulting_charge
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.patient_id=%s
                ORDER BY a.date DESC LIMIT 1
            """, (self.patient_id,))
            appt = cursor.fetchone()

            # Fetch services used
            cursor.execute("""
                SELECT service_name, cost FROM billed_services WHERE bill_id=%s
            """, (self.bill_id,))
            services = cursor.fetchall()
            print("DEBUG: Services fetched from billed_services:", services)
            # Prepare invoice content
            lines = []
            lines.append("=== Hospital Invoice ===\n")
            lines.append(f"Bill ID: {self.bill_id}")
            lines.append(f"Patient ID: {self.patient_id}")
            lines.append(f"Patient Name: {patient['name'] if patient else 'N/A'}")
            lines.append(f"Date: {self.billing_date or datetime.date.today()}\n")

            if appt:
                lines.append(f"Doctor: {appt['doctor_name']} ({appt['specialization']})")
                lines.append(f"Consulting Charge: {appt['consulting_charge']}\n")
            else:
                lines.append("Doctor: N/A\nConsulting Charge: 0\n")

            lines.append("Services Used:")
            service_total = 0
            if services:
                for s in services:
                    lines.append(f"  - {s['service_name']}: {s['cost']}")
                    service_total += float(s['cost'])
            else:
                lines.append(" None")

            lines.append(f"\nService Total: {service_total}")

            consulting_charge = float(appt['consulting_charge']) if appt else 0.0
            total = service_total + consulting_charge
            lines.append(f"Total Amount: {total}\n")
            lines.append("Thank you for choosing our hospital!\n")
            
            # Ensure output/invoices directory exists
            output_dir = os.path.join("output", "invoices")
            os.makedirs(output_dir, exist_ok=True)

            # Write to file
            filename = os.path.join(output_dir, f"bill_{self.patient_id}.txt")
            with open(filename, "w") as f:
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
