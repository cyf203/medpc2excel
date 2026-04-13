import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

Tree = lambda: defaultdict(Tree)


def _timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _append_log(log, message):
    return f"{log}{_timestamp()}>>\t{message}\n"


def _sort_key(value):
    text = str(value)
    try:
        return (0, int(text))
    except ValueError:
        return (1, text)


def _summary_sheet_name(working_var_label):
    if not working_var_label:
        return None
    return f"Summary_({working_var_label})"


def _normalize_msns_df(df):
    columns = ["ID", "Box", "MSN"]
    if df is None or df.empty:
        return pd.DataFrame(columns=columns)

    normalized = df.copy()
    for column in columns:
        if column not in normalized.columns:
            normalized[column] = pd.NA
    normalized = normalized[columns]
    normalized["ID"] = normalized["ID"].astype(str)
    normalized["Box"] = normalized["Box"].astype(str)
    normalized["MSN"] = normalized["MSN"].astype(str)
    normalized = normalized.drop_duplicates(subset=["ID"], keep="first")
    normalized = normalized.sort_values(by="ID", key=lambda series: series.map(lambda value: str(_sort_key(value))))
    normalized.reset_index(drop=True, inplace=True)
    return normalized


def _normalize_summary_df(df):
    if df is None or df.empty:
        return None

    normalized = df.copy()
    normalized.index = normalized.index.astype(str)
    normalized.columns = [str(column) for column in normalized.columns]
    normalized = normalized.reindex(sorted(normalized.index), axis=0)
    normalized = normalized.reindex(sorted(normalized.columns, key=_sort_key), axis=1)
    return normalized


def _load_existing_workbook(filename, working_var_label):
    excel_file = pd.ExcelFile(filename, engine="openpyxl")
    summary_sheet = _summary_sheet_name(working_var_label)
    existing_subjects = {}
    existing_msns = pd.DataFrame(columns=["ID", "Box", "MSN"])
    existing_summary = None

    for sheet_name in excel_file.sheet_names:
        if sheet_name == "MSNs":
            existing_msns = pd.read_excel(filename, sheet_name=sheet_name, engine="openpyxl")
            continue
        if sheet_name.startswith("Summary_("):
            if summary_sheet and sheet_name == summary_sheet:
                existing_summary = pd.read_excel(filename, sheet_name=sheet_name, engine="openpyxl")
                if not existing_summary.empty:
                    existing_summary = existing_summary.set_index(existing_summary.columns[0])
            continue
        existing_subjects[str(sheet_name)] = pd.read_excel(filename, sheet_name=sheet_name, engine="openpyxl")

    return {
        "subjects": existing_subjects,
        "msns": _normalize_msns_df(existing_msns),
        "summary": _normalize_summary_df(existing_summary),
    }


def _merge_msns(existing_df, incoming_df, replace_existing):
    existing = _normalize_msns_df(existing_df)
    incoming = _normalize_msns_df(incoming_df)
    if existing.empty:
        return incoming
    if incoming.empty:
        return existing

    frames = [incoming, existing] if replace_existing else [existing, incoming]
    merged = pd.concat(frames, ignore_index=True)
    return _normalize_msns_df(merged)


def _merge_summary(existing_df, incoming_df, replace_existing):
    existing = _normalize_summary_df(existing_df)
    incoming = _normalize_summary_df(incoming_df)
    if existing is None:
        return incoming
    if incoming is None:
        return existing

    combined = existing.reindex(existing.index.union(incoming.index))
    for column in incoming.columns:
        if replace_existing or column not in combined.columns:
            combined[column] = incoming[column]
    return _normalize_summary_df(combined)


def _write_workbook(filename, msns_df, summary_df, subject_sheets, working_var_label):
    msns = _normalize_msns_df(msns_df)
    summary = _normalize_summary_df(summary_df)
    summary_sheet = _summary_sheet_name(working_var_label)

    with pd.ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
        msns.to_excel(writer, sheet_name="MSNs", index=False)
        if summary_sheet and summary is not None:
            summary.to_excel(writer, sheet_name=summary_sheet, index=True)
        for subject in sorted(subject_sheets, key=_sort_key):
            subject_sheets[subject].to_excel(writer, sheet_name=str(subject)[:31], index=False)


