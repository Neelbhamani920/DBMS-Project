"""
Hospital Management System
Tkinter UI — connects to MySQL via db_config in database.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import mysql.connector
from datetime import datetime

# ── DB connection ──────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",   
    "database": "hospital_db"
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

# ── Colour palette & fonts ─────────────────────────────────────────────────────
BG        = "#0f1923"   # deep navy
PANEL     = "#162030"   # card bg
ACCENT    = "#00c9a7"   # teal
ACCENT2   = "#e63946"   # red for alerts
TEXT      = "#e8f4f8"
SUBTEXT   = "#8ab4c4"
BORDER    = "#1e3448"
ENTRY_BG  = "#1a2e42"
BTN_BG    = "#00c9a7"
BTN_FG    = "#0f1923"
BTN_HOV   = "#00a88d"
ROW_ALT   = "#1a2e42"

FONT_TITLE  = ("Helvetica", 22, "bold")
FONT_HEAD   = ("Helvetica", 13, "bold")
FONT_LABEL  = ("Helvetica", 10)
FONT_SMALL  = ("Helvetica", 9)
FONT_BTN    = ("Helvetica", 10, "bold")
FONT_ENTRY  = ("Helvetica", 10)


# ── Helper widgets ─────────────────────────────────────────────────────────────
def make_label(parent, text, fg=TEXT, font_=FONT_LABEL, bg=PANEL, **kw):
    return tk.Label(parent, text=text, fg=fg, bg=bg,
                    font=font_, **kw)

def make_entry(parent, width=28, **kw):
    e = tk.Entry(parent, width=width, bg=ENTRY_BG, fg=TEXT,
                 insertbackground=ACCENT, relief="flat",
                 font=FONT_ENTRY, **kw)
    return e

def make_btn(parent, text, cmd, bg=BTN_BG, fg=BTN_FG, width=14):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=bg, fg=fg, font=FONT_BTN,
                  relief="flat", cursor="hand2",
                  activebackground=BTN_HOV, activeforeground=BTN_FG,
                  width=width, pady=6)
    b.bind("<Enter>", lambda e: b.config(bg=BTN_HOV))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

def separator(parent, color=BORDER):
    return tk.Frame(parent, bg=color, height=1)

def card(parent, **kw):
    f = tk.Frame(parent, bg=PANEL, bd=0, **kw)
    return f

def section_title(parent, text):
    f = tk.Frame(parent, bg=PANEL)
    tk.Label(f, text=text, fg=ACCENT, bg=PANEL,
             font=FONT_HEAD).pack(side="left")
    tk.Frame(f, bg=ACCENT, height=2, width=200).pack(
        side="left", padx=(10, 0), pady=8)
    return f

def styled_tree(parent, columns, headings, height=10, col_widths=None):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Hospital.Treeview",
                    background=PANEL, foreground=TEXT,
                    fieldbackground=PANEL, rowheight=28,
                    font=FONT_SMALL, borderwidth=0)
    style.configure("Hospital.Treeview.Heading",
                    background=ENTRY_BG, foreground=ACCENT,
                    font=("Helvetica", 9, "bold"), relief="flat")
    style.map("Hospital.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", BG)])

    # outer frame holds tree + both scrollbars
    frame = tk.Frame(parent, bg=BG)

    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        height=height, style="Hospital.Treeview")

    # per-column widths — caller can override via col_widths dict
    default_w = col_widths or {}
    for col, head in zip(columns, headings):
        w = default_w.get(col, 100)
        tree.heading(col, text=head)
        tree.column(col, anchor="center", width=w, minwidth=60, stretch=True)

    # vertical scrollbar
    vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
    # horizontal scrollbar
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid( row=0, column=1, sticky="ns")
    hsb.grid( row=1, column=0, sticky="ew")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    return frame, tree


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — PATIENTS
# ══════════════════════════════════════════════════════════════════════════════
class PatientTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()
        self.load_patients()

    def _build(self):
        # ── left form ─────────────────────────────────────────────────────────
        left = card(self)
        left.pack(side="left", fill="y", padx=(16,8), pady=16)

        section_title(left, "Patient Registration").pack(
            anchor="w", padx=16, pady=(16,8))

        fields = [
            ("Full Name",       "name"),
            ("Date of Birth",   "dob"),
            ("Blood Group",     "blood"),
            ("Phone",           "phone"),
            ("Emergency Contact","emg"),
            ("Address",         "addr"),
        ]
        self.vars = {}
        for label, key in fields:
            r = tk.Frame(left, bg=PANEL)
            r.pack(fill="x", padx=16, pady=4)
            make_label(r, label, fg=SUBTEXT).pack(anchor="w")
            v = tk.StringVar()
            self.vars[key] = v
            make_entry(r, textvariable=v).pack(fill="x", pady=2)

        separator(left).pack(fill="x", padx=16, pady=10)

        # gender
        r = tk.Frame(left, bg=PANEL)
        r.pack(fill="x", padx=16, pady=4)
        make_label(r, "Gender", fg=SUBTEXT).pack(anchor="w")
        self.gender = tk.StringVar(value="Male")
        for g in ("Male", "Female", "Other"):
            tk.Radiobutton(r, text=g, variable=self.gender, value=g,
                           bg=PANEL, fg=TEXT, selectcolor=ENTRY_BG,
                           activebackground=PANEL, font=FONT_LABEL).pack(
                               side="left", padx=4)

        separator(left).pack(fill="x", padx=16, pady=10)

        btn_row = tk.Frame(left, bg=PANEL)
        btn_row.pack(padx=16, pady=8)
        make_btn(btn_row, "+ Add Patient",   self.add_patient).pack(
            side="left", padx=4)
        make_btn(btn_row, "- Delete",        self.delete_patient,
                 bg=ACCENT2, fg=TEXT, width=10).pack(side="left", padx=4)
        make_btn(btn_row, "Clear",           self.clear_form,
                 bg=BORDER, fg=TEXT, width=8).pack(side="left", padx=4)

        # ── right table ───────────────────────────────────────────────────────
        right = card(self)
        right.pack(side="left", fill="both", expand=True,
                   padx=(8,16), pady=16)

        top = tk.Frame(right, bg=PANEL)
        top.pack(fill="x", padx=16, pady=(16,4))
        section_title(top, "All Patients").pack(side="left")

        # search
        self.search_var = tk.StringVar()
        se = make_entry(top, textvariable=self.search_var, width=20)
        se.pack(side="right", padx=4)
        make_label(top, "Search:", fg=SUBTEXT, bg=PANEL).pack(
            side="right")
        self.search_var.trace("w", lambda *_: self.load_patients())

        cols  = ("id","name","dob","blood","gender","phone","emg")
        heads = ("ID","Name","DOB","Blood","Gender","Phone","Emergency Contact")
        widths = {"id":50,"name":150,"dob":100,"blood":70,"gender":80,"phone":120,"emg":140}
        tf, self.tree = styled_tree(right, cols, heads, height=18, col_widths=widths)
        tf.pack(fill="both", expand=True, padx=16, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ── CRUD ──────────────────────────────────────────────────────────────────
    def add_patient(self):
        v = {k: self.vars[k].get().strip() for k in self.vars}
        if not v["name"] or not v["dob"]:
            messagebox.showwarning("Missing", "Name and DOB are required.")
            return
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute("""
                INSERT INTO Patients
                (name, dob, blood_group, gender, phone, emergency_contact, address)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (v["name"], v["dob"], v["blood"], self.gender.get(),
                  v["phone"], v["emg"], v["addr"]))
            conn.commit()
            messagebox.showinfo("Success", "Patient added!")
            self.clear_form(); self.load_patients()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def delete_patient(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a patient.")
            return
        pid = self.tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm", f"Delete patient ID {pid}?"):
            return
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute("DELETE FROM Patients WHERE patient_id=%s", (pid,))
            conn.commit(); self.load_patients()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def load_patients(self):
        q = self.search_var.get().strip()
        try:
            conn = get_conn(); cur = conn.cursor()
            if q:
                cur.execute("""
                    SELECT patient_id,name,dob,blood_group,gender,phone,emergency_contact
                    FROM Patients WHERE name LIKE %s OR phone LIKE %s
                    ORDER BY patient_id
                """, (f"%{q}%", f"%{q}%"))
            else:
                cur.execute("""
                    SELECT patient_id,name,dob,blood_group,gender,phone,emergency_contact
                    FROM Patients ORDER BY patient_id
                """)
            rows = cur.fetchall()
            self.tree.delete(*self.tree.get_children())
            for i, row in enumerate(rows):
                tag = "alt" if i % 2 else ""
                self.tree.insert("", "end", values=row, tags=(tag,))
            self.tree.tag_configure("alt", background=ROW_ALT)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])["values"]
        keys = ["name","dob","blood","gender","phone","emg","addr"]
        mapping = {
            "name": vals[1], "dob": vals[2], "blood": vals[3],
            "phone": vals[5], "emg": vals[6], "addr": ""
        }
        for k, v in mapping.items():
            if k in self.vars:
                self.vars[k].set(v)
        self.gender.set(vals[4])

    def clear_form(self):
        for v in self.vars.values():
            v.set("")
        self.gender.set("Male")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — DOCTORS
