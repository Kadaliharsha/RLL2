from db_config import get_connection
from patient import Patient
from doctor import Doctor
from service import Service, ServiceUsageDB
from appointment import Appointment
from billing import Bill
from billing import compute_total_billing

# --- Patient ---
def patients_menu():
    while True:
        print("\n=== Patients Management ===")
        print("1.Search Patient")
        print("2. Add Patient")
        print("3. View Patient")
        print("4. Update Patient")
        print("5. Delete Patient")
        print("6. Service Usage of Patient")
        print("7. Days Admitted for a Patient")
        print("8. Main Menu")
    
        choice = input("Select an option: ")

        if choice == '1':
            name = input("Enter part or full patient name: ")
            Patient.search_by_name(name)
            
        elif choice == '2':
            patient_id = int(input("Enter Patient ID: "))
            name = input("Enter Name: ")
            age = int(input("Enter Age: "))
            gender = input("Enter Gender (M/F/Other): ")
            admission_date = input("Enter Admission Date (YYYY-MM-DD): ")
            contact_no = input("Enter Contact No: ")
            Patient(patient_id, name, age, gender, admission_date, contact_no).add()
            
        elif choice == '3':
            Patient.view()

        elif choice == '4':
            patient_id = int(input("Enter Patient ID to update: "))
            name = input("Enter New Name: ")
            age = int(input("Enter New Age: "))
            gender = input("Enter New Gender (M/F/Other): ")
            admission_date = input("Enter New Admission Date (YYYY-MM-DD): ")
            contact_no = input("Enter New Contact No: ")
            Patient(patient_id, name, age, gender, admission_date, contact_no).update()

        elif choice == '5':
            patient_id = input("Enter Patient ID to delete: ")
            Patient.delete(patient_id)

        elif choice == "6":
            patient_id = input("Enter Patient ID: ")
            service_usage_menu(patient_id)
        
        elif choice == "7":
            patient_id = input("Enter Patient ID: ")
            Patient.days_admitted(patient_id)

        elif choice == '8':
            break

        else:
            print("Invalid Choice. Please try again.")

# --- Doctor ---
def doctors_menu():
    while True:
        print("\n=== Doctors Management ===")
        print("1. Search Doctor")
        print("2. Add Doctor")
        print("3. View Doctor")
        print("4. Update Doctor")
        print("5. Delete Doctor")
        print("6. Main Menu")
 
        choice = input("Select an option: ")
 
        if choice == "1":
            name = input("Enter part or full doctor name: ")
            Doctor.search_by_name(name)
        
        elif choice == '2':
            doctor_id = input("Enter Doctor ID: ")
            name = input("Enter Name: ")
            specialization = input("Enter Specialization: ")
            contact_no = input("Enter Contact No: ")
            Doctor(doctor_id, name, specialization, contact_no).add()
 
        elif choice == '3':
            Doctor.view()
 
        elif choice == '4':
            doctor_id = input("Enter Doctor ID to update: ")
            name = input("Enter New Name: ")
            specialization = input("Enter New Specialization: ")
            contact_no = input("Enter New Contact No: ")
            Doctor(doctor_id, name, specialization, contact_no).update()
 
        elif choice == '5':
            doctor_id = input("Enter Doctor ID to delete: ")
            Doctor.delete(doctor_id)
 
        elif choice == '6':
            break
 
        else:
            print("Invalid Choice. Please try again.")

# --- Services ---
def services_menu():
    while True:
        print("\n=== Services Management ===")
        print("1. Add Services")
        print("2. View Services")
        print("3. Update Services")
        print("4. Delete Services")
        print("5. Main Menu")
        choice = input("Select an option: ")

        if choice == '1':
            service_id = input("Enter Service ID: ")
            name = input("Enter Service Name: ")
            cost = float(input("Enter Cost: "))
            Service(service_id, name, cost).add()

        elif choice == '2':
            Service.view()

        elif choice == '3':
            service_id = input("Enter Service ID to update: ")
            name = input("Enter New Service Name: ")
            cost = float(input("Enter New Cost: "))
            Service(service_id, name, cost).update()

        elif choice == '4':
            service_id = input("Enter Service ID to delete: ")
            Service.delete(service_id)

        elif choice == '5':
            break
        
        else:
            print("Invalid Choice. Please try again.")

# --- ServiceUsageTracker ---
def service_usage_menu(patient_id):
    while True:
        print("\nService Usage of Patient:", patient_id)
        print("1. Add Service Usage")
        print("2. View Services Used")
        print("3. Clear Services (after billing)")
        print("4. Back to Patients Management")
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
            
