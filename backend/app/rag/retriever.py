import re
import joblib
from sklearn.metrics.pairwise import cosine_similarity


VECTORIZER_FILE = "storage/tfidf_vectorizer.pkl"
MATRIX_FILE = "storage/tfidf_matrix.pkl"


class Retriever:

    vectorizer = None
    matrix = None

    # ==========================================================
    # Initialize TF-IDF Resources
    # ==========================================================

    @classmethod
    def initialize(cls):

        if cls.vectorizer is None:
            cls.vectorizer = joblib.load(VECTORIZER_FILE)

        if cls.matrix is None:
            cls.matrix = joblib.load(MATRIX_FILE)

    # ==========================================================
    # Retrieve Relevant Chunks
    # ==========================================================

    @staticmethod
    def retrieve(
        query,
        chunks,
        top_k=3,
        dataset_filters=None,
        similarity_threshold=0.15,
    ):

        Retriever.initialize()

        if not chunks:
            return []

        # ---------------------------------------------------
        # Validate Index
        # ---------------------------------------------------

        if Retriever.matrix.shape[0] != len(chunks):
            raise RuntimeError(
                "TF-IDF index and chunk store are out of sync. "
                "Please rebuild the knowledge base."
            )

        # ---------------------------------------------------
        # Create Query Vector
        # ---------------------------------------------------

        query_vector = Retriever.vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector,
            Retriever.matrix
        ).flatten()

        ranked_indices = similarities.argsort()[::-1]

        results = []
        seen = set()

        print("\n" + "=" * 80)
        print(f"QUERY : {query}")

        if dataset_filters:
            print(f"DATASET FILTERS : {dataset_filters}")

        print("=" * 80)

        # ---------------------------------------------------
        # Retrieve Chunks
        # ---------------------------------------------------

        for index in ranked_indices:

            if index >= len(chunks):
                continue

            similarity = float(similarities[index])

            if similarity < similarity_threshold:
                break

            chunk = chunks[index]

            # -----------------------------------------------
            # Dataset Filter
            # -----------------------------------------------

            if dataset_filters:

                chunk_dataset = chunk.get("dataset", "").lower()

                if chunk_dataset not in [
                    dataset.lower()
                    for dataset in dataset_filters
                ]:
                    continue

            text = chunk.get("text", "")

            if text in seen:
                continue

            seen.add(text)

            # -----------------------------------------------
            # Exact Keyword Boost
            # -----------------------------------------------

            boosted_score = similarity

            query_words = {

                word.lower()

                for word in query.split()

                if len(word) > 2
            }

            chunk_text = text.lower()

            exact_matches = sum(

                1

                for word in query_words

                if re.search(
                    rf"\b{re.escape(word)}\b",
                    chunk_text
                )
            )

            boosted_score += min(
                exact_matches * 0.05,
                0.20
            )

            results.append(
                {
                    "score": round(boosted_score, 4),
                    "similarity": round(similarity, 4),
                    "dataset": chunk.get("dataset"),
                    "source": chunk.get("source"),
                    "text": text,
                }
            )

        # ---------------------------------------------------
        # Final Ranking
        # ---------------------------------------------------

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        results = results[:top_k]

        # ---------------------------------------------------
        # Logging
        # ---------------------------------------------------

        print(f"\nRetrieved {len(results)} chunks.\n")

        for i, result in enumerate(results, start=1):

            preview = (
                result["text"]
                .replace("\n", " ")
                [:250]
            )

            print("-" * 80)
            print(f"Rank       : {i}")
            print(f"Dataset    : {result['dataset']}")
            print(f"Source     : {result['source']}")
            print(f"Similarity : {result['similarity']:.4f}")
            print(f"Final Score: {result['score']:.4f}")
            print(preview)
            print("-" * 80)

        return results