import json
import random
import time
from datetime import datetime, timedelta
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
import winsound

BILL_FILE = "bills.json"
RECYCLE_FILE = "recycle.json"

# ================= LOAD =================
def load_file(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

bills = load_file(BILL_FILE)
recycle_bin = load_file(RECYCLE_FILE)

# ================= SAVE =================
def save():
    with open(BILL_FILE, "w") as f:
        json.dump(bills, f, indent=4)

def save_recycle():
    with open(RECYCLE_FILE, "w") as f:
        json.dump(recycle_bin, f, indent=4)

# ================= ₹ FORMAT =================
def format_rupee(amount):
    amount = int(amount)
    s = str(amount)
    if len(s) <= 3:
        return "₹" + s
    last3 = s[-3:]
    rest = s[:-3]
    rest = ",".join([rest[max(i-2,0):i] for i in range(len(rest), 0, -2)][::-1])
    return "₹" + rest + "," + last3

# ================= AUTO BILL NUMBER =================
def generate_bill_no():
    if not bills:
        return 10001
    return max(b["bill_no"] for b in bills) + 1

# ================= BILL LOGIC =================
def create_bill_gui_data(cno, name, phone, address, prev, curr, solar):
    if curr < prev:
        return "Error"

    units = curr - prev
    net_units = units - solar

    if net_units < 0:
        credit_amount = abs(net_units) * 4
        net_units = 0
        energy = 0
    else:
        credit_amount = 0
        if net_units <= 100:
            energy = net_units * 3
        elif net_units <= 300:
            energy = (100*3) + (net_units-100)*5
        else:
            energy = (100*3) + (200*5) + (net_units-300)*8

    fixed = 150
    gst = (energy + fixed - credit_amount) * 0.18
    total = energy + fixed + gst - credit_amount

    now = datetime.now()

    bill = {
        "bill_no": generate_bill_no(),
        "customer_no": cno,
        "name": name,
        "phone": phone,
        "address": address,
        "units": units,
        "solar_units": solar,
        "solar_price": 3,
        "net_units": net_units,
        "energy_charge": energy,
        "fixed_charge": fixed,
        "credit_amount": credit_amount,
        "gst": gst,
        "total": total,
        "date": now.strftime("%d/%m/%Y %I:%M %p"),
        "due_date": (now + timedelta(days=15)).strftime("%d/%m/%Y %I:%M %p")
    }

    bills.append(bill)
    save()
    return bill

# ================= RECEIPT =================
def receipt_popup(b):
    win = tk.Toplevel()
    win.title("🧾 Bill Receipt")
    win.geometry("500x600")

    text = tk.Text(win, font=("Consolas", 12))
    text.pack(fill="both", expand=True)

    receipt = f"""
══════════════════════════════════════
           ⚡ ELECTRICITY BILL
══════════════════════════════════════
Bill No       : {b['bill_no']}
Bill Date     : {b['date']}
Due Date      : {b['due_date']}
══════════════════════════════════════
Customer No   : {b['customer_no']}
Name          : {b['name']}
Phone         : {b['phone']}
Address       : {b['address']}
══════════════════════════════════════
Units Used    : {b['units']}
Solar Units   : {b['solar_units']} @ ₹{b['solar_price']}
Net Units     : {b['net_units']}
Energy Charge : {format_rupee(b['energy_charge'])}
Fixed Charge  : {format_rupee(b['fixed_charge'])}
"""

    if b['credit_amount'] > 0:
        receipt += f"Credit Amount : -{format_rupee(b['credit_amount'])}\n"

    receipt += f"""GST (18%)     : {format_rupee(b['gst'])}
══════════════════════════════════════
TOTAL BILL    : {format_rupee(b['total'])}
══════════════════════════════════════
"""

    text.insert("end", receipt)

# ================= GUI =================
def start_gui():
    root = tk.Tk()
    root.title("⚡ Electricity Bill Software")
    root.state("zoomed")
    root.configure(bg="#0d1117")

    def clear():
        for w in root.winfo_children():
            w.destroy()

    def title(text):
        tk.Label(root, text=text, font=("Segoe UI", 28, "bold"),
                 fg="cyan", bg="#0d1117").pack(pady=20)

    def btn(text, cmd):
        tk.Button(root, text=text, width=30, height=2,
                  font=("Segoe UI", 13, "bold"),
                  bg="#161b22", fg="white",
                  command=cmd).pack(pady=10)

    def create_gui():
        clear()
        title("CREATE BILL")

        entries = {}

        tk.Label(root, text="--- Customer Details ---", fg="cyan", bg="#0d1117").pack()
        for f in ["Customer No","Name","Phone","Address"]:
            tk.Label(root,text=f,bg="#0d1117",fg="white").pack()
            e=tk.Entry(root); e.pack()
            entries[f]=e

        tk.Label(root, text="--- Meter Details ---", fg="cyan", bg="#0d1117").pack()
        for f in ["Prev","Curr","Solar"]:
            tk.Label(root,text=f,bg="#0d1117",fg="white").pack()
            e=tk.Entry(root); e.pack()
            entries[f]=e

        def submit():
            try:
                prev = float(entries["Prev"].get())
                curr = float(entries["Curr"].get())
                solar = float(entries["Solar"].get())

                if prev < 0 or curr < 0 or solar < 0:
                    messagebox.showerror("Error", "You can not insert any minus value")
                    return

                bill = create_bill_gui_data(
                    int(entries["Customer No"].get()),
                    entries["Name"].get(),
                    entries["Phone"].get(),
                    entries["Address"].get(),
                    prev,
                    curr,
                    solar
                )

                if isinstance(bill, dict):
                    receipt_popup(bill)

            except:
                messagebox.showerror("Error", "Invalid Input")

        btn("Generate", submit)
        btn("Back", dashboard)

    def view_gui():
        clear()
        title("ALL BILLS")

        box=tk.Listbox(root)
        box.pack(fill="both", expand=True)

        for b in bills:
            box.insert("end", f"{b['bill_no']} | {b['customer_no']} | {b['name']} | {format_rupee(b['total'])} | {b['date']}")

        def show():
            try:
                i=box.curselection()[0]
                receipt_popup(bills[i])
            except:
                pass

        btn("View Bill", show)
        btn("Back", dashboard)

    # ================= UPDATED SEARCH =================
    def search_gui():
        clear()
        title("SEARCH")

        tk.Label(root,text="Enter Customer Number",bg="#0d1117",fg="white").pack()
        e=tk.Entry(root); e.pack()

        def do():
            results=[b for b in bills if str(b["customer_no"])==e.get()]

            if not results:
                messagebox.showerror("Error","No bills found")
                return

            win=tk.Toplevel()
            win.title("Search Results")

            box=tk.Listbox(win, font=("Consolas", 12))
            box.pack(fill="both", expand=True)

            box.insert("end", f"{'Bill':<6} {'CustNo':<8} {'Name':<10} {'Total':>10} {'Date & Time':<20}")
            box.insert("end", "-"*80)

            for b in results:
                box.insert("end",
                    f"{b['bill_no']:<6} {b['customer_no']:<8} {b['name']:<10} {format_rupee(b['total']):>10} {b['date']}")

            def show_full():
                try:
                    i=box.curselection()[0]-2
                    if i>=0:
                        receipt_popup(results[i])
                except:
                    messagebox.showerror("Error","Select a bill")

            tk.Button(win,text="View Full Bill",command=show_full).pack()

        btn("Search", do)
        btn("Back", dashboard)

    # ================= EDIT BILL =================
    def edit_gui():
        clear()
        title("EDIT CUSTOMER")

        tk.Label(root, text="Enter Customer Number", bg="#0d1117", fg="white").pack()
        e = tk.Entry(root)
        e.pack()

        tk.Label(root, text="New Name", bg="#0d1117", fg="white").pack()
        name_e = tk.Entry(root)
        name_e.pack()

        tk.Label(root, text="New Phone", bg="#0d1117", fg="white").pack()
        phone_e = tk.Entry(root)
        phone_e.pack()

        tk.Label(root, text="New Address", bg="#0d1117", fg="white").pack()
        addr_e = tk.Entry(root)
        addr_e.pack()

        def update():
            cust_no = e.get()
            found = False

            for b in bills:
                if str(b["customer_no"]) == cust_no:
                    if name_e.get():
                        b["name"] = name_e.get()
                    if phone_e.get():
                        b["phone"] = phone_e.get()
                    if addr_e.get():
                        b["address"] = addr_e.get()
                    found = True

            if found:
                save()
                messagebox.showinfo("Done", "All bills updated for this customer")
            else:
                messagebox.showerror("Error", "Customer not found")

        btn("Update", update)
        btn("Back", dashboard)

    def delete_gui():
        clear()
        title("DELETE BILL")

        tk.Label(root,text="Enter Bill Number",bg="#0d1117",fg="white").pack()
        e=tk.Entry(root); e.pack()

        def do():
            for b in bills:
                if str(b["bill_no"])==e.get():
                    bills.remove(b)
                    recycle_bin.append(b)
                    save(); save_recycle()
                    messagebox.showinfo("Done","Deleted")
                    return

        btn("Delete", do)
        btn("Back", dashboard)

    def recycle_gui():
        clear()
        title("RECYCLE BIN")

        box=tk.Listbox(root)
        box.pack(fill="both", expand=True)

        for b in recycle_bin:
            box.insert("end", f"{b['bill_no']} {b['name']} {format_rupee(b['total'])} {b['date']}")

        def recover():
            try:
                i=box.curselection()[0]
                bills.append(recycle_bin[i])
                recycle_bin.pop(i)
                save(); save_recycle()
                messagebox.showinfo("Done","Bill Recovered")
            except:
                pass

        def delete_perm():
            try:
                i=box.curselection()[0]
                recycle_bin.pop(i)
                save_recycle()
                messagebox.showinfo("Done","Bill Deleted")
            except:
                pass

        btn("Recover", recover)
        btn("Delete Permanently", delete_perm)
        btn("Back", dashboard)

    def graphs_gui():
        clear()
        title("DATA VISUALIZATION")

        btn("Bar Graph", bar_graph)
        btn("Pie Chart", pie_chart)
        btn("Back", dashboard)

    def bar_graph():
        plt.figure()
        plt.bar(["Electricity","Solar"],
                [sum(b['net_units'] for b in bills),
                 sum(b['solar_units'] for b in bills)])
        plt.show()

    def pie_chart():
        plt.figure()
        plt.pie(
            [sum(b['energy_charge'] for b in bills),
             sum(b['fixed_charge'] for b in bills),
             sum(b['gst'] for b in bills)],
            labels=["Energy","Fixed","GST"],
            autopct='%1.1f%%'
        )
        plt.show()

    def dashboard():
        clear()
        title("⚡ BILL DASHBOARD")
        btn("Create Bill", create_gui)
        btn("View Bills", view_gui)
        btn("Search Bill", search_gui)
        btn("Edit Bill", edit_gui)
        btn("Delete Bill", delete_gui)
        btn("Recycle Bin", recycle_gui)
        btn("Graphs", graphs_gui)
        btn("Exit", root.destroy)

    dashboard()
    root.mainloop()

start_gui()
