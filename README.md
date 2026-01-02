# Instant Church Directory Export

A minimalistic Python scraper for [Instant Church Directory](https://members.instantchurchdirectory.com/) that exports all directory data to organized JSON files with downloaded assets.

## Features

- Exports families, staff, groups, birthdays, anniversaries, and additional pages
- Downloads all photos and assets to organized folders
- Stores data in human-readable JSON format
- Easy to browse and search
- Can be imported into other systems

## Prerequisites

- Python 3.8 or higher
- Valid Instant Church Directory account credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/heathdutton/instantchurchdirectory-export.git
cd instantchurchdirectory-export
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

5. Create a `.env` file with your credentials:
```bash
cp .env.example .env
```

Edit `.env` and add your Instant Church Directory credentials:
```
ICD_USERNAME=your_email@example.com
ICD_PASSWORD=your_password
```

## Usage

Run the scraper:
```bash
python scraper.py
```

The script will:
1. Log in to Instant Church Directory
2. Scrape all sections (families, staff, groups, events, pages)
3. Download all photos and assets
4. Save organized JSON files to the `exports/` directory

## Output Structure

```
exports/
├── families/
│   ├── families.json
│   └── photos/
├── staff/
│   ├── staff.json
│   └── photos/
├── groups/
│   ├── groups.json
│   └── photos/
├── birthdays.json
├── anniversaries.json
└── additional_pages/
    ├── pages.json
    └── assets/
```

## Data Format

All JSON files include metadata and structured data. Example:

```json
{
  "metadata": {
    "export_date": "2026-01-02T15:30:00Z",
    "total_records": 150,
    "source": "https://members.instantchurchdirectory.com"
  },
  "families": [
    {
      "id": "family_001",
      "name": "Smith Family",
      "photo": "exports/families/photos/smith_family.jpg",
      "members": [...],
      "contact": {...}
    }
  ]
}
```

## License

MIT

## Disclaimer

This tool is for personal use only. Please respect your church directory's terms of service and privacy policies. Only export and use data in accordance with your church's guidelines.
