"""
Data loader module for EduPro dataset.
Handles ingestion from Excel (.xlsx) or CSV files, column alias normalization,
data type casting, missing value audits, and relational integrity validation.
"""

import os
from pathlib import Path
from typing import Dict, Tuple, Optional, Any
import pandas as pd
import numpy as np

# Canonical schemas and accepted aliases
USER_ALIASES = {
    "UserID": ["userid", "user_id", "learnerid", "learner_id", "studentid", "student_id", "id"],
    "UserName": ["username", "user_name", "learnername", "name", "fullname", "full_name"],
    "Age": ["age", "learner_age", "user_age"],
    "Gender": ["gender", "sex"]
}

COURSE_ALIASES = {
    "CourseID": ["courseid", "course_id", "id", "cid"],
    "CourseName": ["coursename", "course_name", "title", "coursetitle", "course_title", "name"],
    "CourseCategory": ["coursecategory", "course_category", "category", "subject", "domain"],
    "CourseType": ["coursetype", "course_type", "type", "mode", "delivery_mode", "pricing"],
    "CourseLevel": ["courselevel", "course_level", "level", "difficulty", "difficultylevel", "difficulty_level"]
}

TRANSACTION_ALIASES = {
    "TransactionID": ["transactionid", "transaction_id", "enrollmentid", "enrollment_id", "id", "tid"],
    "UserID": ["userid", "user_id", "learnerid", "learner_id", "studentid", "student_id"],
    "CourseID": ["courseid", "course_id", "id", "cid"],
    "TransactionDate": ["transactiondate", "transaction_date", "enrollmentdate", "enrollment_date", "date", "timestamp"]
}


