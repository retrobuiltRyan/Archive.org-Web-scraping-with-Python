import requests
import urllib.parse
from bs4 import BeautifulSoup
import csv
import os
import shutil
import time


def parse_size(size_str):
    """Convert size strings like '1.5G', '300M', '100K' to bytes."""
    size_str = size_str.strip().upper()
    try:
        if size_str.endswith('G'):
            return float(size_str[:-1]) * 1024 ** 3
        elif size_str.endswith('M'):
            return float(size_str[:-1]) * 1024 ** 2
        elif size_str.endswith('K'):
            return float(size_str[:-1]) * 1024
        return float(size_str)
    except ValueError:
        return 0


def scrape_archive(url):
    """Scrapes Archive.org for file names and URLs."""
    print(f"Scraping URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to retrieve the URL. Details: {e}")
        return [], [], 0

    soup = BeautifulSoup(response.content, 'html.parser')

    game_url_list = []
    game_name_list = []
    total_size = 0

    rows = soup.find_all('tr')
    for row in rows:
        link = row.find('a')
        size_cell = row.find_all('td')[-1] if row.find_all('td') else None
        if link and size_cell:
            try:
                game_url = urllib.parse.urljoin(url, link['href'])
                game_name = urllib.parse.unquote(link['href'].split('/')[-1])
                size = parse_size(size_cell.text)
                game_url_list.append(game_url)
                game_name_list.append(game_name)
                total_size += size
            except Exception as e:
                print(f"Warning: Skipping a file due to error: {e}")

    return game_url_list, game_name_list, total_size


def get_folder_size(folder_path):
    """Returns the total size of all files in the folder."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            total_size += os.path.getsize(file_path)
    return total_size


def download_file(url, name, download_dir):
    """Downloads the file from the URL to the specified folder with download speed display."""
    file_path = os.path.join(download_dir, name)

    if os.path.exists(file_path):
        print(f"File already exists: {file_path}. Skipping...")
        return

    total, used, free = shutil.disk_usage(download_dir)
    free_gb = free // (1024 ** 3)
    print(f"Available disk space: {free_gb} GB")

    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code != 200:
            print(f"Error: Failed to download {url} (Status {response.status_code})")
            return

        total_size = int(response.headers.get('Content-Length', 0))
        start_time = time.time()
        downloaded = 0
        bar_width = 30

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=100 * 1024):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    elapsed_time = time.time() - start_time
                    progress = (downloaded / total_size) * 100
                    num_equals = int((downloaded / total_size) * bar_width)
                    bar = "=" * num_equals + " " * (bar_width - num_equals)

                    # Calculate download speed (MB/s)
                    download_speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                    download_speed_mb = download_speed / (1024 * 1024)  # Convert to MB/s

                    # Print progress bar with download speed
                    print(f"\rDownloading {name}: [{bar}] {progress:.2f}% "
                          f"({downloaded // (1024 * 1024)} MB) Speed: {download_speed_mb:.2f} MB/s", end="")

        print(f"\nDownload complete: {name}")
        print(f"Downloaded {downloaded // (1024 * 1024)} MB in {elapsed_time // 60:.0f}m {elapsed_time % 60:.0f}s")

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def main():
    print("Welcome to the Archive.org Scraper and Downloader!")
    print("=====================================================")

    # Prompt the user for the archive.org URL to scrape
    url = input("Enter a valid archive.org URL (e.g., https://archive.org/download/Sega-32x-Romset-us/): ").strip()

    # Scrape the archive page
    game_url_list, game_name_list, total_size = scrape_archive(url)

    if game_url_list:
        print(f"\nNumber of files found: {len(game_url_list)}")
        print(f"Estimated total size: {total_size / (1024 ** 3):.2f} GB")

        # Save the list to a CSV file
        with open('file_list.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['File Name', 'File URL'])
            for name, url in zip(game_name_list, game_url_list):
                writer.writerow([name, url])

        print("File list saved to 'file_list.csv'.")
    else:
        print("No files found or error occurred.")

    print("\nYou can now edit 'file_list.csv' if needed.")
    input("Press Enter to continue...")

    # Prompt the user for the download folder
    folder_name = input("Enter the folder name to save the downloads: ").strip()
    download_dir = os.path.join(os.getcwd(), folder_name)

    # Create folder if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        print(f"Created folder: {download_dir}")

    # Read the CSV file and download the files
    with open('file_list.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'File Name' in row and 'File URL' in row:
                name = urllib.parse.unquote(row['File Name'].strip())
                url = row['File URL'].strip()
                download_file(url, name, download_dir)

    print("Process completed!")

    # Prompt the user to press Enter to quit
    input("Press Enter to quit...")


if __name__ == "__main__":
    main()
