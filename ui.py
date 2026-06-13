import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import sys
import random
import math
import time
from PIL import Image, ImageTk, ImageDraw

# PulseTracker v5.0 - Starship Command Center
PT_OBSIDIAN = "#0A0E27"
PT_DEEP_SPACE = "#1A1F3A"
PT_NEON_EMERALD = "#00FF88"
PT_AMBER_ALERT = "#FFB700"
PT_PLASMA_RED = "#FF0055"
PT_VOID_BLACK = "#000000"
PT_GRID_CYAN = "#00FFFF"
PT_OFF_WHITE = "#E8E8E8"

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
        self.root.title("PULSETRACKER v5.0 - COMMAND CENTER")
        self.root.geometry("1600x1000")
        self.root.configure(bg=PT_OBSIDIAN)
        
        self.dark_matter_mode = False
        self.dark_matter_clicks = 0
        self.style = ttk.Style()
        self.apply_styles()
        
        self.setup_ui()
        self.refresh_equipment()

    def apply_styles(self):
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=PT_DEEP_SPACE, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=PT_DEEP_SPACE, foreground=PT_NEON_EMERALD, font=("Courier", 12, "bold"), padding=[15, 10])
        self.style.map("TNotebook.Tab", background=[("selected", PT_OBSIDIAN)], foreground=[("selected", PT_AMBER_ALERT)])
        self.style.configure("Treeview", background=PT_VOID_BLACK, fieldbackground=PT_VOID_BLACK, foreground=PT_NEON_EMERALD, font=("Courier", 11), rowheight=40)
        self.style.configure("Treeview.Heading", background=PT_DEEP_SPACE, foreground=PT_AMBER_ALERT, font=("Courier", 11, "bold"))

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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

        # Footer
        footer = tk.Frame(self.root, bg=PT_OBSIDIAN, height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.trigger_frame = tk.Frame(footer, bg=PT_OBSIDIAN)
        self.trigger_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(self.trigger_frame, text="SYSTEM STATUS: OPTIMAL", bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD, font=("Courier", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.hidden_btn = tk.Button(self.trigger_frame, text="●", bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD, bd=0, 
                                   command=self.toggle_dark_matter, activebackground=PT_OBSIDIAN,
                                   font=("Courier", 12), cursor="hand2")
        self.hidden_btn.pack(side=tk.LEFT, padx=2)

    def setup_equipment_view(self):
        header = tk.Frame(self.equip_tab, bg=PT_OBSIDIAN)
        header.pack(fill=tk.X, pady=15, padx=20)
        tk.Label(header, text="FLEET ASSETS", font=("Courier", 24, "bold"), 
                 bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD).pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(self.equip_tab, bg=PT_OBSIDIAN)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(btn_frame, text="+ ADD TO FLEET", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK, 
                 font=("Courier", 12, "bold"), command=self.open_add_to_fleet, padx=20, pady=10).pack(side=tk.LEFT, padx=5)

        self.equip_tree = ttk.Treeview(self.equip_tab, columns=("ID", "Name", "Serial", "Owner", "Status", "Location"), show="headings", height=20)
        self.equip_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.equip_tree.bind("<Double-1>", self.on_equipment_double_click)
        
        for col in ("ID", "Name", "Serial", "Owner", "Status", "Location"):
            self.equip_tree.heading(col, text=col.upper())
            self.equip_tree.column(col, width=140)

    def open_add_to_fleet(self):
        window = tk.Toplevel(self.root)
        window.title("ADD TO FLEET - COMMAND CENTER")
        window.geometry("1000x900")
        window.configure(bg=PT_OBSIDIAN)
        
        nb = ttk.Notebook(window)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
        
        tk.Button(window, text="COMMIT TO FLEET", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK, 
                 font=("Courier", 13, "bold"), command=lambda: self.save_equipment(window), padx=20, pady=12).pack(fill=tk.X, padx=10, pady=10)

    def create_basic_info_fields(self, frame):
        fields = [
            ("EQUIPMENT NAME:", "equip_name"),
            ("SERIAL NUMBER:", "serial"),
            ("LOCATION:", "location"),
        ]
        self.basic_entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 13, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=12)
            entry = tk.Entry(frame, width=60, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 12), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=12)
            self.basic_entries[key] = entry

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
            tk.Label(frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 13, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=12)
            entry = tk.Entry(frame, width=60, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 12), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=12)
            self.prod_entries[key] = entry
        
        tk.Label(frame, text="QA STATUS:", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 13, "bold")).grid(row=5, column=0, sticky=tk.W, padx=15, pady=12)
        self.qa_var = tk.StringVar(value="Passed")
        qa_combo = ttk.Combobox(frame, textvariable=self.qa_var, values=["Passed", "Hold", "Rework"], width=57, font=("Courier", 12))
        qa_combo.grid(row=5, column=1, padx=15, pady=12)

    def create_sales_fields(self, frame):
        tk.Label(frame, text="SALE STATUS:", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 13, "bold")).grid(row=0, column=0, sticky=tk.W, padx=15, pady=12)
        self.sale_status_var = tk.StringVar(value="Sold")
        sale_combo = ttk.Combobox(frame, textvariable=self.sale_status_var, values=["Unsold", "Quoted", "Sold", "Delivered"], width=57, font=("Courier", 12))
        sale_combo.grid(row=0, column=1, padx=15, pady=12)
        
        tk.Label(frame, text="LIFECYCLE STATUS:", bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 13, "bold")).grid(row=1, column=0, sticky=tk.W, padx=15, pady=12)
        self.status_var = tk.StringVar(value="Active")
        status_combo = ttk.Combobox(frame, textvariable=self.status_var, values=["In Production", "Built", "In Stock", "Active", "Maintenance", "Retired"], width=57, font=("Courier", 12))
        status_combo.grid(row=1, column=1, padx=15, pady=12)
        
        fields = [
            ("SALE DATE:", "sale_date"),
            ("INVOICE #:", "invoice"),
            ("WARRANTY END DATE:", "warranty"),
        ]
        self.sales_entries = {}
        for i, (label, key) in enumerate(fields, start=2):
            tk.Label(frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 13, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=12)
            entry = tk.Entry(frame, width=60, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 12), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=12)
            self.sales_entries[key] = entry

    def create_owner_fields(self, frame):
        fields = [
            ("INDIVIDUAL OWNER:", "owner_individual"),
            ("COMPANY OWNER:", "owner_company"),
            ("OWNER NOTES:", "owner_notes"),
        ]
        self.owner_entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 13, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=12)
            if key == "owner_notes":
                entry = tk.Text(frame, width=60, height=8, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 11), insertbackground=PT_NEON_EMERALD)
            else:
                entry = tk.Entry(frame, width=60, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 12), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=12)
            self.owner_entries[key] = entry

    def create_billing_shipping_fields(self, frame):
        # Billing Section
        tk.Label(frame, text="BILLING ADDRESS", bg=PT_DEEP_SPACE, fg=PT_PLASMA_RED, font=("Courier", 13, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=15, pady=12)
        
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
            tk.Label(frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=10)
            entry = tk.Entry(frame, width=60, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 11), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=10)
            self.billing_entries[key] = entry
        
        # Shipping Section
        tk.Label(frame, text="SHIPPING ADDRESS", bg=PT_DEEP_SPACE, fg=PT_PLASMA_RED, font=("Courier", 13, "bold")).grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=15, pady=12)
        
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
            tk.Label(frame, text=label, bg=PT_DEEP_SPACE, fg=PT_AMBER_ALERT, font=("Courier", 12, "bold")).grid(row=i, column=0, sticky=tk.W, padx=15, pady=10)
            entry = tk.Entry(frame, width=60, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 11), insertbackground=PT_NEON_EMERALD)
            entry.grid(row=i, column=1, padx=15, pady=10)
            self.shipping_entries[key] = entry

    def create_attachments_section(self, frame, window):
        tk.Label(frame, text="ATTACH FILES (Drawings, Reports, Certificates, etc.)", bg=PT_DEEP_SPACE, fg=PT_NEON_EMERALD, font=("Courier", 12, "bold")).pack(pady=10)
        
        btn_frame = tk.Frame(frame, bg=PT_DEEP_SPACE)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="+ ADD FILE", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK, 
                 font=("Courier", 11, "bold"), command=lambda: self.add_attachment_file(frame)).pack(side=tk.LEFT, padx=5)
        
        self.attachment_listbox = tk.Listbox(frame, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, height=12, font=("Courier", 11))
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
                'owner_notes': self.owner_entries['owner_notes'].get("1.0", tk.END),
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
                messagebox.showwarning("Incomplete", "Equipment Name and Serial Number are required.")
                return
            
            equip_id = self.db.add_equipment(data)
            
            for filename, filepath in self.attached_files:
                self.db.add_attachment(equip_id, filename, filepath)
            
            self.refresh_equipment()
            window.destroy()
            
            if self.dark_matter_mode:
                remark = random.choice(TIRED_AI_REMARKS).format(n=len(self.equip_tree.get_children()))
                messagebox.showinfo("Added", remark)
            else:
                messagebox.showinfo("Success", "Asset committed to fleet.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def on_equipment_double_click(self, event):
        item = self.equip_tree.selection()[0]
        values = self.equip_tree.item(item)['values']
        equip_id = values[0]
        self.open_equipment_details(equip_id)

    def open_equipment_details(self, equip_id):
        equip = self.db.get_equipment_by_id(equip_id)
        if not equip:
            messagebox.showerror("Error", "Equipment not found.")
            return
        
        window = tk.Toplevel(self.root)
        window.title(f"ASSET DETAILS - {equip[1]}")
        window.geometry("1000x900")
        window.configure(bg=PT_OBSIDIAN)
        
        text_widget = tk.Text(window, bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 10), wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        details = f"""
ASSET DETAILS - COMMAND CENTER
{'='*90}

BASIC INFORMATION
  Name: {equip[1]}
  Serial Number: {equip[2]}
  Location: {equip[20]}
  Created: {equip[30]}

PRODUCTION
  Manufacture Date: {equip[3] or 'N/A'}
  Manufacture Location: {equip[4] or 'N/A'}
  Batch ID: {equip[5] or 'N/A'}
  Batch Size: {equip[6] or 'N/A'}
  Job Number: {equip[7] or 'N/A'}
  QA Status: {equip[8] or 'N/A'}

SALES & STATUS
  Sale Status: {equip[9] or 'N/A'}
  Sale Date: {equip[10] or 'N/A'}
  Invoice Number: {equip[11] or 'N/A'}
  Warranty End: {equip[12] or 'N/A'}
  Install Date: {equip[13] or 'N/A'}
  Lifecycle Status: {equip[14] or 'N/A'}

OWNER INFORMATION
  Individual Owner: {equip[15] or 'N/A'}
  Company Owner: {equip[16] or 'N/A'}
  Owner Notes:
{equip[17] or 'N/A'}

BILLING DETAILS
  Address: {equip[21] or 'N/A'}
  Suburb: {equip[22] or 'N/A'}
  State: {equip[23] or 'N/A'}
  Postcode: {equip[24] or 'N/A'}
  Country: {equip[25] or 'N/A'}
  Payment Methods: {equip[26] or 'N/A'}

SHIPPING DETAILS
  Address: {equip[27] or 'N/A'}
  Suburb: {equip[28] or 'N/A'}
  State: {equip[29] or 'N/A'}
  Postcode: {equip[30] or 'N/A'}
  Country: {equip[31] or 'N/A'}
  Parts Destination: {equip[32] or 'N/A'}
"""
        text_widget.insert(tk.END, details)
        text_widget.config(state=tk.DISABLED)

    def refresh_equipment(self):
        try:
            for item in self.equip_tree.get_children():
                self.equip_tree.delete(item)
            
            equipment_list = self.db.get_all_equipment()
            for equip in equipment_list:
                equip_id = equip[0]
                name = equip[1]
                serial = equip[2]
                owner = equip[15] or equip[16] or "N/A"
                status = equip[14]
                location = equip[20]
                
                self.equip_tree.insert("", "end", values=(equip_id, name, serial, owner, status, location))
        except Exception as e:
            print(f"Error refreshing equipment: {e}")

    def setup_analytics_view(self):
        header = tk.Frame(self.analytics_tab, bg=PT_OBSIDIAN)
        header.pack(fill=tk.X, pady=10, padx=20)
        tk.Label(header, text="FLEET ANALYTICS", font=("Courier", 20, "bold"), 
                 bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD).pack(side=tk.LEFT)
        
        charts_frame = tk.Frame(self.analytics_tab, bg=PT_OBSIDIAN)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        left_frame = tk.Frame(charts_frame, bg=PT_OBSIDIAN)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = tk.Frame(charts_frame, bg=PT_OBSIDIAN)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(left_frame, text="Assets by Individual Owner", bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD, font=("Courier", 12, "bold")).pack()
        self.individual_canvas = tk.Canvas(left_frame, bg=PT_VOID_BLACK, width=400, height=400, highlightthickness=2, highlightbackground=PT_NEON_EMERALD)
        self.individual_canvas.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="Assets by Company Owner", bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD, font=("Courier", 12, "bold")).pack()
        self.company_canvas = tk.Canvas(right_frame, bg=PT_VOID_BLACK, width=400, height=400, highlightthickness=2, highlightbackground=PT_NEON_EMERALD)
        self.company_canvas.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(self.analytics_tab, text="REFRESH ANALYTICS", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK,
                 font=("Courier", 11, "bold"), command=self.update_analytics).pack(pady=10)
        
        self.update_analytics()

    def update_analytics(self):
        try:
            df = self.db.get_owner_stats()
            individual_counts = df['owner_individual'].value_counts()
            self.draw_pie_chart(self.individual_canvas, individual_counts, PT_NEON_EMERALD)
            company_counts = df['owner_company'].value_counts()
            self.draw_pie_chart(self.company_canvas, company_counts, PT_AMBER_ALERT)
        except Exception as e:
            print(f"Error updating analytics: {e}")

    def draw_pie_chart(self, canvas, data, color):
        canvas.delete("all")
        if len(data) == 0:
            canvas.create_text(200, 200, text="No data available", fill=PT_OFF_WHITE, font=("Courier", 12))
            return
        
        width, height = 400, 400
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2 - 40
        
        total = data.sum()
        start_angle = 0
        colors = [PT_NEON_EMERALD, PT_AMBER_ALERT, PT_GRID_CYAN, PT_PLASMA_RED, PT_OFF_WHITE]
        
        for i, (owner, count) in enumerate(data.items()):
            angle = (count / total) * 360
            pie_color = colors[i % len(colors)]
            canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                            start=start_angle, extent=angle, fill=pie_color, outline=PT_DEEP_SPACE, width=2)
            
            label_angle = start_angle + angle / 2
            label_rad = math.radians(label_angle)
            label_x = center_x + (radius * 0.7) * math.cos(label_rad)
            label_y = center_y + (radius * 0.7) * math.sin(label_rad)
            label_text = f"{owner or 'Unassigned'}\n{count}"
            canvas.create_text(label_x, label_y, text=label_text, fill=PT_VOID_BLACK, font=("Courier", 9, "bold"))
            start_angle += angle

    def setup_asteroids_view(self):
        self.asteroids_frame = tk.Frame(self.asteroids_tab, bg=PT_VOID_BLACK)
        self.asteroids_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.asteroids_frame, text="THE VOID - ASTEROIDS", bg=PT_VOID_BLACK, fg=PT_PLASMA_RED, 
                font=("Courier", 18, "bold")).pack(pady=10)
        
        self.game_canvas = tk.Canvas(self.asteroids_frame, bg=PT_VOID_BLACK, width=900, height=600, highlightthickness=2, highlightbackground=PT_NEON_EMERALD)
        self.game_canvas.pack(pady=10)
        
        info_frame = tk.Frame(self.asteroids_frame, bg=PT_VOID_BLACK)
        info_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(info_frame, text="ARROW KEYS: Move | SPACE: Shoot | ESC: Exit", 
                bg=PT_VOID_BLACK, fg=PT_NEON_EMERALD, font=("Courier", 11)).pack(side=tk.LEFT)
        
        self.score_label = tk.Label(info_frame, text="SCORE: 0  |  HIGH SCORE: 0  |  ROUND: 1  |  LIVES: 1", 
                                   bg=PT_VOID_BLACK, fg=PT_AMBER_ALERT, font=("Courier", 11, "bold"))
        self.score_label.pack(side=tk.RIGHT)
        
        self.game_active = False
        self.player_x = 450
        self.player_y = 500
        self.player_angle = 0
        self.score = 0
        self.high_score = 0
        self.round_num = 1
        self.lives = 1
        self.bullets = []
        self.asteroids = []
        self.keys_pressed = set()
        
        self.game_canvas.bind("<KeyPress>", self.on_key_press)
        self.game_canvas.bind("<KeyRelease>", self.on_key_release)
        self.game_canvas.focus()
        
        tk.Button(self.asteroids_frame, text="START GAME", bg=PT_AMBER_ALERT, fg=PT_VOID_BLACK,
                 font=("Courier", 12, "bold"), command=self.start_asteroids_game).pack(pady=5)

    def start_asteroids_game(self):
        self.game_active = True
        self.score = 0
        self.round_num = 1
        self.lives = 1
        self.bullets = []
        self.asteroids = []
        self.player_x = 450
        self.player_y = 500
        self.player_angle = 0
        
        for _ in range(3 + self.round_num):
            self.asteroids.append({
                'x': random.randint(50, 850),
                'y': random.randint(50, 200),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(1, 3),
                'size': 30,
                'health': 1
            })
        
        self.update_asteroids_game()

    def on_key_press(self, event):
        self.keys_pressed.add(event.keysym)
        if event.keysym == 'space':
            self.shoot_bullet()
        elif event.keysym == 'Escape':
            self.game_active = False
            self.game_canvas.delete("all")

    def on_key_release(self, event):
        self.keys_pressed.discard(event.keysym)

    def shoot_bullet(self):
        if self.game_active:
            angle_rad = math.radians(self.player_angle)
            vx = 7 * math.cos(angle_rad)
            vy = -7 * math.sin(angle_rad)
            self.bullets.append({'x': self.player_x, 'y': self.player_y, 'vx': vx, 'vy': vy})

    def update_asteroids_game(self):
        if not self.game_active:
            return
        
        if 'Left' in self.keys_pressed:
            self.player_angle = (self.player_angle - 5) % 360
        if 'Right' in self.keys_pressed:
            self.player_angle = (self.player_angle + 5) % 360
        if 'Up' in self.keys_pressed:
            angle_rad = math.radians(self.player_angle)
            self.player_x += 2.5 * math.cos(angle_rad)
            self.player_y -= 2.5 * math.sin(angle_rad)
        
        self.player_x = self.player_x % 900
        self.player_y = self.player_y % 600
        
        self.bullets = [b for b in self.bullets if 0 <= b['x'] <= 900 and 0 <= b['y'] <= 600]
        for bullet in self.bullets:
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
        
        for asteroid in self.asteroids:
            asteroid['x'] += asteroid['vx']
            asteroid['y'] += asteroid['vy']
            if asteroid['x'] < 0 or asteroid['x'] > 900:
                asteroid['vx'] *= -1
            if asteroid['y'] < 0 or asteroid['y'] > 600:
                asteroid['vy'] *= -1
        
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                dist = ((bullet['x'] - asteroid['x'])**2 + (bullet['y'] - asteroid['y'])**2)**0.5
                if dist < asteroid['size']:
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.score += 10 * (2 - asteroid['size'] // 20)
                    
                    if asteroid['size'] > 15:
                        for _ in range(2):
                            self.asteroids.append({
                                'x': asteroid['x'],
                                'y': asteroid['y'],
                                'vx': random.uniform(-3, 3),
                                'vy': random.uniform(-3, 3),
                                'size': asteroid['size'] // 2,
                                'health': 1
                            })
                    break
        
        for asteroid in self.asteroids:
            dist = ((self.player_x - asteroid['x'])**2 + (self.player_y - asteroid['y'])**2)**0.5
            if dist < asteroid['size'] + 10:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_active = False
                    self.high_score = max(self.high_score, self.score)
                    self.db.save_high_score(self.score, self.round_num)
                    messagebox.showinfo("GAME OVER", f"Final Score: {self.score}\nRound: {self.round_num}\nHigh Score: {self.high_score}")
                    return
                self.asteroids = []
                self.round_num += 1
                for _ in range(3 + self.round_num):
                    self.asteroids.append({
                        'x': random.randint(50, 850),
                        'y': random.randint(50, 200),
                        'vx': random.uniform(-2 - self.round_num * 0.5, 2 + self.round_num * 0.5),
                        'vy': random.uniform(1, 3 + self.round_num * 0.3),
                        'size': 30,
                        'health': 1
                    })
        
        if len(self.asteroids) == 0:
            self.round_num += 1
            for _ in range(3 + self.round_num):
                self.asteroids.append({
                    'x': random.randint(50, 850),
                    'y': random.randint(50, 200),
                    'vx': random.uniform(-2 - self.round_num * 0.5, 2 + self.round_num * 0.5),
                    'vy': random.uniform(1, 3 + self.round_num * 0.3),
                    'size': 30,
                    'health': 1
                })
        
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
        
        if self.game_active:
            self.game_canvas.after(30, self.update_asteroids_game)

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
        """Trigger a glitch/rift effect when easter egg is activated"""
        messagebox.showinfo("RIFT DETECTED", 
            "You've found the void.\n\n"
            "The database is now watching you.\n\n"
            "A new tab has appeared in the depths...\n\n"
            "Welcome to the Asteroids.")
        
        for _ in range(5):
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            self.root.geometry(f"+{self.root.winfo_x() + offset_x}+{self.root.winfo_y() + offset_y}")
            self.root.update()
            time.sleep(0.05)
        
        self.root.geometry(f"+{self.root.winfo_x()}+{self.root.winfo_y()}")

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.configure(bg=PT_OBSIDIAN)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = 500, 300
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        tk.Label(self.root, text="PULSETRACKER", font=("Courier", 32, "bold"), bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD).pack(pady=(60, 5))
        tk.Label(self.root, text="COMMAND CENTER ONLINE", font=("Courier", 12, "bold"), bg=PT_OBSIDIAN, fg=PT_AMBER_ALERT).pack()
        self.status = tk.Label(self.root, text="INITIALIZING FLEET DATABASE...", font=("Courier", 10), bg=PT_OBSIDIAN, fg=PT_NEON_EMERALD)
        self.status.pack(pady=40)

    def update_status(self, text):
        self.status.config(text=text.upper())
        self.root.update()
