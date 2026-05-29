# ============================================================
# visualizer.py — Simple, clean, 3 charts only
# ============================================================

import os
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from colorama import Fore, Style, init

init(autoreset=True)

# Set clean dark style once
plt.rcParams.update({
    'figure.facecolor': '#1e1e2e',
    'axes.facecolor':   '#2a2a3e',
    'axes.labelcolor':  '#cdd6f4',
    'xtick.color':      '#cdd6f4',
    'ytick.color':      '#cdd6f4',
    'text.color':       '#cdd6f4',
    'grid.color':       '#3d3d5c',
    'grid.alpha':        0.5,
})


def save_chart(fig, output_path, filename):
    """Saves a chart and closes it to free memory."""
    os.makedirs(output_path, exist_ok=True)
    filepath = os.path.join(output_path, filename)
    plt.savefig(filepath, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print(Fore.GREEN + f"   ✓ Saved: {filename}")
    return filepath


def plot_skill_frequency(freq_df, output_path):
    """Top 15 skills horizontal bar chart."""
    print(Fore.CYAN + "\n📊 Generating skill frequency chart...")

    fig, ax = plt.subplots(figsize=(12, 8))

    df_sorted = freq_df.head(15).sort_values('count', ascending=True)

    # Color gradient from light to dark blue
    colors = [plt.cm.Blues(0.4 + 0.6 * i / len(df_sorted))
              for i in range(len(df_sorted))]

    ax.barh(df_sorted['skill'], df_sorted['count'],
            color=colors, edgecolor='none', height=0.7)

    # Add count labels on bars
    for i, (count, pct) in enumerate(
            zip(df_sorted['count'], df_sorted['percentage'])):
        ax.text(count + 20, i, f"{count:,} ({pct}%)",
                va='center', fontsize=9, color='#cdd6f4')

    ax.set_xlabel('Number of Job Postings')
    ax.set_title('🏆 Top 15 Most In-Demand Tech Skills (2024)',
                 fontsize=15, fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return save_chart(fig, output_path, 'skill_frequency.png')


def plot_salary_by_skill(salary_df, output_path):
    """Average salary per skill horizontal bar chart."""
    print(Fore.CYAN + "\n💰 Generating salary chart...")

    if len(salary_df) == 0:
        print(Fore.YELLOW + "   ⚠ No salary data available")
        return None

    fig, ax = plt.subplots(figsize=(12, 8))

    df_sorted = salary_df.head(15).sort_values(
        'avg_salary', ascending=True)

    colors = [plt.cm.Greens(0.4 + 0.6 * i / len(df_sorted))
              for i in range(len(df_sorted))]

    ax.barh(df_sorted['skill'], df_sorted['avg_salary'],
            color=colors, edgecolor='none', height=0.7)

    # Dollar labels on bars
    for i, (sal, count) in enumerate(
            zip(df_sorted['avg_salary'], df_sorted['job_count'])):
        ax.text(sal + 500, i, f"${sal:,.0f}  ({count} jobs)",
                va='center', fontsize=9, color='#cdd6f4')

    # Format x axis as dollars
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda x, _: f'${x:,.0f}'))

    ax.set_xlabel('Average Yearly Salary (USD)')
    ax.set_title('💰 Average Salary by Tech Skill (2024)',
                 fontsize=15, fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.annotate('Based on jobs with disclosed salaries only',
                xy=(0.98, 0.02), xycoords='axes fraction',
                ha='right', fontsize=9,
                color='#6c7086', style='italic')

    plt.tight_layout()
    return save_chart(fig, output_path, 'salary_by_skill.png')


def plot_wordcloud(freq_df, output_path):
    """Word cloud — bigger word = higher demand."""
    print(Fore.CYAN + "\n☁️  Generating word cloud...")

    skill_weights = dict(zip(freq_df['skill'], freq_df['count']))

    wc = WordCloud(
        width=1400, height=700,
        background_color='#1e1e2e',
        colormap='Blues',
        max_words=40,
        min_font_size=14,
        max_font_size=120,
        collocations=False
    ).generate_from_frequencies(skill_weights)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('☁️  Tech Skills Word Cloud — Bigger = More In Demand',
                 fontsize=15, fontweight='bold', pad=15)

    plt.tight_layout()
    return save_chart(fig, output_path, 'wordcloud.png')


def generate_all_charts(df, results, output_path='output/charts'):
    """Main function — generates all 3 charts."""

    print(Fore.YELLOW + Style.BRIGHT + "\n" + "="*50)
    print(Fore.YELLOW + Style.BRIGHT + "   GENERATING CHARTS")
    print(Fore.YELLOW + Style.BRIGHT + "="*50)

    plot_skill_frequency(results['frequency'], output_path)
    plot_salary_by_skill(results['salary'],    output_path)
    plot_wordcloud(results['frequency'],        output_path)

    print(Fore.GREEN + Style.BRIGHT +
          f"\n   ✅ All charts saved to {output_path}/\n")