# ============================================================
# main.py
# PURPOSE: The entry point of the program. Loads data, runs
#          analysis, generates charts, then gives the user
#          an interactive menu to explore insights.
# ============================================================

import os
import sys
from colorama import Fore, Style, init

init(autoreset=True)

# Local module imports — our own files from src/
from src.data_loader import load_data
from src.skill_extractor import extract_skills
from src.trend_analyzer import run_analysis, get_skill_frequency
from src.visualizer import generate_all_charts

# ============================================================
# PATH SETUP
# ============================================================
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, 'data')
CHARTS_PATH = os.path.join(BASE_DIR, 'output', 'charts')


# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_banner():
    """Prints the welcome banner when program starts."""
    print(Fore.CYAN + Style.BRIGHT + """
╔══════════════════════════════════════════════════════╗
║       AI SKILL TREND & CAREER INSIGHT SYSTEM         ║
║              LinkedIn Job Market 2024                ║
╚══════════════════════════════════════════════════════╝
    """)


def print_menu():
    print(Fore.YELLOW + Style.BRIGHT + "\n" + "="*54)
    print(Fore.YELLOW + Style.BRIGHT +   "   MAIN MENU")
    print(Fore.YELLOW + Style.BRIGHT +   "="*54)
    print(Fore.WHITE  + "   1. 🏆  View Top In-Demand Skills")
    print(Fore.WHITE  + "   2. 💰  View Salary Insights by Skill")
    print(Fore.WHITE  + "   3. 🔍  Search Skills by Job Role")
    print(Fore.WHITE  + "   4. 🎯  Career Path Recommender")
    print(Fore.WHITE  + "   5. 📊  Generate & Open Charts")
    print(Fore.WHITE  + "   6. 📋  Dataset Summary")
    print(Fore.WHITE  + "   0. 🚪  Exit")
    print(Fore.YELLOW + Style.BRIGHT +   "="*54)

def divider():
    print(Fore.YELLOW + "-"*54)


# ============================================================
# MENU OPTION FUNCTIONS
# ============================================================

def show_top_skills(results, n=15):
    """
    Menu Option 1.
    Displays the top N most demanded skills as a
    formatted table with a mini bar chart in the terminal.
    """
    freq_df = results['frequency']

    print(Fore.CYAN + Style.BRIGHT +
          f"\n🏆 TOP {n} MOST IN-DEMAND TECH SKILLS (2024)")
    divider()
    print(Fore.WHITE +
          f"  {'#':<4} {'Skill':<22} {'Jobs':>6}  {'%':>6}  Chart")
    divider()

    for i, row in freq_df.head(n).iterrows():
        # Build a simple text bar proportional to percentage
        bar_len = int(row['percentage'] / 2)
        bar = '█' * bar_len

        # Color top 3 differently for emphasis
        if i == 0:
            color = Fore.YELLOW  # gold for #1
        elif i == 1:
            color = Fore.WHITE   # silver for #2
        elif i == 2:
            color = Fore.RED     # bronze for #3
        else:
            color = Fore.GREEN

        print(color +
              f"  {i+1:<4} {row['skill']:<22} "
              f"{row['count']:>6,}  "
              f"{row['percentage']:>5.1f}%  {bar}")

    divider()
    print(Fore.CYAN +
          f"  Based on 9,864 tech job postings | 2024\n")


def show_salary_insights(results):
    """
    Menu Option 2.
    Shows average salary per skill in a clean table.
    """
    salary_df = results['salary']

    if len(salary_df) == 0:
        print(Fore.YELLOW + "\n  ⚠ No salary data available.")
        return

    print(Fore.CYAN + Style.BRIGHT +
          "\n💰 AVERAGE SALARY BY TECH SKILL (2024)")
    divider()
    print(Fore.WHITE +
          f"  {'#':<4} {'Skill':<22} {'Avg Salary':>13}  {'Jobs':>6}")
    divider()

    for i, row in salary_df.iterrows():
        # Color by salary tier
        if row['avg_salary'] >= 160000:
            color = Fore.YELLOW   # top tier
        elif row['avg_salary'] >= 130000:
            color = Fore.GREEN    # mid tier
        else:
            color = Fore.WHITE    # standard

        print(color +
              f"  {i+1:<4} {row['skill']:<22} "
              f"${row['avg_salary']:>12,.0f}  "
              f"{row['job_count']:>6}")

    divider()
    print(Fore.CYAN +
          "  Note: Based on jobs with disclosed salaries only\n")


