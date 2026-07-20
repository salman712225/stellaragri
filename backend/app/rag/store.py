import json
import os


class ChunkStore:

    STORAGE_DIR = "storage"
    STORAGE_FILE = "chunks.json"

    @classmethod
    def save(cls, chunks):

        os.makedirs(cls.STORAGE_DIR, exist_ok=True)

        path = os.path.join(
            cls.STORAGE_DIR,
            cls.STORAGE_FILE
        )

        with open(path, "w", encoding="utf-8") as f:

            json.dump(
                chunks,
                f,
                indent=4,
                ensure_ascii=False
            )

    @classmethod
    def load(cls):

        path = os.path.join(
            cls.STORAGE_DIR,
            cls.STORAGE_FILE
        )

        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as f:

            return json.load(f)