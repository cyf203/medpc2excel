import re
import shutil
from pathlib import Path

import pandas as pd
import pytest

from medpc2excel.medpc_read import medpc_read

ROOT = Path(__file__).resolve().parents[1]
TESTDATA_DIR = ROOT / "TestData"

if not TESTDATA_DIR.exists():
    pytest.skip("TestData directory is required for medpc2excel regression tests.", allow_module_level=True)


EXPECTED_DATES = {
    "20260311_StriatumLinear_cohort2_LPtrain": [
        "20260311",
        "20260312",
        "20260313",
        "20260314",
        "20260315",
    ],
    "20260319_StriatumLinear_cohort2_PRL": [
        "20260319",
        "20260323",
        "20260324",
        "20260325",
        "20260326",
        "20260327",
        "20260328",
        "20260330",
        "20260331",
        "20260401",
        "20260402",
        "20260403",
        "20260404",
    ],
    "20260405_StriatumLinear_cohort2_dynaPRL": [
        "20260405",
        "20260406",
        "20260407",
    ],
}


def _copy_testdata(tmp_path):
    data_dir = tmp_path / "TestData"
    shutil.copytree(TESTDATA_DIR, data_dir)
    return data_dir


def _total_subjects(ts_tree):
    return sum(len(subjects) for subjects in ts_tree.values())


def test_real_files_parse_without_crashing(tmp_path):
    data_dir = _copy_testdata(tmp_path)

    for file_name, expected_dates in EXPECTED_DATES.items():
        ts_tree, log = medpc_read(str(data_dir / file_name), save=False)
        assert list(ts_tree.keys()) == expected_dates
        assert "Error!" not in log


def test_save_and_rerun_modes_produce_readable_workbooks(tmp_path):
    data_dir = _copy_testdata(tmp_path)
    input_file = data_dir / "20260311_StriatumLinear_cohort2_LPtrain"

    for options in (
        {"skipold": True, "override": True, "replace": True},
        {"skipold": False, "override": True, "replace": True},
        {"skipold": False, "override": False, "replace": True},
        {"skipold": False, "override": False, "replace": False},
    ):
        _, log = medpc_read(str(input_file), working_var_label="A", save=True, **options)
        assert "Could not" not in log

    for expected_date in EXPECTED_DATES[input_file.name]:
        workbook_path = data_dir / f"{expected_date}.xlsx"
        assert workbook_path.exists()
        workbook = pd.ExcelFile(workbook_path, engine="openpyxl")
        assert "MSNs" in workbook.sheet_names
        assert "Summary_(A)" in workbook.sheet_names


def test_logs_missing_msn_and_skips_broken_chunk(tmp_path):
    data_dir = _copy_testdata(tmp_path)
    broken_file = data_dir / "broken_missing_msn"
    text = (data_dir / "20260311_StriatumLinear_cohort2_LPtrain").read_text()
    broken_file.write_text(text.replace("MSN: YC235_LeverTrn_a\n", "", 1))

    ts_tree, log = medpc_read(str(broken_file), save=False)

    assert "missing MSN line" in log
    assert _total_subjects(ts_tree) == 8


def test_logs_missing_mpc_file(tmp_path):
    data_dir = _copy_testdata(tmp_path)
    broken_file = data_dir / "broken_missing_mpc"
    text = (data_dir / "20260311_StriatumLinear_cohort2_LPtrain").read_text()
    broken_file.write_text(text.replace("MSN: YC235_LeverTrn_a", "MSN: DOES_NOT_EXIST_TASK", 1))

    ts_tree, log = medpc_read(str(broken_file), save=False)

    assert "Please provide MSN program" in log
    assert _total_subjects(ts_tree) == 8


def test_logs_invalid_start_date(tmp_path):
    data_dir = _copy_testdata(tmp_path)
    broken_file = data_dir / "broken_invalid_date"
    text = (data_dir / "20260311_StriatumLinear_cohort2_LPtrain").read_text()
    broken_file.write_text(text.replace("Start Date: 03/11/26", "Start Date: invalid", 1))

    ts_tree, log = medpc_read(str(broken_file), save=False)

    assert "invalid or missing Start Date" in log
    assert _total_subjects(ts_tree) == 8


def test_logs_missing_expected_variable_data(tmp_path):
    data_dir = _copy_testdata(tmp_path)
    broken_file = data_dir / "broken_missing_variables"
    text = (data_dir / "20260311_StriatumLinear_cohort2_LPtrain").read_text()
    text = re.sub(r"\nC:\n.*?(?=\nStart Date:|\Z)", "\n", text, count=1, flags=re.S)
    broken_file.write_text(text)

    ts_tree, log = medpc_read(str(broken_file), save=False)

    assert "missing expected variable data" in log
    assert _total_subjects(ts_tree) == 8
