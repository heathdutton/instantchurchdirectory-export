"""
Additional pages scraper
"""
from playwright.async_api import Page
from typing import List, Dict, Any
import re


async def scrape_pages(page: Page) -> List[Dict[str, Any]]:
    """
    Scrape additional pages like bulletins, forms, etc.

    Args:
        page: Authenticated Playwright page

    Returns:
        List of page records with content and assets
    """
    print("\nScraping additional pages...")

    pages = []

    try:
        # Extract directory ID from current URL
        current_url = page.url
        match = re.search(r'/([a-f0-9-]{36})', current_url)
        if not match:
            print("  Warning: Could not determine directory ID")
            return pages

        directory_id = match.group(1)
        pages_url = f'https://members.instantchurchdirectory.com/additionalpages/{directory_id}'

        print(f"  Navigating to {pages_url}")
        await page.goto(pages_url, timeout=15000)
        await page.wait_for_load_state('networkidle', timeout=10000)
        await page.wait_for_timeout(2000)

        # Find additional page items
        page_elements = await page.query_selector_all('.js-icd-members-family-list-item, a[href*="additionalpage"]')

        print(f"  Found {len(page_elements)} additional page elements")

        for idx, element in enumerate(page_elements):
            try:
                # Extract page name
                text = await element.inner_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]

                page_title = lines[0] if lines else f"Page {idx + 1}"

                # Get link
                link_elem = await element.query_selector('a')
                page_url = ""
                if link_elem:
                    href = await link_elem.get_attribute('href')
                    if href:
                        if href.startswith('/'):
                            page_url = 'https://members.instantchurchdirectory.com' + href
                        else:
                            page_url = href

                page_data = {
                    "id": f"page_{str(idx + 1).zfill(3)}",
                    "title": page_title,
                    "url": page_url,
                    "content": text[:500]  # Limit content
                }

                pages.append(page_data)

            except Exception as e:
                print(f"  Warning: Error processing page element {idx}: {str(e)}")
                continue

        print(f"  Successfully scraped {len(pages)} additional pages")

    except Exception as e:
        print(f"  Error scraping pages: {str(e)}")
        import traceback
        traceback.print_exc()

    return pages
