from db_config import get_connection
import re
from datetime import datetime
import csv

# MySQL-specific error classes
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
        # Data validation
        if not self.appt_id or not isinstance(self.appt_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.appt_id):
            print("Invalid Appointment ID. It must be alphanumeric (no spaces or special characters).")
            return
        if not self.patient_id or not isinstance(self.patient_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.patient_id):
            print("Invalid Patient ID. It must be alphanumeric (no spaces or special characters).")
            return
        if not self.doctor_id or not isinstance(self.doctor_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.doctor_id):
            print("Invalid Doctor ID. It must be alphanumeric (no spaces or special characters).")
            return
        try:
            datetime.datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            print("Invalid Date. Use YYYY-MM-DD format.")
            return
        if not self.diagnosis or not all(x.isalpha() or x.isspace() for x in self.diagnosis):
            print("Invalid Diagnosis. Only letters and spaces allowed.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Check patient exists
            cursor.execute("SELECT 1 FROM patients WHERE patient_id=%s", (self.patient_id,))
            if cursor.fetchone() is None:
                print("Patient ID does not exist.")
                return
            # Check doctor exists
            cursor.execute("SELECT 1 FROM doctors WHERE doctor_id=%s", (self.doctor_id,))
            if cursor.fetchone() is None:
                print("Doctor ID does not exist.")
                return
            # Insert appointment
            sql = "INSERT INTO appointments (appt_id, patient_id, doctor_id, date, diagnosis) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (self.appt_id, self.patient_id, self.doctor_id, self.date, self.diagnosis))
            conn.commit()
            print("Appointment added successfully.")
        except IntegrityError:
            print(f"Error: Duplicate Appointment ID '{self.appt_id}'. Please use a unique ID.")
        except Error as e:
            print("Database error while adding appointment:", e)
        except Exception as e:
            print("Unexpected error while adding appointment:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def update(self):
        # Data validation (same as add)
        if not self.appt_id or not isinstance(self.appt_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.appt_id):
            print("Invalid Appointment ID. It must be alphanumeric (no spaces or special characters).")
            return
        if not self.patient_id or not isinstance(self.patient_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.patient_id):
            print("Invalid Patient ID. It must be alphanumeric (no spaces or special characters).")
            return
        if not self.doctor_id or not isinstance(self.doctor_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.doctor_id):
            print("Invalid Doctor ID. It must be alphanumeric (no spaces or special characters).")
            return
        try:
            datetime.datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            print("Invalid Date. Use YYYY-MM-DD format.")
            return
        if not self.diagnosis or not all(x.isalpha() or x.isspace() for x in self.diagnosis):
            print("Invalid Diagnosis. Only letters and spaces allowed.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Check patient exists
            cursor.execute("SELECT 1 FROM patients WHERE patient_id=%s", (self.patient_id,))
            if cursor.fetchone() is None:
                print("Patient ID does not exist.")
                return
            # Check doctor exists
            cursor.execute("SELECT 1 FROM doctors WHERE doctor_id=%s", (self.doctor_id,))
            if cursor.fetchone() is None:
                print("Doctor ID does not exist.")
                return
            # Update appointment
            sql = "UPDATE appointments SET patient_id=%s, doctor_id=%s, date=%s, diagnosis=%s WHERE appt_id=%s"
            cursor.execute(sql, (self.patient_id, self.doctor_id, self.date, self.diagnosis, self.appt_id))
            conn.commit()
            if cursor.rowcount == 0:
                print("Appointment ID not found.")
            else:
                print("Appointment updated successfully.")
        except Error as e:
            print("Database error while updating appointment:", e)
        except Exception as e:
            print("Unexpected error while updating appointment:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def delete(appt_id):
        if not appt_id or not isinstance(appt_id, str) or not re.match(r'^[A-Za-z0-9]+$', appt_id):
            print("Invalid Appointment ID. It must be alphanumeric (no spaces or special characters).")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM appointments WHERE appt_id=%s"
            cursor.execute(sql, (appt_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print("Appointment ID not found.")
            else:
                print("Appointment deleted successfully.")
        except Error as e:
            print("Database error while deleting appointment:", e)
        except Exception as e:
            print("Unexpected error while deleting appointment:", e)
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
            print("ID | Patient ID | Doctor ID | Date | Diagnosis")
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

