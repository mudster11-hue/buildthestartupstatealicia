# Build the Startup State

**A platform that connects Utah founders with funding and investors with the next great company.**

Built for the Utah AI Builder Day bounty — and for my husband, who wants to start a business and kept hitting walls trying to find out how.

---

## The Problem

Utah has world-class resources for founders. Grants, programs, funding, support — it's all there. But for a first-generation entrepreneur, a working family, someone without a connection or a lawyer, it is nearly impossible to find. The government websites are a maze. The opportunity feels real but out of reach.

That's not just a UX problem. It's a trust problem. When people can't find the help that exists, they stop believing the help exists.

This platform was built to solve that — to be the front door that actually opens.

---

## What It Does

**For Entrepreneurs**
- Cinematic landing page that immediately feels welcoming, not bureaucratic
- A guided grant finder quiz (under 2 minutes) that asks about your business and surfaces exactly what's available to you
- Browse and save from 500+ Utah grants and resources
- Build a startup profile so investors can find you
- Direct messaging with investors

**For Investors**
- Live interactive map of Utah startups, filterable by industry and stage
- Click any startup to see their profile, description, and website
- Save companies worth a second look
- Direct messaging with founders

---

## The Story

My husband dreams of owning a business. We bought a house in Utah — stretched ourselves to do it — because we kept hearing about the Silicon Slopes, the innovation, the opportunity. When we tried to actually access any of it, we hit a wall. We felt what a lot of Utah residents feel: that this world wasn't built for people like us.

When I saw this bounty I didn't see the $10,000. I saw someone at the state level who was having the same conversation we were having at our dinner table every night. I built this because it's a problem my heart is in — and because when I found those spreadsheets full of resources I didn't know existed, I realized solving this wasn't just for Utah. It was for my family.

---

## Running Locally

```powershell
pip install -r requirements.txt
python -m streamlit run app.py
```

Opens at **http://localhost:8501** — no account needed. Choose Entrepreneur or Investor on the landing page.

---

## How the Data Works

Resources and grants pull live from a Google Sheet — a state employee can add or update a resource with no code, and it appears on the platform within 60 minutes. The startup map pulls from a second sheet and geocodes addresses automatically.

| Source | Updated |
|---|---|
| Grants & Resources | Google Sheets, cached every 60 min |
| Startup Map | Google Sheets, geocoded via ArcGIS |
| Entrepreneur Profiles | Stored locally per user |

---

## Tech Stack

| | |
|---|---|
| **Framework** | Streamlit |
| **Map** | Folium + Pydeck |
| **Geocoding** | geopy (ArcGIS, no API key required) |
| **Data** | Google Sheets → JSON cache |
| **Language** | Python 3.10+ |

---

## What's Next

- Real user accounts and persistent sessions
- Mobile optimization
- Connection to official state data sources
- Investor-founder matching

---

*Built in Utah. For Utah. By someone who bet on this state and needed a reason to believe the bet was right.*
