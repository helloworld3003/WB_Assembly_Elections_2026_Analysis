import os
import concurrent.futures
from curl_cffi import requests

OUTPUT_DIR = "eci_html_files"
BASE_URL = "https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseS25{}.htm"

def download_constituency(const_no):
    """Worker function to fetch a single URL using Chrome network spoofing."""
    file_path = os.path.join(OUTPUT_DIR, f"constituency_{const_no}.html")
    url = BASE_URL.format(const_no)
    
    try:
        # We WANT to overwrite existing local files here to get the freshest data.
        # The impersonate flag perfectly fakes a Chrome network signature.
        response = requests.get(url, impersonate="chrome110", timeout=15)
        
        if response.status_code == 200:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return f"Success (Updated): Constituency {const_no}"
        else:
            return f"Failed {const_no}: Status {response.status_code}"
            
    except Exception as e:
        return f"Error {const_no}: {e}"

def fast_stealth_download():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    constituencies_to_fetch = list(range(1, 295))
    
    # Read the completion file to skip 100% finished constituencies
    if os.path.exists("completed_constituencies.txt"):
        try:
            with open("completed_constituencies.txt", "r") as f:
                completed = [int(x) for x in f.read().split(",") if x.strip()]
            # Filter out the completed ones from our master list
            constituencies_to_fetch = [c for c in constituencies_to_fetch if c not in completed]
            print(f"Skipping {len(completed)} fully counted constituencies based on text file.")
        except Exception as e:
            print(f"Could not read completed list: {e}")

    print(f"Fetching {len(constituencies_to_fetch)} live files using fast concurrent TLS spoofing...")

    # Multithreading: Download 5 pages at the exact same time
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(download_constituency, constituencies_to_fetch)
        
        # Print results as they finish
        for result in results:
            print(result)

    print("\nAll live vote downloads complete!")

if __name__ == "__main__":
    fast_stealth_download()