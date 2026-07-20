import json
import os


class ChunkStore:

    STORAGE_DIR = "storage"
    STORAGE_FILE = "chunks.json"

    @classmethod
    def _get_path(cls):
        path = os.path.join(cls.STORAGE_DIR, cls.STORAGE_FILE)
        if not os.path.exists(path):
            alt = os.path.join("backend", cls.STORAGE_DIR, cls.STORAGE_FILE)
            if os.path.exists(alt):
                return alt
        return path

    @classmethod
    def save(cls, chunks):

        path = cls._get_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:

            json.dump(
                chunks,
                f,
                indent=4,
                ensure_ascii=False
            )

    @classmethod
    def load(cls):

        path = cls._get_path()

        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as f:

            return json.load(f)