import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import ex_part_h


def test_synthesis_summary_returns_lines():
    bootstrap_summary = {
        "period_std": 0.01,
        "depth_std": 0.002,
        "duration_std": 0.03,
        "epoch_std": 0.02,
    }

    timing_residuals = np.array([0.0, 1e-5, -1e-5])
    energy_drift = 1e-8

    lines = ex_part_h.synthesis_summary(
        period=3.2,
        epoch=0.0,
        bootstrap_summary=bootstrap_summary,
        timing_residuals=timing_residuals,
        energy_drift=energy_drift,
    )

    assert isinstance(lines, list)
    assert len(lines) > 3
    assert any("RK4" in line for line in lines)
    assert any("bootstrap" in line.lower() for line in lines)


def test_synthesis_identifies_largest_uncertainty():
    bootstrap_summary = {
        "period_std": 0.01,
        "depth_std": 0.002,
        "duration_std": 0.05,
        "epoch_std": 0.02,
    }

    timing_residuals = np.array([0.0, 1e-5, -1e-5])
    energy_drift = 1e-8

    lines = ex_part_h.synthesis_summary(
        period=3.2,
        epoch=0.0,
        bootstrap_summary=bootstrap_summary,
        timing_residuals=timing_residuals,
        energy_drift=energy_drift,
    )

    text = "\n".join(lines).lower()

    assert "duration" in text
    assert "largest bootstrap uncertainty" in text