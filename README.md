# West Bengal Assembly Elections 2026 Data Scraper

An automated Python pipeline designed to scrape, parse, and compile the 2026 West Bengal Assembly Election results directly from the Election Commission of India (ECI) website. 

The tool circumvents standard bot-blocking mechanisms using TLS impersonation and builds comprehensive, beautifully formatted Excel dashboards and raw CSV backups of the data.

## Features

- **Fast & Stealthy Downloads**: Uses `curl_cffi` to mimic real browser TLS signatures, completely bypassing 403 Forbidden errors when scraping ECI pages.
- **Concurrent Processing**: Multi-threaded execution fetches multiple constituencies at once for maximum speed.
- **Advanced Excel Reports**: Parses HTML using `BeautifulSoup4` to generate a wide-format `.xlsx` file detailing the top 3 candidates per constituency, complete with margins and conditional formatting.
- **Dashboard Generation**: Automatically builds an Excel summary dashboard sheet tracking "Leading/Won" seats per party.
- **Master Backup**: Generates a raw `.csv` backup comprising every single candidate's individual EVM and Postal vote counts across all 294 constituencies.
- **Resume Capability**: Tracks fully counted constituencies in a text file to skip re-downloading them on subsequent runs.

## Project Structure

- `runner.py`: The main orchestrator script. Run this to execute the entire pipeline from start to finish.
- `download.py`: Handles the stealth concurrent downloading of HTML pages into the `eci_html_files/` directory.
- `parsing.py`: Parses the raw HTML to extract the Top 3 candidates and builds the formatted `WB_Election_Results_2026.xlsx`.
- `csv_maker.py`: Parses the raw HTML to dump every single candidate across all regions into `WB_Election_Master_Backup_2026.csv`.

## Prerequisites

You need Python 3 installed along with the following packages:

```bash
pip install pandas beautifulsoup4 curl_cffi xlsxwriter
```

## Usage

Simply run the master pipeline script:

```bash
python runner.py
```

This will automatically:
1. Download any missing or updated constituency HTML files.
2. Parse the results and update the `.xlsx` dashboard.
3. Update the master `.csv` backup.

## Outputs

- `WB_Election_Results_2026.xlsx`: Formatted top-3 candidate tracking and party dashboard.
- `WB_Election_Master_Backup_2026.csv`: Complete unformatted data containing all candidates and their specific vote breakdowns.
- `eci_html_files/`: Directory containing the locally cached raw HTML source files for all 294 constituencies.
- `completed_constituencies.txt`: Internal tracker to cache constituencies where 100% of the counting rounds are complete.
