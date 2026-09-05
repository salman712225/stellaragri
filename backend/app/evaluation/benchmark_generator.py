import json
import random
from pathlib import Path


class BenchmarkGenerator:

    QUESTION_TEMPLATES = {

        "crop": [

            "Which crop is suitable for {value}?",

            "Recommend a crop for {value}.",

            "Can I grow crops in {value}?",

            "Suggest the best crop for {value}.",

            "What crop grows well in {value}?"

        ],

        "fertilizer": [

            "Which fertilizer should I use for {value}?",

            "Recommend fertilizer for {value}.",

            "Best fertilizer for {value}?",

            "What nutrients are required for {value}?",

            "How should I fertilize {value}?"

        ],

        "disease": [

            "How do I treat {value}?",

            "My crop has {value}. What should I do?",

            "How can I control {value}?",

            "Symptoms of {value}?",

            "Treatment for {value}?"

        ],

        "pest": [

            "How do I control {value}?",

            "Best pesticide for {value}?",

            "How can I remove {value}?",

            "Treatment for {value} infestation?",

            "Organic control of {value}?"

        ],

        "management": [

            "How should I manage {value}?",

            "Best practices for {value}?",

            "Explain {value}.",

            "Give management tips for {value}.",

            "How do farmers perform {value}?"

        ]

    }

    def __init__(self):

        self.dataset = []

    def add_examples(
        self,
        dataset_name,
        values
    ):

        templates = self.QUESTION_TEMPLATES.get(dataset_name, [])

        for value in values:

            for template in templates:

                self.dataset.append({

                    "question": template.format(
                        value=value
                    ),

                    "intent": dataset_name,

                    "expected_dataset": dataset_name,

                    "expected_keyword": value

                })

    def save(self, output_path):

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.dataset,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"Generated {len(self.dataset)} benchmark questions."
        )


if __name__ == "__main__":

    generator = BenchmarkGenerator()

    generator.add_examples(

        "crop",

        [

            "rice",

            "wheat",

            "maize",

            "cotton",

            "black soil",

            "red soil",

            "loamy soil"

        ]

    )

    generator.add_examples(

        "fertilizer",

        [

            "rice",

            "tomato",

            "cotton",

            "nitrogen deficiency",

            "potassium deficiency"

        ]

    )

    generator.add_examples(

        "disease",

        [

            "leaf blast",

            "powdery mildew",

            "yellow leaf curl",

            "bacterial blight"

        ]

    )

    generator.add_examples(

        "pest",

        [

            "aphid",

            "whitefly",

            "armyworm",

            "thrips"

        ]

    )

    generator.add_examples(

        "management",

        [

            "irrigation",

            "weed management",

            "harvesting",

            "crop rotation"

        ]

    )

    generator.save(
        Path(__file__).parent /
        "benchmark_dataset.json"
    )