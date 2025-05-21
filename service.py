import re
from db_config import get_connection
import mysql.connector
from mysql.connector import IntegrityError, Error

class Service:
    def __init__(self, service_id, service_name, cost):
        self.service_id = service_id
        self.service_name = service_name
        self.cost = cost

    def add(self):
        # Validate service name
        if not self.service_name or not re.match(r'^[A-Za-z0-9\s\-_]+$', self.service_name):
            print("Invalid Service Name. Only letters, numbers, spaces, hyphens, and underscores allowed.")
            return False
        # Validate cost
        try:
            cost_val = float(self.cost)
            if cost_val < 0 or cost_val > 5000:
                print("Cost must be between 0 and 5000.")
                return False
        except ValueError:
            print("Invalid Cost. Enter a valid number.")
            return False

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO services (service_id, service_name, cost) VALUES (%s, %s, %s)"
            cursor.execute(sql, (self.service_id, self.service_name, cost_val))
            conn.commit()
            return True
        except IntegrityError:
            print(f"Error: Duplicate Service ID '{self.service_id}'. Please use a unique ID.")
            return False
        except Error as e:
            print("Database error while adding service:", e)
            return False
        except Exception as e:
            print("Unexpected error while adding service:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def update(self):
        # Validate service name
        if not self.service_name or not re.match(r'^[A-Za-z0-9\s\-_]+$', self.service_name):
            print("Invalid Service Name. Only letters, numbers, spaces, hyphens, and underscores allowed.")
            return False
        # Validate cost
        try:
            cost_val = float(self.cost)
            if cost_val < 0 or cost_val > 5000:
                print("Cost must be between 0 and 5000.")
                return False
        except ValueError:
            print("Invalid Cost. Enter a valid number.")
            return False

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "UPDATE services SET service_name=%s, cost=%s WHERE service_id=%s"
            cursor.execute(sql, (self.service_name, cost_val, self.service_id))
            conn.commit()
            if cursor.rowcount == 0:
                print("Service ID not found.")
                return False
            else:
                print("Service updated successfully.")
                return True
        except Error as e:
            print("Database error while updating service:", e)
            return False
        except Exception as e:
            print("Unexpected error while updating service:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def delete(service_id):
        # No validation for service_id since it's system-generated
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM services WHERE service_id=%s"
            cursor.execute(sql, (service_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print("Service ID not found.")
                return False
            else:
                print("Service deleted successfully.")
                return True
        except Error as e:
            print("Database error while deleting service:", e)
            return False
        except Exception as e:
            print("Unexpected error while deleting service:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def view():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM services")
            rows = cursor.fetchall()
            print("Service_ID | Service Name | Cost")
            for row in rows:
                print(" | ".join(str(x) for x in row))
        except Error as e:
            print("Database error while viewing services:", e)
        except Exception as e:
            print("Unexpected error while viewing services:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

class ServiceUsageDB:
    @staticmethod
    def add_service_for_patient(patient_id, service):
        # Data validation
        if not re.match(r'^[A-Za-z0-9]+$', patient_id):
            print("Invalid Patient ID.")
            return
        if not re.match(r'^[A-Za-z0-9]+$', service.service_id):
            print("Invalid Service ID.")
            return
        if not re.match(r'^[A-Za-z0-9\s\-_]+$', service.service_name):
            print("Invalid Service Name.")
            return
        try:
            cost = float(service.cost)
            if cost < 0 or cost > 5000:
                print("Invalid Cost.")
                return
        except ValueError:
            print("Invalid Cost.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO temp_service_usage (patient_id, service_id, service_name, cost) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (patient_id, service.service_id, service.service_name, cost))
            conn.commit()
            print(f"Added {service.service_name} (ID: {service.service_id}, Cost: {cost}) for patient {patient_id}")
        except IntegrityError:
            print(f"Error: Duplicate service usage entry for patient {patient_id} and service {service.service_id}.")
        except Error as e:
            print("Database error while adding service usage:", e)
        except Exception as e:
            print("Unexpected error while adding service usage:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def get_services_for_patient(patient_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "SELECT service_id, service_name, cost FROM temp_service_usage WHERE patient_id=%s"
            cursor.execute(sql, (patient_id,))
            rows = cursor.fetchall()
            return rows
        except Error as e:
            print("Database error while fetching services:", e)
            return []
        except Exception as e:
            print("Unexpected error while fetching services:", e)
            return []
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def clear_services_for_patient(patient_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM temp_service_usage WHERE patient_id=%s"
            cursor.execute(sql, (patient_id,))
            conn.commit()
            print(f"Cleared services for patient {patient_id}")
        except Error as e:
            print("Database error while clearing services:", e)
        except Exception as e:
            print("Unexpected error while clearing services:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

# --- ServiceUsageTracker ---
def service_usage_menu(patient_id):
    while True:
        print("\nService Usage of Patient:", patient_id)
        print("1. Add Service Usage")
        print("2. View Services Used")
        print("3. Clear Services (after billing)")
        print("4. Back to Patient Management")
        choice = input("Select an option: ")
 
        if choice == '1':
            service_id = input("Enter Service ID: ")
            # Fetch service details from DB
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT service_id, service_name, cost FROM services WHERE service_id=%s", (service_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if not row:
                print("Service ID not found.")
            else:
                service = Service(*row)
                ServiceUsageDB.add_service_for_patient(patient_id, service)
 
        elif choice == '2':
            rows = ServiceUsageDB.get_services_for_patient(patient_id)
            if rows:
                print(f"Services used by {patient_id}:")
                for r in rows:
                    print(f"- {r[1]} (ID: {r[0]}, Cost: {r[2]})")
            else:
                print("No services recorded for this patient.")
 
        elif choice == '3':
            ServiceUsageDB.clear_services_for_patient(patient_id)
 
        elif choice == '4':
            break
 
        else:
            print("Invalid choice. Please try again.")

def generate_next_service_id():
    from db_config import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT service_id FROM services WHERE service_id LIKE 'S%'")
    ids = [int(row[0][1:]) for row in cursor.fetchall() if row[0][1:].isdigit()]
    cursor.close()
    conn.close()
    next_num = max(ids) + 1 if ids else 1
    return f"S{next_num:02d}"  # S01, S02, ..., S99, S100, etc.
