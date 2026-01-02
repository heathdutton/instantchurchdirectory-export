"""
Additional pages scraper
"""
from playwright.async_api import Page
from typing import List, Dict, Any


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
        # Try to find navigation links to discover available pages
        await page.goto('https://members.instantchurchdirectory.com/', timeout=10000)
        await page.wait_for_load_state('networkidle', timeout=5000)
        await page.wait_for_timeout(2000)

        # Find all navigation links
        nav_links = await page.query_selector_all('nav a, header a, .menu a, [role="navigation"] a')

        visited_urls = set()
        page_urls = []

        for link in nav_links:
            try:
                href = await link.get_attribute('href')
                if href and href not in visited_urls:
                    # Make absolute URL
                    if href.startswith('/'):
                        href = 'https://members.instantchurchdirectory.com' + href
                    elif not href.startswith('http'):
                        continue

                    # Skip external links and already scraped sections
                    if 'instantchurchdirectory.com' in href:
                        visited_urls.add(href)
                        page_urls.append(href)
            except:
                continue

        print(f"  Found {len(page_urls)} additional pages to scrape")

        # Limit to reasonable number
        page_urls = page_urls[:20]

        for idx, url in enumerate(page_urls):
            try:
                await page.goto(url, timeout=10000)
                await page.wait_for_load_state('networkidle', timeout=5000)
                await page.wait_for_timeout(1000)

                # Extract page title
                title_elem = await page.query_selector('h1, h2, title')
                title = ""
                if title_elem:
                    title = (await title_elem.inner_text()).strip()
                else:
                    title = url.split('/')[-1].replace('-', ' ').title()

                # Extract page content
                content_elem = await page.query_selector('main, article, .content, [role="main"]')
                content = ""
                if content_elem:
                    content = await content_elem.inner_text()
                else:
                    content = await page.inner_text('body')

                # Find assets (images, PDFs, etc.)
                asset_urls = []
                img_elements = await page.query_selector_all('img')
                for img in img_elements:
                    src = await img.get_attribute('src')
                    if src and not src.startswith('data:'):
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = 'https://members.instantchurchdirectory.com' + src
                        if src not in asset_urls:
                            asset_urls.append(src)

                # Find PDF links
                pdf_links = await page.query_selector_all('a[href$=".pdf"]')
                for link in pdf_links:
                    href = await link.get_attribute('href')
                    if href:
                        if href.startswith('//'):
                            href = 'https:' + href
                        elif href.startswith('/'):
                            href = 'https://members.instantchurchdirectory.com' + href
                        if href not in asset_urls:
                            asset_urls.append(href)

                page_data = {
                    "id": f"page_{str(idx + 1).zfill(3)}",
                    "title": title,
                    "url": url,
                    "content": content[:1000],  # Limit content length
                    "asset_urls": asset_urls
                }

                pages.append(page_data)

            except Exception as e:
                print(f"  Warning: Error scraping page {url}: {str(e)}")
                continue

        print(f"  Successfully scraped {len(pages)} additional pages")

    except Exception as e:
        print(f"  Error scraping pages: {str(e)}")

    return pages
