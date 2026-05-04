import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create an output directory for the plots
output_dir = 'analysis_plots'
os.makedirs(output_dir, exist_ok=True)

# Set global aesthetic parameters for matplotlib/seaborn to match premium look
plt.rcParams.update({
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'axes.labelweight': 'bold',
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16,
    'figure.titleweight': 'bold'
})
sns.set_theme(style="whitegrid", palette="muted")

# Load the dataset
df = pd.read_csv('WB_Election_Master_Backup_2026.csv', encoding='unicode_escape')
print("Dataset loaded successfully. Shape:", df.shape)

# ==========================================
# Q1: Victory Margin Analysis (Landslides vs Nail-biters)
# ==========================================
print('\n' + '='*70)
print('Q1: VICTORY MARGIN ANALYSIS')
print('='*70)

# Sort candidates in each constituency by Total Votes
df_sorted = df.sort_values(by=['Constituency Name', 'Total Votes'], ascending=[True, False])
top2_candidates = df_sorted.groupby('Constituency Name').head(2)

margins_list = []
for const_name, group in top2_candidates.groupby('Constituency Name'):
    if len(group) >= 2:
        winner = group.iloc[0]
        runner_up = group.iloc[1]
        margin = winner['Total Votes'] - runner_up['Total Votes']
        
        margins_list.append({
            'Constituency No': winner.get('Constituency No', -1),
            'Constituency Name': const_name,
            'Winning Party': winner['Party'],
            'Winner Name': winner['Candidate Name'],
            'Winner Total Votes': winner['Total Votes'],
            'Winner EVM Votes': winner['EVM Votes'],
            'Winner Postal Votes': winner['Postal Votes'],
            'Runner Up Party': runner_up['Party'],
            'Runner Up Name': runner_up['Candidate Name'],
            'Runner Up Total Votes': runner_up['Total Votes'],
            'Runner Up EVM Votes': runner_up['EVM Votes'],
            'Runner Up Postal Votes': runner_up['Postal Votes'],
            'Victory Margin': margin
        })

margins_df = pd.DataFrame(margins_list)

# 1A: Distribution Violin Plot
party_win_counts = margins_df['Winning Party'].value_counts()
major_parties = party_win_counts[party_win_counts >= 1].index.tolist()
margins_df_major = margins_df[margins_df['Winning Party'].isin(major_parties)]

plt.figure(figsize=(12, 6))
sns.violinplot(data=margins_df_major, x='Winning Party', y='Victory Margin', hue='Winning Party', palette='viridis', inner='quartile', legend=False)
sns.stripplot(data=margins_df_major, x='Winning Party', y='Victory Margin', color='black', alpha=0.4, jitter=True, size=4)
plt.title('Distribution of Victory Margins by Major Winning Parties')
plt.xlabel('Winning Party')
plt.ylabel('Victory Margin (Votes)')
plt.xticks(rotation=15, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'q1a_margin_distribution.png'), dpi=300)
plt.close()

# 1B: Top 10 Landslides
top_10_landslides = margins_df.nlargest(10, 'Victory Margin')
plt.figure(figsize=(12, 6))
bars = plt.barh(top_10_landslides['Constituency Name'][::-1], top_10_landslides['Victory Margin'][::-1], color='#2ecc71', edgecolor='black')
plt.title('Top 10 Landslide Victories (Highest Margins)')
plt.xlabel('Victory Margin (Votes)')
plt.ylabel('Constituency')
for bar in bars:
    plt.text(bar.get_width() - (bar.get_width() * 0.1), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width()):,}', 
             va='center', ha='right', color='white', fontweight='bold')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'q1b_top10_landslides.png'), dpi=300)
plt.close()

# 1C: Top 10 Nail-biters
top_10_close = margins_df.nsmallest(10, 'Victory Margin')
plt.figure(figsize=(12, 6))
bars = plt.barh(top_10_close['Constituency Name'][::-1], top_10_close['Victory Margin'][::-1], color='#e74c3c', edgecolor='black')
plt.title('Top 10 Nail-Biter Elections (Lowest Margins)')
plt.xlabel('Victory Margin (Votes)')
plt.ylabel('Constituency')
for bar in bars:
    plt.text(bar.get_width() + max(top_10_close['Victory Margin'])*0.02, bar.get_y() + bar.get_height()/2, f'{int(bar.get_width()):,}', 
             va='center', ha='left', color='black', fontweight='bold')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'q1c_top10_nailbiters.png'), dpi=300)
