"""
Simple RAG Evaluator

Evaluates:
1. Intent Detection
2. Dataset Retrieval
3. Keyword Retrieval
4. Retrieval Latency

Author: Mohammed Salman
"""

import json
import time
from pathlib import Path

from app.rag.query_processor import QueryProcessor
from app.rag.rag_service import RAGService


class RAGEvaluator:

    def __init__(
        self,
        benchmark_file=None,
        top_k=5
    ):

        self.top_k = top_k

        self.benchmark_file = benchmark_file or (
            Path(__file__).parent /
            "benchmark_dataset.json"
        )

        self.results = []

    # --------------------------------------------------------
    # Load Benchmark
    # --------------------------------------------------------

    def load_benchmark(self):

        with open(
            self.benchmark_file,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    # --------------------------------------------------------
    # Evaluate One Question
    # --------------------------------------------------------

    def evaluate_question(self, sample):

        question = sample["question"]

        expected_intent = sample["intent"]

        expected_dataset = sample["expected_dataset"]

        expected_keyword = sample["expected_keyword"]

        print("=" * 70)

        print("Question :", question)

        start = time.perf_counter()

        # -----------------------------
        # Query Processing
        # -----------------------------

        query_result = QueryProcessor.process(question)

        predicted_intent = query_result.intent

        # -----------------------------
        # RAG Retrieval
        # -----------------------------

        retrieved_chunks = RAGService.retrieve(

            question,

            top_k=self.top_k

        )

        latency = round(

            time.perf_counter() - start,

            4

        )

        # -----------------------------
        # Extract datasets
        # -----------------------------

        retrieved_datasets = []

        retrieved_text = ""

        for chunk in retrieved_chunks:

            dataset = chunk.get("dataset", "")

            if dataset not in retrieved_datasets:

                retrieved_datasets.append(dataset)

            retrieved_text += " "

            retrieved_text += chunk.get("text", "")
            # --------------------------------------------------
        # Intent Evaluation
        # --------------------------------------------------

        intent_correct = (

            predicted_intent == expected_intent

        )

        # --------------------------------------------------
        # Dataset Evaluation
        # --------------------------------------------------

        dataset_correct = (

            expected_dataset in retrieved_datasets

        )

        # --------------------------------------------------
        # Keyword Evaluation
        # --------------------------------------------------

        keyword_correct = (

            expected_keyword.lower()

            in

            retrieved_text.lower()

        )

        # --------------------------------------------------
        # Overall Result
        # --------------------------------------------------

        passed = (

            intent_correct

            and

            dataset_correct

            and

            keyword_correct

        )

        result = {

            "question": question,

            "expected_intent": expected_intent,

            "predicted_intent": predicted_intent,

            "intent_correct": intent_correct,

            "expected_dataset": expected_dataset,

            "retrieved_datasets": retrieved_datasets,

            "dataset_correct": dataset_correct,

            "expected_keyword": expected_keyword,

            "keyword_correct": keyword_correct,

            "retrieved_chunks": len(retrieved_chunks),

            "latency": latency,

            "passed": passed

        }

        self.results.append(result)

        # --------------------------------------------------
        # Print Result
        # --------------------------------------------------

        print()

        print(

            "Expected Intent  :",

            expected_intent

        )

        print(

            "Predicted Intent :",

            predicted_intent,

            "✅" if intent_correct else "❌"

        )

        print()

        print(

            "Expected Dataset :",

            expected_dataset

        )

        print(

            "Retrieved        :",

            ", ".join(retrieved_datasets),

            "✅" if dataset_correct else "❌"

        )

        print()

        print(

            "Keyword          :",

            expected_keyword,

            "✅" if keyword_correct else "❌"

        )

        print()

        print(

            "Retrieved Chunks :", len(retrieved_chunks)

        )

        print(

            "Latency          :", latency, "sec"

        )

        print()

        print(

            "PASS"

            if passed

            else

            "FAIL"

        )

        print("=" * 70)

        return result

    # --------------------------------------------------------
    # Run Evaluation
    # --------------------------------------------------------

    def run(self):

        benchmark = self.load_benchmark()

        print()

        print("=" * 70)

        print("RUNNING RAG EVALUATION")

        print("=" * 70)

        print()

        for sample in benchmark:

            try:

                self.evaluate_question(sample)

            except Exception as e:

                print()

                print("Error:", sample["question"])

                print(e)

                print()

            # --------------------------------------------------
        # Evaluation Summary
        # --------------------------------------------------

        total_questions = len(self.results)

        passed = sum(
            1
            for r in self.results
            if r["passed"]
        )

        failed = total_questions - passed

        intent_accuracy = (
            sum(
                1
                for r in self.results
                if r["intent_correct"]
            )
            / total_questions
            * 100
        )

        dataset_accuracy = (
            sum(
                1
                for r in self.results
                if r["dataset_correct"]
            )
            / total_questions
            * 100
        )

        keyword_accuracy = (
            sum(
                1
                for r in self.results
                if r["keyword_correct"]
            )
            / total_questions
            * 100
        )

        average_latency = (
            sum(
                r["latency"]
                for r in self.results
            )
            / total_questions
        )

        # --------------------------------------------------
        # Print Summary
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("EVALUATION SUMMARY")
        print("=" * 70)

        print(f"Total Questions  : {total_questions}")
        print(f"Passed           : {passed}")
        print(f"Failed           : {failed}")

        print()

        print(
            f"Intent Accuracy  : {intent_accuracy:.2f}%"
        )

        print(
            f"Dataset Accuracy : {dataset_accuracy:.2f}%"
        )

        print(
            f"Keyword Accuracy : {keyword_accuracy:.2f}%"
        )

        print(
            f"Average Latency  : {average_latency:.4f} sec"
        )

        print("=" * 70)

        # --------------------------------------------------
        # Save Results
        # --------------------------------------------------

        output_file = (
            Path(__file__).parent
            / "results.json"
        )

        summary = {

            "total_questions": total_questions,

            "passed": passed,

            "failed": failed,

            "intent_accuracy": round(
                intent_accuracy,
                2
            ),

            "dataset_accuracy": round(
                dataset_accuracy,
                2
            ),

            "keyword_accuracy": round(
                keyword_accuracy,
                2
            ),

            "average_latency": round(
                average_latency,
                4
            ),

            "results": self.results

        }

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                summary,
                f,
                indent=4,
                ensure_ascii=False
            )

        print()
        print(
            f"Results saved to: {output_file}"
        )

        return summary


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    evaluator = RAGEvaluator(

        top_k=5

    )

    evaluator.run()