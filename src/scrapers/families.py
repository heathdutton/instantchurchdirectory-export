"""
Families scraper for Instant Church Directory
"""
from playwright.async_api import Page
from typing import List, Dict, Any


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
        # Navigate to families/directory section
        # The exact URL structure may vary, try common patterns
        await page.goto('https://members.instantchurchdirectory.com/members', timeout=15000)
        await page.wait_for_load_state('networkidle', timeout=10000)

        # Wait for content to load
        await page.wait_for_timeout(2000)

        # Try to find family/member cards or list items
        # This will need to be adjusted based on the actual HTML structure
        family_elements = await page.query_selector_all('.member, .family, .person-card, [class*="member"], [class*="family"]')

        if not family_elements:
            # Try alternative selectors
            family_elements = await page.query_selector_all('article, .card, [role="article"]')

        print(f"  Found {len(family_elements)} potential family elements")

        for idx, element in enumerate(family_elements):
            try:
                family_data = {
                    "id": f"family_{str(idx + 1).zfill(3)}",
                    "name": "",
                    "photo": "",
                    "members": [],
                    "contact": {}
                }

                # Extract text content
                text_content = await element.inner_text()

                # Try to find name
                name_elem = await element.query_selector('h1, h2, h3, h4, .name, [class*="name"]')
                if name_elem:
                    family_data["name"] = (await name_elem.inner_text()).strip()
                else:
                    # Use first line of text as name
                    lines = text_content.split('\n')
                    if lines:
                        family_data["name"] = lines[0].strip()

                # Try to find photo
                img_elem = await element.query_selector('img')
                if img_elem:
                    photo_url = await img_elem.get_attribute('src')
                    if photo_url and not photo_url.startswith('data:'):
                        # Make absolute URL if needed
                        if photo_url.startswith('//'):
                            photo_url = 'https:' + photo_url
                        elif photo_url.startswith('/'):
                            photo_url = 'https://members.instantchurchdirectory.com' + photo_url
                        family_data["photo"] = photo_url

                # Extract contact info from text
                # Look for email pattern
                import re
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_content)
                if email_match:
                    family_data["contact"]["email"] = email_match.group()

                # Look for phone pattern
                phone_match = re.search(r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b', text_content)
                if phone_match:
                    family_data["contact"]["phone"] = phone_match.group()

                # Look for address (lines with numbers and street indicators)
                address_match = re.search(r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Circle|Cir)[,\s]+[\w\s]+,?\s+[A-Z]{2}\s+\d{5}', text_content, re.IGNORECASE)
                if address_match:
                    family_data["contact"]["address"] = address_match.group()

                # Parse members from text (simplified - actual structure may vary)
                # Skip first line (family name) and look for individual names
                text_lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                for line in text_lines[1:]:
                    # Skip lines that look like contact info
                    if '@' in line or re.search(r'\d{3}[-.)]\d{3}', line):
                        continue
                    # Lines that look like names (2-4 words, capitalized)
                    if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}$', line):
                        family_data["members"].append({
                            "name": line,
                            "role": "",
                            "age": None
                        })

                if family_data["name"]:
                    families.append(family_data)

            except Exception as e:
                print(f"  Warning: Error processing family element {idx}: {str(e)}")
                continue

        print(f"  Successfully scraped {len(families)} families")

    except Exception as e:
        print(f"  Error scraping families: {str(e)}")

    return families
