import asyncio
import time

from app.llm.providers.gemini_provider import GeminiProvider
from app.llm.providers.mistral_provider import MistralProvider
from app.llm.providers.groq_provider import GroqProvider


class FallbackProvider:

    PROVIDERS = [
        ("Gemini", GeminiProvider),
        ("Mistral", MistralProvider),
        ("Groq", GroqProvider)
    ]

    MAX_RETRIES = 2

    RETRY_DELAY = 1

    # ==========================================================
    # Generate Response
    # ==========================================================

    @classmethod
    async def generate(
        cls,
        messages,
        temperature=0.3,
        max_tokens=3000
    ):

        errors = []

        for provider_name, provider in cls.PROVIDERS:

            for attempt in range(1, cls.MAX_RETRIES + 1):

                start = time.perf_counter()

                try:

                    print("\n" + "=" * 80)
                    print(f"Provider : {provider_name}")
                    print(f"Attempt  : {attempt}")
                    print("=" * 80)

                    response = await provider.generate(

                        messages=messages,

                        temperature=temperature,

                        max_tokens=max_tokens

                    )

                    elapsed = time.perf_counter() - start

                    if not response:

                        raise RuntimeError(
                            "Empty response received."
                        )

                    print(
                        f"{provider_name} Success "
                        f"({elapsed:.2f}s)"
                    )

                    return response

                except Exception as e:

                    elapsed = time.perf_counter() - start

                    error = (
                        f"{provider_name} "
                        f"(Attempt {attempt}) "
                        f"Failed after {elapsed:.2f}s : {str(e)}"
                    )

                    print(error)

                    errors.append(error)

                    if attempt < cls.MAX_RETRIES:

                        await asyncio.sleep(
                            cls.RETRY_DELAY
                        )

        raise RuntimeError(
            "\n".join(errors)
        )

    # ==========================================================
    # Stream Response
    # ==========================================================

    @classmethod
    async def stream(
        cls,
        messages,
        temperature=0.3,
        max_tokens=3000
    ):

        errors = []

        for provider_name, provider in cls.PROVIDERS:

            start = time.perf_counter()

            try:

                print("\n" + "=" * 80)
                print(f"Streaming via {provider_name}")
                print("=" * 80)

                chunks = 0

                async for chunk in provider.stream(

                    messages=messages,

                    temperature=temperature,

                    max_tokens=max_tokens

                ):

                    if chunk:

                        chunks += 1

                        yield chunk

                elapsed = time.perf_counter() - start

                print(
                    f"{provider_name} "
                    f"Streaming Completed "
                    f"({elapsed:.2f}s)"
                )

                print(
                    f"Chunks Streamed : {chunks}"
                )

                return

            except Exception as e:

                elapsed = time.perf_counter() - start

                error = (
                    f"{provider_name} Streaming Failed "
                    f"after {elapsed:.2f}s : {str(e)}"
                )

                print(error)

                errors.append(error)

        yield "Unable to generate a response."

        raise RuntimeError(
            "\n".join(errors)
        )