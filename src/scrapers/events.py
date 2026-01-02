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
        # Extract directory ID from current URL
        current_url = page.url
        match = re.search(r'/([a-f0-9-]{36})', current_url)
        if not match:
            print("  Warning: Could not determine directory ID")
            return events

        directory_id = match.group(1)

        # Scrape birthdays
        print("  Navigating to birthdays page...")
        birthdays_url = f'https://members.instantchurchdirectory.com/birthdays/{directory_id}'
        await page.goto(birthdays_url, timeout=15000)
        await page.wait_for_load_state('networkidle', timeout=10000)
        await page.wait_for_timeout(2000)

        # Get all birthday items
        birthday_elements = await page.query_selector_all('.js-icd-members-family-list-item')
        print(f"  Found {len(birthday_elements)} birthday entries")

        for element in birthday_elements:
            try:
                text = await element.inner_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]

                if lines:
                    name = lines[0]
                    date = lines[1] if len(lines) > 1 else ""

                    events["birthdays"].append({
                        "name": name,
                        "date": date
                    })
            except Exception as e:
                print(f"    Warning: Error processing birthday: {str(e)}")
                continue

        # Scrape anniversaries
        print("  Navigating to anniversaries page...")
        anniversaries_url = f'https://members.instantchurchdirectory.com/anniversaries/{directory_id}'
        await page.goto(anniversaries_url, timeout=15000)
        await page.wait_for_load_state('networkidle', timeout=10000)
        await page.wait_for_timeout(2000)

        # Get all anniversary items
        anniversary_elements = await page.query_selector_all('.js-icd-members-family-list-item')
        print(f"  Found {len(anniversary_elements)} anniversary entries")

        for element in anniversary_elements:
            try:
                text = await element.inner_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]

                if lines:
                    family = lines[0]
                    date = lines[1] if len(lines) > 1 else ""

                    events["anniversaries"].append({
                        "family": family,
                        "date": date
                    })
            except Exception as e:
                print(f"    Warning: Error processing anniversary: {str(e)}")
                continue

        print(f"  Total: {len(events['birthdays'])} birthdays and {len(events['anniversaries'])} anniversaries")

    except Exception as e:
        print(f"  Error scraping events: {str(e)}")
        import traceback
        traceback.print_exc()

    return events
