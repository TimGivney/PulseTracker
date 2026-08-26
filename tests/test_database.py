import os
import tempfile
import sqlite3
import pytest
import pandas as pd
from database import DatabaseManager

@pytest.fixture
def db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_pulsetracker.db")
        db_mgr = DatabaseManager(db_path)
        yield db_mgr

def test_add_and_get_equipment(db):
    data = {
        'name': 'Test Drilling Rig',
        'serial_number': 'DR-999',
        'location': 'Site A',
        'status': 'Active',
        'owner_company': 'Apex Mining'
    }
    equip_id = db.add_equipment(data)
    assert equip_id > 0

    equip = db.get_equipment_by_id(equip_id)
    assert equip['name'] == 'Test Drilling Rig'
    assert equip['serial_number'] == 'DR-999'

def test_search_and_filter_equipment(db):
    db.add_equipment({'name': 'Excavator Alpha', 'serial_number': 'EX-01', 'status': 'Active', 'location': 'North Quarry'})
    db.add_equipment({'name': 'Hauler Beta', 'serial_number': 'HB-02', 'status': 'Maintenance', 'location': 'South Workshop'})

    # Search query
    results = db.search_equipment(query="Excavator")
    assert len(results) == 1
    assert results[0]['serial_number'] == 'EX-01'

    # Filter status
    results_maint = db.search_equipment(status_filter="Maintenance")
    assert len(results_maint) == 1
    assert results_maint[0]['name'] == 'Hauler Beta'

def test_update_equipment(db):
    equip_id = db.add_equipment({'name': 'Pump Unit', 'serial_number': 'PU-100', 'status': 'Active'})
    db.update_equipment(equip_id, {'status': 'Retired', 'location': 'Decommissioned Yard'})

    updated = db.get_equipment_by_id(equip_id)
    assert updated['status'] == 'Retired'
    assert updated['location'] == 'Decommissioned Yard'

def test_delete_equipment_and_attachments(db):
    equip_id = db.add_equipment({'name': 'Generator', 'serial_number': 'GEN-50'})

    # Create sample attachment
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"sample manual content")
        tmp_file_path = tmp_file.name

    try:
        att_id = db.add_attachment(equip_id, "manual.txt", tmp_file_path)
        attachments = db.get_attachments(equip_id)
        assert len(attachments) == 1

        db.delete_equipment(equip_id)
        assert db.get_equipment_by_id(equip_id) is None
        assert len(db.get_attachments(equip_id)) == 0
    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

def test_delete_attachment(db):
    equip_id = db.add_equipment({'name': 'Crusher', 'serial_number': 'CR-10'})
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"spec document")
        tmp_file_path = tmp_file.name

    try:
        att_id = db.add_attachment(equip_id, "spec.pdf", tmp_file_path)
        assert len(db.get_attachments(equip_id)) == 1

        db.delete_attachment(att_id)
        assert len(db.get_attachments(equip_id)) == 0
    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

def test_high_scores(db):
    db.save_high_score(1500, 3, player_name="Ace")
    db.save_high_score(3000, 5, player_name="Star")

    scores = db.get_top_scores(limit=5)
    assert len(scores) == 2
    assert scores[0]['player_name'] == 'Star'
    assert scores[0]['score'] == 3000

def test_export_all_equipment(db):
    db.add_equipment({'name': 'Conveyor A', 'serial_number': 'CV-01'})
    df = db.export_all_equipment()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]['serial_number'] == 'CV-01'