def search_by_role(df, results):
    """
    Menu Option 3.
    User types a job role (e.g. 'data scientist') and
    sees the top skills required for that role specifically.
    """
    print(Fore.CYAN + Style.BRIGHT +
          "\n🔍 SEARCH SKILLS BY JOB ROLE")
    divider()
    print(Fore.WHITE +
          "  Examples: data scientist, software engineer,")
    print(Fore.WHITE +
          "            devops, machine learning, frontend")
    divider()

    query = input(Fore.YELLOW +
                  "  Enter job role to search: ").strip().lower()

    if not query:
        print(Fore.RED + "  ⚠ No input entered.")
        return

    # Filter jobs where title contains the query
    mask = df['title'].str.lower().str.contains(query, na=False)
    df_filtered = df[mask]

    if len(df_filtered) == 0:
        print(Fore.RED +
              f"\n  ⚠ No jobs found matching '{query}'")
        print(Fore.YELLOW +
              "  Try: 'engineer', 'developer', 'analyst', 'scientist'")
        return

    print(Fore.GREEN +
          f"\n  ✓ Found {len(df_filtered):,} jobs matching '{query}'")
    divider()

    # Get skill frequency for this filtered subset only
    freq_filtered = get_skill_frequency(df_filtered, top_n=10)

    if len(freq_filtered) == 0:
        print(Fore.YELLOW +
              "  ⚠ No skills extracted for these jobs.")
        return

    print(Fore.CYAN + Style.BRIGHT +
          f"\n  TOP SKILLS FOR: '{query.upper()}'")
    divider()
    print(Fore.WHITE +
          f"  {'#':<4} {'Skill':<22} {'Jobs':>6}  {'% of role':>10}")
    divider()

    for i, row in freq_filtered.iterrows():
        bar = '█' * int(row['percentage'] / 3)
        print(Fore.GREEN +
              f"  {i+1:<4} {row['skill']:<22} "
              f"{row['count']:>6,}  "
              f"{row['percentage']:>9.1f}%  {bar}")

    divider()

    # Also show salary info for this role if available
    df_sal = df_filtered[df_filtered['salary_yearly'].notna()]
    if len(df_sal) >= 5:
        avg_sal = df_sal['salary_yearly'].mean()
        med_sal = df_sal['salary_yearly'].median()
        print(Fore.CYAN +
              f"\n  💰 Salary for '{query}' roles:")
        print(Fore.GREEN +
              f"     Average: ${avg_sal:,.0f}/year")
        print(Fore.GREEN +
              f"     Median:  ${med_sal:,.0f}/year")
        print(Fore.WHITE +
              f"     Based on {len(df_sal)} jobs with disclosed salary")
    print()


