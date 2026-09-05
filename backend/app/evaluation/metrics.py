import json
import time
from typing import List, Set


class Metrics:

    # ==========================================================
    # Precision@K
    # ==========================================================

    @staticmethod
    def precision_at_k(
        retrieved: List[str],
        relevant: Set[str],
        k: int
    ) -> float:

        if k <= 0:
            return 0.0

        retrieved = retrieved[:k]

        if len(retrieved) == 0:
            return 0.0

        hits = sum(
            1
            for item in retrieved
            if item in relevant
        )

        return hits / len(retrieved)

    # ==========================================================
    # Recall@K
    # ==========================================================

    @staticmethod
    def recall_at_k(
        retrieved: List[str],
        relevant: Set[str],
        k: int
    ) -> float:

        if len(relevant) == 0:
            return 0.0

        retrieved = retrieved[:k]

        hits = sum(
            1
            for item in retrieved
            if item in relevant
        )

        return hits / len(relevant)

    # ==========================================================
    # Mean Reciprocal Rank
    # ==========================================================

    @staticmethod
    def reciprocal_rank(
        retrieved: List[str],
        relevant: Set[str]
    ) -> float:

        for index, item in enumerate(retrieved):

            if item in relevant:

                return 1.0 / (index + 1)

        return 0.0

    # ==========================================================
    # Retrieval Accuracy
    # ==========================================================

    @staticmethod
    def retrieval_accuracy(
        retrieved: List[str],
        expected_dataset: str
    ) -> float:

        if not retrieved:
            return 0.0

        first = retrieved[0]

        return 1.0 if first == expected_dataset else 0.0

    # ==========================================================
    # Context Precision
    # ==========================================================

    @staticmethod
    def context_precision(
        retrieved_chunks: List[str],
        expected_keywords: List[str]
    ) -> float:

        if not retrieved_chunks:
            return 0.0

        total = 0

        for chunk in retrieved_chunks:

            text = chunk.lower()

            if any(
                keyword.lower() in text
                for keyword in expected_keywords
            ):

                total += 1

        return total / len(retrieved_chunks)

    # ==========================================================
    # Context Recall
    # ==========================================================

    @staticmethod
    def context_recall(
        retrieved_chunks: List[str],
        expected_keywords: List[str]
    ) -> float:

        if not expected_keywords:
            return 0.0

        found = 0

        corpus = " ".join(
            retrieved_chunks
        ).lower()

        for keyword in expected_keywords:

            if keyword.lower() in corpus:

                found += 1

        return found / len(expected_keywords)

    # ==========================================================
    # JSON Validity
    # ==========================================================

    @staticmethod
    def json_validity(
        response: str
    ) -> float:

        try:

            json.loads(response)

            return 1.0

        except Exception:

            return 0.0

    # ==========================================================
    # Keyword Match Score
    # ==========================================================

    @staticmethod
    def keyword_match_score(
        answer: str,
        expected_keywords: List[str]
    ) -> float:

        if not expected_keywords:

            return 0.0

        answer = answer.lower()

        hits = 0

        for keyword in expected_keywords:

            if keyword.lower() in answer:

                hits += 1

        return hits / len(expected_keywords)

    # ==========================================================
    # Hallucination Estimate
    # ==========================================================

    @staticmethod
    def hallucination_score(
        answer: str,
        retrieved_context: str
    ) -> float:

        if not answer:

            return 1.0

        answer_words = set(
            answer.lower().split()
        )

        context_words = set(
            retrieved_context.lower().split()
        )

        unseen = answer_words - context_words

        return len(unseen) / max(
            len(answer_words),
            1
        )

    # ==========================================================
    # Response Latency
    # ==========================================================

    @staticmethod
    def latency(
        start_time: float,
        end_time: float
    ) -> float:

        return round(
            end_time - start_time,
            3
        )

    # ==========================================================
    # Overall Score
    # ==========================================================

    @staticmethod
    def overall_score(
        scores: List[float]
    ) -> float:

        if not scores:

            return 0.0

        return round(
            sum(scores) / len(scores),
            4
        )