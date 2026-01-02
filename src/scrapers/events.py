"""
Events scraper for birthdays and anniversaries
"""
from playwright.async_api import Page
from typing import Dict, Any, List
import re


async def scrape_events(page: Page) -> Dict[str, List[Dict[str, Any]]]:
    """
    Scrape birthdays and anniversaries.

    Args:
        page: Authenticated Playwright page

    Returns:
        Dict with 'birthdays' and 'anniversaries' lists
    """
    print("\nScraping events (birthdays & anniversaries)...")

    events = {
        "birthdays": [],
        "anniversaries": []
    }

    try:
        # Try to navigate to events/birthdays section
        event_urls = [
            'https://members.instantchurchdirectory.com/birthdays',
            'https://members.instantchurchdirectory.com/events',
            'https://members.instantchurchdirectory.com/calendar'
        ]

        page_loaded = False
        for url in event_urls:
            try:
                await page.goto(url, timeout=10000)
                await page.wait_for_load_state('networkidle', timeout=5000)
                page_loaded = True
                break
            except:
                continue

        if not page_loaded:
            print("  Events page not found, skipping...")
            return events

        await page.wait_for_timeout(2000)

        # Get page content and look for birthdays/anniversaries
        content = await page.content()
        text_content = await page.inner_text('body')

        # Look for birthday patterns
        birthday_matches = re.finditer(r'([A-Z][a-z]+\s+[A-Z][a-z]+).*?(?:birthday|born).*?(\d{1,2}/\d{1,2}|\w+\s+\d{1,2})', text_content, re.IGNORECASE)
        for match in birthday_matches:
            events["birthdays"].append({
                "name": match.group(1).strip(),
                "date": match.group(2).strip(),
                "family_id": ""
            })

        # Look for anniversary patterns
        anniversary_matches = re.finditer(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+).*?(?:anniversary).*?(\d{1,2}/\d{1,2}|\w+\s+\d{1,2})', text_content, re.IGNORECASE)
        for match in anniversary_matches:
            events["anniversaries"].append({
                "family": match.group(1).strip(),
                "date": match.group(2).strip()
            })

        print(f"  Found {len(events['birthdays'])} birthdays and {len(events['anniversaries'])} anniversaries")

    except Exception as e:
        print(f"  Error scraping events: {str(e)}")

    return events
