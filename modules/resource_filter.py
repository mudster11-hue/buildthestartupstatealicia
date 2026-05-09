"""
Filters the resources DataFrame based on the user's questionnaire answers.

Empty / universal cells (blank, 'All', 'Any', 'N/A') always pass through
so that broadly applicable resources are never filtered out.
"""
import pandas as pd
from modules.questionnaire import find_column
from modules.grant_normalizer import expand_industry_selection, expand_location_selection

_UNIVERSAL_VALUES = {"", "nan", "n/a", "all", "any", "none"}


def _cell_matches(cell_value, selected: list[str]) -> bool:
    """True when the cell is universal OR overlaps with the selected list."""
    raw = str(cell_value).strip() if not pd.isna(cell_value) else ""
    if raw.lower() in _UNIVERSAL_VALUES:
        return True
    cell_lower = raw.lower()
    return any(s.lower() in cell_lower for s in selected)


def filter_resources(df: pd.DataFrame, answers: dict) -> pd.DataFrame:
    """
    answers keys: 'industries', 'locations', 'communities', 'topics', 'stage'
    Values are either a string (single) or list of strings (multi).
    """
    if df.empty:
        return df

    mask = pd.Series(True, index=df.index)

    for field in ("industries", "locations", "communities", "topics"):
        selected = answers.get(field, [])
        if not selected:
            continue
        if isinstance(selected, str):
            selected = [selected]

        # Expand grouped display names to the underlying raw values
        if field == "industries":
            selected = expand_industry_selection(selected)
        elif field == "locations":
            selected = expand_location_selection(selected)

        col = find_column(df, field)
        if col is None:
            continue

        col_mask = df[col].apply(lambda x: _cell_matches(x, selected))
        mask = mask & col_mask

    return df[mask].reset_index(drop=True)
