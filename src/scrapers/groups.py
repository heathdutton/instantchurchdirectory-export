"""
Groups scraper for Instant Church Directory
"""
from playwright.async_api import Page
from typing import List, Dict, Any
import re


async def scrape_groups(page: Page) -> List[Dict[str, Any]]:
    """
    Scrape groups/ministries information.

    Args:
        page: Authenticated Playwright page

    Returns:
        List of group records with photos and info
    """
    print("\nScraping groups...")

    groups = []

    try:
        # Extract directory ID from current URL
        current_url = page.url
        match = re.search(r'/([a-f0-9-]{36})', current_url)
        if not match:
            print("  Warning: Could not determine directory ID")
            return groups

        directory_id = match.group(1)
        groups_url = f'https://members.instantchurchdirectory.com/group/{directory_id}'

        print(f"  Navigating to {groups_url}")
        await page.goto(groups_url, timeout=15000)
        await page.wait_for_load_state('networkidle', timeout=10000)
        await page.wait_for_timeout(2000)

        # Find group list items
        group_elements = await page.query_selector_all('.js-icd-members-family-list-item')

        print(f"  Found {len(group_elements)} group elements")

        for idx, element in enumerate(group_elements):
            try:
                # Extract group name and info
                text_content = await element.inner_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]

                group_name = lines[0] if lines else f"Group {idx + 1}"
                description = lines[1] if len(lines) > 1 else ""

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

                # Look for leaders in text
                leaders = []
                if 'leader' in text_content.lower() or 'led by' in text_content.lower():
                    leader_match = re.search(r'(?:Leader|Led by):\s*([^\n]+)', text_content, re.IGNORECASE)
                    if leader_match:
                        leaders = [l.strip() for l in leader_match.group(1).split(',')]

                group_data = {
                    "id": f"group_{str(idx + 1).zfill(3)}",
                    "name": group_name,
                    "description": description,
                    "leaders": leaders,
                    "photo": photo_url
                }

                groups.append(group_data)

            except Exception as e:
                print(f"  Warning: Error processing group element {idx}: {str(e)}")
                continue

        print(f"  Successfully scraped {len(groups)} groups")

    except Exception as e:
        print(f"  Error scraping groups: {str(e)}")
        import traceback
        traceback.print_exc()

    return groups
