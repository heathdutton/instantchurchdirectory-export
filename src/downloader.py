"""
Asset downloader with deduplication
"""
import os
import hashlib
from pathlib import Path
from urllib.parse import urlparse
import aiohttp
import aiofiles


async def download_asset(url: str, destination_dir: str, session: aiohttp.ClientSession = None) -> str:
    """
    Download an asset from a URL to the destination directory.
    Uses SHA-256 hash of URL for deduplication.

    Args:
        url: URL of the asset to download
        destination_dir: Directory to save the asset
        session: Optional aiohttp session for connection pooling

    Returns:
        str: Relative path to the downloaded file

    Raises:
        Exception: If download fails after retries
    """
    if not url:
        return ""

    # Create destination directory
    Path(destination_dir).mkdir(parents=True, exist_ok=True)

    # Extract filename from URL
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    # If no filename, create one from hash
    if not filename or '.' not in filename:
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
        filename = f"asset_{url_hash}.jpg"

    filepath = os.path.join(destination_dir, filename)

    # Check if already downloaded
    if os.path.exists(filepath):
        return filepath

    # Download with retries
    max_retries = 3
    own_session = session is None

    try:
        if own_session:
            session = aiohttp.ClientSession()

        for attempt in range(max_retries):
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        content = await response.read()
                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(content)
                        return filepath
                    else:
                        print(f"  Warning: Failed to download {url} - Status {response.status}")
                        if attempt < max_retries - 1:
                            continue
                        return ""
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  Retry {attempt + 1}/{max_retries} for {url}")
                    continue
                print(f"  Error downloading {url}: {str(e)}")
                return ""
    finally:
        if own_session and session:
            await session.close()

    return ""


async def download_assets_batch(urls: list[str], destination_dir: str) -> dict[str, str]:
    """
    Download multiple assets in parallel.

    Args:
        urls: List of URLs to download
        destination_dir: Directory to save assets

    Returns:
        dict: Mapping of original URLs to local file paths
    """
    if not urls:
        return {}

    results = {}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            if url:
                tasks.append(download_asset(url, destination_dir, session))

        if tasks:
            paths = await asyncio.gather(*tasks, return_exceptions=True)
            for url, path in zip(urls, paths):
                if isinstance(path, str) and path:
                    results[url] = path
                elif isinstance(path, Exception):
                    print(f"  Error downloading {url}: {str(path)}")

    return results


# Import asyncio at the end to avoid circular imports
import asyncio
