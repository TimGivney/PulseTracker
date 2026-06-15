import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import sys
import random
import math
import time
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

    def setup_equipment_view(self):
        self.equip_tab.grid_rowconfigure(1, weight=1)
        self.equip_tab.grid_columnconfigure(0, weight=1)
        
        header = tk.Frame(self.equip_tab, bg=PT_OBSIDIAN)
        header.grid(row=0, column=0, sticky="ew", pady=10, padx=15)
        tk.Label(header, text="FLEET ASSETS", font=("Courier", 20, "bold"), 
                 bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD).pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(self.equip_tab, bg=PT_OBSIDIAN)
        btn_frame.grid(row=0, column=0, sticky="e", padx=15, pady=10)
        tk.Button(btn_frame, text="+ ADD TO FLEET", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK, 
                 font=("Courier", 11, "bold"), command=self.open_add_to_fleet, padx=15, pady=8).pack(side=tk.RIGHT, padx=5)

        tree_frame = tk.Frame(self.equip_tab, bg=PT_OBSIDIAN)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
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

    def create_basic_info_fields(self, frame):
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
        
        frame.grid_columnconfigure(1, weight=1)

    def create_production_fields(self, frame):
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
        
        tk.Label(frame, text="QA STATUS:", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=5, column=0, sticky=tk.W, padx=15, pady=12)
        self.qa_var = tk.StringVar(value="Passed")
        qa_combo = ttk.Combobox(frame, textvariable=self.qa_var, values=["Passed", "Hold", "Rework"], width=47, font=("Courier", 11))
        qa_combo.grid(row=5, column=1, padx=15, pady=12, sticky="ew")
        
        frame.grid_columnconfigure(1, weight=1)

    def create_sales_fields(self, frame):
        tk.Label(frame, text="SALE STATUS:", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=0, column=0, sticky=tk.W, padx=15, pady=12)
        self.sale_status_var = tk.StringVar(value="Sold")
        sale_combo = ttk.Combobox(frame, textvariable=self.sale_status_var, values=["Unsold", "Quoted", "Sold", "Delivered"], width=47, font=("Courier", 11))
        sale_combo.grid(row=0, column=1, padx=15, pady=12, sticky="ew")
        
        tk.Label(frame, text="LIFECYCLE STATUS:", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=1, column=0, sticky=tk.W, padx=15, pady=12)
        self.status_var = tk.StringVar(value="Active")
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
        
        frame.grid_columnconfigure(1, weight=1)

    def create_owner_fields(self, frame):
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
        
        frame.grid_columnconfigure(1, weight=1)

    def create_billing_shipping_fields(self, frame):
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

    def save_equipment(self, window):
        try:
            data = {
                'name': self.basic_entries['equip_name'].get(),
                'serial_number': self.basic_entries['serial'].get(),
                'location': self.basic_entries['location'].get(),
                'manufacture_date': self.prod_entries['mfg_date'].get() or None,
                'manufacture_location': self.prod_entries['mfg_loc'].get(),
                'batch_id': self.prod_entries['batch_id'].get(),
                'batch_size': int(self.prod_entries['batch_size'].get() or 1),
                'job_number': self.prod_entries['job_num'].get(),
                'qa_status': self.qa_var.get(),
                'sale_status': self.sale_status_var.get(),
                'sale_date': self.sales_entries['sale_date'].get() or None,
                'invoice_number': self.sales_entries['invoice'].get(),
                'warranty_end': self.sales_entries['warranty'].get() or None,
                'install_date': datetime.now().strftime("%Y-%m-%d"),
                'status': self.status_var.get(),
                'owner_individual': self.owner_entries['owner_individual'].get(),
                'owner_company': self.owner_entries['owner_company'].get(),
                'owner_notes': self.owner_entries['owner_notes'].get("1.0", tk.END).strip(),
                'billing_address': self.billing_entries['billing_address'].get(),
                'billing_suburb': self.billing_entries['billing_suburb'].get(),
                'billing_state': self.billing_entries['billing_state'].get(),
                'billing_postcode': self.billing_entries['billing_postcode'].get(),
                'billing_country': self.billing_entries['billing_country'].get(),
                'payment_methods': self.billing_entries['payment_methods'].get(),
                'shipping_address': self.shipping_entries['shipping_address'].get(),
                'shipping_suburb': self.shipping_entries['shipping_suburb'].get(),
                'shipping_state': self.shipping_entries['shipping_state'].get(),
                'shipping_postcode': self.shipping_entries['shipping_postcode'].get(),
                'shipping_country': self.shipping_entries['shipping_country'].get(),
                'parts_destination': self.shipping_entries['parts_destination'].get(),
            }
            
            if not data['name'] or not data['serial_number']:
                messagebox.showwarning("Incomplete Data", "Name and Serial Number are mandatory for the fleet records.")
                return

            equip_id = self.db.add_equipment(data)
            
            for filename, filepath in self.attached_files:
                self.db.add_attachment(equip_id, filename, filepath)
            
            # v5.4: Professional messages unless Dark Matter Mode is active
            if self.dark_matter_mode:
                msg = random.choice(TIRED_AI_REMARKS).format(n=equip_id)
            else:
                msg = random.choice(PROFESSIONAL_REMARKS).format(n=equip_id)
                
            messagebox.showinfo("FLEET UPDATED", msg)
            self.refresh_equipment()
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("SYSTEM ERROR", f"Failed to commit to fleet: {str(e)}")

    def refresh_equipment(self):
        for item in self.equip_tree.get_children():
            self.equip_tree.delete(item)
        
        for equip in self.db.get_all_equipment():
            self.equip_tree.insert("", tk.END, values=(
                equip[0], equip[1], equip[2], equip[16] or equip[15], equip[14], equip[18]
            ))

    def on_equipment_double_click(self, event):
        item = self.equip_tree.selection()[0]
        equip_id = self.equip_tree.item(item, "values")[0]
        self.open_equipment_details(equip_id)

    def open_equipment_details(self, equip_id):
        equip = self.db.get_equipment_by_id(equip_id)
        if not equip: return
        
        window = tk.Toplevel(self.root)
        # v5.5: Official Name Update
        window.title(f"ASSET DETAILS: {equip[1]} - PulseTracker")
        window.geometry("1100x850")
        window.configure(bg=PT_OBSIDIAN)
        
        tk.Label(window, text=f"ASSET DETAILS: {equip[1]}", font=("Courier", 18, "bold"), bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD).pack(pady=10)
        
        details_frame = tk.Frame(window, bg=PT_DEEP_SPACE)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        info = [
            ("SERIAL:", equip[2]),
            ("LOCATION:", equip[18]),
            ("STATUS:", equip[14]),
            ("OWNER:", equip[15] or equip[16]),
            ("MFG DATE:", equip[3]),
            ("INVOICE:", equip[11]),
        ]
        
        for i, (label, val) in enumerate(info):
            tk.Label(details_frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=8)
            tk.Label(details_frame, text=val, bg=PT_DEEP_SPACE, fg=PT_OFF_WHITE, font=("Courier", 12)).grid(row=i, column=1, sticky=tk.W, padx=15, pady=8)

        tk.Label(window, text="ATTACHED FILES", bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD, font=("Courier", 12, "bold")).pack(pady=(20, 5))
        attach_list = tk.Listbox(window, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, height=6)
        attach_list.pack(fill=tk.X, padx=40, pady=5)
        
        attachments = self.db.get_attachments(equip_id)
        for att in attachments:
            attach_list.insert(tk.END, att[2])
            
        def download_attachment():
            if not attach_list.curselection(): return
            idx = attach_list.curselection()[0]
            att = attachments[idx]
            save_path = filedialog.asksaveasfilename(initialfile=att[2])
            if save_path:
                try:
                    import shutil
                    shutil.copy2(att[3], save_path)
                    messagebox.showinfo("SUCCESS", "File extracted from database.")
                except Exception as e:
                    messagebox.showerror("ERROR", f"Failed to extract file: {e}")

        tk.Button(window, text="EXTRACT SELECTED FILE", bg=PT_AMBER_ALERT, command=download_attachment).pack(pady=10)

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
        
        self.game_canvas = tk.Canvas(self.asteroids_tab, bg=PT_VOID_BLACK, highlightthickness=0)
        self.game_canvas.grid(row=0, column=0, sticky="nsew")
        
        self.score_label = tk.Label(self.asteroids_tab, text="SCORE: 0", bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 14, "bold"))
        self.score_label.grid(row=1, column=0, sticky="ew", pady=10)
        
        tk.Button(self.asteroids_tab, text="INITIALIZE COMBAT", bg=PT_PLASMA_RED, fg=PT_VOID_BLACK, 
                 font=("Courier", 12, "bold"), command=self.start_asteroids_game).grid(row=2, column=0, pady=10)
        
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

    def start_asteroids_game(self):
        if self.game_active: return
        self.game_active = True
        self.score = 0
        self.lives = 3
        self.round_num = 1
        self.asteroids = []
        self.bullets = []
        self.player_x = self.game_canvas.winfo_width() / 2
        self.player_y = self.game_canvas.winfo_height() / 2
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
        for _ in range(3 + self.round_num * 2):
            self.asteroids.append({
                'x': random.randint(0, 800),
                'y': random.randint(0, 600),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'size': random.randint(20, 40)
            })

    def update_asteroids_game(self):
        if not self.game_active: return
        
        # Update player position with momentum
        self.player_x = (self.player_x + self.player_vel_x) % self.game_canvas.winfo_width()
        self.player_y = (self.player_y + self.player_vel_y) % self.game_canvas.winfo_height()
        
        # Apply friction
        self.player_vel_x *= 0.98
        self.player_vel_y *= 0.98
        
        # Update bullets
        for b in self.bullets[:]:
            b['x'] = (b['x'] + b['vx']) % self.game_canvas.winfo_width()
            b['y'] = (b['y'] + b['vy']) % self.game_canvas.winfo_height()
            b['life'] -= 1
            if b['life'] <= 0: self.bullets.remove(b)
            
        # Update asteroids
        for a in self.asteroids:
            a['x'] = (a['x'] + a['vx']) % self.game_canvas.winfo_width()
            a['y'] = (a['y'] + a['vy']) % self.game_canvas.winfo_height()
            
            # Collision with player
            dist = math.sqrt((a['x']-self.player_x)**2 + (a['y']-self.player_y)**2)
            if dist < a['size'] + 10:
                self.lives -= 1
                self.player_x, self.player_y = 400, 300
                self.player_vel_x, self.player_vel_y = 0, 0
                if self.lives <= 0:
                    self.game_active = False
                    messagebox.showinfo("GAME OVER", f"Your fleet was overwhelmed. Score: {self.score}")
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