# ══════════════════════════════════════════════════════════════════════════════
class DoctorTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()
        self.load_doctors()

    def _build(self):
        left = card(self)
        left.pack(side="left", fill="y", padx=(16,8), pady=16)

        section_title(left, "Add Doctor").pack(anchor="w", padx=16, pady=(16,8))

        fields = [
            ("Full Name",        "name"),
            ("Specialization",   "spec"),
            ("Department ID",    "dept"),
            ("Phone",            "phone"),
            ("Email",            "email"),
        ]
        self.vars = {}
        for label, key in fields:
            r = tk.Frame(left, bg=PANEL)
            r.pack(fill="x", padx=16, pady=4)
            make_label(r, label, fg=SUBTEXT).pack(anchor="w")
            v = tk.StringVar()
            self.vars[key] = v
            make_entry(r, textvariable=v).pack(fill="x", pady=2)

        separator(left).pack(fill="x", padx=16, pady=10)

        btn_row = tk.Frame(left, bg=PANEL)
        btn_row.pack(padx=16, pady=8)
        make_btn(btn_row, "+ Add Doctor", self.add_doctor).pack(
            side="left", padx=4)
        make_btn(btn_row, "- Delete",    self.delete_doctor,
                 bg=ACCENT2, fg=TEXT, width=10).pack(side="left", padx=4)

        right = card(self)
        right.pack(side="left", fill="both", expand=True,
                   padx=(8,16), pady=16)

        section_title(right, "Doctor Directory").pack(
            anchor="w", padx=16, pady=(16,8))

        cols  = ("id","name","spec","dept","phone","email")
        heads = ("ID","Name","Specialization","Dept ID","Phone","Email")
        widths = {"id":50,"name":150,"spec":140,"dept":70,"phone":110,"email":180}
        tf, self.tree = styled_tree(right, cols, heads, height=18, col_widths=widths)
        tf.pack(fill="both", expand=True, padx=16, pady=8)

    def add_doctor(self):
        v = {k: self.vars[k].get().strip() for k in self.vars}
        if not v["name"] or not v["spec"]:
            messagebox.showwarning("Missing", "Name and Specialization required.")
            return
        try:
            conn = get_conn(); cur = conn.cursor()
            dept = int(v["dept"]) if v["dept"] else None
            cur.execute("""
                INSERT INTO Doctors (name, specialization, dept_id, phone, email)
                VALUES (%s,%s,%s,%s,%s)
            """, (v["name"], v["spec"], dept, v["phone"], v["email"]))
            conn.commit()
            messagebox.showinfo("Success", "Doctor added!")
            for sv in self.vars.values(): sv.set("")
            self.load_doctors()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def delete_doctor(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a doctor first.")
            return
        did = self.tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm", f"Delete doctor ID {did}?"): return
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute("DELETE FROM Doctors WHERE doctor_id=%s", (did,))
            conn.commit(); self.load_doctors()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def load_doctors(self):
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute("""
                SELECT doctor_id,name,specialization,dept_id,phone,email
                FROM Doctors ORDER BY name
            """)
            rows = cur.fetchall()
            self.tree.delete(*self.tree.get_children())
            for i, row in enumerate(rows):
                tag = "alt" if i % 2 else ""
                self.tree.insert("", "end", values=row, tags=(tag,))
            self.tree.tag_configure("alt", background=ROW_ALT)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — APPOINTMENTS
# ══════════════════════════════════════════════════════════════════════════════
class AppointmentTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()
        self.load_appointments()

    def _build(self):
        left = card(self)
        left.pack(side="left", fill="y", padx=(16,8), pady=16)

        section_title(left, "Book Appointment").pack(
            anchor="w", padx=16, pady=(16,8))

        fields = [
            ("Patient ID",       "patient_id"),
            ("Doctor ID",        "doctor_id"),
            ("Date (YYYY-MM-DD)","date"),
            ("Time (HH:MM)",     "time"),
        ]
        self.vars = {}
        for label, key in fields:
            r = tk.Frame(left, bg=PANEL)
            r.pack(fill="x", padx=16, pady=4)
            make_label(r, label, fg=SUBTEXT).pack(anchor="w")
            v = tk.StringVar()
            self.vars[key] = v
            make_entry(r, textvariable=v).pack(fill="x", pady=2)

        r = tk.Frame(left, bg=PANEL)
        r.pack(fill="x", padx=16, pady=4)
        make_label(r, "Status", fg=SUBTEXT).pack(anchor="w")
        self.status = tk.StringVar(value="Scheduled")
        ttk.Combobox(r, textvariable=self.status,
                     values=["Scheduled","Completed","Cancelled"],
                     state="readonly", font=FONT_ENTRY, width=26).pack(
                         fill="x", pady=2)

        r2 = tk.Frame(left, bg=PANEL)
        r2.pack(fill="x", padx=16, pady=4)
        make_label(r2, "Notes", fg=SUBTEXT).pack(anchor="w")
        self.notes = tk.Text(r2, height=4, bg=ENTRY_BG, fg=TEXT,
                             insertbackground=ACCENT, font=FONT_ENTRY,
                             relief="flat", width=30)
        self.notes.pack(fill="x", pady=2)

        separator(left).pack(fill="x", padx=16, pady=10)

        btn_row = tk.Frame(left, bg=PANEL)
        btn_row.pack(padx=16, pady=8)
        make_btn(btn_row, "Book",     self.book).pack(side="left", padx=4)
        make_btn(btn_row, "Complete", self.mark_complete,
                 bg="#2d6a4f", fg=TEXT, width=12).pack(side="left", padx=4)
        make_btn(btn_row, "Cancel",   self.cancel_appt,
                 bg=ACCENT2, fg=TEXT, width=10).pack(side="left", padx=4)

        right = card(self)
        right.pack(side="left", fill="both", expand=True,
                   padx=(8,16), pady=16)

        section_title(right, "Appointments").pack(
            anchor="w", padx=16, pady=(16,8))

        cols  = ("id","patient","doctor","date","time","status")
        heads = ("Appt ID","Patient","Doctor","Date","Time","Status")
        widths = {"id":60,"patient":150,"doctor":150,"date":100,"time":80,"status":100}
        tf, self.tree = styled_tree(right, cols, heads, height=18, col_widths=widths)
        tf.pack(fill="both", expand=True, padx=16, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def book(self):
        v = {k: self.vars[k].get().strip() for k in self.vars}
        if not v["patient_id"] or not v["doctor_id"] or not v["date"]:
            messagebox.showwarning("Missing", "Patient, Doctor and Date are required.")
            return
        try:
            dt = f"{v['date']} {v['time']}:00"
            conn = get_conn(); cur = conn.cursor()
            cur.execute("""
                INSERT INTO Appointments
                (patient_id, doctor_id, scheduled_at, status, notes)
                VALUES (%s,%s,%s,%s,%s)
            """, (v["patient_id"], v["doctor_id"], dt,
                  self.status.get(), self.notes.get("1.0","end").strip()))
            conn.commit()
            messagebox.showinfo("Booked", "Appointment booked!")
            self.load_appointments()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def mark_complete(self):
        self._update_status("Completed")

    def cancel_appt(self):
        self._update_status("Cancelled")

    def _update_status(self, new_status):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select an appointment first.")
            return
        aid = self.tree.item(sel[0])["values"][0]
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute(
                "UPDATE Appointments SET status=%s WHERE appt_id=%s",
                (new_status, aid))
            conn.commit(); self.load_appointments()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def load_appointments(self):
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute("""
                SELECT a.appt_id,
                       p.name AS patient,
                       d.name AS doctor,
                       DATE(a.scheduled_at), TIME(a.scheduled_at),
                       a.status
                FROM Appointments a
                JOIN Patients p ON a.patient_id = p.patient_id
                JOIN Doctors  d ON a.doctor_id  = d.doctor_id
                ORDER BY a.scheduled_at DESC
            """)
            rows = cur.fetchall()
            self.tree.delete(*self.tree.get_children())
            for i, row in enumerate(rows):
                color = ""
                if row[5] == "Completed":   color = "done"
                elif row[5] == "Cancelled": color = "cancel"
                elif row[5] == "Scheduled": color = "sched"
                self.tree.insert("", "end", values=row, tags=(color,))
            self.tree.tag_configure("done",   foreground="#2d9e5f")
            self.tree.tag_configure("cancel", foreground=ACCENT2)
            self.tree.tag_configure("sched",  foreground=ACCENT)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])["values"]
        # fill in appt id for reference (read-only action)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — BEDS