# --- Appointments ---
def appointments_menu():
    while True:
        print("\n=== Appointments Management ===")
        print("1. Add Appointments")
        print("2. View Appointments")
        print("3. Update Appointments")
        print("4. Delete Appointments")
        print("5. Filter Appointments by Date")
        print("6. Total Days between Appointments of Patient")
        print("7. Main Menu")
        choice = input("Select an option: ")

        if choice == '1':
            appointment_id = input("Enter Appointment ID: ")
            patient_id = input("Enter Patient ID: ")
            doctor_id = input("Enter Doctor ID: ")
            date = input("Enter Appointment Date (YYYY-MM-DD): ")
            diagnosis = input("Enter Diagnosis: ")
            Appointment(appointment_id, patient_id, doctor_id, date, diagnosis).add()

        elif choice == '2':
            Appointment.view()

        elif choice == '3':
            appointment_id = input("Enter Appointment ID to update: ")
            patient_id = input("Enter New Patient ID: ")
            doctor_id = input("Enter New Doctor ID: ")
            date = input("Enter New Appointment Date (YYYY-MM-DD): ")
            diagnosis = input("Enter New Diagnosis: ")
            Appointment(appointment_id, patient_id, doctor_id, date, diagnosis).update()

        elif choice == '4':
            appointment_id = input("Enter Appointment ID to delete: ")
            Appointment.delete(appointment_id)

        elif choice == '5':
            Appointment.filter_appointments()

        elif choice == '6':
            patient_id = input("Enter Patient ID: ")
            Appointment.days_between_appointments(patient_id)
            
        elif choice == "7":
            break
        else:
            print("Invalid Choice. Please try again.")

# --- Bill ---
def billing_menu():
    while True:
        print("\nBilling Management")
        print("1. Add Bill")
        print("2. View Bills")
        print("3. Update Bill")
        print("4. Delete Bill")
        print("5. Compute total billing")
        print("6. Generate Invoice for Bill")
        print("7. Main Menu")
        choice = input("Select an option: ")
 
        if choice == '1':
            bill_id = input("Enter Bill ID: ")
            patient_id = input("Enter Patient ID: ")
            billing_date = input("Enter Billing Date (YYYY-MM-DD) [leave blank for today]: ")
            if not billing_date.strip():
                bill = Bill(bill_id, patient_id)
            else:
                bill = Bill(bill_id, patient_id, billing_date)
            bill.add()
            # Generate bill ivoice immediately
            bill.generate_invoice()
            
        elif choice == '2':
            Bill.view()
 
        elif choice == '3':
            bill_id = input("Enter Bill ID to update: ")
            patient_id = input("Enter New Patient ID: ")
            billing_date = input("Enter New Billing Date (YYYY-MM-DD) [leave blank for today]: ")
            if not billing_date.strip():
                bill = Bill(bill_id, patient_id)
            else:
                bill = Bill(bill_id, patient_id, billing_date)
            bill.update()
 
        elif choice == '4':
            bill_id = input("Enter Bill ID to delete: ")
            Bill.delete(bill_id)
 
        elif choice == '5':
            patient_id = input("Enter Patient ID to compute total billing: ")
            total = compute_total_billing(patient_id)
            if total is not None:
                print(f"Total bill for patient {patient_id}: {total}")

        elif choice == '6':
            bill_id = input("Enter Bill ID to generate invoice: ")
            # You may need to fetch patient_id and billing_date from the database
            # For demonstration, let's assume you fetch them:
            from db_config import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT patient_id, billing_date FROM billing WHERE bill_id=%s", (bill_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                patient_id, billing_date = row
                bill = Bill(bill_id, patient_id, billing_date)
                bill.generate_invoice()
            else:
                print("Bill not found.")
            break
        
        elif choice == '7':
            break
        
        else:
            print("Invalid Choice. Please try again.")

def export_menu():
    while True:
        print("\n=== Export Menu ===")
        print("1. Export Billing Summary to CSV")
        print("2. Export Appointment Summary to CSV")
        print("3. Main Menu")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            filename = input("Enter filename for billing summary (default: billing_summary.csv): ").strip() or "billing_summary.csv"
            Bill.export_billing_summary_to_csv(filename)
        elif choice == '2':
            filename = input("Enter filename for appointment summary (default: appointment_summary.csv): ").strip() or "appointment_summary.csv"
            Appointment.export_appointment_summary_to_csv(filename)
        elif choice == '3':
            break
        else:
            print("Invalid choice.")

def main_menu():
    while True:
        print("\n=== Hospital Management CLI ===")
        print("1. Patients Management")
        print("2. Doctors Management")
        print("3. Services Management")
        print("4. Appointments Management")
        print("5. Billing Management")
        print("6. Export Management")
        print("7. Exit")
        
        choice = input("Select an option: ")

        if choice == '1':
            patients_menu()
        elif choice == '2':
            doctors_menu()
        elif choice == '3':
            services_menu()
        elif choice == '4':
            appointments_menu()
        elif choice == '5':
            billing_menu()
        elif choice == '6':
            export_menu()
        elif choice == '7':
            print("Exiting Hospital Management CLI. Bye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
