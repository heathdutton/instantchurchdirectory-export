#!/usr/bin/env python3
"""
Debug script to test data extraction
"""
import asyncio
import json
from src.auth import get_authenticated_page


async def main():
    """Test data extraction."""
    print("Authenticating...")

    page, browser = await get_authenticated_page()

    try:
        # Extract family data
        print("\n=== TESTING FAMILY EXTRACTION ===")
        family_items = await page.query_selector_all('.js-icd-members-family-list-item')
        print(f"Found {len(family_items)} family items")

        if family_items:
            # Get first few families as examples
            for i, item in enumerate(family_items[:3]):
                print(f"\n--- Family {i+1} ---")
                # Get the HTML
                html = await item.inner_html()
                text = await item.inner_text()
                print(f"Text: {text[:200]}")

                # Try to find image
                img = await item.query_selector('img')
                if img:
                    src = await img.get_attribute('src')
                    print(f"Image: {src}")

                # Try to find link
                link = await item.query_selector('a')
                if link:
                    href = await link.get_attribute('href')
                    print(f"Link: {href}")

        # Navigate to other sections
        print("\n=== TESTING STAFF EXTRACTION ===")
        staff_link = await page.query_selector('a[href*="/staff/"]')
        if staff_link:
            await staff_link.click()
            await page.wait_for_load_state('networkidle', timeout=10000)
            await page.wait_for_timeout(2000)

            print(f"Staff page URL: {page.url}")
            staff_items = await page.query_selector_all('.js-icd-members-family-list-item, .staff-item, [class*="staff"]')
            print(f"Found {len(staff_items)} potential staff items")

        # Try birthdays
        print("\n=== TESTING BIRTHDAYS EXTRACTION ===")
        await page.goto(page.url.replace('/staff/', '/birthdays/'))
        await page.wait_for_load_state('networkidle', timeout=10000)
        await page.wait_for_timeout(2000)

        print(f"Birthdays page URL: {page.url}")
        birthday_items = await page.query_selector_all('.js-icd-members-family-list-item, [class*="birthday"]')
        print(f"Found {len(birthday_items)} potential birthday items")

        # Get body text to look for birthday data
        body_text = await page.inner_text('body')
        print(f"Page text length: {len(body_text)}")
        print(f"First 500 chars: {body_text[:500]}")

    finally:
        await browser.close()

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
