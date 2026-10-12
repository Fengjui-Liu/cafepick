from datetime import datetime, timedelta

from app.models.sync_state import SyncState
from app.services import nomad_store
from tests.conftest import nomad_item


def test_save_then_nearby(temp_db):
    assert nomad_store.save([nomad_item(), nomad_item(id="n2", latitude="25.10", longitude="121.60")]) == 2
    found = nomad_store.nearby(25.0417, 121.5437, 0.08)
    assert [c["id"] for _, c in found] == ["n1"]
    assert found[0][1]["socket"] == 4.5


def test_save_is_upsert(temp_db):
    nomad_store.save([nomad_item()])
    nomad_store.save([nomad_item(wifi=1)])
    assert nomad_store.count() == 1
    assert nomad_store.nearby(25.0416, 121.5436, 0.01)[0][1]["wifi"] == 1


def test_sync_skips_when_fresh(temp_db, monkeypatch):
    calls = []
    monkeypatch.setattr(nomad_store, "fetch_raw", lambda: calls.append(1) or [nomad_item()])
    assert nomad_store.sync() == 1  # empty DB → stale
    assert nomad_store.sync() is None  # fresh → skipped
    assert len(calls) == 1


def test_sync_refreshes_after_a_day(temp_db, monkeypatch):
    monkeypatch.setattr(nomad_store, "fetch_raw", lambda: [nomad_item()])
    nomad_store.sync()
    db = temp_db()
    db.get(SyncState, nomad_store.SOURCE_KEY).synced_at = datetime.utcnow() - timedelta(hours=25)
    db.commit()
    db.close()
    assert nomad_store.is_stale()
    assert nomad_store.sync() == 1
