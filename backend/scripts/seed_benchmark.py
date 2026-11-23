import json
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.models import Dataset, TestCase

PATH = Path(__file__).resolve().parents[2] / "datasets" / "sample_benchmark.json"


def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    with SessionLocal() as db:
        existing = db.scalar(
            select(Dataset).where(Dataset.name == data["name"], Dataset.version == data["version"])
        )
        if existing:
            print(f"Already seeded: dataset id={existing.id}")
            return
        ds = Dataset(name=data["name"], description=data["description"], version=data["version"])
        db.add(ds)
        db.flush()
        for c in data["test_cases"]:
            db.add(
                TestCase(
                    dataset_id=ds.id,
                    input_text=c["input_text"],
                    expected_output=c["expected_output"],
                    evaluation_type="exact_match",
                    meta=c.get("metadata"),
                )
            )
        db.commit()
        print(f"Seeded dataset id={ds.id} with {len(data['test_cases'])} test cases")


if __name__ == "__main__":
    main()