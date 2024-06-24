"""
Firmware Downloader Script

Author:
Andreas

Date:
24.06.2024

Description:
This script downloads PlayStation 3 firmware files from https://darksoftware.xyz/PS3/FWlist
either as HTML file or URL. It organizes the firmware files into directories by section and
version, and creates a text file with the MD5 hash for each firmware.

Usage:
1. Run the script. (Tested with Python 3.12.3)
2. Enter the path to a local HTML file when prompted, or press Enter to provide a URL.
3. Provide a destination path where the files shall be placed
4. The script will download the firmware files and organize them accordingly.

Dependencies:
- requests: To handle HTTP requests.
- beautifulsoup4: To parse HTML content.

Install dependencies with:
pip install requests beautifulsoup4

References:
- File Hoster: https://darksoftware.xyz/PS3/FWlist
- Beautiful Soup Documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Requests Documentation: https://docs.python-requests.org/en/master/
"""

import os
import time

import requests
from bs4 import BeautifulSoup


# Base URL for downloads
# base_url = "https://psarchive.darksoftware.xyz/PS3/"


def get_html_content():
    html_file = input("Enter the path to the local HTML file (or press Enter to provide a URL): ").strip()
    if html_file:
        with open(html_file, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        url = input("Enter the URL of the HTML file: ").strip()
        response = requests.get(url)
        return response.text


def download_with_retries(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an error for bad status codes
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Skipping this file.")
                return None


def download_firmwares(soup, base_dir):
    # Base URL for downloads
    base_url = "https://psarchive.darksoftware.xyz/PS3/"

    # Create directories and download files
    sections = ['Retail Firmwares', 'Testkit Firmwares', 'PS3 GEX FW', 'DECR Firmware']

    for section in sections:
        section_dir = os.path.join(base_dir, section.replace(" ", "_"))
        os.makedirs(section_dir, exist_ok=True)

        table = soup.find('span', string=section).find_next('table')
        rows = table.find_all('tr')[1:]  # Skip the header row

        for row in rows:
            cols = row.find_all('td')
            version = cols[1].text.strip()
            size = cols[2].text.strip()
            download_url = cols[3].find('button')['data-url']
            md5_hash = cols[4].find('a')['data-copy']

            firmware_dir = os.path.join(section_dir, version)
            os.makedirs(firmware_dir, exist_ok=True)

            # Download the firmware file
            response = download_with_retries(download_url)
            if response:
                firmware_path = os.path.join(firmware_dir, 'PS3UPDAT.PUP')
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024
                wrote = 0
                with open(firmware_path, 'wb') as firmware_file:
                    for data in response.iter_content(block_size):
                        wrote = wrote + len(data)
                        firmware_file.write(data)
                        done = int(50 * wrote / total_size)
                        percent = (wrote / total_size) * 100
                        print(f"\r[{section} - {version}] {'█' * done}{'.' * (50-done)} {percent:.2f}% ({wrote / (1024 * 1024):.2f} MB / {total_size / (1024 * 1024):.2f} MB)", end='')

                # Write the MD5 hash to a text file
                md5_path = os.path.join(firmware_dir, 'md5.txt')
                with open(md5_path, 'w') as md5_file:
                    md5_file.write(md5_hash)

                print()  # Move to the next line after progress bar is complete

            # Introduce a delay to avoid triggering rate limits
            time.sleep(5)

    print("All firmware files have been downloaded.")


def main():
    html_content = get_html_content()
    soup = BeautifulSoup(html_content, 'html.parser')

    base_dir = input("Enter the directory to store firmware files (or press Enter to use the current directory): ").strip()
    if not base_dir:
        base_dir = os.getcwd()

    download_firmwares(soup, base_dir)


if __name__ == "__main__":
    main()