def _parse_header_value(header, field_name):
    match = re.search(rf"{re.escape(field_name)}:\s*(.+)", header)
    if not match:
        return None
    return match.group(1).strip()


def _parse_msn_metadata(msn_path, working_var_label):
    ts_var_name_map = {}
    array_name_map = {}
    with open(msn_path, "r", errors="replace") as handle:
        for line in handle:
            if "DIM" in line:
                dim_match = re.search(r"\bDIM\s+([A-Z])\b", line)
                if not dim_match:
                    continue
                var = dim_match.group(1)
                _, _, comment = line.partition("\\")
                name = re.split(r"\s{2,}", comment.strip())[0].strip()
                if var != working_var_label and name:
                    ts_var_name_map[var] = f"({var}){re.sub(r'\\s+', '', name)}"
                continue

            if not working_var_label:
                continue
            array_match = re.match(
                rf"\s*\\\s*{re.escape(working_var_label)}\((\d+)\)\W*(.*)$",
                line,
            )
            if array_match:
                idx, name = array_match.groups()
                array_name_map[idx] = f"{working_var_label}({idx}){name.strip()}"

    return ts_var_name_map, array_name_map


def _parse_variable_sections(lines):
    sections = defaultdict(list)
    current_var = None

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        section_match = re.fullmatch(r"([A-Z]):", stripped)
        if section_match:
            current_var = section_match.group(1)
            continue
        if current_var is None or ":" not in raw_line:
            continue
        _, _, values = raw_line.partition(":")
        sections[current_var].extend(token for token in re.split(r"\s+", values.strip()) if token)

    return dict(sections)


def _parse_dataset(dataset_index, dataset_text, file, working_var_label, rat_id_set, log):
    normalized = dataset_text.replace("\r\n", "\n")
    date_match = re.match(r"\s*(\d{2}/\d{2}/\d{2})", normalized)
    if not date_match:
        return None, _append_log(log, f"Error!Skipped dataset #{dataset_index} in {file}: invalid or missing Start Date.")

    try:
        this_date = datetime.strptime(date_match.group(1), "%m/%d/%y").strftime("%Y%m%d")
    except ValueError:
        return None, _append_log(log, f"Error!Skipped dataset #{dataset_index} in {file}: invalid Start Date '{date_match.group(1)}'.")

    header, separator, body = normalized.partition("MSN:")
    if not separator:
        return None, _append_log(log, f"Error!Skipped dataset #{dataset_index} on {this_date} in {file}: missing MSN line.")

    subject = _parse_header_value(header, "Subject")
    if not subject:
        return None, _append_log(log, f"Error!Skipped dataset #{dataset_index} on {this_date} in {file}: missing Subject.")

    if rat_id_set is not None and str(subject) not in rat_id_set:
        return None, log

    box = _parse_header_value(header, "Box")
    if not box:
        return None, _append_log(log, f"Error!Skipped dataset #{dataset_index} for subject {subject} on {this_date} in {file}: missing Box.")

    body_lines = [line for line in body.split("\n") if line.strip()]
    if not body_lines:
        return None, _append_log(log, f"Error!Skipped dataset #{dataset_index} for subject {subject} on {this_date} in {file}: missing program body.")

    program_name = body_lines[0].strip()
    if not program_name:
        return None, _append_log(log, f"Error!Skipped dataset #{dataset_index} for subject {subject} on {this_date} in {file}: missing program name.")

    msn_path = os.path.join(os.path.dirname(file), f"{program_name}.MPC")
    if not os.path.exists(msn_path):
        return None, _append_log(log, f"Error!Please provide MSN program in the data folder: {msn_path}")

    try:
        ts_var_name_map, array_name_map = _parse_msn_metadata(msn_path, working_var_label)
    except OSError as exc:
        return None, _append_log(log, f"Error!Could not read MSN program {msn_path}: {exc}")

    variable_sections = _parse_variable_sections(body_lines[1:])
    if not variable_sections:
        return None, _append_log(log, f"Error!Skipped dataset #{dataset_index} for subject {subject} on {this_date} in {file}: no variable sections found.")

    timestamp_vars = [var for var in ts_var_name_map if var in variable_sections]
    should_read_working_var = bool(working_var_label and working_var_label in variable_sections)
    if not timestamp_vars and not should_read_working_var:
        return None, _append_log(
            log,
            f"Error!Skipped dataset #{dataset_index} for subject {subject} on {this_date} in {file}: missing expected variable data.",
        )

    data_dict = {}
    for var in timestamp_vars:
        data_dict[var] = pd.to_numeric(
            pd.Series(variable_sections[var], name=var, dtype="float64"),
            errors="coerce",
        )
    if should_read_working_var:
        data_dict[working_var_label] = pd.to_numeric(
            pd.Series(variable_sections[working_var_label], name=working_var_label, dtype="float64"),
            errors="coerce",
        )

    return {
        "date": this_date,
        "subject": str(subject),
        "box": str(box),
        "program_name": program_name,
        "data_dict": data_dict,
        "ts_var_name_map": ts_var_name_map,
        "array_name_map": array_name_map,
    }, log


