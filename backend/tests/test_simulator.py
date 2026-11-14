from vitalis.ingestion.simulator import ScenarioSimulator


def test_scenario_is_reproducible_and_explicitly_synthetic() -> None:
    first = ScenarioSimulator(seed=42).generate()
    second = ScenarioSimulator(seed=42).generate()

    assert len(first) == 35
    assert [(item.id, item.metric_id, item.value) for item in first] == [
        (item.id, item.metric_id, item.value) for item in second
    ]
    assert all(item.synthetic for item in first)
    assert all(item.source == "simulator" for item in first)
    assert all(item.context["scenario_label"] == "SYNTHETIC DEMO" for item in first)
