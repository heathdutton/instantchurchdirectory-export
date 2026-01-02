#!/usr/bin/env python3
"""
Debug script to inspect the Instant Church Directory page structure
"""
import asyncio
from src.auth import get_authenticated_page


async def main():
    """Inspect page structure."""
    print("Authenticating and inspecting page structure...")

    page, browser = await get_authenticated_page()

    try:
        # Wait for page to fully load
        await page.wait_for_timeout(3000)

        # Save screenshot
        await page.screenshot(path="debug_screenshot.png", full_page=True)
        print("Saved screenshot to debug_screenshot.png")

        # Save HTML
        html = await page.content()
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved HTML to debug_page.html")

        # Print URL
        print(f"Current URL: {page.url}")

        # Try to find main navigation
        nav_links = await page.query_selector_all('a')
        print(f"\nFound {len(nav_links)} links on the page")

        # Print first 20 links
        print("\nFirst 20 links:")
        for i, link in enumerate(nav_links[:20]):
            href = await link.get_attribute('href')
            text = await link.inner_text() if await link.inner_text() else ""
            print(f"  {i+1}. {text[:50]} -> {href}")

        # Look for common content containers
        print("\nLooking for common content containers...")
        containers = await page.query_selector_all('main, [role="main"], .container, .content, #content')
        print(f"Found {len(containers)} potential content containers")

        # Check for member/family cards
        print("\nLooking for member/family elements...")
        member_selectors = [
            '.member',
            '.family',
            '.person',
            '[class*="member"]',
            '[class*="family"]',
            'article',
            '.card'
        ]

        for selector in member_selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"  {selector}: found {len(elements)} elements")

    finally:
        await browser.close()

    print("\nDone! Check debug_screenshot.png and debug_page.html for details.")


if __name__ == "__main__":
    asyncio.run(main())
