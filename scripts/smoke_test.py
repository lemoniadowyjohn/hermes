from iqda.config import Settings
from iqda.factory import build_components, rebuild_index

if __name__ == "__main__":
    settings = Settings()
    rebuild_index(settings)
    service, *_ = build_components(settings)
    response = service.ask("What is the torque requirement for component AX17?")
    print(response.model_dump_json(indent=2))
    if response.status.value != "answered":
        raise SystemExit(1)
