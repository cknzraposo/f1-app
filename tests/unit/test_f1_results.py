from app import f1_results


def test_fetch_season_results_paginates_and_merges_race_results(monkeypatch):
    pages = [
        {
            "MRData": {
                "limit": "2",
                "offset": "0",
                "total": "3",
                "RaceTable": {
                    "season": "2025",
                    "Races": [
                        {
                            "season": "2025",
                            "round": "1",
                            "Results": [
                                {"Driver": {"driverId": "driver_a"}},
                                {"Driver": {"driverId": "driver_b"}},
                            ],
                        }
                    ],
                },
            }
        },
        {
            "MRData": {
                "limit": "2",
                "offset": "2",
                "total": "3",
                "RaceTable": {
                    "season": "2025",
                    "Races": [
                        {
                            "season": "2025",
                            "round": "1",
                            "Results": [
                                {"Driver": {"driverId": "driver_b"}},
                                {"Driver": {"driverId": "driver_c"}},
                            ],
                        }
                    ],
                },
            }
        },
    ]
    requested_offsets = []

    def get_page(url, params):
        requested_offsets.append(params["offset"])
        return pages.pop(0)

    monkeypatch.setattr(f1_results, "_get", get_page)

    result = f1_results.fetch_season_results(2025)

    races = result["MRData"]["RaceTable"]["Races"]
    assert requested_offsets == [0, 2]
    assert len(races) == 1
    assert [row["Driver"]["driverId"] for row in races[0]["Results"]] == [
        "driver_a",
        "driver_b",
        "driver_c",
    ]
