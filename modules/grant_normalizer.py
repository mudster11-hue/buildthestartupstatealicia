"""
Maps broad display-friendly group names to the raw values stored in resources.csv.
Used by questionnaire.py (to build filter options) and resource_filter.py (to expand
selections back to raw values before cell matching).
"""

INDUSTRY_GROUPS: dict[str, list[str]] = {
    "Technology & Aerospace": [
        "Software and Information Technology",
        "Aerospace and Defense",
    ],
    "Healthcare & Life Sciences": [
        "Life Sciences and Healthcare",
    ],
    "Food, Agriculture & Consumer": [
        "Agriculture",
        "Hospitality and Food Services",
        "Consumer Packaged Goods",
    ],
    "Creative & Entertainment": [
        "Arts and Entertainment and Recreation",
    ],
    "Finance & Business Services": [
        "Financial Services",
    ],
    "Manufacturing": [
        "Manufacturing",
    ],
    "Other": [
        "Other",
    ],
}

LOCATION_REGIONS: dict[str, list[str]] = {
    "Salt Lake Area": [
        "Salt Lake",
        "Tooele",
    ],
    "Northern Utah": [
        "Davis",
        "Weber",
        "Morgan",
        "Box Elder",
        "Cache",
        "Rich",
    ],
    "Utah Valley": [
        "Utah",
        "Wasatch",
        "Juab",
        "Summit",
    ],
    "Southern Utah": [
        "Washington",
        "Iron",
        "Kane",
        "Garfield",
        "Wayne",
        "Piute",
        "Beaver",
        "Millard",
        "Sevier",
        "Sanpete",
        "San Juan",
    ],
    "Eastern Utah": [
        "Carbon",
        "Emery",
        "Grand",
        "Duchesne",
        "Daggett",
        "Uintah",
    ],
}


def expand_industry_selection(groups: list[str]) -> list[str]:
    """Return raw industry values for the given group display names."""
    raw: list[str] = []
    for g in groups:
        raw.extend(INDUSTRY_GROUPS.get(g, [g]))
    return raw


def expand_location_selection(regions: list[str]) -> list[str]:
    """Return raw county names for the given region display names."""
    raw: list[str] = []
    for r in regions:
        raw.extend(LOCATION_REGIONS.get(r, [r]))
    return raw
