import os
import pandas as pd


class DocumentParser:

    @staticmethod
    def parse(file_path: str):

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".csv":
            return DocumentParser._parse_csv(file_path)

        elif extension in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        return ""


    @staticmethod
    def _parse_csv(file_path: str):

        df = pd.read_csv(file_path)

        # Remove extra spaces from column names
        df.columns = [str(col).strip() for col in df.columns]

        rows = []

        for _, row in df.iterrows():

            record = []

            for column in df.columns:

                value = row[column]

                if pd.isna(value):
                    continue

                record.append(f"{column}: {value}")

            # One CSV row = One RAG document
            rows.append("\n".join(record))

        return "\n\n".join(rows)