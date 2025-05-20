from db_config import get_connection
import re

# Import MySQL-specific error classes
import mysql.connector
from mysql.connector import IntegrityError, Error

class Service:
    def __init__(self, service_id, service_name, cost):
        self.service_id = service_id
        self.service_name = service_name
        self.cost = cost

    def __repr__(self):
        return f"{self.service_name} (ID: {self.service_id}, Cost: {self.cost})"

    def add(self):
        # Data validation
        if not self.service_id or not isinstance(self.service_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.service_id):
            print("Invalid Service ID. It must be alphanumeric (no spaces or special characters).")
            return
        if not self.service_name or not re.match(r'^[A-Za-z0-9\s\-_]+$', self.service_name):
            print("Invalid Service Name.")
            return

        try:
            cost_val = float(self.cost)
            if cost_val < 0 or cost_val > 5000:
                print("Cost must be between 0 and 5000.")
                return
        except ValueError:
            print("Invalid Cost. Enter a valid number.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO services (service_id, service_name, cost) VALUES (%s, %s, %s)"
            cursor.execute(sql, (self.service_id, self.service_name, cost_val))
            conn.commit()
            print("Service added successfully.")
        except IntegrityError:
            print(f"Error: Duplicate Service ID '{self.service_id}'. Please use a unique ID.")
        except Error as e:
            print("Database error while adding service:", e)
        except Exception as e:
            print("Unexpected error while adding service:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def update(self):
        # Data validation (same as add)
        if not self.service_id or not isinstance(self.service_id, str) or not re.match(r'^[A-Za-z0-9]+$', self.service_id):
            print("Invalid Service ID. It must be alphanumeric (no spaces or special characters).")
            return
        if not self.service_name or not re.match(r'^[A-Za-z0-9\s\-_]+$', self.service_name):
            print("Invalid Service Name.")
            return
        try:
            cost_val = float(self.cost)
            if cost_val < 0 or cost_val > 5000:
                print("Cost must be between 0 and 5000.")
                return
        except ValueError:
            print("Invalid Cost. Enter a valid number.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "UPDATE services SET service_name=%s, cost=%s WHERE service_id=%s"
            cursor.execute(sql, (self.service_name, cost_val, self.service_id))
            conn.commit()
            if cursor.rowcount == 0:
                print("Service ID not found.")
            else:
                print("Service updated successfully.")
        except Error as e:
            print("Database error while updating service:", e)
        except Exception as e:
            print("Unexpected error while updating service:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def delete(service_id):
        if not service_id or not isinstance(service_id, str) or not re.match(r'^[A-Za-z0-9]+$', service_id):
            print("Invalid Service ID. It must be alphanumeric (no spaces or special characters).")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM services WHERE service_id=%s"
            cursor.execute(sql, (service_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print("Service ID not found.")
            else:
                print("Service deleted successfully.")
        except Error as e:
            print("Database error while deleting service:", e)
        except Exception as e:
            print("Unexpected error while deleting service:", e)
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
            print("ID | Name | Cost")
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
