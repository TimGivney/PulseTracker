import os
import tempfile
import pytest
import tkinter as tk
from unittest.mock import patch
from database import DatabaseManager
from ui import PulseTrackerApp

@pytest.fixture
def app_instance():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "ui_test.db")
        db_mgr = DatabaseManager(db_path)
        root = tk.Tk()
        root.withdraw()
        with patch("tkinter.messagebox.showinfo"), patch("tkinter.messagebox.showwarning"), patch("tkinter.messagebox.showerror"), patch("tkinter.messagebox.askyesno", return_value=True):
            app = PulseTrackerApp(root, db_mgr)
            yield app, db_mgr, root
        root.destroy()

def test_app_initialization(app_instance):
    app, db, root = app_instance
    assert "PulseTracker" in root.title()
    assert hasattr(app, "equip_tree")

def test_add_and_refresh_equipment_ui(app_instance):
    app, db, root = app_instance
    db.add_equipment({
        'name': 'Rig 101',
        'serial_number': 'R-101',
        'location': 'Zone A',
        'status': 'Active',
        'owner_company': 'Mining Corp'
    })
    app.refresh_equipment()
    items = app.equip_tree.get_children()
    assert len(items) == 1
    vals = app.equip_tree.item(items[0], 'values')
    assert vals[1] == 'Rig 101'
    assert vals[2] == 'R-101'

def test_search_and_filter_ui(app_instance):
    app, db, root = app_instance
    db.add_equipment({'name': 'Alpha Unit', 'serial_number': 'SN-001', 'status': 'Active'})
    db.add_equipment({'name': 'Beta Loader', 'serial_number': 'SN-002', 'status': 'Maintenance'})

    app.search_var.set("Alpha")
    app.refresh_equipment()
    items = app.equip_tree.get_children()
    assert len(items) == 1

    app.search_var.set("")
    app.status_filter_var.set("Maintenance")
    app.refresh_equipment()
    items = app.equip_tree.get_children()
    assert len(items) == 1

    app.reset_search_filter()
    assert len(app.equip_tree.get_children()) == 2

def test_dark_matter_toggle(app_instance):
    app, db, root = app_instance
    assert app.dark_matter_mode is False
    with patch("ui.messagebox.showinfo"), patch("ui.time.sleep"):
        for _ in range(3):
            app.toggle_dark_matter()
    assert app.dark_matter_mode is True
