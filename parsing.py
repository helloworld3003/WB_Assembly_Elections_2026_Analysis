import os
from bs4 import BeautifulSoup
import pandas as pd
import re

def parse_local_html_files():
    input_dir = "eci_html_files"
    all_election_data = []
    completed_constituencies = [] 

    if not os.path.exists(input_dir):
        print(f"Directory '{input_dir}' not found. Please ensure the files are downloaded.")
        return

    print("Starting local HTML parsing...")

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

            # 2. Parse Rounds Done vs Total Rounds
            round_div = soup.find('div', class_='round-status')
            rounds_done, total_rounds = 0, 0
            if round_div:
                match = re.search(r"(\d+)\s*/\s*(\d+)", round_div.text)
                if match:
                    rounds_done = int(match.group(1))
                    total_rounds = int(match.group(2))

            if rounds_done == total_rounds and total_rounds > 0:
                completed_constituencies.append(const_no)

            # 3. Locate the Results Table
            table = soup.find('table')
            if not table:
                continue

            rows = table.find_all('tr')
            candidates_in_constituency = []

            # 4. Parse Rows
            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 6 and cols[0].text.strip().isdigit():
                    candidate = cols[1].text.strip()
                    party = cols[2].text.strip()
                    
                    try:
                        total_votes = int(cols[5].text.strip().replace(',', ''))
                    except ValueError:
                        total_votes = 0
                    
                    candidates_in_constituency.append({
                        'Candidate': candidate,
                        'Party': party,
                        'Total Votes': total_votes
                    })

            # Sort by Votes (Descending)
            candidates_in_constituency.sort(key=lambda x: x['Total Votes'], reverse=True)
            top_3_candidates = candidates_in_constituency[:3]

            # --- NEW: Build a single-row dictionary for the constituency ---
            const_data = {
                'Constituency Name': const_name,
                'Total Rounds': total_rounds,
                'Rounds Done': rounds_done
            }

            # Map the top 3 candidates into their respective columns
            for idx in range(3):
                rank = idx + 1
                if idx < len(top_3_candidates):
                    cand = top_3_candidates[idx]
                    
                    if rounds_done == total_rounds and total_rounds > 0:
                        status = "Won" if idx == 0 else "Lost"
                    else:
                        status = "Leading" if idx == 0 else "Trailing"

                    const_data[f'Rank {rank} Candidate'] = cand['Candidate']
                    const_data[f'Rank {rank} Party'] = cand['Party']
                    const_data[f'Rank {rank} Votes'] = cand['Total Votes']
                    const_data[f'Rank {rank} Status'] = status
                else:
                    # Fallback just in case a constituency has fewer than 3 candidates
                    const_data[f'Rank {rank} Candidate'] = "N/A"
                    const_data[f'Rank {rank} Party'] = "N/A"
                    const_data[f'Rank {rank} Votes'] = 0
                    const_data[f'Rank {rank} Status'] = "N/A"

            all_election_data.append(const_data)
            print(f"Successfully parsed: {const_name}")

        except Exception as e:
            print(f"Error parsing Constituency {const_no}: {e}")

    # Export Completed Constituencies
    if completed_constituencies:
        with open("completed_constituencies.txt", "w") as f:
            f.write(",".join(map(str, completed_constituencies)))
        print(f"\nSaved {len(completed_constituencies)} fully counted constituencies.")

    # 6. Compile into a pandas DataFrame and Export to Excel
    if all_election_data:
        df = pd.DataFrame(all_election_data)
        
        # Add Margin formula
        df['Margin'] = [f"=F{i+2}-K{i+2}" for i in range(len(df))]
        
        # Define the exact column order
        columns_order = [
            'Constituency Name', 'Total Rounds', 'Rounds Done',
            'Rank 1 Candidate', 'Rank 1 Party', 'Rank 1 Votes', 'Rank 1 Status',
            'Margin',
            'Rank 2 Candidate', 'Rank 2 Party', 'Rank 2 Votes', 'Rank 2 Status',
            'Rank 3 Candidate', 'Rank 3 Party', 'Rank 3 Votes', 'Rank 3 Status'
        ]
        df = df[columns_order]
        
        excel_filename = "WB_Election_Results_2026.xlsx"
        
        # --- NEW: Advanced Wide-Format Excel Formatting ---
        with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Election Results')
            
            workbook = writer.book
            worksheet = writer.sheets['Election Results']
            
            # Freeze the top header row AND the first column (Constituency Name)
            worksheet.freeze_panes(1, 1)
            
            # Header formats with different colors to group ranks visually
            header_base = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
            header_rank1 = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#D9EAD3'}) # Light Green
            header_margin = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#EAD1DC'}) # Light Pink
            header_rank2 = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#FFF2CC'}) # Light Yellow
            header_rank3 = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#FCE5CD'}) # Light Orange

            # Apply headers
            for col_num, value in enumerate(df.columns.values):
                if 'Rank 1' in value:
                    worksheet.write(0, col_num, value, header_rank1)
                elif 'Margin' in value:
                    worksheet.write(0, col_num, value, header_margin)
                elif 'Rank 2' in value:
                    worksheet.write(0, col_num, value, header_rank2)
                elif 'Rank 3' in value:
                    worksheet.write(0, col_num, value, header_rank3)
                else:
                    worksheet.write(0, col_num, value, header_base)
            
            # Set Column Widths
            worksheet.set_column('A:A', 35) # Constituency Name
            worksheet.set_column('B:C', 13) # Rounds
            
            worksheet.set_column('D:D', 22) # Rank 1 Cand
            worksheet.set_column('E:E', 30) # Rank 1 Party
            worksheet.set_column('F:F', 14) # Rank 1 Votes
            worksheet.set_column('G:G', 12) # Rank 1 Status
            
            worksheet.set_column('H:H', 14) # Margin
            
            worksheet.set_column('I:I', 22) # Rank 2 Cand
            worksheet.set_column('J:J', 30) # Rank 2 Party
            worksheet.set_column('K:K', 14) # Rank 2 Votes
            worksheet.set_column('L:L', 12) # Rank 2 Status
            
            worksheet.set_column('M:M', 22) # Rank 3 Cand
            worksheet.set_column('N:N', 30) # Rank 3 Party
            worksheet.set_column('O:O', 14) # Rank 3 Votes
            worksheet.set_column('P:P', 12) # Rank 3 Status
            
            # Conditional Formatting for Status
            green_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
            yellow_format = workbook.add_format({'bg_color': '#FFFF00', 'font_color': '#000000'})
            orange_format = workbook.add_format({'bg_color': '#F79646', 'font_color': '#000000'})
            green2_format = workbook.add_format({'bg_color': '#00B050', 'font_color': '#000000'})
            red_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
            
            row_count = len(df) + 1
            
            # Margin Data Bar
            worksheet.conditional_format(f'H2:H{row_count}', {'type': 'data_bar', 'bar_color': '#63C384'})
            
            status_columns = ['G', 'L', 'P']
            for col in status_columns:
                range_str = f'{col}2:{col}{row_count}'
                worksheet.conditional_format(range_str, {'type': 'text', 'criteria': 'containing', 'value': 'Won', 'format': green_format})
                worksheet.conditional_format(range_str, {'type': 'text', 'criteria': 'containing', 'value': 'Leading', 'format': yellow_format})
                worksheet.conditional_format(range_str, {'type': 'text', 'criteria': 'containing', 'value': 'Lost', 'format': red_format})
                worksheet.conditional_format(range_str, {'type': 'text', 'criteria': 'containing', 'value': 'Trailing', 'format': red_format})
                
            party_columns = ['E']
            for col in party_columns:
                range_str = f'{col}2:{col}{row_count}'
                worksheet.conditional_format(range_str, {'type': 'text', 'criteria': 'containing', 'value': 'Bharatiya Janata Party', 'format': orange_format})
                worksheet.conditional_format(range_str, {'type': 'text', 'criteria': 'containing', 'value': 'All India Trinamool Congress', 'format': green2_format})

            # --- NEW: Dashboard Summary Sheet ---
            summary_sheet = workbook.add_worksheet('Summary Dashboard')
            
            title_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'bg_color': '#4A86E8', 'font_color': 'white', 'border': 1})
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D9EAD3', 'border': 1, 'align': 'center'})
            cell_format = workbook.add_format({'border': 1, 'align': 'center'})
            party_format = workbook.add_format({'border': 1, 'align': 'left', 'bold': True})
            total_format = workbook.add_format({'border': 1, 'align': 'center', 'bold': True, 'bg_color': '#F3F3F3'})
            
            summary_sheet.merge_range('A1:D1', 'West Bengal Election 2026 - Party Summary', title_format)
            
            summary_sheet.write('A3', 'Party', header_format)
            summary_sheet.write('B3', 'Leading', header_format)
            summary_sheet.write('C3', 'Won', header_format)
            summary_sheet.write('D3', 'Total Seats', header_format)
            
            unique_parties = df['Rank 1 Party'].unique()
            unique_parties = [p for p in unique_parties if p != "N/A" and str(p) != 'nan']
            
            for i, party in enumerate(unique_parties):
                row = i + 3
                summary_sheet.write_string(row, 0, party, party_format)
                # Formula for Leading
                summary_sheet.write_formula(row, 1, f'=COUNTIFS(\'Election Results\'!E:E, "{party}", \'Election Results\'!G:G, "Leading")', cell_format)
                # Formula for Won
                summary_sheet.write_formula(row, 2, f'=COUNTIFS(\'Election Results\'!E:E, "{party}", \'Election Results\'!G:G, "Won")', cell_format)
                # Formula for Total
                summary_sheet.write_formula(row, 3, f'=B{row+1}+C{row+1}', total_format)
                
            summary_sheet.set_column('A:A', 40)
            summary_sheet.set_column('B:D', 15)

        print(f"\nExtraction complete! Wide-format data successfully saved to '{excel_filename}'")
    else:
        print("\nNo data extracted.")

if __name__ == "__main__":
    parse_local_html_files()