def career_recommender(results):
    """
    Menu Option 4.
    User enters skills they already have.
    System recommends what to learn next based on
    co-occurrence — skills that commonly appear
    alongside the ones they already know.
    """
    print(Fore.CYAN + Style.BRIGHT +
          "\n🎯 CAREER PATH RECOMMENDER")
    divider()
    print(Fore.WHITE +
          "  Enter skills you already know (comma separated)")
    print(Fore.WHITE +
          "  Example: Python, SQL, AWS")
    divider()

    user_input = input(Fore.YELLOW +
                       "  Your skills: ").strip()

    if not user_input:
        print(Fore.RED + "  ⚠ No skills entered.")
        return

    # Parse user skills — split by comma, strip spaces,
    # convert to lowercase for matching
    user_skills = [s.strip().lower() for s in user_input.split(',')]

    print(Fore.GREEN +
          f"\n  ✓ Skills entered: {', '.join(user_skills)}")
    divider()

    # Load the full skills data from results
    freq_df = results['frequency']
    all_known_skills = [s.lower() for s in freq_df['skill'].tolist()]

    # Find which entered skills we actually recognize
    recognized = [s for s in user_skills if s in all_known_skills]
    unrecognized = [s for s in user_skills if s not in all_known_skills]

    if unrecognized:
        print(Fore.YELLOW +
              f"  ⚠ Unrecognized skills (check spelling): "
              f"{', '.join(unrecognized)}")

    if not recognized:
        print(Fore.RED +
              "  ✗ None of your skills were recognized. "
              "Try: python, sql, aws, java, javascript")
        return

    # Determine skill tier based on what they know
    high_demand = ['python', 'sql', 'aws', 'javascript',
                   'java', 'azure', 'linux']
    ai_skills   = ['machine learning', 'deep learning', 'nlp',
                   'tensorflow', 'pytorch', 'generative ai', 'mlops']
    devops      = ['docker', 'kubernetes', 'ci/cd',
                   'terraform', 'jenkins']

    known_lower = [s.lower() for s in recognized]

    # Build personalized recommendations
    recommendations = []

    # If they know Python but not ML → suggest ML
    if 'python' in known_lower and \
       not any(s in known_lower for s in ai_skills):
        recommendations.append(
            ('Machine Learning', '📈 High Growth',
             'Python is the gateway — ML is the natural next step'))
        recommendations.append(
            ('TensorFlow', '💰 $166k avg salary',
             'Most demanded deep learning framework'))

    # If they know SQL but not cloud → suggest cloud
    if 'sql' in known_lower and \
       not any(s in known_lower for s in ['aws', 'azure', 'gcp']):
        recommendations.append(
            ('AWS', '🏆 #4 most demanded skill',
             'Cloud is essential for modern data roles'))
        recommendations.append(
            ('Snowflake', '💰 High paying cloud DB skill',
             'Cloud data warehousing is booming'))

    # If they know any cloud but not DevOps
    if any(s in known_lower for s in ['aws', 'azure', 'gcp']) and \
       not any(s in known_lower for s in devops):
        recommendations.append(
            ('Docker', '📈 Growing fast',
             'Container skills pair perfectly with cloud'))
        recommendations.append(
            ('Kubernetes', '💰 High salary premium',
             'K8s is the standard for cloud orchestration'))

    # If they know JS but not TypeScript
    if 'javascript' in known_lower and \
       'typescript' not in known_lower:
        recommendations.append(
            ('TypeScript', '📈 Rapidly growing',
             'TypeScript is replacing plain JS in most companies'))

    # If they know ML but not MLOps
    if any(s in known_lower for s in ['machine learning',
                                       'tensorflow', 'pytorch']):
        recommendations.append(
            ('MLOps', '💰 $174k avg salary',
             'Deploying ML models is the next frontier'))
        recommendations.append(
            ('Generative AI', '🔥 Hottest emerging skill',
             'LLMs and GenAI are transforming every tech role'))

    # Generic recommendations if nothing specific matched
    if not recommendations:
        recommendations = [
            ('Python',   '🏆 #2 most demanded skill',
             'Essential for almost every tech role'),
            ('SQL',      '🏆 #1 most demanded skill',
             'Data literacy is required everywhere'),
            ('AWS',      '💰 High salary + demand',
             'Cloud is the foundation of modern tech'),
            ('CI/CD',    '📈 DevOps culture is everywhere',
             'Automation skills are universally valued'),
        ]

    print(Fore.CYAN + Style.BRIGHT +
          "\n  🎯 RECOMMENDED SKILLS TO LEARN NEXT:")
    divider()

    for i, (skill, badge, reason) in enumerate(
            recommendations[:5], 1):
        print(Fore.YELLOW +
              f"  {i}. {skill}")
        print(Fore.GREEN +
              f"     {badge}")
        print(Fore.WHITE +
              f"     💡 {reason}")
        print()

    divider()


