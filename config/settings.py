from pathlib import Path

# ── Project root ──────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
PROFILES_DIR = DATA_DIR / "profiles"
SAVED_DIR = DATA_DIR / "saved"
MESSAGES_DIR = DATA_DIR / "messages"
RAW_DIR = DATA_DIR / "raw"

# ── Google Sheets ─────────────────────────────────────────────────────────────
RESOURCES_URL = "https://docs.google.com/spreadsheets/d/1AdfJ9TDWdICQuzoYQn-6cBmUkOVXWD8mTqJNDnuKD-E/export?format=csv"
MAP_URL = "https://docs.google.com/spreadsheets/d/1D9CUtXpyPubOkt51wD9SDCpglkQv6W6oa33iTs73cCk/export?format=csv"

# Cache refreshes if older than this many minutes
CACHE_TTL_MINUTES = 60

# ── App branding ──────────────────────────────────────────────────────────────
APP_TITLE = "Build the Startup State."
APP_ICON = "🚀"

# ── Demo users ────────────────────────────────────────────────────────────────
DEMO_USERS = {
    "entrepreneur": {
        "id": "demo_entrepreneur",
        "name": "Jill",
        "email": "jill@techventure.co",
        "role": "entrepreneur",
    },
    "investor": {
        "id": "demo_investor",
        "name": "Jane",
        "email": "jane@utahvc.com",
        "role": "investor",
    },
}

# ── Startup stages ────────────────────────────────────────────────────────────
STAGE_OPTIONS = {
    "Pre-Seed": {
        "label": "🌱 Pre-Seed — Ideation & Validation",
        "description": (
            "You have a big idea and are figuring out if the world needs it. "
            "You're asking exactly the right questions — keep going!"
        ),
    },
    "Seed": {
        "label": "🌿 Seed — MVP & Initial Traction",
        "description": (
            "You're building your first version and finding your first customers. "
            "Exciting territory — the market is listening!"
        ),
    },
    "Early": {
        "label": "🚀 Early — Product-Market Fit & Series A/B",
        "description": (
            "You've found what works and now you're ready to grow fast. "
            "The market has spoken — now it's time to scale!"
        ),
    },
    "Growth": {
        "label": "📈 Growth — Scaling & Expansion",
        "description": (
            "You're scaling fast and capturing market share. "
            "Often supported by Series C or later funding — the sky's the limit!"
        ),
    },
    "Maturity": {
        "label": "🏆 Maturity / Exit — Established & Exit Ready",
        "description": (
            "You've built something amazing. An acquisition or IPO allows investors "
            "to monetize — congratulations on getting here!"
        ),
    },
}

# ── Employee count bands ──────────────────────────────────────────────────────
EMPLOYEE_OPTIONS = ["1-10", "11-50", "51-200", "201-500", "500-1K", "1K-5K"]

# ── Business types ────────────────────────────────────────────────────────────
BUSINESS_TYPES = {
    "": {
        "label": "Not Sure Yet",
        "description": "That's totally fine — many great companies take time to find their category.",
    },
    "B2B Software": {
        "label": "💻 B2B Software",
        "description": "You build software tools that help other businesses work better, faster, or smarter.",
    },
    "Bio/Medical Tech": {
        "label": "🔬 Bio/Medical Tech",
        "description": "You're at the intersection of science and technology, improving health outcomes for people.",
    },
    "Consumer": {
        "label": "🛍️ Consumer",
        "description": "You're building products or services that everyday people love and rely on.",
    },
    "Energy": {
        "label": "⚡ Energy",
        "description": "You're powering the future — renewable, clean, or innovative energy solutions.",
    },
    "FinTech": {
        "label": "💳 FinTech",
        "description": "You're reimagining how money moves, is saved, invested, or accessed.",
    },
    "Marketplaces": {
        "label": "🏪 Marketplaces",
        "description": "You connect buyers and sellers, creating real value for both sides of the transaction.",
    },
    "Security": {
        "label": "🔒 Security",
        "description": "You protect people, data, or physical assets in an increasingly complex world.",
    },
}

# ── Map styling ───────────────────────────────────────────────────────────────
STAGE_COLORS = {
    "Pre-Seed": "#9B59B6",   # purple
    "Seed":     "#3498DB",   # blue
    "Early":    "#2ECC71",   # green
    "Growth":   "#F39C12",   # orange
    "Maturity": "#E74C3C",   # red
    "":         "#95A5A6",   # gray
}

EMPLOYEE_RADIUS = {
    "1-10":    6,
    "11-50":   9,
    "51-200":  12,
    "201-500": 16,
    "500-1K":  20,
    "1K-5K":   26,
    "":        8,
}

UTAH_CENTER = [39.82, -111.09]
UTAH_ZOOM = 7
