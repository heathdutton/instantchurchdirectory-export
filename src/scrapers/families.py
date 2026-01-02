"""
Families scraper for Instant Church Directory
"""
from playwright.async_api import Page
from typing import List, Dict, Any
import re


async def scrape_families(page: Page) -> List[Dict[str, Any]]:
    """
    Scrape family directory information.

    Args:
        page: Authenticated Playwright page

    Returns:
        List of family records with photos and contact info
    """
    print("\nScraping families...")

    families = []

    try:
        # We're already on the families page after login
        # Just ensure we're on the right page
        current_url = page.url
        if '/families/' not in current_url:
            # Extract directory ID from current URL
            match = re.search(r'/([a-f0-9-]{36})', current_url)
            if match:
                directory_id = match.group(1)
                await page.goto(f'https://members.instantchurchdirectory.com/families/{directory_id}', timeout=15000)
            else:
                print("  Warning: Could not determine directory ID")
                return families

        await page.wait_for_load_state('networkidle', timeout=10000)
        await page.wait_for_timeout(2000)

        # Find family list items using the correct selector
        family_elements = await page.query_selector_all('.js-icd-members-family-list-item')

        print(f"  Found {len(family_elements)} family elements")

        for idx, element in enumerate(family_elements):
            try:
                # Extract family name from text content
                text_content = await element.inner_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]

                family_name = lines[0] if lines else f"Family {idx + 1}"
                members_text = lines[1] if len(lines) > 1 else ""

                # Get the link to family detail page
                link_elem = await element.query_selector('a')
                detail_url = ""
                if link_elem:
                    href = await link_elem.get_attribute('href')
                    if href:
                        if href.startswith('/'):
                            detail_url = 'https://members.instantchurchdirectory.com' + href
                        else:
                            detail_url = href

                # Try to find photo
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

                family_data = {
                    "id": f"family_{str(idx + 1).zfill(3)}",
                    "name": family_name,
                    "members_text": members_text,
                    "photo": photo_url,
                    "detail_url": detail_url,
                    "contact": {}
                }

                # If we have a detail URL, we could navigate there to get more info
                # But for performance, we'll just collect the basic info for now
                # The detail page would have full contact info, addresses, etc.

                families.append(family_data)

            except Exception as e:
                print(f"  Warning: Error processing family element {idx}: {str(e)}")
                continue

        print(f"  Successfully scraped {len(families)} families")

    except Exception as e:
        print(f"  Error scraping families: {str(e)}")
        import traceback
        traceback.print_exc()

    return families