def show_dataset_summary(df, results):
    """
    Menu Option 6.
    Shows a quick summary of the dataset and analysis.
    """
    freq_df   = results['frequency']
    salary_df = results['salary']

    print(Fore.CYAN + Style.BRIGHT + "\n📋 DATASET SUMMARY")
    divider()
    print(Fore.WHITE +
          f"  Source:          LinkedIn Job Postings 2024")
    print(Fore.WHITE +
          f"  Total tech jobs: {len(df):,}")
    print(Fore.WHITE +
          f"  Date range:      March – April 2024")
    print(Fore.WHITE +
          f"  Jobs with salary:{df['salary_yearly'].notna().sum():,} "
          f"({df['salary_yearly'].notna().mean()*100:.1f}%)")
    print(Fore.WHITE +
          f"  Unique companies:{df['company_name'].nunique():,}")
    print(Fore.WHITE +
          f"  Unique locations:{df['location'].nunique():,}")
    print(Fore.WHITE +
          f"  Skills tracked:  {len(freq_df)}")
    divider()

    # Experience level breakdown
    if 'formatted_experience_level' in df.columns:
        print(Fore.CYAN + "\n  Experience Level Distribution:")
        exp_counts = df['formatted_experience_level'].value_counts()
        for level, count in exp_counts.items():
            if isinstance(level, str):
                pct = count / len(df) * 100
                bar = '█' * int(pct / 3)
                print(Fore.GREEN +
                      f"    {level:<20} {count:>5,}  "
                      f"({pct:.1f}%)  {bar}")

    divider()

    if len(salary_df) > 0:
        print(Fore.CYAN + "\n  Salary Statistics (disclosed jobs only):")
        sal_data = df['salary_yearly'].dropna()
        print(Fore.GREEN +
              f"    Average salary: ${sal_data.mean():>10,.0f}")
        print(Fore.GREEN +
              f"    Median salary:  ${sal_data.median():>10,.0f}")
        print(Fore.GREEN +
              f"    Highest salary: ${sal_data.max():>10,.0f}")
        print(Fore.GREEN +
              f"    Lowest salary:  ${sal_data.min():>10,.0f}")
    print()


def open_charts(df, results):
    """
    Menu Option 5.
    Generates charts and tries to open the output folder.
    """
    generate_all_charts(df, results, CHARTS_PATH)

    # Try to open the folder automatically
    # Different commands for Windows, Mac, Linux
    try:
        if sys.platform == 'win32':
            os.startfile(CHARTS_PATH)    # Windows
        elif sys.platform == 'darwin':
            os.system(f'open "{CHARTS_PATH}"')   # Mac
        else:
            os.system(f'xdg-open "{CHARTS_PATH}"')  # Linux
        print(Fore.GREEN + "  ✓ Charts folder opened!\n")
    except Exception:
        print(Fore.YELLOW +
              f"  Charts saved to: {CHARTS_PATH}\n")


# ============================================================
# STARTUP — runs once when program launches
# ============================================================

def startup():
    """
    Loads all data and runs analysis once at startup.
    Returns df and results so menu functions can use them.
    We do this ONCE at the start so the user doesn't wait
    every time they pick a menu option.
    """
    print_banner()

    print(Fore.CYAN +
          "  Initializing system — please wait...\n")

    # Load and process data
    df      = load_data(DATA_PATH)
    df      = extract_skills(df)
    results = run_analysis(df)

    print(Fore.GREEN + Style.BRIGHT +
          "\n  ✅ System ready! All data loaded.\n")

    return df, results


# ============================================================
# MAIN LOOP
# ============================================================

def main():
    # Run startup — load everything once
    df, results = startup()

    # Interactive menu loop
    # Keeps running until user types 0 to exit
    while True:
        print_menu()

        choice = input(Fore.YELLOW +
                       "\n  Enter your choice (0-6): ").strip()

        if choice == '1':
            show_top_skills(results)

        elif choice == '2':
            show_salary_insights(results)

        elif choice == '3':
            search_by_role(df, results)

        elif choice == '4':
            career_recommender(results)

        elif choice == '5':
            open_charts(df, results)

        elif choice == '6':
            show_dataset_summary(df, results)

        elif choice == '0':
            print(Fore.CYAN + Style.BRIGHT +
                  "\n  Thanks for using AI Skill Trend Analyzer!")
            print(Fore.CYAN +
                  "  Good luck with your project! 👋\n")
            break

        else:
            print(Fore.RED +
                  "\n  ⚠ Invalid choice. Please enter 0-6.\n")

        # Pause before showing menu again
        input(Fore.YELLOW + "  Press Enter to return to menu...")


# ============================================================
# ENTRY POINT
# This block only runs when you execute main.py directly.
# If another file imports main.py, this block is skipped.
# This is a Python best practice for all entry point files.
# ============================================================

if __name__ == '__main__':
    main()