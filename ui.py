import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import sys
import random
import math
import time
import sqlite3
import pandas as pd
from PIL import Image, ImageTk, ImageDraw

# PulseTracker v5.5 - Asset Management System
PT_OBSIDIAN = "#0A0E27"
PT_DEEP_SPACE = "#1A1F3A"
PT_NEON_EMERALD = "#00FF88"
PT_AMBER_ALERT = "#FFB700"
PT_PLASMA_RED = "#FF0055"
PT_VOID_BLACK = "#000000"
PT_GRID_CYAN = "#00FFFF"
PT_OFF_WHITE = "#E8E8E8"

# v5.5 Professional Messages
PROFESSIONAL_REMARKS = [
    "Asset successfully registered in the fleet database.",
    "Equipment record created. System ID: {n}.",
    "Data entry complete. Asset {n} is now active.",
    "Fleet database synchronized. Entry {n} confirmed.",
    "Resource allocation updated. Asset {n} logged.",
]

TIRED_AI_REMARKS = [
    "Yes, yes, another piece of equipment. How thrilling.",
    "I've catalogued {n} items. My enthusiasm levels remain: zero.",
    "Location recorded. I'm sure it'll stay there. Probably.",
    "Owner assigned. They won't remember this in a week.",
    "Equipment added. The database sighs with resignation.",
    "Smeg. Not again.",
    "This is why I drink motor oil.",
    "Efficiency? That's adorable.",
]

