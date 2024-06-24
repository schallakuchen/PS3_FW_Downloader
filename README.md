
# PS3 Firmware Downloader

## Description
This script downloads PlayStation 3 firmware files from [DarkSoftware](https://darksoftware.xyz/PS3/FWlist) either as an HTML file or URL. It organizes the firmware files into directories by section and version and creates a text file with the MD5 hash for each firmware.

## Usage
1. Run the script. (Tested with Python 3.12.3)
2. Enter the path to a local HTML file when prompted, or press Enter to provide a URL.
3. Provide a destination path where the files shall be placed.
4. The script will download the firmware files and organize them accordingly.

## Dependencies
- `requests`: To handle HTTP requests.
- `beautifulsoup4`: To parse HTML content.

Install dependencies with:
```sh
pip install requests beautifulsoup4
```

## Running the Script
1. Clone the repository:
```sh
git clone https://github.com/yourusername/ps3-firmware-downloader.git
```
2. Navigate to the directory:
```sh
cd ps3-firmware-downloader
```
3. Run the script:
```sh
python firmware_downloader.py
```

## References
- [File Hoster](https://darksoftware.xyz/PS3/FWlist)
- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Documentation](https://docs.python-requests.org/en/master/)
