"""
Builds the question list from the resources DataFrame and manages answer state.

Column detection is fuzzy — we look for common aliases so the app keeps working
even if the Google Sheet column names change slightly.
"""
import pandas as pd
from config.settings import STAGE_OPTIONS
from modules.grant_normalizer import INDUSTRY_GROUPS, LOCATION_REGIONS

# Maps our canonical key → possible column name variants (lowercase)
COLUMN_ALIASES: dict[str, list[str]] = {
    "communities": ["communities", "community", "who", "target audience", "target"],
    "industries":  ["industries", "industry", "sector", "field"],
    "locations":   ["locations", "location", "region", "area", "geography", "county", "city"],
    "topics":      ["topics", "topic", "type", "category", "focus", "resource type"],
}


def find_column(df: pd.DataFrame, field: str) -> str | None:
    aliases = COLUMN_ALIASES.get(field, [field])
    for col in df.columns:
        if col.lower().strip() in aliases:
            return col
    return None


def extract_unique_values(df: pd.DataFrame, column: str) -> list[str]:
    """Split pipe- or comma-separated cells and return a sorted unique list."""
    values: set[str] = set()
    skip = {"nan", "n/a", "all", "any", "none", ""}
    for cell in df[column].dropna():
        raw = str(cell)
        # Resources use | as separator; fall back to , for any other data
        parts = raw.split("|") if "|" in raw else raw.split(",")
        for part in parts:
            v = part.strip()
            if v.lower() not in skip:
                values.add(v)
    return sorted(values)


def build_questions(resources_df: pd.DataFrame) -> list[dict]:
    """
    Derive up to 10 questions from the resource data.
    Returns a list of question dicts consumed by the quiz view.
    """
    questions: list[dict] = []

    # Q1 — Industry (broad groups, not raw values)
    col = find_column(resources_df, "industries")
    if col:
        questions.append({
            "key": "industries",
            "column": col,
            "question": "What industry best describes your business?",
            "type": "single",
            "options": list(INDUSTRY_GROUPS.keys()),
            "emoji": "🏭",
        })

    # Q2 — Location (named regions, not raw counties)
    col = find_column(resources_df, "locations")
    if col:
        questions.append({
            "key": "locations",
            "column": col,
            "question": "Where is your business primarily located?",
            "type": "single",
            "options": list(LOCATION_REGIONS.keys()),
            "emoji": "📍",
        })

    # Q3 — Communities (multi-select)
    col = find_column(resources_df, "communities")
    if col:
        opts = extract_unique_values(resources_df, col)
        if opts:
            questions.append({
                "key": "communities",
                "column": col,
                "question": "Do you identify with any of these communities?",
                "subtitle": "Select all that apply — or skip if none fit.",
                "type": "multi",
                "options": opts,
                "emoji": "🤝",
            })

    # Q4 — Topics (multi-select)
    col = find_column(resources_df, "topics")
    if col:
        opts = extract_unique_values(resources_df, col)
        if opts:
            questions.append({
                "key": "topics",
                "column": col,
                "question": "What type of support are you looking for?",
                "subtitle": "Select all that apply.",
                "type": "multi",
                "options": opts,
                "emoji": "💡",
            })

    # Q5 — Business stage (always included, drives profile too)
    questions.append({
        "key": "stage",
        "column": None,
        "question": "What stage is your business in?",
        "type": "single_described",
        "options": list(STAGE_OPTIONS.keys()),
        "option_descriptions": {k: v["description"] for k, v in STAGE_OPTIONS.items()},
        "emoji": "📊",
    })

    return questions