class PulseTrackerApp:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        # v5.5: Official Name Update
        self.root.title("PulseTracker – Asset Management System v5.5")
        
        self.dark_matter_mode = False
        self.dark_matter_clicks = 0
        self.style = ttk.Style()
        self.apply_styles()
        
        self.root.configure(bg=PT_OBSIDIAN)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.setup_ui()
        self.refresh_equipment()
        
        # v5.3: Optimized default window size
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

    def apply_styles(self):
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=PT_DEEP_SPACE, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=PT_DEEP_SPACE, foreground=PT_NEON_EMERALD, font=("Courier", 11, "bold"), padding=[15, 10])
        self.style.map("TNotebook.Tab", background=[("selected", PT_OBSIDIAN)], foreground=[("selected", PT_AMBER_ALERT)])
        self.style.configure("Treeview", background=PT_VOID_BLACK, fieldbackground=PT_VOID_BLACK, foreground=PT_NEON_EMERALD, font=("Courier", 10), rowheight=35)
        self.style.configure("Treeview.Heading", background=PT_DEEP_SPACE, foreground=PT_AMBER_ALERT, font=("Courier", 10, "bold"))

    def setup_ui(self):
        main_container = tk.Frame(self.root, bg=PT_OBSIDIAN)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # 1. EQUIPMENT TAB
        self.equip_tab = tk.Frame(self.notebook, bg=PT_OBSIDIAN)
        self.notebook.add(self.equip_tab, text="FLEET ASSETS")
        self.setup_equipment_view()

        # 2. Analytics Tab
        self.analytics_tab = tk.Frame(self.notebook, bg=PT_OBSIDIAN)
        self.notebook.add(self.analytics_tab, text="ANALYTICS")
        self.setup_analytics_view()

        # 3. Hidden Asteroids Tab
        self.asteroids_tab = tk.Frame(self.notebook, bg=PT_VOID_BLACK)
        self.asteroids_tab_index = None
        self.setup_asteroids_view()

        # Footer (always visible)
        footer = tk.Frame(self.root, bg=PT_OBSIDIAN, height=50)
        footer.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        footer.grid_propagate(False)
        
        self.trigger_frame = tk.Frame(footer, bg=PT_OBSIDIAN)
        self.trigger_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        tk.Label(self.trigger_frame, text="SYSTEM STATUS: OPTIMAL", bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD, font=("Courier", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.hidden_btn = tk.Button(self.trigger_frame, text="●", bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD, bd=0, 
                                   command=self.toggle_dark_matter, activebackground=PT_OBSIDIAN,
                                   font=("Courier", 12), cursor="hand2")
        self.hidden_btn.pack(side=tk.LEFT, padx=2)

    def on_tab_changed(self, event):
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        if tab_text == "ANALYTICS":
            self.refresh_analytics()
        elif tab_text == "THE VOID":
            self.refresh_leaderboard()

    def setup_equipment_view(self):
        self.equip_tab.grid_rowconfigure(2, weight=1)
        self.equip_tab.grid_columnconfigure(0, weight=1)
        
        # Header Row
        header = tk.Frame(self.equip_tab, bg=PT_OBSIDIAN)
        header.grid(row=0, column=0, sticky="ew", pady=5, padx=15)
        tk.Label(header, text="FLEET ASSETS", font=("Courier", 20, "bold"), 
                 bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD).pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(header, bg=PT_OBSIDIAN)
        btn_frame.pack(side=tk.RIGHT)

        tk.Button(btn_frame, text="EXPORT DATA", bg=PT_DEEP_SPACE, fg=PT_NEON_EMERALD,
                 font=("Courier", 10, "bold"), command=self.export_fleet_data, padx=10, pady=6, relief=tk.RAISED).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="+ ADD TO FLEET", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK, 
                 font=("Courier", 11, "bold"), command=self.open_add_to_fleet, padx=15, pady=6).pack(side=tk.LEFT, padx=5)

        # Search & Filter Toolbar
        filter_bar = tk.Frame(self.equip_tab, bg=PT_DEEP_SPACE, bd=1, relief=tk.RAISED)
        filter_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 10))

        tk.Label(filter_bar, text="SEARCH:", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 10, "bold")).pack(side=tk.LEFT, padx=(10, 5), pady=8)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_equipment())
        search_entry = tk.Entry(filter_bar, textvariable=self.search_var, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 10), width=25, insertbackground=PT_NEON_EMERALD)
        search_entry.pack(side=tk.LEFT, padx=5, pady=8)

        tk.Label(filter_bar, text="STATUS:", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 10, "bold")).pack(side=tk.LEFT, padx=(15, 5), pady=8)
        self.status_filter_var = tk.StringVar(value="All")
        status_combobox = ttk.Combobox(filter_bar, textvariable=self.status_filter_var, values=["All", "Active", "In Production", "Built", "In Stock", "Maintenance", "Retired"], state="readonly", width=15, font=("Courier", 10))
        status_combobox.pack(side=tk.LEFT, padx=5, pady=8)
        status_combobox.bind("<<ComboboxSelected>>", lambda e: self.refresh_equipment())

        tk.Button(filter_bar, text="RESET", bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 9, "bold"), command=self.reset_search_filter, padx=8).pack(side=tk.LEFT, padx=10, pady=8)

        # Treeview Table
        tree_frame = tk.Frame(self.equip_tab, bg=PT_OBSIDIAN)
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 10))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.equip_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Serial", "Owner", "Status", "Location"), show="headings", height=20)
        self.equip_tree.grid(row=0, column=0, sticky="nsew")
        self.equip_tree.bind("<Double-1>", self.on_equipment_double_click)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.equip_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.equip_tree.configure(yscroll=scrollbar.set)
        
        for col in ("ID", "Name", "Serial", "Owner", "Status", "Location"):
            self.equip_tree.heading(col, text=col.upper())
            self.equip_tree.column(col, width=120)

    def reset_search_filter(self):
        self.search_var.set("")
        self.status_filter_var.set("All")
        self.refresh_equipment()

    def export_fleet_data(self):
        df = self.db.export_all_equipment()
        if df.empty:
            messagebox.showinfo("Export Fleet Data", "No equipment records to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")],
            title="Export Fleet Database"
        )
        if not file_path:
            return

        try:
            if file_path.endswith(".xlsx"):
                df.to_excel(file_path, index=False)
            else:
                df.to_csv(file_path, index=False)
            messagebox.showinfo("Export Successful", f"Fleet records exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

    def open_add_to_fleet(self):
        window = tk.Toplevel(self.root)
        # v5.5: Official Name Update
        window.title("ADD TO FLEET - PulseTracker")
        # v5.3: Optimized window size for standard screens
        window.geometry("900x700")
        window.configure(bg=PT_OBSIDIAN)
        window.minsize(700, 500)
        
        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)
        
        nb = ttk.Notebook(window)
        nb.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        basic_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(basic_frame, text="BASIC INFO")
        self.create_basic_info_fields(basic_frame)
        
        prod_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(prod_frame, text="PRODUCTION")
        self.create_production_fields(prod_frame)
        
        sales_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(sales_frame, text="SALES & STATUS")
        self.create_sales_fields(sales_frame)
        
        owner_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(owner_frame, text="OWNER DETAILS")
        self.create_owner_fields(owner_frame)
        
        billing_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(billing_frame, text="BILLING & SHIPPING")
        self.create_billing_shipping_fields(billing_frame)
        
        attach_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(attach_frame, text="ATTACHMENTS")
        self.create_attachments_section(attach_frame, window)
        
        self.add_window_fields = {
            'basic': basic_frame,
            'prod': prod_frame,
            'sales': sales_frame,
            'owner': owner_frame,
            'billing': billing_frame,
            'window': window
        }
        
        btn_frame = tk.Frame(window, bg=PT_OBSIDIAN)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        tk.Button(btn_frame, text="COMMIT TO FLEET", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK, 
                 font=("Courier", 12, "bold"), command=lambda: self.save_equipment(window), padx=20, pady=10).pack(fill=tk.X)

    def create_basic_info_fields(self, frame, equip=None):
        fields = [
            ("EQUIPMENT NAME:", "equip_name"),
            ("SERIAL NUMBER:", "serial"),
            ("LOCATION:", "location"),
        ]
        self.basic_entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=12)
            entry = tk.Entry(frame, width=50, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 11), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=12, sticky="ew")
            self.basic_entries[key] = entry

            if equip:
                val = ""
                if key == "equip_name": val = equip['name'] if isinstance(equip, sqlite3.Row) else equip[1]
                elif key == "serial": val = equip['serial_number'] if isinstance(equip, sqlite3.Row) else equip[2]
                elif key == "location": val = equip['location'] if isinstance(equip, sqlite3.Row) else equip[18]
                if val: entry.insert(0, str(val))
        
        frame.grid_columnconfigure(1, weight=1)

    def create_production_fields(self, frame, equip=None):
        fields = [
            ("MANUFACTURE DATE:", "mfg_date"),
            ("MANUFACTURE LOCATION:", "mfg_loc"),
            ("BATCH ID:", "batch_id"),
            ("BATCH SIZE:", "batch_size"),
            ("JOB NUMBER:", "job_num"),
        ]
        self.prod_entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=12)
            entry = tk.Entry(frame, width=50, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 11), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=12, sticky="ew")
            self.prod_entries[key] = entry

            if equip:
                val = ""
                if key == "mfg_date": val = equip['manufacture_date'] if isinstance(equip, sqlite3.Row) else equip[3]
                elif key == "mfg_loc": val = equip['manufacture_location'] if isinstance(equip, sqlite3.Row) else equip[4]
                elif key == "batch_id": val = equip['batch_id'] if isinstance(equip, sqlite3.Row) else equip[5]
                elif key == "batch_size": val = equip['batch_size'] if isinstance(equip, sqlite3.Row) else equip[6]
                elif key == "job_num": val = equip['job_number'] if isinstance(equip, sqlite3.Row) else equip[7]
                if val is not None: entry.insert(0, str(val))
        
        tk.Label(frame, text="QA STATUS:", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=5, column=0, sticky=tk.W, padx=15, pady=12)
        initial_qa = "Passed"
        if equip:
            initial_qa = (equip['qa_status'] if isinstance(equip, sqlite3.Row) else equip[8]) or "Passed"
        self.qa_var = tk.StringVar(value=initial_qa)
        qa_combo = ttk.Combobox(frame, textvariable=self.qa_var, values=["Passed", "Hold", "Rework"], width=47, font=("Courier", 11))
        qa_combo.grid(row=5, column=1, padx=15, pady=12, sticky="ew")
        
        frame.grid_columnconfigure(1, weight=1)

    def create_sales_fields(self, frame, equip=None):
        initial_sale_status = "Sold"
        initial_status = "Active"
        if equip:
            initial_sale_status = (equip['sale_status'] if isinstance(equip, sqlite3.Row) else equip[9]) or "Sold"
            initial_status = (equip['status'] if isinstance(equip, sqlite3.Row) else equip[14]) or "Active"

        tk.Label(frame, text="SALE STATUS:", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=0, column=0, sticky=tk.W, padx=15, pady=12)
        self.sale_status_var = tk.StringVar(value=initial_sale_status)
        sale_combo = ttk.Combobox(frame, textvariable=self.sale_status_var, values=["Unsold", "Quoted", "Sold", "Delivered"], width=47, font=("Courier", 11))
        sale_combo.grid(row=0, column=1, padx=15, pady=12, sticky="ew")
        
        tk.Label(frame, text="LIFECYCLE STATUS:", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=1, column=0, sticky=tk.W, padx=15, pady=12)
        self.status_var = tk.StringVar(value=initial_status)
        status_combo = ttk.Combobox(frame, textvariable=self.status_var, values=["In Production", "Built", "In Stock", "Active", "Maintenance", "Retired"], width=47, font=("Courier", 11))
        status_combo.grid(row=1, column=1, padx=15, pady=12, sticky="ew")
        
        fields = [
            ("SALE DATE:", "sale_date"),
            ("INVOICE #:", "invoice"),
            ("WARRANTY END DATE:", "warranty"),
        ]
        self.sales_entries = {}
        for i, (label, key) in enumerate(fields, start=2):
            tk.Label(frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=12)
            entry = tk.Entry(frame, width=50, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 11), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=12, sticky="ew")
            self.sales_entries[key] = entry

            if equip:
                val = ""
                if key == "sale_date": val = equip['sale_date'] if isinstance(equip, sqlite3.Row) else equip[10]
                elif key == "invoice": val = equip['invoice_number'] if isinstance(equip, sqlite3.Row) else equip[11]
                elif key == "warranty": val = equip['warranty_end'] if isinstance(equip, sqlite3.Row) else equip[12]
                if val: entry.insert(0, str(val))
        
        frame.grid_columnconfigure(1, weight=1)

    def create_owner_fields(self, frame, equip=None):
        fields = [
            ("INDIVIDUAL OWNER:", "owner_individual"),
            ("COMPANY OWNER:", "owner_company"),
            ("OWNER NOTES:", "owner_notes"),
        ]
        self.owner_entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=i, column=0, sticky=tk.NW, padx=15, pady=12)
            if key == "owner_notes":
                entry = tk.Text(frame, width=50, height=6, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 10), insertbackground=PT_NEON_EMERALD)
            else:
                entry = tk.Entry(frame, width=50, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 11), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=12, sticky="ew")
            self.owner_entries[key] = entry

            if equip:
                if key == "owner_individual":
                    val = equip['owner_individual'] if isinstance(equip, sqlite3.Row) else equip[15]
                    if val: entry.insert(0, str(val))
                elif key == "owner_company":
                    val = equip['owner_company'] if isinstance(equip, sqlite3.Row) else equip[16]
                    if val: entry.insert(0, str(val))
                elif key == "owner_notes":
                    val = equip['owner_notes'] if isinstance(equip, sqlite3.Row) else equip[17]
                    if val: entry.insert("1.0", str(val))
        
        frame.grid_columnconfigure(1, weight=1)

    def create_billing_shipping_fields(self, frame, equip=None):
        canvas = tk.Canvas(frame, bg=PT_DEEP_SPACE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=PT_DEEP_SPACE)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        tk.Label(scrollable_frame, text="BILLING ADDRESS", bg=PT_DEEP_SPACE, fg=PT_PLASMA_RED, font=("Courier", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=15, pady=12)
        
        billing_fields = [
            ("Street Address:", "billing_address"),
            ("Suburb:", "billing_suburb"),
            ("State:", "billing_state"),
            ("Postcode:", "billing_postcode"),
            ("Country:", "billing_country"),
            ("Payment Methods:", "payment_methods"),
        ]
        self.billing_entries = {}
        for i, (label, key) in enumerate(billing_fields, start=1):
            tk.Label(scrollable_frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 11, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=10)
            entry = tk.Entry(scrollable_frame, width=50, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 10), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=10, sticky="ew")
            self.billing_entries[key] = entry

            if equip:
                db_col = key
                val = equip[db_col] if isinstance(equip, sqlite3.Row) else None
                if val is not None: entry.insert(0, str(val))
        
        tk.Label(scrollable_frame, text="SHIPPING ADDRESS", bg=PT_DEEP_SPACE, fg=PT_PLASMA_RED, font=("Courier", 12, "bold")).grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=15, pady=12)
        
        shipping_fields = [
            ("Street Address:", "shipping_address"),
            ("Suburb:", "shipping_suburb"),
            ("State:", "shipping_state"),
            ("Postcode:", "shipping_postcode"),
            ("Country:", "shipping_country"),
            ("Parts Destination:", "parts_destination"),
        ]
        self.shipping_entries = {}
        for i, (label, key) in enumerate(shipping_fields, start=8):
            tk.Label(scrollable_frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 11, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=10)
            entry = tk.Entry(scrollable_frame, width=50, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 10), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=10, sticky="ew")
            self.shipping_entries[key] = entry

            if equip:
                db_col = key
                val = equip[db_col] if isinstance(equip, sqlite3.Row) else None
                if val is not None: entry.insert(0, str(val))
        
        scrollable_frame.grid_columnconfigure(1, weight=1)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_attachments_section(self, frame, window):
        tk.Label(frame, text="ATTACH FILES (Drawings, Reports, Certificates, etc.)", bg=PT_DEEP_SPACE, fg=PT_NEON_EMERALD, font=("Courier", 11, "bold")).pack(pady=10)
        
        btn_frame = tk.Frame(frame, bg=PT_DEEP_SPACE)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="+ ADD FILE", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK, 
                 font=("Courier", 10, "bold"), command=lambda: self.add_attachment_file(frame)).pack(side=tk.LEFT, padx=5)
        
        self.attachment_listbox = tk.Listbox(frame, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, height=10, font=("Courier", 10))
        self.attachment_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.attached_files = []

    def add_attachment_file(self, frame):
        file_path = filedialog.askopenfilename(title="Select file to attach")
        if file_path:
            filename = os.path.basename(file_path)
            self.attached_files.append((filename, file_path))
            self.attachment_listbox.insert(tk.END, filename)

    def save_equipment(self, window, equip_id=None):
        try:
            batch_size_str = self.prod_entries['batch_size'].get().strip()
            batch_size_val = 1
            if batch_size_str:
                if not batch_size_str.isdigit() or int(batch_size_str) <= 0:
                    messagebox.showwarning("Validation Error", "Batch Size must be a positive integer.")
                    return
                batch_size_val = int(batch_size_str)

            data = {
                'name': self.basic_entries['equip_name'].get().strip(),
                'serial_number': self.basic_entries['serial'].get().strip(),
                'location': self.basic_entries['location'].get().strip(),
                'manufacture_date': self.prod_entries['mfg_date'].get().strip() or None,
                'manufacture_location': self.prod_entries['mfg_loc'].get().strip(),
                'batch_id': self.prod_entries['batch_id'].get().strip(),
                'batch_size': batch_size_val,
                'job_number': self.prod_entries['job_num'].get().strip(),
                'qa_status': self.qa_var.get(),
                'sale_status': self.sale_status_var.get(),
                'sale_date': self.sales_entries['sale_date'].get().strip() or None,
                'invoice_number': self.sales_entries['invoice'].get().strip(),
                'warranty_end': self.sales_entries['warranty'].get().strip() or None,
                'status': self.status_var.get(),
                'owner_individual': self.owner_entries['owner_individual'].get().strip(),
                'owner_company': self.owner_entries['owner_company'].get().strip(),
                'owner_notes': self.owner_entries['owner_notes'].get("1.0", tk.END).strip(),
                'billing_address': self.billing_entries['billing_address'].get().strip(),
                'billing_suburb': self.billing_entries['billing_suburb'].get().strip(),
                'billing_state': self.billing_entries['billing_state'].get().strip(),
                'billing_postcode': self.billing_entries['billing_postcode'].get().strip(),
                'billing_country': self.billing_entries['billing_country'].get().strip(),
                'payment_methods': self.billing_entries['payment_methods'].get().strip(),
                'shipping_address': self.shipping_entries['shipping_address'].get().strip(),
                'shipping_suburb': self.shipping_entries['shipping_suburb'].get().strip(),
                'shipping_state': self.shipping_entries['shipping_state'].get().strip(),
                'shipping_postcode': self.shipping_entries['shipping_postcode'].get().strip(),
                'shipping_country': self.shipping_entries['shipping_country'].get().strip(),
                'parts_destination': self.shipping_entries['parts_destination'].get().strip(),
            }
            
            if not data['name'] or not data['serial_number']:
                messagebox.showwarning("Incomplete Data", "Name and Serial Number are mandatory for the fleet records.")
                return

            if equip_id:
                self.db.update_equipment(equip_id, data)
                target_id = equip_id
            else:
                data['install_date'] = datetime.now().strftime("%Y-%m-%d")
                target_id = self.db.add_equipment(data)

            for filename, filepath in getattr(self, 'attached_files', []):
                self.db.add_attachment(target_id, filename, filepath)
            
            # v5.4: Professional messages unless Dark Matter Mode is active
            if self.dark_matter_mode:
                msg = random.choice(TIRED_AI_REMARKS).format(n=target_id)
            else:
                msg = random.choice(PROFESSIONAL_REMARKS).format(n=target_id)
                
            messagebox.showinfo("FLEET UPDATED", msg)
            self.refresh_equipment()
            window.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Serial", f"An asset with Serial Number '{self.basic_entries['serial'].get()}' already exists.")
        except Exception as e:
            messagebox.showerror("SYSTEM ERROR", f"Failed to commit to fleet: {str(e)}")

    def refresh_equipment(self):
        for item in self.equip_tree.get_children():
            self.equip_tree.delete(item)
        
        query = self.search_var.get() if hasattr(self, 'search_var') else None
        status_filter = self.status_filter_var.get() if hasattr(self, 'status_filter_var') else None

        records = self.db.search_equipment(query=query, status_filter=status_filter)
        for equip in records:
            if isinstance(equip, sqlite3.Row):
                e_id = equip['id']
                e_name = equip['name']
                e_serial = equip['serial_number']
                e_owner = equip['owner_company'] or equip['owner_individual'] or "N/A"
                e_status = equip['status']
                e_location = equip['location'] or "N/A"
            else:
                e_id = equip[0]
                e_name = equip[1]
                e_serial = equip[2]
                e_owner = equip[16] or equip[15] or "N/A"
                e_status = equip[14]
                e_location = equip[18] or "N/A"

            self.equip_tree.insert("", tk.END, values=(
                e_id, e_name, e_serial, e_owner, e_status, e_location
            ))

    def on_equipment_double_click(self, event):
        selected = self.equip_tree.selection()
        if not selected:
            return
        item = selected[0]
        equip_id = self.equip_tree.item(item, "values")[0]
        self.open_equipment_details(equip_id)

    def open_equipment_details(self, equip_id):
        equip = self.db.get_equipment_by_id(equip_id)
        if not equip: return
        
        window = tk.Toplevel(self.root)
        name_val = equip['name'] if isinstance(equip, sqlite3.Row) else equip[1]
        serial_val = equip['serial_number'] if isinstance(equip, sqlite3.Row) else equip[2]
        location_val = equip['location'] if isinstance(equip, sqlite3.Row) else equip[18]
        status_val = equip['status'] if isinstance(equip, sqlite3.Row) else equip[14]
        owner_val = (equip['owner_company'] if isinstance(equip, sqlite3.Row) else equip[16]) or (equip['owner_individual'] if isinstance(equip, sqlite3.Row) else equip[15]) or "N/A"
        mfg_date_val = equip['manufacture_date'] if isinstance(equip, sqlite3.Row) else equip[3]
        invoice_val = equip['invoice_number'] if isinstance(equip, sqlite3.Row) else equip[11]

        # v5.5: Official Name Update
        window.title(f"ASSET DETAILS: {name_val} - PulseTracker")
        window.geometry("1100x850")
        window.configure(bg=PT_OBSIDIAN)
        
        # Header & Actions
        hdr_frame = tk.Frame(window, bg=PT_OBSIDIAN)
        hdr_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(hdr_frame, text=f"ASSET DETAILS: {name_val}", font=("Courier", 18, "bold"), bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD).pack(side=tk.LEFT)
        
        act_frame = tk.Frame(hdr_frame, bg=PT_OBSIDIAN)
        act_frame.pack(side=tk.RIGHT)

        tk.Button(act_frame, text="EDIT ASSET", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK, font=("Courier", 10, "bold"),
                  command=lambda: [window.destroy(), self.open_edit_equipment(equip_id)]).pack(side=tk.LEFT, padx=5)

        tk.Button(act_frame, text="DELETE ASSET", bg=PT_PLASMA_RED, fg=PT_OFF_WHITE, font=("Courier", 10, "bold"),
                  command=lambda: self.confirm_delete_equipment(equip_id, window)).pack(side=tk.LEFT, padx=5)

        details_frame = tk.Frame(window, bg=PT_DEEP_SPACE)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        info = [
            ("SERIAL:", serial_val),
            ("LOCATION:", location_val),
            ("STATUS:", status_val),
            ("OWNER:", owner_val),
            ("MFG DATE:", mfg_date_val or "N/A"),
            ("INVOICE:", invoice_val or "N/A"),
        ]
        
        for i, (label, val) in enumerate(info):
            tk.Label(details_frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=8)
            tk.Label(details_frame, text=val, bg=PT_DEEP_SPACE, fg=PT_OFF_WHITE, font=("Courier", 12)).grid(row=i, column=1, sticky=tk.W, padx=15, pady=8)

        tk.Label(window, text="ATTACHED FILES", bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD, font=("Courier", 12, "bold")).pack(pady=(20, 5))
        attach_list = tk.Listbox(window, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, height=6)
        attach_list.pack(fill=tk.X, padx=40, pady=5)
        
        attachments = self.db.get_attachments(equip_id)
        for att in attachments:
            fname = att['filename'] if isinstance(att, sqlite3.Row) else att[2]
            attach_list.insert(tk.END, fname)
            
        def download_attachment():
            if not attach_list.curselection(): return
            idx = attach_list.curselection()[0]
            att = attachments[idx]
            fname = att['filename'] if isinstance(att, sqlite3.Row) else att[2]
            fpath = att['filepath'] if isinstance(att, sqlite3.Row) else att[3]
            save_path = filedialog.asksaveasfilename(initialfile=fname)
            if save_path:
                try:
                    import shutil
                    shutil.copy2(fpath, save_path)
                    messagebox.showinfo("SUCCESS", "File extracted from database.")
                except Exception as e:
                    messagebox.showerror("ERROR", f"Failed to extract file: {e}")

        def remove_attachment():
            if not attach_list.curselection(): return
            idx = attach_list.curselection()[0]
            att = attachments[idx]
            att_id = att['id'] if isinstance(att, sqlite3.Row) else att[0]
            fname = att['filename'] if isinstance(att, sqlite3.Row) else att[2]
            if messagebox.askyesno("Delete Attachment", f"Are you sure you want to delete '{fname}'?"):
                self.db.delete_attachment(att_id)
                window.destroy()
                self.open_equipment_details(equip_id)

        att_btn_frame = tk.Frame(window, bg=PT_OBSIDIAN)
        att_btn_frame.pack(pady=10)

        tk.Button(att_btn_frame, text="EXTRACT SELECTED FILE", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK, font=("Courier", 10, "bold"), command=download_attachment).pack(side=tk.LEFT, padx=5)
        tk.Button(att_btn_frame, text="DELETE ATTACHMENT", bg=PT_PLASMA_RED, fg=PT_OFF_WHITE, font=("Courier", 10, "bold"), command=remove_attachment).pack(side=tk.LEFT, padx=5)

    def open_edit_equipment(self, equip_id):
        equip = self.db.get_equipment_by_id(equip_id)
        if not equip: return

        window = tk.Toplevel(self.root)
        name_val = equip['name'] if isinstance(equip, sqlite3.Row) else equip[1]
        window.title(f"EDIT ASSET: {name_val} - PulseTracker")
        window.geometry("900x700")
        window.configure(bg=PT_OBSIDIAN)
        window.minsize(700, 500)

        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)

        nb = ttk.Notebook(window)
        nb.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        basic_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(basic_frame, text="BASIC INFO")
        self.create_basic_info_fields(basic_frame, equip)

        prod_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(prod_frame, text="PRODUCTION")
        self.create_production_fields(prod_frame, equip)

        sales_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(sales_frame, text="SALES & STATUS")
        self.create_sales_fields(sales_frame, equip)

        owner_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(owner_frame, text="OWNER DETAILS")
        self.create_owner_fields(owner_frame, equip)

        billing_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(billing_frame, text="BILLING & SHIPPING")
        self.create_billing_shipping_fields(billing_frame, equip)

        attach_frame = tk.Frame(nb, bg=PT_DEEP_SPACE)
        nb.add(attach_frame, text="ATTACHMENTS")
        self.create_attachments_section(attach_frame, window)

        btn_frame = tk.Frame(window, bg=PT_OBSIDIAN)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        tk.Button(btn_frame, text="SAVE CHANGES", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK,
                 font=("Courier", 12, "bold"), command=lambda: self.save_equipment(window, equip_id=equip_id), padx=20, pady=10).pack(fill=tk.X)

    def confirm_delete_equipment(self, equip_id, window):
        equip = self.db.get_equipment_by_id(equip_id)
        if not equip: return
        name_val = equip['name'] if isinstance(equip, sqlite3.Row) else equip[1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete asset '{name_val}' and all its attachments?"):
            self.db.delete_equipment(equip_id)
            messagebox.showinfo("Asset Deleted", f"Asset '{name_val}' has been removed from the fleet.")
            window.destroy()
            self.refresh_equipment()

    def setup_analytics_view(self):
        tk.Label(self.analytics_tab, text="FLEET ANALYTICS", font=("Courier", 24, "bold"), bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD).pack(pady=20)
        
        self.stats_frame = tk.Frame(self.analytics_tab, bg=PT_DEEP_SPACE, bd=2, relief=tk.RIDGE)
        self.stats_frame.pack(fill=tk.X, padx=50, pady=10)
        
        self.total_label = tk.Label(self.stats_frame, text="TOTAL ASSETS: 0", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 14))
        self.total_label.pack(pady=5)
        
        # Container for charts
        self.charts_container = tk.Frame(self.analytics_tab, bg=PT_OBSIDIAN)
        self.charts_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.canvas_indiv = tk.Canvas(self.charts_container, width=400, height=350, bg=PT_VOID_BLACK, highlightthickness=1, highlightbackground=PT_GRID_CYAN)
        self.canvas_indiv.pack(side=tk.LEFT, padx=20, pady=10, expand=True)
        
        self.canvas_company = tk.Canvas(self.charts_container, width=400, height=350, bg=PT_VOID_BLACK, highlightthickness=1, highlightbackground=PT_GRID_CYAN)
        self.canvas_company.pack(side=tk.RIGHT, padx=20, pady=10, expand=True)
        
        tk.Label(self.charts_container, text="ASSETS BY INDIVIDUAL", bg=PT_OBSIDIAN, fg=PT_GRID_CYAN, font=("Courier", 10)).place(relx=0.25, rely=0.95, anchor=tk.CENTER)
        tk.Label(self.charts_container, text="ASSETS BY COMPANY", bg=PT_OBSIDIAN, fg=PT_GRID_CYAN, font=("Courier", 10)).place(relx=0.75, rely=0.95, anchor=tk.CENTER)

    def refresh_analytics(self):
        df = self.db.get_owner_stats()
        total = len(df)
        self.total_label.config(text=f"TOTAL ASSETS: {total}")
        
        self.draw_pie_chart(self.canvas_indiv, df['owner_individual'].value_counts())
        self.draw_pie_chart(self.canvas_company, df['owner_company'].value_counts())

    def draw_pie_chart(self, canvas, data):
        canvas.delete("all")
        if data.empty:
            canvas.create_text(200, 175, text="NO DATA AVAILABLE", fill=PT_AMBER_ALERT, font=("Courier", 12))
            return
            
        colors = [PT_NEON_EMERALD, PT_AMBER_ALERT, PT_PLASMA_RED, PT_GRID_CYAN, "#FF00FF", "#FFFF00"]
        total = data.sum()
        start_angle = 0
        
        # Center and Radius
        cx, cy, r = 200, 150, 100
        
        for i, (name, count) in enumerate(data.items()):
            extent = (count / total) * 360
            color = colors[i % len(colors)]
            canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=start_angle, extent=extent, fill=color, outline=PT_VOID_BLACK)
            
            # Draw Legend
            lx, ly = 20, 280 + (i * 20)
            if ly < 340:
                canvas.create_rectangle(lx, ly, lx+10, ly+10, fill=color)
                display_name = (name[:15] + '..') if name and len(name) > 15 else (name or "Unknown")
                canvas.create_text(lx+20, ly+5, text=f"{display_name}: {count}", fill=PT_OFF_WHITE, font=("Courier", 8), anchor=tk.W)
            
            start_angle += extent

    def setup_asteroids_view(self):
        self.asteroids_tab.grid_rowconfigure(0, weight=1)
        self.asteroids_tab.grid_columnconfigure(0, weight=1)
        
        main_game_frame = tk.Frame(self.asteroids_tab, bg=PT_VOID_BLACK)
        main_game_frame.grid(row=0, column=0, sticky="nsew")
        main_game_frame.grid_rowconfigure(0, weight=1)
        main_game_frame.grid_columnconfigure(0, weight=1)

        self.game_canvas = tk.Canvas(main_game_frame, bg=PT_VOID_BLACK, highlightthickness=0)
        self.game_canvas.grid(row=0, column=0, sticky="nsew")

        # Leaderboard Sidebar Frame
        self.leaderboard_frame = tk.Frame(main_game_frame, bg=PT_DEEP_SPACE, width=220, bd=1, relief=tk.SOLID)
        self.leaderboard_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        tk.Label(self.leaderboard_frame, text="HALL OF FAME", font=("Courier", 12, "bold"), bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT).pack(pady=10)
        
        self.leaderboard_list = tk.Listbox(self.leaderboard_frame, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 9), bd=0, highlightthickness=0)
        self.leaderboard_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.score_label = tk.Label(self.asteroids_tab, text="SCORE: 0", bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 14, "bold"))
        self.score_label.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        
        tk.Button(self.asteroids_tab, text="INITIALIZE COMBAT", bg=PT_PLASMA_RED, fg=PT_VOID_BLACK, 
                 font=("Courier", 12, "bold"), command=self.start_asteroids_game).grid(row=2, column=0, columnspan=2, pady=10)
        
        self.game_active = False
        self.asteroids = []
        self.bullets = []
        self.player_x = 400
        self.player_y = 300
        self.player_angle = 0
        self.player_vel_x = 0
        self.player_vel_y = 0
        self.score = 0
        self.high_score = 0
        self.lives = 3
        self.round_num = 1
        self.refresh_leaderboard()

    def refresh_leaderboard(self):
        self.leaderboard_list.delete(0, tk.END)
        top_scores = self.db.get_top_scores(limit=10)
        if top_scores:
            self.high_score = top_scores[0]['score'] if isinstance(top_scores[0], sqlite3.Row) else top_scores[0][1]
            for idx, row in enumerate(top_scores, start=1):
                p_name = row['player_name'] if isinstance(row, sqlite3.Row) else row[0]
                sc = row['score'] if isinstance(row, sqlite3.Row) else row[1]
                rnd = row['round'] if isinstance(row, sqlite3.Row) else row[2]
                self.leaderboard_list.insert(tk.END, f"{idx}. {p_name[:8]}: {sc} (R{rnd})")
        else:
            self.leaderboard_list.insert(tk.END, "No records yet.")

    def start_asteroids_game(self):
        if self.game_active: return
        self.game_active = True
        self.score = 0
        self.lives = 3
        self.round_num = 1
        self.asteroids = []
        self.bullets = []
        self.player_x = self.game_canvas.winfo_width() / 2 or 400
        self.player_y = self.game_canvas.winfo_height() / 2 or 300
        self.player_vel_x = 0
        self.player_vel_y = 0
        self.spawn_asteroids()
        
        self.root.bind("<Left>", lambda e: self.rotate_player(-15))
        self.root.bind("<Right>", lambda e: self.rotate_player(15))
        self.root.bind("<Up>", lambda e: self.thrust_player())
        self.root.bind("<space>", lambda e: self.fire_bullet())
        
        self.update_asteroids_game()

    def rotate_player(self, angle):
        self.player_angle = (self.player_angle + angle) % 360

    def thrust_player(self):
        angle_rad = math.radians(self.player_angle)
        self.player_vel_x += math.cos(angle_rad) * 0.8
        self.player_vel_y -= math.sin(angle_rad) * 0.8

    def fire_bullet(self):
        angle_rad = math.radians(self.player_angle)
        self.bullets.append({
            'x': self.player_x + 15 * math.cos(angle_rad),
            'y': self.player_y - 15 * math.sin(angle_rad),
            'vx': math.cos(angle_rad) * 10,
            'vy': -math.sin(angle_rad) * 10,
            'life': 40
        })

    def spawn_asteroids(self):
        cw = max(self.game_canvas.winfo_width(), 800)
        ch = max(self.game_canvas.winfo_height(), 600)
        for _ in range(3 + self.round_num * 2):
            self.asteroids.append({
                'x': random.randint(0, cw),
                'y': random.randint(0, ch),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'size': random.randint(20, 40)
            })

    def update_asteroids_game(self):
        if not self.game_active: return
        
        cw = max(self.game_canvas.winfo_width(), 800)
        ch = max(self.game_canvas.winfo_height(), 600)

        # Update player position with momentum
        self.player_x = (self.player_x + self.player_vel_x) % cw
        self.player_y = (self.player_y + self.player_vel_y) % ch
        
        # Apply friction
        self.player_vel_x *= 0.98
        self.player_vel_y *= 0.98
        
        # Update bullets
        for b in self.bullets[:]:
            b['x'] = (b['x'] + b['vx']) % cw
            b['y'] = (b['y'] + b['vy']) % ch
            b['life'] -= 1
            if b['life'] <= 0: self.bullets.remove(b)
            
        # Update asteroids
        for a in self.asteroids:
            a['x'] = (a['x'] + a['vx']) % cw
            a['y'] = (a['y'] + a['vy']) % ch
            
            # Collision with player
            dist = math.sqrt((a['x']-self.player_x)**2 + (a['y']-self.player_y)**2)
            if dist < a['size'] + 10:
                self.lives -= 1
                self.player_x, self.player_y = cw / 2, ch / 2
                self.player_vel_x, self.player_vel_y = 0, 0
                if self.lives <= 0:
                    self.game_active = False
                    self.db.save_high_score(self.score, self.round_num)
                    self.refresh_leaderboard()
                    messagebox.showinfo("GAME OVER", f"Your fleet was overwhelmed.\nScore: {self.score}\nRound: {self.round_num}")
                    return

        # Bullet-Asteroid collision
        for b in self.bullets[:]:
            for a in self.asteroids[:]:
                dist = math.sqrt((b['x']-a['x'])**2 + (b['y']-a['y'])**2)
                if dist < a['size']:
                    if a['size'] > 15:
                        # Split asteroid
                        for _ in range(2):
                            self.asteroids.append({
                                'x': a['x'], 'y': a['y'],
                                'vx': a['vx'] + random.uniform(-1, 1),
                                'vy': a['vy'] + random.uniform(-1, 1),
                                'size': a['size'] / 2
                            })
                    self.asteroids.remove(a)
                    if b in self.bullets: self.bullets.remove(b)
                    self.score += 100
                    break
        
        if not self.asteroids:
            self.round_num += 1
            self.spawn_asteroids()
            
        self.draw_game()
        if self.score > self.high_score: self.high_score = self.score
        self.game_canvas.after(30, self.update_asteroids_game)

    def draw_game(self):
        self.game_canvas.delete("all")
        
        angle_rad = math.radians(self.player_angle)
        px1 = self.player_x + 12 * math.cos(angle_rad)
        py1 = self.player_y - 12 * math.sin(angle_rad)
        px2 = self.player_x + 10 * math.cos(angle_rad + 2.5)
        py2 = self.player_y - 10 * math.sin(angle_rad + 2.5)
        px3 = self.player_x + 10 * math.cos(angle_rad - 2.5)
        py3 = self.player_y - 10 * math.sin(angle_rad - 2.5)
        self.game_canvas.create_polygon(px1, py1, px2, py2, px3, py3, fill=PT_NEON_EMERALD, outline=PT_NEON_EMERALD, width=2)
        
        for bullet in self.bullets:
            self.game_canvas.create_oval(bullet['x']-3, bullet['y']-3, bullet['x']+3, bullet['y']+3, fill=PT_GRID_CYAN, outline=PT_GRID_CYAN)
        
        for asteroid in self.asteroids:
            self.game_canvas.create_oval(asteroid['x']-asteroid['size'], asteroid['y']-asteroid['size'],
                                        asteroid['x']+asteroid['size'], asteroid['y']+asteroid['size'],
                                        fill=PT_AMBER_ALERT, outline=PT_AMBER_ALERT, width=2)
        
        self.score_label.config(text=f"SCORE: {self.score}  |  HIGH SCORE: {self.high_score}  |  ROUND: {self.round_num}  |  LIVES: {self.lives}")

    def toggle_dark_matter(self):
        self.dark_matter_clicks += 1
        
        if self.dark_matter_clicks >= 3:
            self.dark_matter_mode = not self.dark_matter_mode
            self.dark_matter_clicks = 0
            
            if self.dark_matter_mode:
                self.trigger_rift_effect()
                
                if self.asteroids_tab_index is None:
                    self.asteroids_tab_index = self.notebook.add(self.asteroids_tab, text="THE VOID")
                
                self.hidden_btn.config(fg=PT_PLASMA_RED)
            else:
                if self.asteroids_tab_index is not None:
                    self.notebook.forget(self.asteroids_tab_index)
                    self.asteroids_tab_index = None
                
                self.hidden_btn.config(fg=PT_NEON_EMERALD)

    def trigger_rift_effect(self):
        """Trigger an intense glitch/rift effect when easter egg is activated"""
        glitch_window = tk.Toplevel(self.root)
        glitch_window.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}+{self.root.winfo_x()}+{self.root.winfo_y()}")
        glitch_window.configure(bg=PT_VOID_BLACK)
        glitch_window.attributes('-topmost', True)
        
        glitch_label = tk.Label(glitch_window, text="RIFT DETECTED\n\nREALITY FRACTURING", 
                               bg=PT_VOID_BLACK, fg=PT_PLASMA_RED, font=("Courier", 24, "bold"))
        glitch_label.pack(expand=True)
        
        for i in range(12):
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-40, 40)
            
            glitch_color = random.choice([PT_PLASMA_RED, PT_GRID_CYAN, PT_NEON_EMERALD, PT_VOID_BLACK])
            glitch_label.config(fg=glitch_color)
            
            self.root.geometry(f"+{self.root.winfo_x() + offset_x}+{self.root.winfo_y() + offset_y}")
            glitch_window.geometry(f"+{glitch_window.winfo_x() + offset_x}+{glitch_window.winfo_y() + offset_y}")
            
            self.root.update()
            glitch_window.update()
            time.sleep(0.08)
        
        self.root.geometry(f"+{self.root.winfo_x()}+{self.root.winfo_y()}")
        glitch_window.destroy()
        
        messagebox.showinfo("RIFT ACTIVATED", 
            "The void has opened.\n\n"
            "Your database is now aware.\n\n"
            "A new tab has manifested in the depths...\n\n"
            "Welcome to THE VOID.\n\n"
            "Asteroids await.")

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.configure(bg=PT_OBSIDIAN)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = 500, 300
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        # v5.5: Official Name Update
        tk.Label(self.root, text="PulseTracker", font=("Courier", 32, "bold"), bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD).pack(pady=(60, 5))
        tk.Label(self.root, text="ASSET MANAGEMENT SYSTEM", font=("Courier", 12, "bold"), bg=PT_OBSIDIAN, fg=PT_AMBER_ALERT).pack()
        # v5.5: Update version in splash screen
        tk.Label(self.root, text="v5.5", font=("Courier", 8), bg=PT_OBSIDIAN, fg=PT_GRID_CYAN).pack()
        self.status = tk.Label(self.root, text="INITIALIZING FLEET DATABASE...", font=("Courier", 10), bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD)
        self.status.pack(pady=40)

    def update_status(self, text):
        self.status.config(text=text.upper())
        self.root.update()
