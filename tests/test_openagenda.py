"""Tests unitaires pour la recuperation des donnees OpenAgenda"""
from unittest.mock import patch

from src.data.openagenda_client import fetch_events


class FakeResponse:
    """Reponse HTTP simulee (evite un vrai appel reseau pendant les tests)"""
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_fetch_events_pagine_et_sarrete_sur_page_vide():
    # 1ere page : 2 evenements, 2eme page vide -> la boucle doit s'arreter
    pages = [
        FakeResponse({"results": [{"uid": "1"}, {"uid": "2"}]}),
        FakeResponse({"results": []}),
    ]
    with patch("src.data.openagenda_client.requests.get") as mock_get:
        mock_get.side_effect = pages
        events = fetch_events("Nouvelle-Aquitaine", "2025-01-01")

    assert len(events) == 2
    assert events[0]["uid"] == "1"


def test_fetch_events_respecte_max_events():
    # Une page pleine de 100 avec max_events=100 on ne fait qu'un seul appel
    full_page = FakeResponse({"results": [{"uid": str(i)} for i in range(100)]})
    with patch("src.data.openagenda_client.requests.get") as mock_get:
        mock_get.return_value = full_page
        events = fetch_events("Nouvelle-Aquitaine", "2025-01-01", max_events=100)

    assert len(events) == 100
    assert mock_get.call_count == 1
