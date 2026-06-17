import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build


CONFIG_FILE = Path.home() / ".hermes" / "config" / "google_sheets.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


class GoogleSheets:
    def __init__(self):
        with open(CONFIG_FILE, "r") as f:
            self.config = json.load(f)

        creds = service_account.Credentials.from_service_account_file(
            self.config["credentials_file"],
            scopes=SCOPES
        )

        self.service = build("sheets", "v4", credentials=creds)

    def get_sheet_config(self, name: str):
        return self.config["spreadsheets"][name]

    def read_rows(self, spreadsheet_name: str, range_override: str | None = None):
        sheet_config = self.get_sheet_config(spreadsheet_name)

        spreadsheet_id = sheet_config["id"]
        sheet_name = sheet_config["sheet"]

        read_range = range_override or f"{sheet_name}!A:Z"

        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=read_range
        ).execute()

        rows = result.get("values", [])

        if not rows:
            return []

        headers = rows[0]
        records = []

        for row_number, row in enumerate(rows[1:], start=2):
            record = {
                "_row_number": row_number
            }

            for index, header in enumerate(headers):
                record[header] = row[index] if index < len(row) else ""

            records.append(record)

        return records

    def get_player_feedback(self):
        return self.read_rows("player_feedback")

    def filter_by_feedback_type(self, feedback_type: str):
        feedback_type = feedback_type.lower().strip()

        return [
            item for item in self.get_player_feedback()
            if item.get("feedbackType", "").lower().strip() == feedback_type
        ]

    def get_bugs(self):
        return self.filter_by_feedback_type("bug")

    def get_feedback(self):
        return self.filter_by_feedback_type("feedback")

    def get_ideas(self):
        return self.filter_by_feedback_type("idea")

    def get_items_by_status(self, status: str):
        status = status.lower().strip()

        return [
            item for item in self.get_player_feedback()
            if item.get("status", "").lower().strip() == status
        ]

    def get_new_items(self):
        return self.get_items_by_status("new")

    def get_triaged_items(self):
        return self.get_items_by_status("triaged")

    def get_in_progress_items(self):
        return self.get_items_by_status("in_progress")

    def get_fixed_items(self):
        return self.get_items_by_status("fixed")

    def get_released_items(self):
        return self.get_items_by_status("released")

    def get_wont_fix_items(self):
        return self.get_items_by_status("wont_fix")

    def get_new_bugs(self):
        return self.filter_feedback(
            feedback_type="bug",
            status="new"
        )

    def get_new_feedback(self):
        return self.filter_feedback(
            feedback_type="feedback",
            status="new"
        )

    def get_new_ideas(self):
        return self.filter_feedback(
            feedback_type="idea",
            status="new"
        )

    def filter_feedback(
        self,
        feedback_type: str | None = None,
        status: str | None = None
    ):
        records = self.get_player_feedback()

        if feedback_type:
            feedback_type = feedback_type.lower().strip()

            records = [
                item for item in records
                if item.get("feedbackType", "").lower().strip() == feedback_type
            ]

        if status:
            status = status.lower().strip()

            records = [
                item for item in records
                if item.get("status", "").lower().strip() == status
            ]

        return records

    def get_status_counts(self):
        counts = {}

        for item in self.get_player_feedback():
            status = item.get("status", "").strip().lower()

            if not status:
                status = "unknown"

            counts[status] = counts.get(status, 0) + 1

        return counts

    def _find_column_letter(self, column_name: str):
        records = self.read_rows("player_feedback")

        if not records:
            raise ValueError("No records found")

        headers = list(records[0].keys())

        headers = [h for h in headers if h != "_row_number"]

        for index, header in enumerate(headers, start=1):
            if header.strip().lower() == column_name.strip().lower():
                result = ""
                current = index

                while current > 0:
                    current, remainder = divmod(current - 1, 26)
                    result = chr(65 + remainder) + result

                return result

        raise ValueError(f"Column not found: {column_name}")

    def update_cell(self, row_number: int, column_name: str, value: str):
        sheet_config = self.get_sheet_config("player_feedback")

        spreadsheet_id = sheet_config["id"]
        sheet_name = sheet_config["sheet"]

        column_letter = self._find_column_letter(column_name)

        cell_range = f"{sheet_name}!{column_letter}{row_number}"

        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=cell_range,
            valueInputOption="RAW",
            body={
                "values": [[value]]
            }
        ).execute()

        return True

    def update_status(self, row_number: int, status: str):
        return self.update_cell(
            row_number=row_number,
            column_name="status",
            value=status
        )

    def update_notes(self, row_number: int, notes: str):
        return self.update_cell(
            row_number=row_number,
            column_name="notes",
            value=notes
        )

    def mark_triaged(self, row_number: int, notes: str = ""):
        self.update_status(row_number, "triaged")

        if notes:
            self.update_notes(row_number, notes)

    def mark_in_progress(self, row_number: int, notes: str = ""):
        self.update_status(row_number, "in_progress")

        if notes:
            self.update_notes(row_number, notes)

    def mark_fixed(self, row_number: int, notes: str = ""):
        self.update_status(row_number, "fixed")

        if notes:
            self.update_notes(row_number, notes)

    def mark_released(self, row_number: int, notes: str = ""):
        self.update_status(row_number, "released")

        if notes:
            self.update_notes(row_number, notes)

    def mark_wont_fix(self, row_number: int, notes: str = ""):
        self.update_status(row_number, "wont_fix")

        if notes:
            self.update_notes(row_number, notes)

    def search_feedback(self, keyword: str):
        keyword = keyword.lower().strip()

        if not keyword:
            return []

        results = []

        for item in self.get_player_feedback():
            searchable_text = json.dumps(item, ensure_ascii=False).lower()

            if keyword in searchable_text:
                results.append(item)

        return results

    def get_recent_feedback(self, days: int = 7, timestamp_field: str = "timestamp"):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        results = []

        for item in self.get_player_feedback():
            raw_timestamp = item.get(timestamp_field, "").strip()

            if not raw_timestamp:
                continue

            parsed = self._parse_timestamp(raw_timestamp)

            if parsed and parsed >= cutoff:
                results.append(item)

        return results

    def summarize_recent_feedback(self, days: int = 7):
        recent = self.get_recent_feedback(days=days)

        bugs = [
            item for item in recent
            if item.get("feedbackType", "").lower().strip() == "bug"
        ]

        feedback = [
            item for item in recent
            if item.get("feedbackType", "").lower().strip() == "feedback"
        ]

        ideas = [
            item for item in recent
            if item.get("feedbackType", "").lower().strip() == "idea"
        ]

        return {
            "days": days,
            "total": len(recent),
            "bug_count": len(bugs),
            "feedback_count": len(feedback),
            "idea_count": len(ideas),
            "bugs": bugs,
            "feedback": feedback,
            "ideas": ideas,
        }

    def _parse_timestamp(self, value: str):
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y %I:%M:%S %p",
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(value, fmt)

                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)

                return parsed
            except ValueError:
                pass

        return None


if __name__ == "__main__":
    sheets = GoogleSheets()

    print("=== Counts ===")
    print(f"All: {len(sheets.get_player_feedback())}")
    print(f"Bugs: {len(sheets.get_bugs())}")
    print(f"Feedback: {len(sheets.get_feedback())}")
    print(f"Ideas: {len(sheets.get_ideas())}")

    print("\n=== Status Counts ===")
    print(json.dumps(
        sheets.get_status_counts(),
        indent=2,
        ensure_ascii=False
    ))

    print(f"\nNew Bugs: {len(sheets.get_new_bugs())}")

    print("\nWrite support enabled:")
    print("- update_status(row, status)")
    print("- update_notes(row, notes)")
    print("- mark_triaged(row)")
    print("- mark_fixed(row)")

    print("\n=== Recent Summary ===")
    print(json.dumps(
        sheets.summarize_recent_feedback(days=7),
        indent=2,
        ensure_ascii=False
    ))