# ══════════════════════════════════════════════════════════════════════════════
class BedTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()
        self.load_beds()

    def _build(self):
        left = card(self)
        left.pack(side="left", fill="y", padx=(16,8), pady=16)

        section_title(left, "Bed Management").pack(
            anchor="w", padx=16, pady=(16,8))

        fields = [("Ward", "ward"), ("Bed Number", "bed_no")]
        self.vars = {}
        for label, key in fields:
            r = tk.Frame(left, bg=PANEL)
            r.pack(fill="x", padx=16, pady=4)
            make_label(r, label, fg=SUBTEXT).pack(anchor="w")
            v = tk.StringVar()
            self.vars[key] = v
            make_entry(r, textvariable=v).pack(fill="x", pady=2)

        r = tk.Frame(left, bg=PANEL)
        r.pack(fill="x", padx=16, pady=4)
        make_label(r, "Type", fg=SUBTEXT).pack(anchor="w")
        self.bed_type = tk.StringVar(value="General")
        ttk.Combobox(r, textvariable=self.bed_type,
                     values=["General","ICU","Emergency","Private"],
                     state="readonly", font=FONT_ENTRY, width=26).pack(
                         fill="x", pady=2)

        separator(left).pack(fill="x", padx=16, pady=10)

        # stats
        self.stats_frame = tk.Frame(left, bg=PANEL)
        self.stats_frame.pack(fill="x", padx=16, pady=8)

        btn_row = tk.Frame(left, bg=PANEL)
        btn_row.pack(padx=16, pady=8)
        make_btn(btn_row, "+ Add Bed",  self.add_bed).pack(
            side="left", padx=4)
        make_btn(btn_row, "Free Bed",   self.free_bed,
                 bg="#2d6a4f", fg=TEXT, width=10).pack(side="left", padx=4)
        make_btn(btn_row, "Occupy",     self.occupy_bed,
                 bg=ACCENT2, fg=TEXT, width=10).pack(side="left", padx=4)

        right = card(self)
        right.pack(side="left", fill="both", expand=True,
                   padx=(8,16), pady=16)

        section_title(right, "Bed Availability").pack(
            anchor="w", padx=16, pady=(16,8))

        # filter
        filt = tk.Frame(right, bg=PANEL)
        filt.pack(fill="x", padx=16, pady=(0,8))
        make_label(filt, "Filter:", fg=SUBTEXT).pack(side="left")
        self.filter_var = tk.StringVar(value="All")
        for opt in ("All", "Free", "Occupied"):
            tk.Radiobutton(filt, text=opt, variable=self.filter_var,
                           value=opt, bg=PANEL, fg=TEXT,
                           selectcolor=ENTRY_BG, activebackground=PANEL,
                           font=FONT_LABEL,
                           command=self.load_beds).pack(side="left", padx=6)

        cols  = ("id","ward","bed_no","type","occupied")
        heads = ("Bed ID","Ward","Bed No","Type","Status")
        widths = {"id":60,"ward":120,"bed_no":80,"type":100,"occupied":100}
        tf, self.tree = styled_tree(right, cols, heads, height=18, col_widths=widths)
        tf.pack(fill="both", expand=True, padx=16, pady=8)

    def add_bed(self):
        v = {k: self.vars[k].get().strip() for k in self.vars}
        if not v["ward"] or not v["bed_no"]:
            messagebox.showwarning("Missing", "Ward and Bed Number required.")
            return
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute("""
                INSERT INTO Beds (ward, bed_number, type, is_occupied)
                VALUES (%s,%s,%s,0)
            """, (v["ward"], v["bed_no"], self.bed_type.get()))
            conn.commit(); messagebox.showinfo("Added", "Bed added!")
            self.load_beds()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def free_bed(self):    self._set_occupied(0)
    def occupy_bed(self):  self._set_occupied(1)

    def _set_occupied(self, val):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a bed first.")
            return
        bid = self.tree.item(sel[0])["values"][0]
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute(
                "UPDATE Beds SET is_occupied=%s WHERE bed_id=%s", (val, bid))
            conn.commit(); self.load_beds()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def load_beds(self):
        filt = self.filter_var.get()
        try:
            conn = get_conn(); cur = conn.cursor()
            q = "SELECT bed_id,ward,bed_number,type,is_occupied FROM Beds"
            if filt == "Free":     q += " WHERE is_occupied=0"
            elif filt == "Occupied": q += " WHERE is_occupied=1"
            q += " ORDER BY ward,bed_number"
            cur.execute(q)
            rows = cur.fetchall()
            self.tree.delete(*self.tree.get_children())
            free_count = occ_count = 0
            for row in rows:
                status = "Occupied" if row[4] else "Free"
                display = list(row[:-1]) + [status]
                tag = "occ" if row[4] else "free"
                self.tree.insert("", "end", values=display, tags=(tag,))
                if row[4]: occ_count += 1
                else:       free_count += 1
            self.tree.tag_configure("occ",  foreground=ACCENT2)
            self.tree.tag_configure("free", foreground="#2d9e5f")
            # update stats
            for w in self.stats_frame.winfo_children():
                w.destroy()
            tk.Label(self.stats_frame, text=f"Free: {free_count}",
                     fg="#2d9e5f", bg=PANEL, font=FONT_HEAD).pack(
                         side="left", padx=8)
            tk.Label(self.stats_frame, text=f"Occupied: {occ_count}",
                     fg=ACCENT2, bg=PANEL, font=FONT_HEAD).pack(
                         side="left", padx=8)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 5 — EMERGENCY
