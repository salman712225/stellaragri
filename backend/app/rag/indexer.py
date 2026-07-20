import os
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer

from app.rag.chunker import Chunker


VECTORIZER_FILE = "storage/tfidf_vectorizer.pkl"
MATRIX_FILE = "storage/tfidf_matrix.pkl"


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

        os.makedirs("storage", exist_ok=True)

        joblib.dump(
            vectorizer,
            VECTORIZER_FILE,
        )

        joblib.dump(
            matrix,
            MATRIX_FILE,
        )

        print(f"Vocabulary Size : {len(vectorizer.vocabulary_)}")
        print(f"Matrix Shape    : {matrix.shape}")
        print("TF-IDF Index Saved Successfully.")