#!/usr/bin/env python3
"""
Instant Church Directory Scraper
Main entry point for scraping all directory data
"""
import asyncio
import sys
from datetime import datetime

from src.auth import get_authenticated_page, AuthenticationError
from src.exporter import export_to_json, create_export_structure
from src.downloader import download_asset
from src.scrapers.families import scrape_families
from src.scrapers.staff import scrape_staff
from src.scrapers.groups import scrape_groups
from src.scrapers.events import scrape_events
from src.scrapers.pages import scrape_pages


async def download_photos_for_records(records, photo_key, dest_dir):
    """Download photos for a list of records."""
    if not records:
        return records

    print(f"  Downloading {len(records)} photos...")
    downloaded = 0

    for record in records:
        photo_url = record.get(photo_key, "")
        if photo_url:
            try:
                local_path = await download_asset(photo_url, dest_dir)
                if local_path:
                    record[photo_key] = local_path
                    downloaded += 1
            except Exception as e:
                print(f"    Error downloading photo: {str(e)}")
                record[photo_key] = ""

    print(f"  Downloaded {downloaded} photos")
    return records


async def main():
    """Main scraper function."""
    start_time = datetime.now()

    print("=" * 60)
    print("Instant Church Directory Scraper")
    print("=" * 60)

    # Create export directory structure
    create_export_structure()

    page = None
    browser = None
    summary = {
        "families": 0,
        "staff": 0,
        "groups": 0,
        "birthdays": 0,
        "anniversaries": 0,
        "pages": 0,
        "errors": []
    }

    try:
        # Authenticate
        print("\nAuthenticating...")
        page, browser = await get_authenticated_page()

        # Scrape families
        try:
            families = await scrape_families(page)
            summary["families"] = len(families)

            if families:
                # Download family photos
                families = await download_photos_for_records(
                    families, "photo", "exports/families/photos"
                )
                # Export to JSON
                await export_to_json("families", families)
        except Exception as e:
            error_msg = f"Error scraping families: {str(e)}"
            print(f"  {error_msg}")
            summary["errors"].append(error_msg)

        # Scrape staff
        try:
            staff = await scrape_staff(page)
            summary["staff"] = len(staff)

            if staff:
                # Download staff photos
                staff = await download_photos_for_records(
                    staff, "photo", "exports/staff/photos"
                )
                # Export to JSON
                await export_to_json("staff", staff)
        except Exception as e:
            error_msg = f"Error scraping staff: {str(e)}"
            print(f"  {error_msg}")
            summary["errors"].append(error_msg)

        # Scrape groups
        try:
            groups = await scrape_groups(page)
            summary["groups"] = len(groups)

            if groups:
                # Download group photos
                groups = await download_photos_for_records(
                    groups, "photo", "exports/groups/photos"
                )
                # Export to JSON
                await export_to_json("groups", groups)
        except Exception as e:
            error_msg = f"Error scraping groups: {str(e)}"
            print(f"  {error_msg}")
            summary["errors"].append(error_msg)

        # Scrape events (birthdays & anniversaries)
        try:
            events = await scrape_events(page)
            summary["birthdays"] = len(events.get("birthdays", []))
            summary["anniversaries"] = len(events.get("anniversaries", []))

            if events:
                # Export to JSON (stored at root level)
                import json
                from pathlib import Path

                events_data = {
                    "metadata": {
                        "export_date": datetime.utcnow().isoformat() + "Z",
                        "total_records": summary["birthdays"] + summary["anniversaries"],
                        "source": "https://members.instantchurchdirectory.com"
                    },
                    "birthdays": events.get("birthdays", []),
                    "anniversaries": events.get("anniversaries", [])
                }

                Path("exports").mkdir(parents=True, exist_ok=True)
                with open("exports/events.json", 'w', encoding='utf-8') as f:
                    json.dump(events_data, f, indent=2, ensure_ascii=False)
                print(f"  Exported events to exports/events.json")
        except Exception as e:
            error_msg = f"Error scraping events: {str(e)}"
            print(f"  {error_msg}")
            summary["errors"].append(error_msg)

        # Scrape additional pages
        try:
            pages = await scrape_pages(page)
            summary["pages"] = len(pages)

            if pages:
                # Download assets for pages
                print(f"  Downloading assets for {len(pages)} pages...")
                for page_data in pages:
                    asset_urls = page_data.get("asset_urls", [])
                    for asset_url in asset_urls[:10]:  # Limit assets per page
                        try:
                            await download_asset(asset_url, "exports/additional_pages/assets")
                        except:
                            pass

                # Export to JSON
                await export_to_json("additional_pages", pages)
        except Exception as e:
            error_msg = f"Error scraping pages: {str(e)}"
            print(f"  {error_msg}")
            summary["errors"].append(error_msg)

    except AuthenticationError as e:
        print(f"\nAuthentication failed: {str(e)}")
        print("Please check your credentials in the .env file")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up
        if browser:
            print("\nClosing browser...")
            await browser.close()

    # Print summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("Scraping Complete!")
    print("=" * 60)
    print(f"Duration: {duration:.1f} seconds")
    print(f"\nResults:")
    print(f"  Families: {summary['families']}")
    print(f"  Staff: {summary['staff']}")
    print(f"  Groups: {summary['groups']}")
    print(f"  Birthdays: {summary['birthdays']}")
    print(f"  Anniversaries: {summary['anniversaries']}")
    print(f"  Additional Pages: {summary['pages']}")

    if summary["errors"]:
        print(f"\nErrors: {len(summary['errors'])}")
        for error in summary["errors"]:
            print(f"  - {error}")

    print(f"\nExported data saved to: exports/")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
