import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

import ex_part_a

def test_relative_time_starts_at_zero():
    df = ex_part_a.load_light_curve("TESSA_lc.dat")
    df = ex_part_a.make_relative_time(df)
    assert np.isclose(df["t_rel"].iloc[0], 0.0)

def test_normalization_median_near_one():
    df = ex_part_a.load_light_curve("TESSA_lc.dat")
    df = ex_part_a.normalize_flux(df)
    assert np.isclose(np.median(df["flux_norm"]), 1.0, atol=1e-10)

def test_detrending_constant_returns_constant():
    detrended = ex_part_a.detrend_constant_test()
    assert np.allclose(detrended, 1.0, atol=1e-10)