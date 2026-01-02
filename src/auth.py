"""
Authentication module for Instant Church Directory
"""
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page, Browser

# Load environment variables
load_dotenv()

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


async def get_authenticated_page() -> tuple[Page, Browser]:
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

        # Wait for login form to load
        await page.wait_for_selector('input[type="email"], input[type="text"]', timeout=10000)

        print(f"Logging in as {username}...")
        # Fill in credentials
        email_input = await page.query_selector('input[type="email"], input[type="text"]')
        if email_input:
            await email_input.fill(username)

        password_input = await page.query_selector('input[type="password"]')
        if password_input:
            await password_input.fill(password)

        # Submit the form
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
        if submit_button:
            await submit_button.click()
        else:
            # Try pressing Enter on the password field
            await page.press('input[type="password"]', 'Enter')

        # Wait for navigation after login
        await page.wait_for_load_state('networkidle', timeout=15000)

        # Verify login success by checking if we're still on the login page
        current_url = page.url
        if 'login' in current_url.lower() or current_url == 'https://members.instantchurchdirectory.com/':
            # Check for error messages
            error_element = await page.query_selector('.error, .alert, [role="alert"]')
            if error_element:
                error_text = await error_element.inner_text()
                raise AuthenticationError(f"Login failed: {error_text}")
            raise AuthenticationError("Login failed: Still on login page")

        print("Authentication successful!")
        return page, browser

    except Exception as e:
        await browser.close()
        if isinstance(e, AuthenticationError):
            raise
        raise AuthenticationError(f"Authentication failed: {str(e)}")
