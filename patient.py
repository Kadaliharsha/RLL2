from db_config import get_connection
import re
from datetime import datetime, date

# Import MySQL-specific error classes
import mysql.connector
from mysql.connector import IntegrityError, Error

class Patient:
    def __init__(self, patient_id, name, age, gender, admission_date, contact_no):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.gender = gender
        self.admission_date = admission_date
        self.contact_no = contact_no

    def add(self):
        # Validate Patient ID (integer)
        try:
            patient_id = int(self.patient_id)
            if patient_id <= 0:
                print("Invalid Patient ID. Must be a positive integer.")
                return
        except ValueError:
            print("Invalid Patient ID. Must be an integer.")
            return

        # Validate Name
        if not self.name or not self.name.replace(' ', '').isalpha():
            print("Invalid Name. Name must contain only letters and spaces.")
            return

        # Validate Age
        try:
            age = int(self.age)
            if age < 0 or age > 120:
                print("Invalid Age. Must be between 0 and 120.")
                return
        except ValueError:
            print("Invalid Age. Must be a number.")
            return

        # Validate Gender
        if self.gender not in ['M', 'F', 'Other']:
            print("Invalid Gender. Choose from M, F, Other.")
            return

        # Validate Admission Date using regex
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', self.admission_date):
            print("Invalid Admission Date. Use YYYY-MM-DD format.")
            return

        # Validate Contact Number
        if not self.contact_no.isdigit() or len(self.contact_no) < 10:
            print("Invalid Contact Number. Must be at least 10 digits.")
            return

        # Insert into DB with exception handling
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO patients (patient_id, name, age, gender, admission_date, contact_no) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (patient_id, self.name, age, self.gender, self.admission_date, self.contact_no))
            conn.commit()
            print("Patient added successfully.")
        except IntegrityError:
            print(f"Error: Duplicate Patient ID '{patient_id}'. Please use a unique ID.")
        except Error as e:
            print("Database error while adding patient:", e)
        except Exception as e:
            print("Unexpected error while adding patient:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def update(self):
        # Validate Patient ID (integer)
        try:
            patient_id = int(self.patient_id)
            if patient_id <= 0:
                print("Invalid Patient ID. Must be a positive integer.")
                return
        except ValueError:
            print("Invalid Patient ID. Must be an integer.")
            return

        if not self.name or not self.name.replace(' ', '').isalpha():
            print("Invalid Name.")
            return

        try:
            age = int(self.age)
            if age <= 0 or age > 120:
                print("Invalid Age.")
                return
        except ValueError:
            print("Invalid Age.")
            return

        if self.gender not in ['M', 'F', 'Other']:
            print("Invalid Gender. Choose from M, F, Other.")
            return

        try:
            import datetime
            datetime.datetime.strptime(self.admission_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid Admission Date. Use YYYY-MM-DD format.")
            return

        if not self.contact_no.isdigit() or len(self.contact_no) < 10:
            print("Invalid Contact Number.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = """UPDATE patients SET name=%s, age=%s, gender=%s, admission_date=%s, contact_no=%s WHERE patient_id=%s"""
            cursor.execute(sql, (self.name, age, self.gender, self.admission_date, self.contact_no, patient_id))
            conn.commit()
            if cursor.rowcount == 0:
                print(f"No patient found with ID '{patient_id}'.")
            else:
                print("Patient updated successfully.")
        except Error as e:
            print("Database error while updating patient:", e)
        except Exception as e:
            print("Unexpected error while updating patient:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def delete(patient_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM patients WHERE patient_id=%s"
            cursor.execute(sql, (patient_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print(f"No patient found with ID '{patient_id}'.")
            else:
                print("Patient deleted successfully.")
        except Error as e:
            print("Database error while deleting patient:", e)
        except Exception as e:
            print("Unexpected error while deleting patient:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def view():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients")
            rows = cursor.fetchall()
            print("patient_ID | Name | Age | Gender | Admission Date | Contact No")
            for row in rows:
                print(" | ".join(str(x) for x in row))
        except Error as e:
            print("Database error while viewing patients:", e)
        except Exception as e:
            print("Unexpected error while viewing patients:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def days_admitted(patient_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT admission_date FROM patients WHERE patient_id=%s", (patient_id,))
            row = cursor.fetchone()
            if row and row[0]:
                admission_date = row[0]
                today = date.today()
                days = (today - admission_date).days
                print(f"Patient {patient_id} has been admitted for {days} days.")
                return days
            else:
                print("Patient not found or admission date missing.")
                return None
        except Exception as e:
            print("Error calculating days admitted:", e)
            return None
        finally:
            cursor.close()
            conn.close()
            
    @staticmethod
    def search_by_name(name_substring):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            search_pattern = f"%{name_substring}%"
            cursor.execute("SELECT * FROM patients WHERE name LIKE %s", (search_pattern,))
            rows = cursor.fetchall()
            if rows:
                print("patient_ID | Name | Age | Gender | Admission Date | Contact No")
                for row in rows:
                    print(" | ".join(str(x) for x in row))
            else:
                print("No patients found matching that name.")
        except Exception as e:
            print("Error searching patients:", e)
        finally:
            cursor.close()
            conn.close()
