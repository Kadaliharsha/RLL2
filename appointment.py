import re
from db_config import get_connection
import mysql.connector
from mysql.connector import IntegrityError, Error

class Appointment:
    def __init__(self, appt_id, patient_id, doctor_id, date, diagnosis):
        self.appt_id = appt_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date = date
        self.diagnosis = diagnosis

    def add(self):
        # Validate patient_id
        if not self.patient_id or not str(self.patient_id).isdigit():
            print("Invalid Patient ID.")
            return False
        # Validate doctor_id
        if not self.doctor_id or not isinstance(self.doctor_id, str):
            print("Invalid Doctor ID.")
            return False
        # Validate date
        if not self.date or not re.match(r'^\d{4}-\d{2}-\d{2}$', self.date):
            print("Invalid Date. Use YYYY-MM-DD format.")
            return False
        # Validate diagnosis
        if not self.diagnosis or not isinstance(self.diagnosis, str):
            print("Invalid Diagnosis.")
            return False

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO appointments (appt_id, patient_id, doctor_id, date, diagnosis) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (self.appt_id, self.patient_id, self.doctor_id, self.date, self.diagnosis))
            conn.commit()
            return True
        except mysql.connector.errors.IntegrityError as e:
            if "PRIMARY" in str(e):
                print(f"Error: Duplicate Appointment ID '{self.appt_id}'. Please use a unique ID.")
            else:
                print("Database integrity error: ", e)
            return False
        except Exception as e:
            print("Unexpected error while adding appointment:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def update(self):
        # Validate patient_id
        if not self.patient_id or not str(self.patient_id).isdigit():
            print("Invalid Patient ID.")
            return False
        # Validate doctor_id
        if not self.doctor_id or not isinstance(self.doctor_id, str):
            print("Invalid Doctor ID.")
            return False
        # Validate date
        if not self.date or not re.match(r'^\d{4}-\d{2}-\d{2}$', self.date):
            print("Invalid Date. Use YYYY-MM-DD format.")
            return False
        # Validate diagnosis
        if not self.diagnosis or not isinstance(self.diagnosis, str):
            print("Invalid Diagnosis.")
            return False

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "UPDATE appointments SET patient_id=%s, doctor_id=%s, date=%s, diagnosis=%s WHERE appt_id=%s"
            cursor.execute(sql, (self.patient_id, self.doctor_id, self.date, self.diagnosis, self.appt_id))
            conn.commit()
            if cursor.rowcount == 0:
                print("Appointment ID not found.")
                return False
            else:
                print("Appointment updated successfully.")
                return True
        except Error as e:
            print("Database error while updating appointment:", e)
            return False
        except Exception as e:
            print("Unexpected error while updating appointment:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def delete(appt_id):
        # No validation for appt_id since it's system-generated
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM appointments WHERE appt_id=%s"
            cursor.execute(sql, (appt_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print("Appointment ID not found.")
                return False
            else:
                print("Appointment deleted successfully.")
                return True
        except Error as e:
            print("Database error while deleting appointment:", e)
            return False
        except Exception as e:
            print("Unexpected error while deleting appointment:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def view():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM appointments")
            rows = cursor.fetchall()
            print("Appointment_ID | Patient_ID | Doctor_ID | Date | Diagnosis")
            for row in rows:
                print(" | ".join(str(x) for x in row))
        except Error as e:
            print("Database error while viewing appointments:", e)
        except Exception as e:
            print("Unexpected error while viewing appointments:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def filter_appointments():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            start_date = input("Enter start date(YYYY-MM-DD): ")
            end_date = input("Enter end date(YYYY-MM-DD):")
            cursor.execute("SELECT * FROM appointments WHERE date BETWEEN %s and %s", (start_date, end_date))
            for row in cursor.fetchall():
                print(row)
        except Error as e:
            print("Database error while fetching appointments for given dates:", e)
        except Exception as e:
            print("Unexpected error while fetching appointments for given dates:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    @staticmethod
    def days_between_appointments(patient_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT date FROM appointments WHERE patient_id=%s ORDER BY date", (patient_id,))
            rows = cursor.fetchall()
            dates = [row[0] for row in rows if row[0]]
            if len(dates) < 2:
                print("Not enough appointments to calculate days between.")
                return []
            days_between = []
            for i in range(1, len(dates)):
                days = (dates[i] - dates[i-1]).days
                days_between.append(days)
            for idx, days in enumerate(days_between, 1):
                print(f"Days between appointment {idx} and {idx+1}: {days}")
            return days_between
        except Exception as e:
            print("Error calculating days between appointments:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def export_appointment_summary_to_csv(filename="appointment_summary.csv"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT appt_id, patient_id, doctor_id, date, diagnosis, consulting_charge FROM appointments")
            rows = cursor.fetchall()
            if not rows:
                print("No appointment records to export.")
                return
            with open(filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Appointment ID", "Patient ID", "Doctor ID", "Date", "Diagnosis", "Consulting Charge"])
                for row in rows:
                    writer.writerow(row)
            print(f"Appointment summary exported to {filename}")
        except Exception as e:
            print("Error exporting appointment summary:", e)
        finally:
            cursor.close()
            conn.close()

def generate_next_appointment_id():
    from db_config import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT appt_id FROM appointments WHERE appt_id LIKE 'A%'")
    ids = [int(row[0][1:]) for row in cursor.fetchall() if row[0][1:].isdigit()]
    cursor.close()
    conn.close()
    next_num = max(ids) + 1 if ids else 1
    return f"A{next_num:03d}"  # A001, A002, ..., A999, etc.

