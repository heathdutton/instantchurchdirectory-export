"""
Groups scraper for Instant Church Directory
"""
from playwright.async_api import Page
from typing import List, Dict, Any


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
        # Try to navigate to groups section
        group_urls = [
            'https://members.instantchurchdirectory.com/groups',
            'https://members.instantchurchdirectory.com/ministries',
            'https://members.instantchurchdirectory.com/smallgroups'
        ]

        page_loaded = False
        for url in group_urls:
            try:
                await page.goto(url, timeout=10000)
                await page.wait_for_load_state('networkidle', timeout=5000)
                page_loaded = True
                break
            except:
                continue

        if not page_loaded:
            print("  Groups page not found, skipping...")
            return groups

        await page.wait_for_timeout(2000)

        # Find group elements
        group_elements = await page.query_selector_all('.group, .ministry, [class*="group"], [class*="ministry"]')

        if not group_elements:
            group_elements = await page.query_selector_all('article, .card, [role="article"]')

        print(f"  Found {len(group_elements)} potential group elements")

        for idx, element in enumerate(group_elements):
            try:
                group_data = {
                    "id": f"group_{str(idx + 1).zfill(3)}",
                    "name": "",
                    "description": "",
                    "leaders": [],
                    "members": [],
                    "photo": ""
                }

                text_content = await element.inner_text()

                # Extract name
                name_elem = await element.query_selector('h1, h2, h3, h4, .name, [class*="name"]')
                if name_elem:
                    group_data["name"] = (await name_elem.inner_text()).strip()
                else:
                    lines = text_content.split('\n')
                    if lines:
                        group_data["name"] = lines[0].strip()

                # Extract description
                desc_elem = await element.query_selector('.description, p, [class*="description"]')
                if desc_elem:
                    group_data["description"] = (await desc_elem.inner_text()).strip()

                # Extract photo
                img_elem = await element.query_selector('img')
                if img_elem:
                    photo_url = await img_elem.get_attribute('src')
                    if photo_url and not photo_url.startswith('data:'):
                        if photo_url.startswith('//'):
                            photo_url = 'https:' + photo_url
                        elif photo_url.startswith('/'):
                            photo_url = 'https://members.instantchurchdirectory.com' + photo_url
                        group_data["photo"] = photo_url

                # Extract leaders (look for "Leader:" or "Led by:" patterns)
                if 'leader' in text_content.lower() or 'led by' in text_content.lower():
                    import re
                    leader_match = re.search(r'(?:Leader|Led by):\s*([^\n]+)', text_content, re.IGNORECASE)
                    if leader_match:
                        leaders = [l.strip() for l in leader_match.group(1).split(',')]
                        group_data["leaders"] = leaders

                if group_data["name"]:
                    groups.append(group_data)

            except Exception as e:
                print(f"  Warning: Error processing group element {idx}: {str(e)}")
                continue

        print(f"  Successfully scraped {len(groups)} groups")

    except Exception as e:
        print(f"  Error scraping groups: {str(e)}")

    return groups