plt.close()
print("Saved: q1a_margin_distribution.png, q1b_top10_landslides.png, q1c_top10_nailbiters.png")


# ==========================================
# Q2: NOTA Impact Analysis
# ==========================================
print('\n' + '='*70)
print('Q2: NOTA IMPACT ANALYSIS')
print('='*70)

nota_df = df[df['Party'].str.contains('NOTA|None of the Above', case=False, na=False)].copy()
nota_votes = nota_df[['Constituency Name', 'Total Votes']].rename(columns={'Total Votes': 'NOTA Votes'})
q2_df = pd.merge(margins_df, nota_votes, on='Constituency Name', how='left')
q2_df['NOTA Votes'] = q2_df['NOTA Votes'].fillna(0)
nota_exceeds_margin = q2_df[q2_df['NOTA Votes'] > q2_df['Victory Margin']].copy()

print(f"Constituencies where NOTA > Victory Margin: {len(nota_exceeds_margin)}")

# 2A: Dual Bar Chart for Flipped Seats
if len(nota_exceeds_margin) > 0:
    nota_exceeds_margin = nota_exceeds_margin.sort_values('Victory Margin')
    labels = nota_exceeds_margin['Constituency Name']
    margins = nota_exceeds_margin['Victory Margin']
    notas = nota_exceeds_margin['NOTA Votes']
    
    x = np.arange(len(labels))
    width = 0.35
    
    plt.figure(figsize=(10, 6))
    plt.bar(x - width/2, margins, width, label='Victory Margin', color='#3498db', edgecolor='black')
    plt.bar(x + width/2, notas, width, label='NOTA Votes', color='#e67e22', edgecolor='black')
    
    plt.ylabel('Vote Count')
    plt.title('Constituencies Where NOTA Votes Exceeded the Victory Margin')
    plt.xticks(x, labels, rotation=15)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    for i in range(len(labels)):
        plt.text(x[i] - width/2, margins.iloc[i] + 50, str(int(margins.iloc[i])), ha='center', fontweight='bold', fontsize=9)
        plt.text(x[i] + width/2, notas.iloc[i] + 50, str(int(notas.iloc[i])), ha='center', fontweight='bold', fontsize=9)
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'q2a_nota_flipped_seats.png'), dpi=300)
    plt.close()

# 2B: Scatter Plot of NOTA vs Margin with Shaded Danger Zone
# plt.figure(figsize=(10, 8))
# plt.scatter(q2_df['Victory Margin'], q2_df['NOTA Votes'], alpha=0.7, color='teal', edgecolor='black', s=50)

# # Shade the area where NOTA > Margin
# max_val = max(q2_df['Victory Margin'].max(), q2_df['NOTA Votes'].max())
# plt.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='NOTA = Victory Margin')
# plt.fill_between([0, max_val], [0, max_val], [max_val, max_val], color='red', alpha=0.1, label='Danger Zone (NOTA > Margin)')

# plt.xlim(0, q2_df['Victory Margin'].quantile(0.95)) # Cap at 95th percentile to zoom in on the important area
# plt.ylim(0, q2_df['NOTA Votes'].max() + 500)
# plt.title('Victory Margin vs NOTA Votes (Zoomed to 95th Percentile)')
# plt.xlabel('Victory Margin')
# plt.ylabel('NOTA Votes')
# plt.legend(loc='upper right')
# plt.grid(alpha=0.3)
# plt.tight_layout()
# plt.savefig(os.path.join(output_dir, 'q2b_nota_scatter.png'), dpi=300)
# plt.close()
# print("Saved: q2a_nota_flipped_seats.png, q2b_nota_scatter.png")


# ==========================================
# Q3: EVM vs Postal Votes Disparity
# ==========================================
print('\n' + '='*70)
print('Q3: EVM vs POSTAL VOTES DISPARITY')
print('='*70)

q3_df = margins_df.copy()
q3_df['Winner Postal %'] = (q3_df['Winner Postal Votes'] / q3_df['Winner Total Votes'] * 100).fillna(0)
q3_df['Runner Up Postal %'] = (q3_df['Runner Up Postal Votes'] / q3_df['Runner Up Total Votes'] * 100).fillna(0)
q3_df['Postal % Disparity'] = q3_df['Winner Postal %'] - q3_df['Runner Up Postal %']

