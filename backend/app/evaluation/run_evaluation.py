"""
Run Complete Evaluation

Runs:
1. RAG Evaluation
2. LLM Evaluation
3. Generates Final Report
"""

import asyncio

from app.evaluation.rag_evaluator import RAGEvaluator
from app.evaluation.llm_evaluator import LLMEvaluator
from app.evaluation.evaluation_report import EvaluationReport


async def main():

    print("\n" + "=" * 80)
    print("STARTING COMPLETE RAG + LLM EVALUATION")
    print("=" * 80)

    # -----------------------------------
    # RAG Evaluation
    # -----------------------------------

    rag = RAGEvaluator()

    rag_summary = rag.run()

    # -----------------------------------
    # LLM Evaluation
    # -----------------------------------

    llm = LLMEvaluator()

    llm_summary = await llm.run()

    # -----------------------------------
    # Final Report
    # -----------------------------------

    report = EvaluationReport()

    report.generate(
        rag_summary,
        llm_summary
    )

    print("\nEvaluation Completed Successfully.")


if __name__ == "__main__":

    asyncio.run(main())