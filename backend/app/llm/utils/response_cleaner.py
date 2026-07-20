import json
import re


class ResponseCleaner:

    @staticmethod
    def repair_json(text: str) -> str:
        """Autofix unclosed JSON strings, arrays, and objects caused by max token limits."""
        start = text.find("{")
        if start == -1:
            return text
        text = text[start:]

        # Balance quotes
        quote_count = text.count('"') - text.count('\\"')
        if quote_count % 2 != 0:
            text += '"'

        # Stack balance brackets
        stack = []
        in_string = False
        escape = False

        for char in text:
            if escape:
                escape = False
                continue
            if char == '\\':
                escape = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if not in_string:
                if char in '{[':
                    stack.append(char)
                elif char in '}]':
                    if stack:
                        stack.pop()

        # Remove trailing comma before closing if any
        text = re.sub(r",\s*$", "", text.strip())

        # Close unclosed elements in reverse
        for open_char in reversed(stack):
            if open_char == '{':
                text += '\n}'
            elif open_char == '[':
                text += '\n]'

        return text

    @staticmethod
    def clean(text: str) -> str:

        if not text:
            return ""

        # Remove markdown code fences
        text = re.sub(
            r"```json",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"```",
            "",
            text
        )

        text = text.strip()

        # Extract JSON block
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            candidate = text[start:end + 1]
            try:
                parsed = json.loads(candidate)
                return json.dumps(parsed, ensure_ascii=False)
            except Exception:
                pass

        # Try repairing truncated JSON
        repaired = ResponseCleaner.repair_json(text)
        try:
            parsed = json.loads(repaired)
            return json.dumps(parsed, ensure_ascii=False)
        except Exception:
            return text