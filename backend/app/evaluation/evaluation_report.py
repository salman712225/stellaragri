"""
Simple Evaluation Report
"""

import json
from pathlib import Path


class EvaluationReport:

    def __init__(self):

        self.output_file = (
            Path(__file__).parent /
            "evaluation_report.json"
        )

    def generate(
        self,
        rag_summary,
        llm_summary
    ):

        report = {

            "rag": rag_summary,

            "llm": llm_summary

        }

        with open(

            self.output_file,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                report,

                f,

                indent=4,

                ensure_ascii=False

            )

        print()

        print("=" * 70)

        print("FINAL EVALUATION REPORT")

        print("=" * 70)

        print()

        print("RAG Evaluation")

        print("-------------------------")

        print(

            "Intent Accuracy   :",

            rag_summary["intent_accuracy"],

            "%"

        )

        print(

            "Dataset Accuracy  :",

            rag_summary["dataset_accuracy"],

            "%"

        )

        print(

            "Keyword Accuracy  :",

            rag_summary["keyword_accuracy"],

            "%"

        )

        print(

            "Average Latency   :",

            rag_summary["average_latency"],

            "sec"

        )

        print()

        print("LLM Evaluation")

        print("-------------------------")

        print(

            "JSON Accuracy     :",

            llm_summary["json_accuracy"],

            "%"

        )

        print(

            "Success Rate      :",

            llm_summary["success_rate"],

            "%"

        )

        print(

            "Keyword Accuracy  :",

            llm_summary["keyword_accuracy"],

            "%"

        )

        print(

            "Average Latency   :",

            llm_summary["average_latency"],

            "sec"

        )

        print()

        print("=" * 70)

        print(

            "Report saved to:",

            self.output_file

        )

        print("=" * 70)

        print()

        return report