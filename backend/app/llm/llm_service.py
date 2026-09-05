import time
from typing import List, Dict, Any

from app.llm.fallback_provider import FallbackProvider
from app.llm.utils.response_cleaner import ResponseCleaner


class LLMService:
    """
    Central LLM Service.

    Responsibilities:
    - Send prompts to the active provider
    - Measure latency
    - Clean responses
    - Handle provider failures
    """

    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 3000

    # ==========================================================
    # Validate Messages
    # ==========================================================

    @staticmethod
    def _validate_messages(messages: List[Dict[str, Any]]):

        if not messages:
            raise ValueError("Messages cannot be empty.")

        if not isinstance(messages, list):
            raise TypeError("Messages must be a list.")

        for message in messages:

            if not isinstance(message, dict):
                raise TypeError("Each message must be a dictionary.")

            if "role" not in message:
                raise ValueError("Message missing 'role'.")

            if "content" not in message:
                raise ValueError("Message missing 'content'.")

    # ==========================================================
    # Generate Response
    # ==========================================================

    @classmethod
    async def generate(
        cls,
        messages,
        temperature=None,
        max_tokens=None
    ):

        cls._validate_messages(messages)

        temperature = (
            temperature
            if temperature is not None
            else cls.DEFAULT_TEMPERATURE
        )

        max_tokens = (
            max_tokens
            if max_tokens is not None
            else cls.DEFAULT_MAX_TOKENS
        )

        print("\n" + "=" * 80)
        print("LLM SERVICE")
        print("=" * 80)
        print(f"Messages     : {len(messages)}")
        print(f"Temperature  : {temperature}")
        print(f"Max Tokens   : {max_tokens}")

        start = time.perf_counter()

        try:

            response = await FallbackProvider.generate(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

        except Exception as e:

            print(f"LLM Error : {e}")

            raise

        elapsed = time.perf_counter() - start

        print(f"Generation Time : {elapsed:.2f} sec")

        if not response:

            raise RuntimeError(
                "LLM returned an empty response."
            )

        response = ResponseCleaner.clean(response)

        print(f"Response Length : {len(response)}")

        return response

    # ==========================================================
    # Stream Response
    # ==========================================================

    @classmethod
    async def stream_response(
        cls,
        messages,
        temperature=None,
        max_tokens=None
    ):

        cls._validate_messages(messages)

        temperature = (
            temperature
            if temperature is not None
            else cls.DEFAULT_TEMPERATURE
        )

        max_tokens = (
            max_tokens
            if max_tokens is not None
            else cls.DEFAULT_MAX_TOKENS
        )

        print("\n" + "=" * 80)
        print("STREAMING RESPONSE")
        print("=" * 80)

        start = time.perf_counter()

        token_count = 0

        async for chunk in FallbackProvider.stream(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        ):

            if chunk:

                token_count += 1

                yield chunk

        elapsed = time.perf_counter() - start

        print("=" * 80)
        print(f"Streaming Finished")
        print(f"Time         : {elapsed:.2f} sec")
        print(f"Chunks       : {token_count}")
        print("=" * 80)