import json
#Ai helped partially with the optout function since I am unfamiliar with how it works and interacts within Slack
from purrbot.optout import OptOutStore


def test_new_store_starts_empty(tmp_path):
    store = OptOutStore(str(tmp_path / "optouts.json"))
    assert not store.is_opted_out("U1") 


def test_add_and_remove(tmp_path):
    store = OptOutStore(str(tmp_path / "optouts.json"))
    store.add("U1")
    assert store.is_opted_out("U1")
    store.remove("U1")
    assert not store.is_opted_out("U1")


def test_persists_across_instances(tmp_path):
    path = tmp_path / "optouts.json"
    first =  OptOutStore(str(path))
    first.add("U1")
    second = OptOutStore(str(path))
    assert second.is_opted_out("U1")


def test_add_add_remove_are_idempotent(tmp_path):
    path = tmp_path / "optouts.json"
    store = OptOutStore(str(path))
    store.add("U1")
    store.add("U1")
    assert json.loads(path.read_text()) == ["U1"]
    store.remove("U1")
    store.remove("U1")
    assert json.loads(path.read_text()) == []


def test_file_content_is_sorted_json(tmp_path):
    path = tmp_path / "optouts.json"
    store = OptOutStore(str(path))
    store.add("U2")
    store.add("U1")
    assert json.loads(path.read_text()) == ["U1", "U2"]


def test_corrupted_file_starts_empty(tmp_path):
    path = tmp_path / "optouts.json"
    path.write_text("{not json")
    store = OptOutStore(str(path))
    assert not store.is_opted_out("U1")
    store.add("U1")
    assert json.loads(path.read_text()) == ["U1"]