import os
import pandas as pd


class Chunker:

    @staticmethod
    def chunk(file_path):

        extension = os.path.splitext(file_path)[1].lower()

        if extension != ".csv":
            return Chunker._chunk_text(file_path)

        filename = os.path.basename(file_path).lower()

        df = pd.read_csv(file_path)
        df.columns = [str(c).strip() for c in df.columns]

        # Row Chunking for all CSV files
        return Chunker._row_chunks(df)

    @staticmethod
    def _chunk_text(file_path):

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        rows = text.split("\n\n")

        return [r.strip() for r in rows if r.strip()]

    @staticmethod
    def _row_chunks(df):

        chunks = []

        for _, row in df.iterrows():

            lines = []

            for column in df.columns:

                value = row[column]

                if pd.isna(value):
                    continue

                lines.append(f"{column}: {value}")

            chunks.append("\n".join(lines))

        return chunks

    @staticmethod
    def _section_chunks(df):

        chunks = []

        grouped = df.groupby("crop")

        for crop, group in grouped:

            lines = []

            lines.append("=" * 60)
            lines.append(f"CROP: {crop}")
            lines.append("=" * 60)
            lines.append("")

            for _, row in group.iterrows():

                for column in df.columns:

                    if column == "crop":
                        continue

                    value = row[column]

                    if pd.isna(value):
                        continue

                    lines.append(f"{column}: {value}")

                lines.append("")
                lines.append("-" * 40)
                lines.append("")

            chunks.append("\n".join(lines))

        return chunks