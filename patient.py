from db_config import get_connection
from datetime import datetime, date
from person import Person
import re
import mysql.connector
from mysql.connector import IntegrityError, Error

class Patient(Person):
    def __init__(self, patient_id, name, age, gender, admission_date, contact_no):
        super().__init__(patient_id, name, contact_no)
        self.patient_id = patient_id
        self.age = age
        self.gender = gender
        self.admission_date = admission_date

    def add(self):
        # Name validation
        if not self.name or not re.match(r'^[A-Za-z. ]+$', self.name):
            print("Invalid Name. Only letters, spaces, and periods allowed.")
            return False
        # Age validation
        try:
            age = int(self.age)
            if age < 0 or age > 120:
                print("Invalid Age. Must be between 0 and 120.")
                return False
        except ValueError:
            print("Invalid Age. Must be a number.")
            return False
        # Gender validation
        if self.gender not in ['M', 'F', 'Other']:
            print("Invalid Gender. Choose from M, F, Other.")
            return False
        # Admission date validation
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', self.admission_date):
            print("Invalid Admission Date. Use YYYY-MM-DD format.")
            return False
        # Contact number validation
        if not self.contact_no.isdigit() or len(self.contact_no) < 10:
            print("Invalid Contact Number. Must be at least 10 digits.")
            return False

        # Insert into DB with exception handling
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO patients (patient_id, name, age, gender, admission_date, contact_no) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (self.patient_id, self.name, age, self.gender, self.admission_date, self.contact_no))
            conn.commit()
            return True
        except mysql.connector.errors.IntegrityError as e:
            if "PRIMARY" in str(e):
                print(f"Error: Duplicate Patient ID '{self.patient_id}'. Please use a unique ID.")
            else:
                print("Database integrity error: ", e)
            return False
        except Exception as e:
            print("Unexpected error while adding patient:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def update(self):
        # Name validation
        if not self.name or not re.match(r'^[A-Za-z. ]+$', self.name):
            print("Invalid Name. Only letters, spaces, and periods allowed.")
            return False
        # Age validation
        try:
            age = int(self.age)
            if age < 0 or age > 120:
                print("Invalid Age. Must be between 0 and 120.")
                return False
        except ValueError:
            print("Invalid Age. Must be a number.")
            return False
        # Gender validation
        if self.gender not in ['M', 'F', 'Other']:
            print("Invalid Gender. Choose from M, F, Other.")
            return False
        # Admission date validation
        try:
            datetime.strptime(self.admission_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid Admission Date. Use YYYY-MM-DD format.")
            return False
        # Contact number validation
        if not self.contact_no.isdigit() or len(self.contact_no) < 10:
            print("Invalid Contact Number. Must be at least 10 digits.")
            return False

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = """UPDATE patients SET name=%s, age=%s, gender=%s, admission_date=%s, contact_no=%s WHERE patient_id=%s"""
            cursor.execute(sql, (self.name, age, self.gender, self.admission_date, self.contact_no, self.patient_id))
            conn.commit()
            if cursor.rowcount == 0:
                print(f"No patient found with ID '{self.patient_id}'.")
                return False
            else:
                print("Patient updated successfully.")
                return True
        except mysql.connector.errors.IntegrityError as e:
            print("Database integrity error: ", e)
            return False
        except Exception as e:
            print("Unexpected error while updating patient:", e)
            return False
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
                return False
            else:
                print("Patient deleted successfully.")
                return True
        except Error as e:
            print("Database error while deleting patient:", e)
            return False
        except Exception as e:
            print("Unexpected error while deleting patient:", e)
            return False
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
            print("Patient_ID | Name | Age | Gender | Admission Date | Contact No")
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
                print("Patient_ID | Name | Age | Gender | Admission Date | Contact No")
                for row in rows:
                    print(" | ".join(str(x) for x in row))
            else:
                print("No patients found matching that name.")
        except Exception as e:
            print("Error searching patients:", e)
        finally:
            cursor.close()
            conn.close()

def generate_next_patient_id():
    from db_config import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(patient_id) FROM patients")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    max_id = row[0]
    if max_id is None:
        return 1001
    return int(max_id) + 1
