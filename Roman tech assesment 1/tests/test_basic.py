import csv
import json
import subprocess
import sys
from pathlib import Path


def test_sample_data_exists():
    assert Path("data/job_description.txt").exists()
    assert Path("data/resumes").exists()
    assert len(list(Path("data/resumes").glob("*"))) >= 10


def test_agent_generates_ranked_outputs_with_fit_signals():
    result = subprocess.run(
        [
            sys.executable,
            "main.py",
            "--jd",
            "data/job_description.txt",
            "--resumes",
            "data/resumes",
            "--output",
            "outputs",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0
    assert Path("outputs/ranked_candidates.csv").exists()
    assert Path("outputs/ranked_candidates.json").exists()

    with open("outputs/ranked_candidates.json", "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    assert payload["total_candidates"] >= 2
    assert payload["candidates"]
    first_candidate = payload["candidates"][0]
    assert "confidence" in first_candidate
    assert "fit_level" in first_candidate
    assert first_candidate["fit_level"] in {"Strong", "Moderate", "Weak"}

    with open("outputs/ranked_candidates.csv", "r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert "match_strength" in rows[0]
