"""
Authentication module for Instant Church Directory
"""
import os
from typing import Tuple
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page, Browser

# Load environment variables
load_dotenv()

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


async def get_authenticated_page() -> Tuple[Page, Browser]:
    """
    Authenticate with Instant Church Directory and return authenticated page.

    Returns:
        tuple[Page, Browser]: Authenticated page and browser instance

    Raises:
        AuthenticationError: If credentials are missing or login fails
    """
    username = os.getenv('ICD_USERNAME')
    password = os.getenv('ICD_PASSWORD')

    if not username or not password:
        raise AuthenticationError(
            "ICD_USERNAME and ICD_PASSWORD must be set in .env file"
        )

    print("Starting browser...")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()

    try:
        print(f"Navigating to login page...")
        await page.goto('https://members.instantchurchdirectory.com/')

        # Step 1: Enter email
        print(f"Entering email: {username}...")
        await page.wait_for_selector('input[type="email"], input[type="text"]', timeout=10000)

        email_input = await page.query_selector('input[type="email"], input[type="text"]')
        if not email_input:
            raise AuthenticationError("Could not find email input field")

        await email_input.fill(username)

        # Click submit or press Enter to go to password page
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Sign In"), button:has-text("Continue")')
        if submit_button:
            await submit_button.click()
        else:
            await email_input.press('Enter')

        # Wait for password page to load
        print("Waiting for password page...")
        await page.wait_for_selector('input[type="password"]', timeout=10000)

        # Step 2: Enter password
        print("Entering password...")
        password_input = await page.query_selector('input[type="password"]')
        if not password_input:
            raise AuthenticationError("Could not find password input field")

        await password_input.fill(password)

        # Submit password form
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Sign In")')
        if submit_button:
            await submit_button.click()
        else:
            await password_input.press('Enter')

        # Wait for navigation after login
        print("Waiting for login to complete...")
        await page.wait_for_load_state('networkidle', timeout=15000)

        # Give it a moment to fully load
        await page.wait_for_timeout(2000)

        # Verify login success by checking if we're NOT on sign-in page
        current_url = page.url
        if 'signin' in current_url.lower() or 'login' in current_url.lower():
            # Check for error messages
            error_element = await page.query_selector('.error, .alert, [role="alert"]')
            if error_element:
                error_text = await error_element.inner_text()
                raise AuthenticationError(f"Login failed: {error_text}")
            raise AuthenticationError(f"Login failed: Still on sign-in page ({current_url})")

        print(f"Authentication successful! Logged in to: {current_url}")
        return page, browser

    except Exception as e:
        await browser.close()
        if isinstance(e, AuthenticationError):
            raise
        raise AuthenticationError(f"Authentication failed: {str(e)}")
