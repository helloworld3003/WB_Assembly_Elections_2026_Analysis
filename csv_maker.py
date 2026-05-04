import os
from bs4 import BeautifulSoup
import pandas as pd
import re

def create_master_csv_backup():
    input_dir = "eci_html_files"
    all_election_data = []

    if not os.path.exists(input_dir):
        print(f"Directory '{input_dir}' not found. Please ensure the HTML files are present.")
        return

    print("Starting extraction for Master CSV Backup...")

    # Iterate through all possible local HTML files
    for const_no in range(1, 295):
        file_path = os.path.join(input_dir, f"constituency_{const_no}.html")
        
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # 1. Parse Constituency Name
            h2_tag = soup.find('h2')
            if h2_tag:
                const_name = h2_tag.text.replace('Assembly Constituency', '').strip()
            else:
                const_name = f"Constituency {const_no}"

            # 2. Parse Rounds
            round_div = soup.find('div', class_='round-status')
            rounds_done, total_rounds = 0, 0
            if round_div:
                match = re.search(r"(\d+)\s*/\s*(\d+)", round_div.text)
                if match:
                    rounds_done = int(match.group(1))
                    total_rounds = int(match.group(2))

            # 3. Parse the Main Table
            table = soup.find('table')
            if not table:
                continue

            rows = table.find_all('tr')

            # 4. Extract ALL rows and ALL columns (Skip header and footer)
            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                
                # Check if it's a valid row by looking for the Serial Number in the first column
                if len(cols) >= 7 and cols[0].text.strip().isdigit():
                    
                    # Safe integer conversion helper function
                    def clean_int(text):
                        try:
                            return int(text.strip().replace(',', ''))
                        except ValueError:
                            return 0

                    # Append every single detail from the HTML table
                    all_election_data.append({
                        'Constituency No': const_no,
                        'Constituency Name': const_name,
                        'Total Rounds': total_rounds,
                        'Rounds Done': rounds_done,
                        'Candidate S.N.': int(cols[0].text.strip()),
                        'Candidate Name': cols[1].text.strip(),
                        'Party': cols[2].text.strip(),
                        'EVM Votes': clean_int(cols[3].text),
                        'Postal Votes': clean_int(cols[4].text),
                        'Total Votes': clean_int(cols[5].text),
                        '% of Votes': cols[6].text.strip()
                    })

            print(f"Scraped all data for: {const_name}")

        except Exception as e:
            print(f"Error parsing Constituency {const_no}: {e}")

    # 5. Export directly to CSV
    if all_election_data:
        df = pd.DataFrame(all_election_data)
        
        csv_filename = "WB_Election_Master_Backup_2026.csv"
        
        # We use .to_csv instead of .to_excel. index=False prevents pandas from adding row numbers
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        
        print(f"\nSUCCESS: Master CSV Backup saved as '{csv_filename}'.")
        print(f"Total rows extracted: {len(df)}")
    else:
        print("\nNo data extracted.")

if __name__ == "__main__":
    create_master_csv_backup()