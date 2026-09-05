import os
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer

from app.rag.chunker import Chunker


def _get_storage_path(filename: str):
    if os.path.exists(os.path.join("storage", filename)):
        return os.path.join("storage", filename)
    if os.path.exists(os.path.join("backend", "storage", filename)):
        return os.path.join("backend", "storage", filename)
    return os.path.join("storage", filename)


class Indexer:

    @staticmethod
    def _get_dataset(filename: str):

        filename = filename.lower()

        if "crop_recommendation" in filename:
            return "crop"

        elif "fertilizer" in filename:
            return "fertilizer"

        elif "crop_disease" in filename:
            return "disease"

        elif "crop_pest" in filename:
            return "pest"

        elif "crop_management" in filename:
            return "management"

        return "general"

    @staticmethod
    def build_chunks(upload_folder):

        all_chunks = []

        if not os.path.exists(upload_folder):
            backend_upload = os.path.join("backend", upload_folder)
            if os.path.exists(backend_upload):
                upload_folder = backend_upload
            else:
                return all_chunks

        for filename in sorted(os.listdir(upload_folder)):

            file_path = os.path.join(upload_folder, filename)

            if not os.path.isfile(file_path):
                continue

            print("\n" + "=" * 80)
            print(f"Processing : {filename}")

            dataset = Indexer._get_dataset(filename)

            chunks = Chunker.chunk(file_path)

            print(f"Dataset    : {dataset}")
            print(f"Chunks     : {len(chunks)}")

            for idx, chunk in enumerate(chunks):

                all_chunks.append(
                    {
                        "id": f"{filename}-{idx}",
                        "dataset": dataset,
                        "source": filename,
                        "text": chunk,
                    }
                )

        print("\n" + "=" * 80)
        print(f"Total Chunks Indexed : {len(all_chunks)}")
        print("=" * 80)

        return all_chunks

    @staticmethod
    def build(chunks):

        if not chunks:
            raise ValueError("No chunks available to build TF-IDF index.")

        print("\nBuilding TF-IDF Index...")

        texts = [chunk["text"] for chunk in chunks]

        vectorizer = TfidfVectorizer(
            stop_words="english",
            lowercase=True,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )

        matrix = vectorizer.fit_transform(texts)

        vectorizer_file = _get_storage_path("tfidf_vectorizer.pkl")
        matrix_file = _get_storage_path("tfidf_matrix.pkl")

        os.makedirs(os.path.dirname(vectorizer_file), exist_ok=True)

        joblib.dump(
            vectorizer,
            vectorizer_file,
        )

        joblib.dump(
            matrix,
            matrix_file,
        )

        print(f"Vocabulary Size : {len(vectorizer.vocabulary_)}")
        print(f"Matrix Shape    : {matrix.shape}")
        print("TF-IDF Index Saved Successfully.")