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
        # Try to navigate to staff section
        # Common patterns: /staff, /leaders, /ministry
        staff_urls = [
            'https://members.instantchurchdirectory.com/staff',
            'https://members.instantchurchdirectory.com/leaders',
            'https://members.instantchurchdirectory.com/ministry'
        ]

        page_loaded = False
        for url in staff_urls:
            try:
                await page.goto(url, timeout=10000)
                await page.wait_for_load_state('networkidle', timeout=5000)
                page_loaded = True
                break
            except:
                continue

        if not page_loaded:
            print("  Staff page not found, skipping...")
            return staff

        await page.wait_for_timeout(2000)

        # Find staff elements
        staff_elements = await page.query_selector_all('.staff, .leader, .ministry, [class*="staff"], [class*="leader"]')

        if not staff_elements:
            staff_elements = await page.query_selector_all('article, .card, [role="article"]')

        print(f"  Found {len(staff_elements)} potential staff elements")

        for idx, element in enumerate(staff_elements):
            try:
                staff_data = {
                    "id": f"staff_{str(idx + 1).zfill(3)}",
                    "name": "",
                    "title": "",
                    "email": "",
                    "phone": "",
                    "bio": "",
                    "photo": ""
                }

                text_content = await element.inner_text()

                # Extract name
                name_elem = await element.query_selector('h1, h2, h3, h4, .name, [class*="name"]')
                if name_elem:
                    staff_data["name"] = (await name_elem.inner_text()).strip()
                else:
                    lines = text_content.split('\n')
                    if lines:
                        staff_data["name"] = lines[0].strip()

                # Extract title
                title_elem = await element.query_selector('.title, .position, .role, [class*="title"], [class*="position"]')
                if title_elem:
                    staff_data["title"] = (await title_elem.inner_text()).strip()

                # Extract photo
                img_elem = await element.query_selector('img')
                if img_elem:
                    photo_url = await img_elem.get_attribute('src')
                    if photo_url and not photo_url.startswith('data:'):
                        if photo_url.startswith('//'):
                            photo_url = 'https:' + photo_url
                        elif photo_url.startswith('/'):
                            photo_url = 'https://members.instantchurchdirectory.com' + photo_url
                        staff_data["photo"] = photo_url

                # Extract contact info
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_content)
                if email_match:
                    staff_data["email"] = email_match.group()

                phone_match = re.search(r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b', text_content)
                if phone_match:
                    staff_data["phone"] = phone_match.group()

                # Extract bio (longer text content)
                bio_elem = await element.query_selector('.bio, .description, p, [class*="bio"]')
                if bio_elem:
                    staff_data["bio"] = (await bio_elem.inner_text()).strip()

                if staff_data["name"]:
                    staff.append(staff_data)

            except Exception as e:
                print(f"  Warning: Error processing staff element {idx}: {str(e)}")
                continue

        print(f"  Successfully scraped {len(staff)} staff members")

    except Exception as e:
        print(f"  Error scraping staff: {str(e)}")

    return staff
