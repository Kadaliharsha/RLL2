from db_config import get_connection
from patient import Patient, generate_next_patient_id
from doctor import Doctor, generate_next_doctor_id
from service import Service, ServiceUsageDB, service_usage_menu, generate_next_service_id
from appointment import Appointment, generate_next_appointment_id
from billing import Bill, compute_total_billing, generate_next_bill_id

# --- Patient ---
def patients_menu():
    while True:
        print("\n=== Patient Management ===")
        print("1. Search Patient")
        print("2. Add Patient")
        print("3. View All Patients")
        print("4. Update Patient")
        print("5. Delete Patient")
        print("6. Service Usage of Patient")
        print("7. Days Admitted for a Patient")
        print("8. Back to Main Menu")
    
        choice = input("Select an option: ")

        if choice == '1':
            name = input("Enter part or full patient name: ")
            Patient.search_by_name(name)
            
        elif choice == '2':
            patient_id = generate_next_patient_id()
            print(f"Auto-generated Patient ID: {patient_id}")
            name = input("Enter Name: ")
            age = input("Enter Age: ")
            gender = input("Enter Gender: ")
            admission_date = input("Enter Admission Date (YYYY-MM-DD): ")
            contact_no = input("Enter Contact No: ")
            patient = Patient(patient_id, name, age, gender, admission_date, contact_no)
            result = patient.add()
            if result:
                print("Patient added successfully.")
            else:
                print("Patient was not added.")
                
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
        print("\n=== Doctor Management ===")
        print("1. Search Doctor")
        print("2. Add Doctor")
        print("3. View All Doctors")
        print("4. Update Doctor")
        print("5. Delete Doctor")
        print("6. Back to Main Menu")
 
        choice = input("Select an option: ")
 
        if choice == "1":
            name = input("Enter part or full doctor name: ")
            Doctor.search_by_name(name)
        
        elif choice == '2':
            doctor_id = generate_next_doctor_id()
            print(f"Auto-generated Doctor ID: {doctor_id}")
            name = input("Enter Name: ")
            specialization = input("Enter Specialization: ")
            contact_no = input("Enter contact no: ")
            doctor = Doctor(doctor_id, name, specialization, contact_no)
            result = doctor.add()
            if result:
                print("Doctor added successfully.")
            else:
                print("Doctor was not added.")
 
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
        print("\n=== Service Management ===")
        print("1. Add Service")
        print("2. View All Services")
        print("3. Update Service")
        print("4. Delete Service")
        print("5. Back to Main Menu")
        choice = input("Select an option: ")

        if choice == '1':
            service_id = generate_next_service_id()
            print(f"Auto-generated Service ID: {service_id}")
            service_name = input("Enter Service Name: ")
            cost = input("Enter Cost: ")
            service = Service(service_id, service_name, cost)
            result = service.add()
            if result:
                print("Service added successfully.")
            else:
                print("Service was not added.")

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
          