# 3A: Disparity Distribution Histogram
plt.figure(figsize=(10, 6))
sns.histplot(q3_df['Postal % Disparity'], bins=40, kde=True, color='purple', edgecolor='black')
plt.axvline(0, color='red', linestyle='dashed', linewidth=2, label='No Disparity (0%)')
plt.title('Distribution of Postal Vote % Disparity (Winner - Runner Up)')
plt.xlabel('Disparity in Postal Vote Share (%)')
plt.ylabel('Number of Constituencies')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'q3a_postal_disparity_hist.png'), dpi=300)
plt.close()

# 3B: Top 10 Constituencies by Total Postal Votes
df['Postal Votes'] = pd.to_numeric(df['Postal Votes'], errors='coerce').fillna(0)
total_postal_per_const = df.groupby('Constituency Name')['Postal Votes'].sum().reset_index()
top10_postal = total_postal_per_const.nlargest(10, 'Postal Votes')

plt.figure(figsize=(12, 6))
bars = plt.barh(top10_postal['Constituency Name'][::-1], top10_postal['Postal Votes'][::-1], color='#9b59b6', edgecolor='black')
plt.title('Top 10 Constituencies with the Highest Total Postal Votes')
plt.xlabel('Total Postal Votes')
plt.ylabel('Constituency Name')
for bar in bars:
    plt.text(bar.get_width() - (bar.get_width() * 0.05), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width()):,}', 
             va='center', ha='right', color='white', fontweight='bold')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'q3b_highest_postal_regions.png'), dpi=300)
plt.close()
print("Saved: q3a_postal_disparity_hist.png, q3b_highest_postal_regions.png")


# ==========================================
# Q4: Competitiveness by Party Combinations
# ==========================================
print('\n' + '='*70)
print('Q4: COMPETITIVENESS BY PARTY COMBOS (<5% MARGIN)')
print('='*70)

total_votes_per_const = df.groupby('Constituency Name')['Total Votes'].sum().reset_index()
total_votes_per_const.rename(columns={'Total Votes': 'Constituency Total Votes'}, inplace=True)

q4_df = pd.merge(margins_df, total_votes_per_const, on='Constituency Name', how='left')
q4_df['Margin %'] = (q4_df['Victory Margin'] / q4_df['Constituency Total Votes']) * 100
q4_df['Is Competitive'] = q4_df['Margin %'] < 5.0

matchups = q4_df.groupby(['Winning Party', 'Runner Up Party']).agg(
    Total_Matchups=('Constituency Name', 'count'),
    Competitive_Matchups=('Is Competitive', 'sum')
).reset_index()

# Filter for relevant matchups
matchups_filtered = matchups[matchups['Total_Matchups'] >= 3].copy()
matchups_filtered['Competitive %'] = (matchups_filtered['Competitive_Matchups'] / matchups_filtered['Total_Matchups']) * 100
matchups_filtered['Combo_Name'] = matchups_filtered['Winning Party'] + ' vs ' + matchups_filtered['Runner Up Party']
matchups_sorted = matchups_filtered.sort_values(by='Competitive %', ascending=False)

# 4A: Heatmap
heatmap_data = matchups_filtered.pivot(index='Winning Party', columns='Runner Up Party', values='Competitive %')
plt.figure(figsize=(10, 8))
sns.heatmap(heatmap_data, annot=True, cmap='RdYlGn_r', fmt='.1f', linewidths=1, linecolor='black',
            cbar_kws={'label': '% of Races that were Competitive (< 5% Margin)'}, annot_kws={"size": 12, "weight": "bold"})
plt.title('Competitiveness Heatmap: Winning Party vs Runner-Up', pad=20)
plt.xticks(rotation=15, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'q4a_competitiveness_heatmap.png'), dpi=300)
plt.close()

# 4B: Horizontal Bar Chart of Competitiveness
plt.figure(figsize=(12, 6))
colors = plt.cm.RdYlGn_r(matchups_sorted['Competitive %'] / 100)
bars = plt.barh(matchups_sorted['Combo_Name'][::-1], matchups_sorted['Competitive %'][::-1], color=colors[::-1], edgecolor='black')
plt.title('Which Matchups Are the Most Fiercely Fought? (Competitive Rate %)')
plt.xlabel('Percentage of Races Decided by < 5% Margin')
plt.ylabel('Matchup (Winner vs Runner-Up)')
plt.xlim(0, 100)
for bar in bars:
    plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{bar.get_width():.1f}%', 
             va='center', fontweight='bold')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'q4b_competitiveness_ranking.png'), dpi=300)
plt.close()
print("Saved: q4a_competitiveness_heatmap.png, q4b_competitiveness_ranking.png\n")

print("All advanced visualizations generated successfully in the 'analysis_plots/' directory!")
