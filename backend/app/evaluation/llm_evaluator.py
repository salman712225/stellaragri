"""
Simple LLM Evaluator

Evaluates:
1. JSON Validity
2. Success Rate
3. Keyword Match
4. Response Latency

Author: Mohammed Salman
"""

import json
import asyncio
import time
from pathlib import Path

from app.services.chat_service import ChatService


class LLMEvaluator:

    def __init__(
        self,
        benchmark_file=None
    ):

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

    async def evaluate_question(self, sample):

        question = sample["question"]

        expected_keyword = sample["expected_keyword"]

        print("=" * 70)

        print("Question :", question)

        start = time.perf_counter()

        # ---------------------------------------
        # Generate Response
        # ---------------------------------------

        response = await ChatService.answer(
            question
        )

        latency = round(

            time.perf_counter() - start,

            4

        )

        # ---------------------------------------
        # JSON Validation
        # ---------------------------------------

        json_valid = isinstance(
            response,
            dict
        )

        # ---------------------------------------
        # Success Flag
        # ---------------------------------------

        success = False

        if json_valid:

            success = response.get(
                "success",
                False
            )

        # ---------------------------------------
        # Convert Response to Text
        # ---------------------------------------

        response_text = json.dumps(

            response,

            ensure_ascii=False

        ).lower()

        # ---------------------------------------
        # Keyword Check
        # ---------------------------------------

        keyword_found = (

            expected_keyword.lower()

            in

            response_text

        )
            # ---------------------------------------
        # Overall Result
        # ---------------------------------------

        passed = (

            json_valid

            and

            success

            and

            keyword_found

        )

        result = {

            "question": question,

            "json_valid": json_valid,

            "success": success,

            "keyword": expected_keyword,

            "keyword_found": keyword_found,

            "latency": latency,

            "passed": passed

        }

        self.results.append(result)

        # ---------------------------------------
        # Print Result
        # ---------------------------------------

        print()

        print(

            "JSON Valid     :",

            "✅" if json_valid else "❌"

        )

        print(

            "Success        :",

            "✅" if success else "❌"

        )

        print(

            "Keyword Found  :",

            "✅" if keyword_found else "❌"

        )

        print(

            "Latency        :",

            latency,

            "sec"

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

    async def run(self):

        benchmark = self.load_benchmark()

        print()

        print("=" * 70)

        print("RUNNING LLM EVALUATION")

        print("=" * 70)

        print()

        for sample in benchmark:

            try:

                await self.evaluate_question(

                    sample

                )

            except Exception as e:

                print()

                print(

                    "Error:",

                    sample["question"]

                )

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

        json_accuracy = (
            sum(
                1
                for r in self.results
                if r["json_valid"]
            )
            / total_questions
            * 100
        )

        success_rate = (
            sum(
                1
                for r in self.results
                if r["success"]
            )
            / total_questions
            * 100
        )

        keyword_accuracy = (
            sum(
                1
                for r in self.results
                if r["keyword_found"]
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
        print("LLM EVALUATION SUMMARY")
        print("=" * 70)

        print(f"Total Questions : {total_questions}")
        print(f"Passed          : {passed}")
        print(f"Failed          : {failed}")

        print()

        print(
            f"JSON Accuracy   : {json_accuracy:.2f}%"
        )

        print(
            f"Success Rate    : {success_rate:.2f}%"
        )

        print(
            f"Keyword Accuracy: {keyword_accuracy:.2f}%"
        )

        print(
            f"Average Latency : {average_latency:.4f} sec"
        )

        print("=" * 70)

        # --------------------------------------------------
        # Save Results
        # --------------------------------------------------

        output_file = (
            Path(__file__).parent
            / "llm_results.json"
        )

        summary = {

            "total_questions": total_questions,

            "passed": passed,

            "failed": failed,

            "json_accuracy": round(
                json_accuracy,
                2
            ),

            "success_rate": round(
                success_rate,
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

    evaluator = LLMEvaluator()

    asyncio.run(

        evaluator.run()

    )