# --- Appointments ---
def appointments_menu():
    while True:
        print("\n=== Appointments Management ===")
        print("1. Add Appointment")
        print("2. View All Appointments")
        print("3. Update Appointment")
        print("4. Delete Appointment")
        print("5. Filter Appointments by Date")
        print("6. Total Days between Appointments of Patient")
        print("7. Back to Main Menu")
        
        choice = input("Select an option: ")

        if choice == '1':
            appointment_id = generate_next_appointment_id()
            print(f"Auto-generated Appointment ID: {appointment_id}")
            patient_id = input("Enter Patient ID: ")
            doctor_id = input("Enter Doctor ID: ")
            date = input("Enter Appointment Date (YYYY-MM-DD): ")
            diagnosis = input("Enter Diagnosis: ")
            appointment = Appointment(appointment_id, patient_id, doctor_id, date, diagnosis)
            result = appointment.add()
            if result:
                print("Appointment added successfully.")
            else:
                print("Appointment was not added.")
                
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
        print("2. View All Bills")
        print("3. Update Bill")
        print("4. Delete Bill")
        print("5. Compute Total Billing")
        print("6. Generate Invoice")
        print("7. Back to Main Menu")
        
        choice = input("Select an option: ")
 
        if choice == "1":
            bill_id = generate_next_bill_id()
            print(f"Auto-generated Bill ID: {bill_id}")
            patient_id = input("Enter Patient ID: ")
            billing_date = input("Enter Billing Date (YYYY-MM-DD) [leave blank for today]: ")
            if not billing_date.strip():
                bill = Bill(bill_id, patient_id)
            else:
                bill = Bill(bill_id, patient_id, billing_date)
            result = bill.add()
            if result:
                bill.generate_invoice()
            else:
                print("Bill was not added. Invoice not generated.")
 
        elif choice == "2":
            Bill.view()
 
        elif choice == "3":
            bill_id = input("Enter Bill ID to update: ")
            patient_id = input("Enter New Patient ID: ")
            billing_date = input("Enter New Billing Date (YYYY-MM-DD) [leave blank for today]: ")
            if not billing_date.strip():
                bill = Bill(bill_id, patient_id)
            else:
                bill = Bill(bill_id, patient_id, billing_date)
            bill.update()
 
        elif choice == "4":
            bill_id = input("Enter Bill ID to delete: ")
            Bill.delete(bill_id)
 
        elif choice == "5":
            patient_id = input("Enter Patient ID to compute total billing: ")
            total = compute_total_billing(patient_id)
            if total is not None:
                print(f"Total bill for patient {patient_id}: {total}")
 
        elif choice == "6":
            print("Generate Invoice Options:")
            print("1. By Bill ID")
            print("2. By Patient ID")
            invoice_choice = input("Select an option: ")
            if invoice_choice == "1":
                bill_id = input("Enter Bill ID to generate invoice: ")
                # Fetch patient_id and billing_date from DB
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
                    
            elif invoice_choice == "2":
                patient_id = input("Enter Patient ID to generate invoice: ")
                from db_config import get_connection
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT bill_id, billing_date FROM billing WHERE patient_id=%s", (patient_id,))
                bills = cursor.fetchall()
                if not bills:
                    print("No bills found for this patient.")
                elif len(bills) == 1:
                    bill_id = bills[0]['bill_id']
                    billing_date = bills[0]['billing_date']
                    bill = Bill(bill_id, patient_id, billing_date)
                    bill.generate_invoice()
                else:
                    print("Multiple bills found for this patient:")
                    for idx, b in enumerate(bills):
                        print(f"{idx+1}. Bill ID: {b['bill_id']}, Date: {b['billing_date']}")
                    user_input = input("Select bill number to generate invoice: ").strip()
                    if user_input.isdigit():
                        selection = int(user_input) - 1
                        if 0 <= selection < len(bills):
                            selected_bill = bills[selection]
                            bill = Bill(selected_bill['bill_id'], patient_id, selected_bill['billing_date'])
                            bill.generate_invoice()
                            # EXIT after generating invoice!
                            return  # or break if inside a loop
                        else:
                            print("Invalid selection.")
                    else:
                        print("Invalid input. Please enter a number.")
                cursor.close()
                conn.close()
            else:
                print("Invalid option for invoice generation.")
 
        elif choice == "7":
            break
 
        else:
            print("Invalid Choice. Please try again.")

def export_menu():
    while True:
        print("\n=== Export Management ===")
        print("1. Export Billing Summary to CSV")
        print("2. Export Appointment Summary to CSV")
        print("3. Back to Main Menu")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            filename = input("Enter filename for billing summary (default: billing_summary.csv): ").strip() or "billing_summary.csv"
            if not filename.lower().endswith(".csv"):
                filename += ".csv"
            Bill.export_billing_summary_to_csv(filename)
            
        elif choice == '2':
            filename = input("Enter filename for appointment summary (default: appointment_summary.csv): ").strip() or "appointment_summary.csv"
            if not filename.lower().endswith(".csv"):
                filename += ".csv"
            Appointment.export_appointment_summary_to_csv(filename)
            
        elif choice == '3':
            break
        else:
            print("Invalid choice.")

def main_menu():
    while True:
        print("\n=== Hospital Management CLI ===")
        print("1. Patient Management")
        print("2. Doctor Management")
        print("3. Service Management")
        print("4. Appointment Management")
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