# ══════════════════════════════════════════════════════════════════════════════
class EmergencyTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()
        self.load_emergency()

    def _build(self):
        left = card(self)
        left.pack(side="left", fill="y", padx=(16,8), pady=16)

        section_title(left, "Register Emergency").pack(
            anchor="w", padx=16, pady=(16,8))

        r = tk.Frame(left, bg=PANEL)
        r.pack(fill="x", padx=16, pady=4)
        make_label(r, "Patient ID", fg=SUBTEXT).pack(anchor="w")
        self.patient_var = tk.StringVar()
        make_entry(r, textvariable=self.patient_var).pack(fill="x", pady=2)

        r2 = tk.Frame(left, bg=PANEL)
        r2.pack(fill="x", padx=16, pady=4)
        make_label(r2, "Triage Level (1=Critical, 5=Minor)", fg=SUBTEXT).pack(
            anchor="w")
        self.triage = tk.IntVar(value=3)
        for lvl in range(1, 6):
            color = [ACCENT2,"#ff6b6b","#f4a261","#2ec4b6","#2d9e5f"][lvl-1]
            tk.Radiobutton(r2, text=str(lvl), variable=self.triage,
                           value=lvl, bg=PANEL, fg=color,
                           selectcolor=ENTRY_BG, activebackground=PANEL,
                           font=("Helvetica", 12, "bold")).pack(
                               side="left", padx=6)

        r3 = tk.Frame(left, bg=PANEL)
        r3.pack(fill="x", padx=16, pady=4)
        make_label(r3, "Symptoms / Notes", fg=SUBTEXT).pack(anchor="w")
        self.symptoms = tk.Text(r3, height=5, bg=ENTRY_BG, fg=TEXT,
                                insertbackground=ACCENT, font=FONT_ENTRY,
                                relief="flat", width=30)
        self.symptoms.pack(fill="x", pady=2)

        separator(left).pack(fill="x", padx=16, pady=10)

        make_btn(left, "REGISTER EMERGENCY", self.register,
                 bg=ACCENT2, fg=TEXT, width=20).pack(padx=16, pady=4)
        make_btn(left, "Discharge",          self.discharge,
                 bg="#2d6a4f", fg=TEXT, width=20).pack(padx=16, pady=4)

        right = card(self)
        right.pack(side="left", fill="both", expand=True,
                   padx=(8,16), pady=16)

        section_title(right, "Emergency Queue").pack(
            anchor="w", padx=16, pady=(16,8))

        cols  = ("id","patient","triage","arrival","symptoms")
        heads = ("ER ID","Patient","Triage","Arrival","Symptoms")
        widths = {"id":60,"patient":140,"triage":70,"arrival":140,"symptoms":300}
        tf, self.tree = styled_tree(right, cols, heads, height=18, col_widths=widths)
        # remove old manual column override — handled by col_widths now
        tf.pack(fill="both", expand=True, padx=16, pady=8)

    def register(self):
        pid = self.patient_var.get().strip()
        if not pid:
            messagebox.showwarning("Missing", "Enter Patient ID.")
            return
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute("""
                INSERT INTO Emergency_Cases
                (patient_id, triage_level, arrival_time, symptoms, status)
                VALUES (%s,%s,NOW(),%s,'Active')
            """, (pid, self.triage.get(),
                  self.symptoms.get("1.0","end").strip()))
            conn.commit()
            messagebox.showinfo("Registered", "Emergency case registered!")
            self.patient_var.set("")
            self.symptoms.delete("1.0","end")
            self.load_emergency()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def discharge(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a case first.")
            return
        eid = self.tree.item(sel[0])["values"][0]
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute(
                "UPDATE Emergency_Cases SET status='Discharged' WHERE emergency_id=%s",
                (eid,))
            conn.commit(); self.load_emergency()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def load_emergency(self):
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute("""
                SELECT e.emergency_id, p.name, e.triage_level,
                       e.arrival_time, e.symptoms
                FROM Emergency_Cases e
                JOIN Patients p ON e.patient_id = p.patient_id
                WHERE e.status = 'Active'
                ORDER BY e.triage_level ASC, e.arrival_time ASC
            """)
            rows = cur.fetchall()
            self.tree.delete(*self.tree.get_children())
            for row in rows:
                lvl = row[2]
                tag = f"t{lvl}"
                self.tree.insert("", "end", values=row, tags=(tag,))
            colors = {1: ACCENT2, 2:"#ff6b6b", 3:"#f4a261",
                      4:"#2ec4b6", 5:"#2d9e5f"}
            for lvl, col in colors.items():
                self.tree.tag_configure(f"t{lvl}", foreground=col)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        self.configure(bg=BG)
        # Build main FIRST so header_title and active_tab exist
        # before sidebar buttons can fire
        self._build_main()
        self._build_sidebar()
        self.switch_tab("patients")

    # ── sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = self.sidebar_frame   # already packed in _build_main

        # logo
        logo = tk.Frame(sb, bg="#0a1220")
        logo.pack(fill="x", pady=(24,8))
        tk.Label(logo, text="+", fg=ACCENT, bg="#0a1220",
                 font=("Helvetica", 32, "bold")).pack()
        tk.Label(logo, text="HMS", fg=TEXT, bg="#0a1220",
                 font=("Helvetica", 16, "bold")).pack()
        tk.Label(logo, text="Hospital Management", fg=SUBTEXT, bg="#0a1220",
                 font=FONT_SMALL).pack()

        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x", padx=16, pady=16)

        self.nav_btns = {}
        nav_items = [
            ("  Patients",    "patients"),
            ("  Doctors",     "doctors"),
            ("  Appointments","appointments"),
            ("  Beds",        "beds"),
            ("  Emergency",   "emergency"),
        ]
        for label, key in nav_items:
            b = tk.Button(sb, text=label, anchor="w",
                          bg="#0a1220", fg=SUBTEXT,
                          font=("Helvetica", 11),
                          relief="flat", cursor="hand2",
                          padx=20, pady=10,
                          activebackground="#162030",
                          activeforeground=TEXT,
                          command=lambda k=key: self.switch_tab(k))
            b.pack(fill="x", pady=1)
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg="#162030", fg=TEXT))
            b.bind("<Leave>", lambda e, btn=b, k2=key: btn.config(
                bg="#162030" if self.active_tab == k2 else "#0a1220",
                fg=TEXT if self.active_tab == k2 else SUBTEXT))
            self.nav_btns[key] = b

        # clock
        self.clock_lbl = tk.Label(sb, fg=SUBTEXT, bg="#0a1220",
                                   font=FONT_SMALL)
        self.clock_lbl.pack(side="bottom", pady=16)
        self._tick()

    def _tick(self):
        self.clock_lbl.config(
            text=datetime.now().strftime("%d %b %Y\n%H:%M:%S"))
        self.after(1000, self._tick)

    # ── main area ─────────────────────────────────────────────────────────────
    def _build_main(self):
        self.active_tab = None   # must exist before sidebar buttons fire

        # header bar
        header = tk.Frame(self, bg=PANEL, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        self.header_title = tk.Label(header, text="", fg=TEXT, bg=PANEL,
                                      font=FONT_TITLE)
        self.header_title.pack(side="left", padx=24)
        tk.Label(header, text="Hospital Management System v1.0",
                 fg=SUBTEXT, bg=PANEL, font=FONT_SMALL).pack(
                     side="right", padx=24)

        separator(self).pack(fill="x")

        # content row: sidebar + tab area side by side
        self.content_row = tk.Frame(self, bg=BG)
        self.content_row.pack(fill="both", expand=True)

        # sidebar placeholder packed LEFT first so it claims its space
        # _build_sidebar() will place widgets inside this frame
        self.sidebar_frame = tk.Frame(self.content_row, bg="#0a1220", width=200)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # tab frame fills remaining space to the right
        self.tab_frame = tk.Frame(self.content_row, bg=BG)
        self.tab_frame.pack(side="left", fill="both", expand=True)

        self.tabs = {
            "patients":     PatientTab,
            "doctors":      DoctorTab,
            "appointments": AppointmentTab,
            "beds":         BedTab,
            "emergency":    EmergencyTab,
        }
        self.tab_instances = {}

    def switch_tab(self, key):
        self.active_tab = key
        titles = {
            "patients":     "Patient Registry",
            "doctors":      "Doctor Directory",
            "appointments": "Appointments",
            "beds":         "Bed Availability",
            "emergency":    "Emergency Queue",
        }
        self.header_title.config(text=titles.get(key, ""))

        # update nav highlight
        for k, btn in self.nav_btns.items():
            if k == key:
                btn.config(bg="#162030", fg=TEXT)
            else:
                btn.config(bg="#0a1220", fg=SUBTEXT)

        # show tab
        for w in self.tab_frame.winfo_children():
            w.pack_forget()

        if key not in self.tab_instances:
            self.tab_instances[key] = self.tabs[key](self.tab_frame)

        self.tab_instances[key].pack(fill="both", expand=True)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = HospitalApp()
    app.mainloop()