def medpc_read(file, working_var_label="", rat_id=None, save=True, skipold=True, override=True, replace=True, log=""):
    """
    Inputs:
    1. file (str, path)
    2. working_var_label (str, default is '')
    3. rat_id (array like)
    4. save (Boolean value, default is True)
    5. override (Boolean value, default is True)
    6. replace (Boolean value, default is True)

    Outputs:
    1. TS_df_tree (a tree, like {'date': {'rat': df}})
    2. log (string, capture essential events)
    """

    file = str(file)
    rat_id_set = None if rat_id is None else {str(item).strip() for item in rat_id}
    alldata_tree = Tree()
    ts_var_name_maps = {}
    array_name_maps = {}
    msn_rows = defaultdict(list)

    try:
        datasets = Path(file).read_text(errors="replace").split("Start Date: ")
    except OSError as exc:
        return Tree(), _append_log(log, f"Error!Could not read MED-PC data file {file}: {exc}")

    for dataset_index, dataset_text in enumerate(datasets[1:], start=1):
        parsed_dataset, log = _parse_dataset(
            dataset_index,
            dataset_text,
            file,
            working_var_label,
            rat_id_set,
            log,
        )
        if parsed_dataset is None:
            continue

        program_name = parsed_dataset["program_name"]
        this_date = parsed_dataset["date"]
        subject = parsed_dataset["subject"]

        ts_var_name_maps[program_name] = parsed_dataset["ts_var_name_map"]
        array_name_maps[program_name] = parsed_dataset["array_name_map"]
        alldata_tree[program_name][this_date][subject] = parsed_dataset["data_dict"]
        msn_rows[this_date].append(
            {
                "ID": subject,
                "Box": parsed_dataset["box"],
                "MSN": program_name,
            }
        )

    msn_dict = {date: _normalize_msns_df(pd.DataFrame(rows)) for date, rows in msn_rows.items()}
    ts_df_tree = Tree()

    for program_name, dated_data in alldata_tree.items():
        for this_date, subject_data in dated_data.items():
            for subject, data_dict in subject_data.items():
                temp_df_list = []
                for var, name in ts_var_name_maps.get(program_name, {}).items():
                    series = data_dict.get(var)
                    if series is None:
                        continue
                    renamed_series = series.copy()
                    renamed_series.name = name
                    temp_df_list.append(renamed_series)
                if not temp_df_list:
                    log = _append_log(
                        log,
                        f"Error!Skipped subject {subject} on {this_date} in {file}: no timestamp variables were extracted.",
                    )
                    continue
                ts_df_tree[this_date][subject] = pd.concat(temp_df_list, axis=1)

    working_var_dfs = {}
    if working_var_label:
        working_var_tree = defaultdict(dict)
        for program_name, dated_data in alldata_tree.items():
            array_name_map = array_name_maps.get(program_name, {})
            if not array_name_map:
                continue
            for this_date, subject_data in dated_data.items():
                subject_frames = []
                for subject, data_dict in subject_data.items():
                    working_series = data_dict.get(working_var_label)
                    if working_series is None:
                        log = _append_log(
                            log,
                            f"Error!Working variable {working_var_label} was not found for subject {subject} on {this_date} in {file}.",
                        )
                        continue
                    values = {}
                    for idx, name in array_name_map.items():
                        index = int(idx)
                        if index >= len(working_series):
                            log = _append_log(
                                log,
                                f"Error!{name} in MSN ({program_name}) cannot be found in file {file}.",
                            )
                            values[name] = np.nan
                            continue
                        values[name] = working_series.iloc[index]
                    if values:
                        subject_frames.append(pd.DataFrame.from_dict(values, orient="index", columns=[subject]))
                if subject_frames:
                    working_var_tree[this_date][program_name] = pd.concat(subject_frames, axis=1)

        for this_date, program_data in working_var_tree.items():
            if not program_data:
                continue
            working_var_dfs[this_date] = _normalize_summary_df(pd.concat(list(program_data.values()), axis=1, join="outer"))

    if save:
        file_path = os.path.dirname(file)
        summary_sheet = _summary_sheet_name(working_var_label)
        for this_date, subject_frames in ts_df_tree.items():
            filename = os.path.join(file_path, f"{this_date}.xlsx")
            incoming_subjects = {str(subject): df for subject, df in subject_frames.items()}
            incoming_msns = msn_dict.get(this_date)
            incoming_summary = working_var_dfs.get(this_date)

            if os.path.exists(filename):
                if skipold:
                    log = _append_log(log, f"Skip existing local excel file {filename}")
                    continue

                try:
                    existing_workbook = _load_existing_workbook(filename, working_var_label)
                except Exception as exc:
                    if override:
                        existing_workbook = {
                            "subjects": {},
                            "msns": pd.DataFrame(columns=["ID", "Box", "MSN"]),
                            "summary": None,
                        }
                        log = _append_log(
                            log,
                            f"Error!Existing workbook {filename} could not be read ({exc}). Rebuilding it from current data.",
                        )
                    else:
                        log = _append_log(
                            log,
                            f"Error!Existing workbook {filename} could not be read ({exc}). Skipped date {this_date}.",
                        )
                        continue

                existing_subjects = existing_workbook["subjects"]
                existing_msns = existing_workbook["msns"]
                existing_summary = existing_workbook["summary"]
                overlap = set(existing_subjects).intersection(incoming_subjects)

                if override:
                    final_subjects = incoming_subjects
                    final_msns = incoming_msns
                    final_summary = incoming_summary
                    log = _append_log(log, f"Override the existing local excel file {filename}")
                elif replace:
                    final_subjects = existing_subjects.copy()
                    final_subjects.update(incoming_subjects)
                    final_msns = _merge_msns(existing_msns, incoming_msns, replace_existing=True)
                    final_summary = _merge_summary(existing_summary, incoming_summary, replace_existing=True)
                    if overlap:
                        log = _append_log(log, f"Replace overlapped MED-PC data in the existing local excel file {filename}")
                    else:
                        log = _append_log(log, f"No overlap. Append new MED-PC data to an existing local excel file {filename}.")
                else:
                    new_subjects = {subject: df for subject, df in incoming_subjects.items() if subject not in existing_subjects}
                    if not new_subjects:
                        log = _append_log(log, f"No new MED-PC data were appended to {filename}.")
                        continue
                    final_subjects = existing_subjects.copy()
                    final_subjects.update(new_subjects)
                    filtered_msns = None
                    if incoming_msns is not None:
                        filtered_msns = incoming_msns[incoming_msns["ID"].isin(new_subjects)]
                    filtered_summary = None
                    if incoming_summary is not None:
                        filtered_columns = [column for column in incoming_summary.columns if str(column) in new_subjects]
                        if filtered_columns:
                            filtered_summary = incoming_summary[filtered_columns]
                    final_msns = _merge_msns(existing_msns, filtered_msns, replace_existing=False)
                    final_summary = _merge_summary(existing_summary, filtered_summary, replace_existing=False)
                    log = _append_log(log, f"Append new MED-PC data to an existing local excel file {filename}. Old data was not changed.")

                try:
                    _write_workbook(filename, final_msns, final_summary, final_subjects, working_var_label)
                except Exception as exc:
                    log = _append_log(log, f"Error!Could not save workbook {filename}: {exc}")
            else:
                try:
                    _write_workbook(filename, incoming_msns, incoming_summary, incoming_subjects, working_var_label)
                    log = _append_log(log, f"Extract MED-PC data file to a new local excel file {file_path}")
                except Exception as exc:
                    log = _append_log(log, f"Error!Could not create workbook {filename}: {exc}")

    return ts_df_tree, log
