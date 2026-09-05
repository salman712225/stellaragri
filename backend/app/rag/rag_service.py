import time

from app.rag.store import ChunkStore
from app.rag.indexer import Indexer
from app.rag.retriever import Retriever
from app.rag.query_processor import QueryProcessor


class RAGService:

    DEFAULT_TOP_K = 5
    DEFAULT_SIMILARITY = 0.15

    DATASET_PRIORITY = {
        "crop_recommendation": {
            "crop": 0.30,
            "management": 0.15,
            "general": 0.05,
        },
        "fertilizer": {
            "fertilizer": 0.30,
            "management": 0.15,
            "general": 0.05,
        },
        "disease": {
            "disease": 0.30,
            "management": 0.20,
            "general": 0.05,
        },
        "pest": {
            "pest": 0.30,
            "management": 0.20,
            "general": 0.05,
        },
        "management": {
            "management": 0.30,
            "general": 0.10,
        },
        "market": {
            "general": 0.05,
        },
        "weather": {
            "general": 0.05,
        },
    }

    # ==========================================================
    # Build Knowledge Base
    # ==========================================================

    @staticmethod
    def ingest_folder(folder_path="uploads"):

        print("\n" + "=" * 80)
        print("DOCUMENT INGESTION")
        print("=" * 80)

        chunks = Indexer.build_chunks(folder_path)

        if not chunks:
            existing = ChunkStore.load()
            if existing:
                print(f"Using {len(existing)} pre-indexed chunks from storage.")
                return len(existing)
            print("No documents in uploads folder and no pre-indexed chunks. Continuing in dynamic advisory mode.")
            return 0

        ChunkStore.save(chunks)

        Indexer.build(chunks)

        print(f"Indexed {len(chunks)} chunks successfully.")

        return len(chunks)

    # ==========================================================
    # Retrieve Knowledge
    # ==========================================================

    @staticmethod
    def retrieve(
        query: str,
        top_k: int = DEFAULT_TOP_K
    ):

        overall_start = time.perf_counter()

        chunks = ChunkStore.load()

        if not chunks:
            return []

        query_result = QueryProcessor.process(query)

        print("\n" + "=" * 80)
        print("QUERY ANALYSIS")
        print("=" * 80)
        print(f"Original Query : {query_result.original_query}")
        print(f"Intent         : {query_result.intent}")
        print(f"Confidence     : {query_result.confidence}")
        print(f"Entities       : {query_result.entities}")
        print(f"Datasets       : {query_result.dataset_filters}")
        print("=" * 80)

        all_results = []

        for retrieval_query in query_result.retrieval_queries:

            retrieved = Retriever.retrieve(
                query=retrieval_query,
                chunks=chunks,
                top_k=top_k,
                dataset_filters=query_result.dataset_filters,
                similarity_threshold=RAGService.DEFAULT_SIMILARITY,
            )

            all_results.extend(retrieved)

        # ------------------------------------------------------
        # Remove Duplicates
        # ------------------------------------------------------

        merged = {}

        for chunk in all_results:

            key = (
                chunk.get("dataset"),
                chunk.get("source"),
                chunk.get("text"),
            )

            if (
                key not in merged
                or chunk["score"] > merged[key]["score"]
            ):
                merged[key] = chunk

        results = list(merged.values())

        # ------------------------------------------------------
        # Dataset Filter
        # ------------------------------------------------------

        if query_result.dataset_filters:

            allowed = {
                d.lower()
                for d in query_result.dataset_filters
            }

            results = [
                r
                for r in results
                if r.get("dataset", "").lower() in allowed
            ]

        # ------------------------------------------------------
        # Intent-Aware Ranking
        # ------------------------------------------------------

        priority = RAGService.DATASET_PRIORITY.get(
            query_result.intent,
            {}
        )

        crop = str(
            query_result.entities.get("crop", "")
        ).lower()

        crop_aliases = (
            QueryProcessor.CROP_ALIASES.get(crop, [crop])
            if crop and crop in QueryProcessor.CROP_ALIASES
            else ([crop] if crop else [])
        )

        disease = str(
            query_result.entities.get("disease", "")
        ).lower()

        pest = str(
            query_result.entities.get("pest", "")
        ).lower()

        for chunk in results:

            score = chunk["score"]

            dataset = chunk.get(
                "dataset",
                "general"
            )

            score += priority.get(dataset, 0)

            text = chunk.get(
                "text",
                ""
            ).lower()

            if crop_aliases and any(alias in text for alias in crop_aliases):
                score += 0.15

            if disease and disease in text:
                score += 0.15

            if pest and pest in text:
                score += 0.15

            chunk["final_score"] = round(score, 4)

        results.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        results = results[:top_k]

        # ------------------------------------------------------
        # Logging
        # ------------------------------------------------------

        elapsed = time.perf_counter() - overall_start

        print("\n" + "=" * 80)
        print("RETRIEVAL SUMMARY")
        print("=" * 80)
        print(f"Intent            : {query_result.intent}")
        print(f"Queries Generated : {len(query_result.retrieval_queries)}")
        print(f"Retrieved         : {len(all_results)}")
        print(f"Unique Chunks     : {len(results)}")
        print(f"Time              : {elapsed:.3f} sec")

        print("\nTop Results")
        print("-" * 80)

        for i, chunk in enumerate(results, start=1):

            print(
                f"[{i}] "
                f"{chunk.get('dataset')} | "
                f"{chunk.get('final_score'):.3f} | "
                f"{chunk.get('source')}"
            )

        print("=" * 80)

        return results