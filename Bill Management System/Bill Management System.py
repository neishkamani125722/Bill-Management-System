import json
import random
from datetime import datetime, timedelta

BILL_FILE = "bills.json"
RECYCLE_FILE = "recycle_bin.json"

# ================= LOAD DATA =================
try:
    with open(BILL_FILE, "r") as f:
        bills = json.load(f)
except:
    bills = []

try:
    with open(RECYCLE_FILE, "r") as f:
        recycle_bin = json.load(f)
except:
    recycle_bin = []

# ================= SAVE =================
def save():
    with open(BILL_FILE, "w") as f:
        json.dump(bills, f, indent=4)

def save_recycle():
    with open(RECYCLE_FILE, "w") as f:
        json.dump(recycle_bin, f, indent=4)

# ================= RECEIPT =================
def print_receipt(b):
    print("\n================ ELECTRICITY BILL RECEIPT ================")
    print(f"Bill No      : {b['bill_number']}")
    print(f"Bill Date    : {b['bill_date']}  {b['bill_time']}")
    print(f"Due Date     : {b['due_date']}")
    print("-----------------------------------------------------------")
    print(f"Customer No  : {b['customer_number']}")
    print(f"Name         : {b['name']}")
    print(f"Address      : {b['address']}")
    print(f"Mobile       : {b['mobile']}")
    print("-----------------------------------------------------------")
    print(f"Previous Rdg : {b['previous_reading']}")
    print(f"Current Rdg  : {b['current_reading']}")
    print(f"Units Used   : {b['units']}")
    print("-----------------------------------------------------------")
    print(f"Energy Charge: ₹{b['energy_charge']}")
    print(f"Solar Disc   : -₹{b['solar_discount']}")
    print(f"Fixed Charge : ₹{b['fixed_charge']}")
    print(f"Late Fine    : ₹{b['late_fine']}")
    print(f"GST (18%)    : ₹{b['gst']}")
    print("-----------------------------------------------------------")
    print(f"TOTAL BILL   : ₹{b['total_bill']}")
    print(f"Payment Mode : {b['payment_method']}")
    print("===========================================================")
    print("⚠ Please Pay Before Due Date To Avoid Late Fine")
    print("🙏 Thank You For Using Our Electricity Service 🙏")
    print("===========================================================")

# ================= CREATE =================
def create_bill():
    print("\n=========== CREATE BILL ===========")

    customer_number = int(input("Enter Customer Number: "))
    name = input("Enter Name: ")
    address = input("Enter Address: ")
    mobile = input("Enter Mobile: ")

    prev = float(input("Enter Previous Reading: "))
    curr = float(input("Enter Current Reading: "))

    units = curr - prev

    if units <= 100:
        energy = units * 3
    elif units <= 300:
        energy = (100*3) + (units-100)*5
    else:
        energy = (100*3) + (200*5) + (units-300)*8

    solar = input("Solar Panel? (yes/no): ").lower()
    solar_discount = energy * 0.10 if solar == "yes" else 0

    late = input("Late Payment? (yes/no): ").lower()
    late_fine = 100 if late == "yes" else 0

    fixed = 150
    subtotal = energy - solar_discount + fixed + late_fine
    gst = subtotal * 0.18
    total = subtotal + gst

    bill = {
        "bill_number": random.randint(10000,99999),
        "customer_number": customer_number,
        "bill_date": datetime.now().strftime("%d/%m/%y"),
        "bill_time": datetime.now().strftime("%I:%M:%S %p"),
        "due_date": (datetime.now()+timedelta(days=random.randint(10,12))).strftime("%d/%m/%y"),
        "name": name,
        "address": address,
        "mobile": mobile,
        "previous_reading": prev,
        "current_reading": curr,
        "units": units,
        "energy_charge": round(energy,2),
        "solar_discount": round(solar_discount,2),
        "fixed_charge": fixed,
        "late_fine": late_fine,
        "gst": round(gst,2),
        "total_bill": round(total,2),
        "payment_method": input("Payment Method (Cash/UPI/Card): ")
    }

    bills.append(bill)
    save()
    print_receipt(bill)

# ================= VIEW =================
def view_all():
    for b in bills:
        print(f"{b['customer_number']} | {b['name']} | ₹{b['total_bill']}")

# ================= SEARCH =================
def search():
    num = input("Enter Customer Number: ")
    found = False

    for b in bills:
        if str(b["customer_number"]) == num:
            print_receipt(b)
            found = True

    if not found:
        print("❌ No Bills Found!")

# ================= EDIT =================
def edit():
    num = input("Enter Customer Number: ")

    for b in bills:
        if str(b["customer_number"]) == num:
            b["name"] = input("New Name: ") or b["name"]
            b["address"] = input("New Address: ") or b["address"]
            b["mobile"] = input("New Mobile: ") or b["mobile"]
            save()
            print("✅ Updated Successfully!")
            return

    print("❌ Not Found")

# ================= DELETE =================
def delete_bill():
    bill_no = input("Enter Bill Number: ")

    for b in bills[:]:
        if str(b["bill_number"]) == bill_no:
            recycle_bin.append(b)
            bills.remove(b)
            save()
            save_recycle()
            print("♻ Bill moved to Recycle Bin!")
            return

    print("❌ Bill not found!")

# ================= RECYCLE BIN =================
def recycle_menu():
    if not recycle_bin:
        print("Recycle Bin Empty!")
        return

    print("\n=========== RECYCLE BIN ===========")
    for b in recycle_bin:
        print(f"{b['bill_number']} | ₹{b['total_bill']}")

    ch = input("1 Restore  2 Permanent Delete: ")

    if ch == "1":
        bill_no = input("Enter Bill Number: ")

        for b in recycle_bin:
            if str(b["bill_number"]) == bill_no:
                bills.append(b)
                recycle_bin.remove(b)
                save()
                save_recycle()
                print("✅ Restored")
                return

    elif ch == "2":
        bill_no = input("Enter Bill Number: ")

        for b in recycle_bin:
            if str(b["bill_number"]) == bill_no:
                recycle_bin.remove(b)
                save_recycle()
                print("🗑 Permanently Deleted")
                return

    print("❌ Not Found")

# ================= MAIN =================
while True:
    print("\n=========== ELECTRICITY BILL MANAGEMENT SYSTEM ===========")
    print("1. Create Bill")
    print("2. View All Bills")
    print("3. Search Bill")
    print("4. Edit Bill")
    print("5. Delete Bill")
    print("6. Recycle Bin")
    print("7. Exit")

    ch = input("Choice: ")

    if ch == "1":
        create_bill()
    elif ch == "2":
        view_all()
    elif ch == "3":
        search()
    elif ch == "4":
        edit()
    elif ch == "5":
        delete_bill()
    elif ch == "6":
        recycle_menu()
    elif ch == "7":
        print("System Closed Successfully!")
        break
    else:
        print("Invalid Choice!")