def normalize_columns(df: pd.DataFrame, alias_map: Dict[str, list]) -> pd.DataFrame:
    """Standardizes column headers by trimming, lowercasing, and mapping known variations."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    clean_df = df.copy()
    clean_df.columns = [str(c).strip() for c in clean_df.columns]
    lower_cols = {c.lower().replace(" ", "").replace("_", ""): c for c in clean_df.columns}
    
    rename_dict = {}
    for canonical, aliases in alias_map.items():
        if canonical in clean_df.columns:
            continue
        for alias in aliases:
            clean_alias = alias.lower().replace(" ", "").replace("_", "")
            if clean_alias in lower_cols:
                rename_dict[lower_cols[clean_alias]] = canonical
                break
                
    if rename_dict:
        clean_df = clean_df.rename(columns=rename_dict)
    return clean_df


class EduProDataLoader:
    """Manages loading, cleaning, validation, and relational integrity of EduPro datasets."""

    def __init__(self):
        self.users_df: pd.DataFrame = pd.DataFrame()
        self.courses_df: pd.DataFrame = pd.DataFrame()
        self.transactions_df: pd.DataFrame = pd.DataFrame()
        self.data_source_type: str = "Uninitialized"
        self.validation_report: Dict[str, Any] = {}

    def load_from_excel(self, excel_path: str | Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Loads Users, Courses, and Transactions sheets from an Excel workbook."""
        path = Path(excel_path)
        if not path.exists():
            raise FileNotFoundError(f"Excel file not found at: {path}")

        xl = pd.ExcelFile(path)
        sheet_map = {s.lower().strip(): s for s in xl.sheet_names}

        # Resolve Users sheet
        u_sheet = next((sheet_map[s] for s in sheet_map if "user" in s or "student" in s or "learner" in s), None)
        c_sheet = next((sheet_map[s] for s in sheet_map if "course" in s), None)
        t_sheet = next((sheet_map[s] for s in sheet_map if "trans" in s or "enroll" in s), None)

        if not (u_sheet and c_sheet and t_sheet):
            raise ValueError(f"Workbook missing required sheets. Found sheets: {xl.sheet_names}")

        u_df = pd.read_excel(path, sheet_name=u_sheet)
        c_df = pd.read_excel(path, sheet_name=c_sheet)
        t_df = pd.read_excel(path, sheet_name=t_sheet)

        self._process_and_store(u_df, c_df, t_df, source_type=f"Excel ({path.name})")
        return self.users_df, self.courses_df, self.transactions_df

    def load_from_csv_files(
        self,
        users_file: Any,
        courses_file: Any,
        transactions_file: Any,
        source_label: str = "CSV Files"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Loads dataset from three CSV files or file-like buffers."""
        u_df = pd.read_csv(users_file)
        c_df = pd.read_csv(courses_file)
        t_df = pd.read_csv(transactions_file)

        self._process_and_store(u_df, c_df, t_df, source_type=source_label)
        return self.users_df, self.courses_df, self.transactions_df

    def _process_and_store(
        self,
        u_df: pd.DataFrame,
        c_df: pd.DataFrame,
        t_df: pd.DataFrame,
        source_type: str
    ):
        """Normalizes columns, sanitizes types, checks integrity, and stores tables."""
        # 1. Normalize
        u_df = normalize_columns(u_df, USER_ALIASES)
        c_df = normalize_columns(c_df, COURSE_ALIASES)
        t_df = normalize_columns(t_df, TRANSACTION_ALIASES)

        # 2. String conversion for IDs
        if "UserID" in u_df.columns:
            u_df["UserID"] = u_df["UserID"].astype(str).str.strip()
        if "CourseID" in c_df.columns:
            c_df["CourseID"] = c_df["CourseID"].astype(str).str.strip()
        if "TransactionID" in t_df.columns:
            t_df["TransactionID"] = t_df["TransactionID"].astype(str).str.strip()
        if "UserID" in t_df.columns:
            t_df["UserID"] = t_df["UserID"].astype(str).str.strip()
        if "CourseID" in t_df.columns:
            t_df["CourseID"] = t_df["CourseID"].astype(str).str.strip()

        # 3. Clean Age
        if "Age" in u_df.columns:
            u_df["Age"] = pd.to_numeric(u_df["Age"], errors="coerce").fillna(u_df["Age"].median() if not u_df["Age"].empty else 25).astype(int)

        # 4. Clean Date
        if "TransactionDate" in t_df.columns:
            t_df["TransactionDate"] = pd.to_datetime(t_df["TransactionDate"], errors="coerce")

        # 5. Remove exact duplicates
        u_df = u_df.drop_duplicates(subset=["UserID"]) if "UserID" in u_df.columns else u_df.drop_duplicates()
        c_df = c_df.drop_duplicates(subset=["CourseID"]) if "CourseID" in c_df.columns else c_df.drop_duplicates()
        t_df = t_df.drop_duplicates(subset=["TransactionID"]) if "TransactionID" in t_df.columns else t_df.drop_duplicates()

        # 6. Referential Integrity audit
        valid_u = set(u_df["UserID"]) if "UserID" in u_df.columns else set()
        valid_c = set(c_df["CourseID"]) if "CourseID" in c_df.columns else set()

        orphan_trans_u = 0
        orphan_trans_c = 0
        if "UserID" in t_df.columns and valid_u:
            orphan_trans_u = int((~t_df["UserID"].isin(valid_u)).sum())
            t_df = t_df[t_df["UserID"].isin(valid_u)].copy()
        if "CourseID" in t_df.columns and valid_c:
            orphan_trans_c = int((~t_df["CourseID"].isin(valid_c)).sum())
            t_df = t_df[t_df["CourseID"].isin(valid_c)].copy()

        self.users_df = u_df.reset_index(drop=True)
        self.courses_df = c_df.reset_index(drop=True)
        self.transactions_df = t_df.reset_index(drop=True)
        self.data_source_type = source_type

        # Generate validation summary
        self.validation_report = {
            "source_type": source_type,
            "total_users": len(self.users_df),
            "total_courses": len(self.courses_df),
            "total_transactions": len(self.transactions_df),
            "orphan_user_transactions_removed": orphan_trans_u,
            "orphan_course_transactions_removed": orphan_trans_c,
            "user_columns": list(self.users_df.columns),
            "course_columns": list(self.courses_df.columns),
            "transaction_columns": list(self.transactions_df.columns),
            "missing_users": self.users_df.isnull().sum().to_dict(),
            "missing_courses": self.courses_df.isnull().sum().to_dict(),
            "missing_transactions": self.transactions_df.isnull().sum().to_dict(),
            "date_range": (
                f"{self.transactions_df['TransactionDate'].min().strftime('%Y-%m-%d')} to {self.transactions_df['TransactionDate'].max().strftime('%Y-%m-%d')}"
                if "TransactionDate" in self.transactions_df.columns and not self.transactions_df['TransactionDate'].dropna().empty
                else "N/A"
            )
        }

    def get_summary(self) -> Dict[str, Any]:
        """Returns the data validation and quality report."""
        return self.validation_report
