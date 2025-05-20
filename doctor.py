import re
from db_config import get_connection

# Add these imports for MySQL exception handling
import mysql.connector
from mysql.connector import IntegrityError, Error

class Doctor:
    def __init__(self, doctor_id, name, specialization, contact_no):
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization
        self.contact_no = contact_no

    def add(self):
        # Enhanced Data validation
        if not self.doctor_id or not isinstance(self.doctor_id, str) or not re.match(r'^(?=.*[A-Za-z])[A-Za-z0-9]+$', self.doctor_id):
            print("Invalid Doctor ID. It must be alphanumeric and contain at least one letter (no spaces or special characters).")
            return
        if not self.name or not all(x.isalpha() or x.isspace() for x in self.name):
            print("Invalid Name. Only letters and spaces allowed.")
            return
        if not self.specialization or not all(x.isalpha() or x.isspace() for x in self.specialization):
            print("Invalid Specialization. Only letters and spaces allowed.")
            return
        if not self.contact_no.isdigit() or len(self.contact_no) < 10:
            print("Invalid Contact Number. Only digits allowed, minimum 10 digits.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO doctors (doctor_id, name, specialization, contact_no) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (self.doctor_id, self.name, self.specialization, self.contact_no))
            conn.commit()
            print("Doctor added successfully.")
        except IntegrityError:
            print(f"Error: Duplicate Doctor ID '{self.doctor_id}'. Please use a unique ID.")
        except Error as e:
            print("Database error while adding doctor:", e)
        except Exception as e:
            print("Unexpected error while adding doctor:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def update(self):
        # Enhanced Data validation (same as add)
        if not self.doctor_id or not isinstance(self.doctor_id, str) or not re.match(r'^(?=.*[A-Za-z])[A-Za-z0-9]+$', self.doctor_id):
            print("Invalid Doctor ID. It must be alphanumeric and contain at least one letter (no spaces or special characters).")
            return
        if not self.name or not all(x.isalpha() or x.isspace() for x in self.name):
            print("Invalid Name. Only letters and spaces allowed.")
            return
        if not self.specialization or not all(x.isalpha() or x.isspace() for x in self.specialization):
            print("Invalid Specialization. Only letters and spaces allowed.")
            return
        if not self.contact_no.isdigit() or len(self.contact_no) < 10:
            print("Invalid Contact Number. Only digits allowed, minimum 10 digits.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "UPDATE doctors SET name=%s, specialization=%s, contact_no=%s WHERE doctor_id=%s"
            cursor.execute(sql, (self.name, self.specialization, self.contact_no, self.doctor_id))
            conn.commit()
            if cursor.rowcount == 0:
                print(f"Doctor ID '{self.doctor_id}' not found.")
            else:
                print("Doctor updated successfully.")
        except Error as e:
            print("Database error while updating doctor:", e)
        except Exception as e:
            print("Unexpected error while updating doctor:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def delete(doctor_id):
        if not doctor_id or not isinstance(doctor_id, str) or not re.match(r'^(?=.*[A-Za-z])[A-Za-z0-9]+$', doctor_id):
            print("Invalid Doctor ID. It must be alphanumeric and contain at least one letter (no spaces or special characters).")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM doctors WHERE doctor_id=%s"
            cursor.execute(sql, (doctor_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print(f"Doctor ID '{doctor_id}' not found.")
            else:
                print("Doctor deleted successfully.")
        except Error as e:
            print("Database error while deleting doctor:", e)
        except Exception as e:
            print("Unexpected error while deleting doctor:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def view():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM doctors")
            rows = cursor.fetchall()
            print("ID | Name | Specialization | Contact No")
            for row in rows:
                print(" | ".join(str(x) for x in row))
        except Error as e:
            print("Database error while viewing doctors:", e)
        except Exception as e:
            print("Unexpected error while viewing doctors:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def search_by_name(name_substring):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            search_pattern = f"%{name_substring}%"
            cursor.execute("SELECT * FROM doctors WHERE name LIKE %s", (search_pattern,))
            rows = cursor.fetchall()
            if rows:
                print("Doctor ID | Name | Specialization | Contact No")
                for row in rows:
                    print(" | ".join(str(x) for x in row))
            else:
                print("No doctors found matching that name.")
        except Exception as e:
            print("Error searching doctors:", e)
        finally:
            cursor.close()
            conn.close()
