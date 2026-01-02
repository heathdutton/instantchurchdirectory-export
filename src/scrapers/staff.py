"""
Staff scraper for Instant Church Directory
"""
from playwright.async_api import Page
from typing import List, Dict, Any
import re


async def scrape_staff(page: Page) -> List[Dict[str, Any]]:
    """
    Scrape staff directory information.

    Args:
        page: Authenticated Playwright page

    Returns:
        List of staff records with photos and contact info
    """
    print("\nScraping staff...")

    staff = []

    try:
        # Extract directory ID from current URL
        current_url = page.url
        match = re.search(r'/([a-f0-9-]{36})', current_url)
        if not match:
            print("  Warning: Could not determine directory ID")
            return staff

        directory_id = match.group(1)
        staff_url = f'https://members.instantchurchdirectory.com/staff/{directory_id}'

        print(f"  Navigating to {staff_url}")
        await page.goto(staff_url, timeout=15000)
        await page.wait_for_load_state('networkidle', timeout=10000)
        await page.wait_for_timeout(2000)

        # Find staff list items (likely uses same selector as families)
        staff_elements = await page.query_selector_all('.js-icd-members-family-list-item')

        print(f"  Found {len(staff_elements)} staff elements")

        for idx, element in enumerate(staff_elements):
            try:
                # Extract staff name and info from text content
                text_content = await element.inner_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]

                staff_name = lines[0] if lines else f"Staff {idx + 1}"
                title = lines[1] if len(lines) > 1 else ""

                # Get photo
                img_elem = await element.query_selector('img')
                photo_url = ""
                if img_elem:
                    src = await img_elem.get_attribute('src')
                    if src and not src.startswith('data:'):
                        if src.startswith('//'):
                            photo_url = 'https:' + src
                        elif src.startswith('/'):
                            photo_url = 'https://members.instantchurchdirectory.com' + src
                        else:
                            photo_url = src

                # Extract contact info from text
                email = ""
                phone = ""
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_content)
                if email_match:
                    email = email_match.group()

                phone_match = re.search(r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b', text_content)
                if phone_match:
                    phone = phone_match.group()

                staff_data = {
                    "id": f"staff_{str(idx + 1).zfill(3)}",
                    "name": staff_name,
                    "title": title,
                    "email": email,
                    "phone": phone,
                    "photo": photo_url
                }

                staff.append(staff_data)

            except Exception as e:
                print(f"  Warning: Error processing staff element {idx}: {str(e)}")
                continue

        print(f"  Successfully scraped {len(staff)} staff members")

    except Exception as e:
        print(f"  Error scraping staff: {str(e)}")
        import traceback
        traceback.print_exc()

    return staff
