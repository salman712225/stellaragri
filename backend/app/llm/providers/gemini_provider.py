# pyrefly: ignore [missing-import]

import asyncio
import time

# pyrefly: ignore [missing-import]
from litellm import acompletion

from app.core.config import settings
from app.llm.utils.response_cleaner import ResponseCleaner


class GeminiProvider:

    MODEL = "gemini/gemini-2.5-flash"

    TIMEOUT = 60
    MAX_RETRIES = 2

    @classmethod
    async def generate(
        cls,
        messages,
        temperature=0.3,
        max_tokens=3000
    ):
        """
        Generate complete response using Gemini.
        """

        last_exception = None

        for attempt in range(cls.MAX_RETRIES):

            try:

                print(f"\nUsing Gemini ({cls.MODEL})")
                print(f"Attempt : {attempt + 1}")

                start = time.perf_counter()

                response = await asyncio.wait_for(

                    acompletion(

                        model=cls.MODEL,

                        api_key=settings.GEMINI_API_KEY,

                        messages=messages,

                        temperature=temperature,

                        max_tokens=max_tokens,

                        stream=False
                    ),

                    timeout=cls.TIMEOUT
                )

                elapsed = time.perf_counter() - start

                usage = getattr(response, "usage", None)

                if usage:

                    print("\nToken Usage")

                    print(
                        f"Prompt      : {usage.prompt_tokens}"
                    )

                    print(
                        f"Completion  : {usage.completion_tokens}"
                    )

                    print(
                        f"Total       : {usage.total_tokens}"
                    )

                print(f"Response Time : {elapsed:.2f}s")

                content = response.choices[0].message.content

                return ResponseCleaner.clean(content)

            except Exception as e:

                last_exception = e

                print(f"Gemini Attempt {attempt + 1} Failed")

                print(str(e))

                if attempt < cls.MAX_RETRIES - 1:

                    await asyncio.sleep(1)

        raise RuntimeError(
            f"Gemini Provider Failed : {last_exception}"
        )

    @classmethod
    async def stream(
        cls,
        messages,
        temperature=0.3,
        max_tokens=3000
    ):
        """
        Stream response from Gemini.
        """

        try:

            response = await asyncio.wait_for(

                acompletion(

                    model=cls.MODEL,

                    api_key=settings.GEMINI_API_KEY,

                    messages=messages,

                    temperature=temperature,

                    max_tokens=max_tokens,

                    stream=True

                ),

                timeout=cls.TIMEOUT
            )

            async for chunk in response:

                choices = getattr(chunk, "choices", None)

                if not choices:
                    continue

                delta = getattr(
                    choices[0],
                    "delta",
                    None
                )

                if delta is None:
                    continue

                content = getattr(
                    delta,
                    "content",
                    ""
                )

                if content:

                    yield content

        except Exception as e:

            raise RuntimeError(
                f"Gemini Streaming Failed : {e}"
            )