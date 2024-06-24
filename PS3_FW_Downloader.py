"""
Firmware Downloader Script

Author: Andreas

Date: 24.06.2024

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
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import logging

ASCII_ART_TITLE = r"""

  ____  ____ _____     _____ _                                           ____                      _                 _           
 |  _ \/ ___|___ /    |  ___(_)_ __ _ __ _____      ____ _ _ __ ___     |  _ \  _____      ___ __ | | ___   __ _  __| | ___ _ __ 
 | |_) \___ \ |_ \    | |_  | | '__| '_ ` _ \ \ /\ / / _` | '__/ _ \    | | | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
 |  __/ ___) |__) |   |  _| | | |  | | | | | \ V  V / (_| | | |  __/    | |_| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   
 |_|   |____/____/    |_|   |_|_|  |_| |_| |_|\_/\_/ \__,_|_|  \___|    |____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   

"""


def get_html_content():
    html_file = input("Enter the path to the local HTML file (or press Enter to provide a URL): ").strip()
    if html_file:
        with open(html_file, 'r', encoding='utf-8') as file:
            return file.read(), html_file
    else:
        url = input("Enter the URL of the HTML file: ").strip()
        response = requests.get(url)
        return response.text, url


def download_with_retries(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an error for bad status codes
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error("Max retries reached. Skipping this file.")
                return None


def download_firmwares(soup, base_dir, log_file):
    # Base URL for downloads
    base_url = "https://psarchive.darksoftware.xyz/PS3/"

    # Save current timestamp
    start_of_downloading = datetime.now()

    # Create directories and download files
    sections = ['Retail Firmwares', 'Testkit Firmwares', 'PS3 GEX FW', 'DECR Firmware']
    log_entries = []

    total_files = 0
    success_count = 0
    failure_count = 0

    for section in sections:
        section_dir = os.path.join(base_dir, section.replace(" ", "_"))
        os.makedirs(section_dir, exist_ok=True)

        table = soup.find('span', string=section).find_next('table')
        rows = table.find_all('tr')[1:]
        #rows = table.find_all('tr')[1:2]  # Limit the number of files to download during testing

        total_files += len(rows)

        for row in rows:
            cols = row.find_all('td')
            version = cols[1].text.strip()
            size = cols[2].text.strip()
            download_url = cols[3].find('button')['data-url']
            md5_hash = cols[4].find('a')['data-copy']

            firmware_dir = os.path.join(section_dir, version)
            os.makedirs(firmware_dir, exist_ok=True)

            start_time = datetime.now()
            response = download_with_retries(download_url)
            if response:
                firmware_path = os.path.join(firmware_dir, 'PS3UPDAT.PUP')
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024
                wrote = 0
                with open(firmware_path, 'wb') as firmware_file:
                    for data in response.iter_content(block_size):
                        wrote += len(data)
                        firmware_file.write(data)
                        done = int(50 * wrote / total_size)
                        percent = (wrote / total_size) * 100
                        print(f"\r[{section} - {version}] {'█' * done}{'.' * (50-done)} {percent:.2f}% ({wrote / (1024 * 1024):.2f} MB / {total_size / (1024 * 1024):.2f} MB)", end='')

                end_time = datetime.now()
                print() # Move to the next line after progress bar is complete

                time_taken = (end_time - start_time).total_seconds()
                average_speed = wrote / time_taken / 1024 / 1024 if time_taken > 0 else 0  # in MB/s

                log_entries.append({
                    'version': version,
                    'section': section,
                    'status': 'success',
                    'url': download_url,
                    'size': size,
                    'md5': md5_hash,
                    'time_taken': time_taken,
                    'average_speed': average_speed
                })
                logging.info(f"Completed download for [{section} - {version}]: {percent:.2f}% ({wrote / (1024 * 1024):.2f} MB / {total_size / (1024 * 1024):.2f} MB) in {time_taken:.2f} seconds with average speed {average_speed:.2f} MB/s")
                success_count += 1
            else:
                end_time = datetime.now()
                log_entries.append({
                    'version': version,
                    'section': section,
                    'status': 'failed',
                    'url': download_url,
                    'size': size,
                    'md5': md5_hash,
                    'time_taken': 'N/A',
                    'average_speed': 'N/A'
                })
                logging.error(f"Failed download for [{section} - {version}]")
                failure_count += 1

            # Introduce a delay to avoid triggering rate limits
            time.sleep(10)

    # Save current timestamp
    end_of_downloading = datetime.now()

    with open(log_file, 'w') as log:
        log.write("<html><head><title>PS3 Firmware Downloader Log</title></head><body>")
        log.write("<h1>PS3 Firmware Downloader Log</h1>")
        log.write(f"<p>Start Time: {start_of_downloading.strftime('%Y-%m-%d %H:%M:%S')}</p>")
        log.write(f"<p>End Time: {end_of_downloading.strftime('%Y-%m-%d %H:%M:%S')}</p>")
        log.write(f"<p>Total Files Parsed: {total_files}</p>")
        log.write(f"<p>Successful Downloads: {success_count}</p>")
        log.write(f"<p>Failed Downloads: {failure_count}</p>")
        log.write("<table border='1'><tr><th>Section</th><th>Version</th><th>Status</th><th>Download URL</th><th>Size</th><th>MD5</th><th>Time Taken (s)</th><th>Average Speed (MB/s)</th></tr>")

        for entry in log_entries:
            color = "green" if entry['status'] == 'success' else "red"
            log.write(f"<tr style='color: {color};'><td>{entry['section']}</td><td>{entry['version']}</td><td>{entry['status']}</td><td><a href='{entry['url']}'>{entry['url']}</a></td><td>{entry['size']}</td><td>{entry['md5']}</td><td>{entry['time_taken']}</td><td>{entry['average_speed']}</td></tr>")

        log.write("</table></body></html>")

    logging.info("All firmware files have been downloaded.")


def main():
    print(ASCII_ART_TITLE)  # Print ASCII Banner
    html_content, source = get_html_content()
    soup = BeautifulSoup(html_content, 'html.parser')

    base_dir = input("Enter the directory to store firmware files (or press Enter to use the current directory): ").strip()
    if not base_dir:
        base_dir = os.getcwd()

    log_dir = os.path.join(base_dir, '.log')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'firmware_download_log.html')

    # Save HTML content of the source
    html_save_path = os.path.join(log_dir, 'source.html')
    with open(html_save_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

    # Configure logging
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    execution_log_path = os.path.join(log_dir, f'{timestamp}_execution.log')
    logging.basicConfig(filename=execution_log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler())  # Also log to console

    logging.info(ASCII_ART_TITLE)  # Log ASCII Banner

    download_firmwares(soup, base_dir, log_file)


if __name__ == "__main__":
    main()
