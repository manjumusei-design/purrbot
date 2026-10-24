import json
#Ai helped partially with the optout function since I am unfamiliar with how it works and interacts within Slack
from purrbot.optout import OptOutStore

def test_new_store_starts_empty(tmp_path):
    store = OptOutStore(str(tmp_path / "optouts.json"))
    assert not store.is_opted_out("U1") 
    