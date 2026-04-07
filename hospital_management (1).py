# ─────────────────────────────────────────────────────────────
#  Team 8 – Hospital Management System
#  Topic: Maintain patient records, schedule appointments with
#         doctors, generate bills, and manage basic hospital
#         operations efficiently.
#
#  Run:  python hospital_management.py
#  Requires: Python 3.6+ (no extra libraries needed)
# ─────────────────────────────────────────────────────────────

import sqlite3
import os
from datetime import date, datetime

DB_FILE = "hospital.db"

# ── Pre-registered doctors ─────────────────────────────────────
DOCTORS = [
    (1, "Dr. Priya Sharma",  "Cardiology"),
    (2, "Dr. Arjun Mehta",   "Neurology"),
    (3, "Dr. Sunita Rao",    "Orthopedics"),
    (4, "Dr. Vikram Nair",   "General Medicine"),
    (5, "Dr. Kavya Iyer",    "Pediatrics"),
    (6, "Dr. Ramesh Pillai", "Gynecology"),
    (7, "Dr. Suresh Gupta",  "Oncology"),
    (8, "Dr. Anjali Verma",  "ENT"),
]

# ══════════════════════════════════════════════════════════════
#  DATABASE SETUP
# ══════════════════════════════════════════════════════════════

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            age      INTEGER NOT NULL,
            gender   TEXT    NOT NULL,
            blood    TEXT,
            contact  TEXT    NOT NULL,
            address  TEXT,
            status   TEXT    DEFAULT 'Admitted',
            created  TEXT    DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  INTEGER NOT NULL,
            doctor_id   INTEGER NOT NULL,
            doctor_name TEXT    NOT NULL,
            specialty   TEXT,
            appt_date   TEXT    NOT NULL,
            appt_time   TEXT,
            reason      TEXT,
            status      TEXT    DEFAULT 'Scheduled',
            created     TEXT    DEFAULT (date('now')),
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS bills (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  INTEGER NOT NULL,
            consult     REAL    DEFAULT 0,
            medicine    REAL    DEFAULT 0,
            lab         REAL    DEFAULT 0,
            room        REAL    DEFAULT 0,
            other       REAL    DEFAULT 0,
            total       REAL    DEFAULT 0,
            status      TEXT    DEFAULT 'Pending',
            notes       TEXT,
            issued      TEXT    DEFAULT (date('now')),
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );
    """)
    conn.commit()
    conn.close()

# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def hr(char="─", width=60):
    print(char * width)

def header(title):
    clear()
    hr("═")
    print(f"  🏥  MEDICORE — Hospital Management System")
    hr("═")
    print(f"  ▶  {title}")
    hr()

def pause():
    input("\n  Press Enter to continue...")

def inp(prompt, required=True):
    while True:
        val = input(f"  {prompt}: ").strip()
        if val or not required:
            return val
        print("  ⚠  This field is required.")

def inp_int(prompt, lo=0, hi=9999, required=True):
    while True:
        raw = inp(prompt, required)
        if not raw and not required:
            return None
        try:
            v = int(raw)
            if lo <= v <= hi:
                return v
            print(f"  ⚠  Enter a number between {lo} and {hi}.")
        except ValueError:
            print("  ⚠  Please enter a valid number.")

def inp_float(prompt, required=False):
    while True:
        raw = inp(prompt, required)
        if not raw:
            return 0.0
        try:
            return float(raw)
        except ValueError:
            print("  ⚠  Please enter a valid amount.")

def choose(prompt, options):
    """Show numbered list and return chosen index (0-based)."""
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        raw = inp(prompt)
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx
            print(f"  ⚠  Enter a number between 1 and {len(options)}.")
        except ValueError:
            print("  ⚠  Invalid input.")

def select_patient(conn, label="Select Patient"):
    """List patients and return chosen patient row."""
    rows = conn.execute("SELECT id, name, contact FROM patients ORDER BY id").fetchall()
    if not rows:
        print("\n  ⚠  No patients registered yet.")
        return None
    print(f"\n  {label}:")
    for r in rows:
        print(f"    [{r['id']:>3}]  {r['name']:<25}  📞 {r['contact']}")
    pid = inp_int("  Enter Patient ID", lo=1)
    p = conn.execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone()
    if not p:
        print("  ⚠  Patient ID not found.")
        return None
    return p

# ══════════════════════════════════════════════════════════════
#  1. PATIENT MANAGEMENT
# ══════════════════════════════════════════════════════════════

def add_patient():
    header("Add New Patient")
    name    = inp("Full Name")
    age     = inp_int("Age", lo=0, hi=130)
    print("\n  Gender:")
    gender  = ["Male","Female","Other"][choose("Select", ["Male","Female","Other"])]
    print("\n  Blood Group:")
    blood   = ["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"][
        choose("Select", ["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"])
    ]
    contact = inp("Contact Number")
    address = inp("Address", required=False)
    print("\n  Patient Status:")
    status  = ["Admitted","Observation","Critical","Discharged"][
        choose("Select", ["Admitted","Observation","Critical","Discharged"])
    ]

    conn = get_conn()
    conn.execute(
        "INSERT INTO patients(name,age,gender,blood,contact,address,status) VALUES(?,?,?,?,?,?,?)",
        (name, age, gender, blood, contact, address, status)
    )
    conn.commit()
    pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    print(f"\n  ✅  Patient registered successfully!  ID: P-{pid:05d}")
    pause()

def view_patients():
    header("All Patient Records")
    conn   = get_conn()
    rows   = conn.execute("SELECT * FROM patients ORDER BY id DESC").fetchall()
    conn.close()
    if not rows:
        print("\n  No patients registered yet.")
        pause()
        return
    print(f"\n  {'ID':<8} {'Name':<22} {'Age':>4}  {'Gender':<8} {'Blood':<6} {'Status':<14} {'Contact'}")
    hr()
    for r in rows:
        print(f"  P-{r['id']:05d}  {r['name']:<22} {r['age']:>4}  {r['gender']:<8} {r['blood'] or '—':<6} {r['status']:<14} {r['contact']}")
    pause()

def search_patient():
    header("Search Patient")
    q    = inp("Enter name or contact number")
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM patients WHERE name LIKE ? OR contact LIKE ?",
        (f"%{q}%", f"%{q}%")
    ).fetchall()
    conn.close()
    if not rows:
        print("\n  No matching patients found.")
    else:
        print(f"\n  Found {len(rows)} record(s):\n")
        for r in rows:
            print(f"  ┌── P-{r['id']:05d}  {r['name']} ({r['age']} yrs, {r['gender']}, {r['blood'] or 'N/A'})")
            print(f"  │   Status : {r['status']}")
            print(f"  │   Contact : {r['contact']}")
            print(f"  └   Address : {r['address'] or '—'}")
            print()
    pause()

def update_patient_status():
    header("Update Patient Status")
    conn = get_conn()
    p    = select_patient(conn)
    if not p:
        conn.close(); pause(); return
    print(f"\n  Current Status: {p['status']}")
    print("\n  New Status:")
    status = ["Admitted","Observation","Critical","Discharged"][
        choose("Select", ["Admitted","Observation","Critical","Discharged"])
    ]
    conn.execute("UPDATE patients SET status=? WHERE id=?", (status, p["id"]))
    conn.commit()
    conn.close()
    print(f"\n  ✅  Status updated to '{status}'.")
    pause()

def patient_menu():
    while True:
        header("Patient Management")
        print("  1. Register New Patient")
        print("  2. View All Patients")
        print("  3. Search Patient")
        print("  4. Update Patient Status")
        print("  0. Back to Main Menu")
        hr()
        ch = inp("Choice")
        if ch == "1": add_patient()
        elif ch == "2": view_patients()
        elif ch == "3": search_patient()
        elif ch == "4": update_patient_status()
        elif ch == "0": break
        else: print("  ⚠  Invalid choice.")

# ══════════════════════════════════════════════════════════════
#  2. APPOINTMENT MANAGEMENT
# ══════════════════════════════════════════════════════════════

def book_appointment():
    header("Book Appointment")
    conn = get_conn()
    p    = select_patient(conn, "Select Patient for Appointment")
    if not p:
        conn.close(); pause(); return

    print(f"\n  Patient: {p['name']} (P-{p['id']:05d})")
    print("\n  Available Doctors:")
    for doc in DOCTORS:
        print(f"    {doc[0]}. {doc[1]:<28}  🏥 {doc[2]}")
    doc_idx = choose("\n  Select Doctor Number", [f"{d[1]} – {d[2]}" for d in DOCTORS])
    doctor  = DOCTORS[doc_idx]

    appt_date = inp("Appointment Date (YYYY-MM-DD)")
    appt_time = inp("Appointment Time (HH:MM, 24hr)", required=False)
    reason    = inp("Reason / Chief Complaint", required=False)

    conn.execute(
        "INSERT INTO appointments(patient_id,doctor_id,doctor_name,specialty,appt_date,appt_time,reason) VALUES(?,?,?,?,?,?,?)",
        (p["id"], doctor[0], doctor[1], doctor[2], appt_date, appt_time, reason)
    )
    conn.commit()
    conn.close()
    print(f"\n  ✅  Appointment scheduled!")
    print(f"      Patient : {p['name']}")
    print(f"      Doctor  : {doctor[1]} ({doctor[2]})")
    print(f"      Date    : {appt_date}  {appt_time or ''}")
    pause()

def view_appointments():
    header("All Appointments")
    conn = get_conn()
    rows = conn.execute("""
        SELECT a.*, p.name AS patient_name
        FROM appointments a
        JOIN patients p ON p.id = a.patient_id
        ORDER BY a.appt_date DESC, a.appt_time DESC
    """).fetchall()
    conn.close()
    if not rows:
        print("\n  No appointments booked yet.")
        pause()
        return
    print(f"\n  {'ID':<6} {'Patient':<22} {'Doctor':<26} {'Date':<12} {'Time':<7} {'Status'}")
    hr()
    for r in rows:
        print(f"  A-{r['id']:04d}  {r['patient_name']:<22} {r['doctor_name']:<26} {r['appt_date']:<12} {r['appt_time'] or '—':<7} {r['status']}")
    pause()

def update_appt_status():
    header("Update Appointment Status")
    conn  = get_conn()
    rows  = conn.execute("""
        SELECT a.id, p.name, a.doctor_name, a.appt_date, a.status
        FROM appointments a JOIN patients p ON p.id=a.patient_id
        ORDER BY a.id DESC
    """).fetchall()
    if not rows:
        print("\n  No appointments found.")
        conn.close(); pause(); return
    for r in rows:
        print(f"  [{r['id']:>4}]  {r['name']:<22}  {r['doctor_name']:<26}  {r['appt_date']}  [{r['status']}]")
    aid    = inp_int("\n  Enter Appointment ID", lo=1)
    status = ["Scheduled","Completed","Cancelled"][
        choose("  New Status", ["Scheduled","Completed","Cancelled"])
    ]
    conn.execute("UPDATE appointments SET status=? WHERE id=?", (status, aid))
    conn.commit()
    conn.close()
    print(f"\n  ✅  Appointment #{aid} status set to '{status}'.")
    pause()

def appointment_menu():
    while True:
        header("Appointment Management")
        print("  1. Book New Appointment")
        print("  2. View All Appointments")
        print("  3. Update Appointment Status")
        print("  0. Back to Main Menu")
        hr()
        ch = inp("Choice")
        if ch == "1": book_appointment()
        elif ch == "2": view_appointments()
        elif ch == "3": update_appt_status()
        elif ch == "0": break
        else: print("  ⚠  Invalid choice.")

# ══════════════════════════════════════════════════════════════
#  3. BILLING
# ══════════════════════════════════════════════════════════════

def generate_bill():
    header("Generate Patient Bill")
    conn = get_conn()
    p    = select_patient(conn, "Select Patient to Bill")
    if not p:
        conn.close(); pause(); return

    print(f"\n  Patient: {p['name']} (P-{p['id']:05d})")
    print("\n  Enter charges (press Enter to skip / set 0):\n")
    consult  = inp_float("  Consultation Fee    (₹)")
    medicine = inp_float("  Medicine Charges    (₹)")
    lab      = inp_float("  Lab / Test Charges  (₹)")
    room     = inp_float("  Room / Ward Charges (₹)")
    other    = inp_float("  Other Charges       (₹)")
    total    = consult + medicine + lab + room + other
    notes    = inp("  Description / Notes", required=False)
    print("\n  Payment Status:")
    status   = ["Pending","Paid","Partial","Waived"][
        choose("  Select", ["Pending","Paid","Partial","Waived"])
    ]

    conn.execute(
        "INSERT INTO bills(patient_id,consult,medicine,lab,room,other,total,status,notes) VALUES(?,?,?,?,?,?,?,?,?)",
        (p["id"], consult, medicine, lab, room, other, total, status, notes)
    )
    conn.commit()
    bid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()

    hr()
    print(f"  🧾  BILL RECEIPT — B-{bid:04d}")
    hr()
    print(f"  Patient     : {p['name']}")
    print(f"  Date        : {date.today()}")
    print(f"  Consultation: ₹ {consult:>10,.2f}")
    print(f"  Medicine    : ₹ {medicine:>10,.2f}")
    print(f"  Lab / Tests : ₹ {lab:>10,.2f}")
    print(f"  Room / Ward : ₹ {room:>10,.2f}")
    print(f"  Other       : ₹ {other:>10,.2f}")
    hr("-")
    print(f"  TOTAL       : ₹ {total:>10,.2f}")
    print(f"  Status      : {status}")
    hr()
    pause()

def view_bills():
    header("All Bills")
    conn = get_conn()
    rows = conn.execute("""
        SELECT b.*, p.name AS patient_name
        FROM bills b JOIN patients p ON p.id = b.patient_id
        ORDER BY b.id DESC
    """).fetchall()
    conn.close()
    if not rows:
        print("\n  No bills generated yet.")
        pause()
        return
    print(f"\n  {'ID':<7} {'Patient':<22} {'Total (₹)':>12}  {'Status':<10}  {'Date'}")
    hr()
    for r in rows:
        print(f"  B-{r['id']:04d}  {r['patient_name']:<22} {r['total']:>12,.2f}  {r['status']:<10}  {r['issued']}")
    pause()

def update_bill_status():
    header("Update Bill Payment Status")
    conn = get_conn()
    rows = conn.execute("""
        SELECT b.id, p.name, b.total, b.status
        FROM bills b JOIN patients p ON p.id=b.patient_id
        ORDER BY b.id DESC
    """).fetchall()
    if not rows:
        print("\n  No bills found.")
        conn.close(); pause(); return
    for r in rows:
        print(f"  [{r['id']:>4}]  {r['name']:<22}  ₹{r['total']:>10,.2f}  [{r['status']}]")
    bid    = inp_int("\n  Enter Bill ID", lo=1)
    status = ["Pending","Paid","Partial","Waived"][
        choose("  New Status", ["Pending","Paid","Partial","Waived"])
    ]
    conn.execute("UPDATE bills SET status=? WHERE id=?", (status, bid))
    conn.commit()
    conn.close()
    print(f"\n  ✅  Bill #{bid} status set to '{status}'.")
    pause()

def billing_menu():
    while True:
        header("Billing Management")
        print("  1. Generate New Bill")
        print("  2. View All Bills")
        print("  3. Update Bill Status")
        print("  0. Back to Main Menu")
        hr()
        ch = inp("Choice")
        if ch == "1": generate_bill()
        elif ch == "2": view_bills()
        elif ch == "3": update_bill_status()
        elif ch == "0": break
        else: print("  ⚠  Invalid choice.")

# ══════════════════════════════════════════════════════════════
#  4. HOSPITAL OPERATIONS — SUMMARY
# ══════════════════════════════════════════════════════════════

def hospital_summary():
    header("Hospital Operations Summary")
    conn = get_conn()

    total_p  = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    admitted = conn.execute("SELECT COUNT(*) FROM patients WHERE status='Admitted'").fetchone()[0]
    critical = conn.execute("SELECT COUNT(*) FROM patients WHERE status='Critical'").fetchone()[0]
    disc     = conn.execute("SELECT COUNT(*) FROM patients WHERE status='Discharged'").fetchone()[0]

    total_a  = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    sched    = conn.execute("SELECT COUNT(*) FROM appointments WHERE status='Scheduled'").fetchone()[0]
    done     = conn.execute("SELECT COUNT(*) FROM appointments WHERE status='Completed'").fetchone()[0]

    total_b  = conn.execute("SELECT COUNT(*) FROM bills").fetchone()[0]
    pending  = conn.execute("SELECT COUNT(*) FROM bills WHERE status='Pending'").fetchone()[0]
    paid     = conn.execute("SELECT COUNT(*) FROM bills WHERE status='Paid'").fetchone()[0]
    revenue  = conn.execute("SELECT COALESCE(SUM(total),0) FROM bills WHERE status='Paid'").fetchone()[0]
    pending_amt = conn.execute("SELECT COALESCE(SUM(total),0) FROM bills WHERE status='Pending'").fetchone()[0]
    conn.close()

    print(f"\n  📅  Date: {date.today()}")
    print()
    print("  ── PATIENTS ─────────────────────────────────")
    print(f"  Total Registered : {total_p}")
    print(f"  Currently Admitted: {admitted}")
    print(f"  Critical Cases   : {critical}")
    print(f"  Discharged       : {disc}")
    print()
    print("  ── APPOINTMENTS ─────────────────────────────")
    print(f"  Total Appointments: {total_a}")
    print(f"  Scheduled (Upcoming): {sched}")
    print(f"  Completed         : {done}")
    print()
    print("  ── BILLING ──────────────────────────────────")
    print(f"  Total Bills       : {total_b}")
    print(f"  Paid              : {paid}   (₹ {revenue:,.2f})")
    print(f"  Pending           : {pending}  (₹ {pending_amt:,.2f})")
    hr()
    pause()

def list_doctors():
    header("Registered Doctors")
    print(f"\n  {'ID':<5} {'Name':<30}  {'Specialty'}")
    hr()
    for d in DOCTORS:
        print(f"  {d[0]:<5} {d[1]:<30}  {d[2]}")
    pause()

def operations_menu():
    while True:
        header("Hospital Operations")
        print("  1. Hospital Summary Report")
        print("  2. View Registered Doctors")
        print("  0. Back to Main Menu")
        hr()
        ch = inp("Choice")
        if ch == "1": hospital_summary()
        elif ch == "2": list_doctors()
        elif ch == "0": break
        else: print("  ⚠  Invalid choice.")

# ══════════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════════

def main():
    init_db()
    while True:
        header("Main Menu")
        print("  1. 🧑‍🤝‍🧑  Patient Management")
        print("  2. 📅  Appointment Scheduling")
        print("  3. 💳  Billing")
        print("  4. 🏥  Hospital Operations & Reports")
        print("  0. 🚪  Exit")
        hr()
        ch = inp("Select option")
        if ch == "1":   patient_menu()
        elif ch == "2": appointment_menu()
        elif ch == "3": billing_menu()
        elif ch == "4": operations_menu()
        elif ch == "0":
            clear()
            print("\n  Goodbye! Stay healthy. 🏥\n")
            break
        else:
            print("  ⚠  Invalid option. Please try again.")

if __name__ == "__main__":
    main()
