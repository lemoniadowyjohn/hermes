from iqda.config import Settings
from iqda.factory import rebuild_index

if __name__ == "__main__":
    settings = Settings()
    count = rebuild_index(settings)
    print(f"indexed_chunks={count} db={settings.db_path}")
