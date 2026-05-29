# ============================================================
# trend_analyzer.py
# PURPOSE: Takes the DataFrame with extracted skills and
#          produces four types of analysis:
#          1. Overall skill frequency (most demanded skills)
#          2. Month-by-month skill trends
#          3. Skill growth rates
#          4. Average salary per skill
# ============================================================

import pandas as pd
from collections import Counter
from colorama import Fore, Style, init

init(autoreset=True)


def get_skill_frequency(df, top_n=20):
    """
    Counts how many job postings mention each skill.
    Returns a DataFrame sorted by frequency descending.

    Example output:
        skill       count   percentage
        Python      2917    29.6%
        SQL         2971    30.1%
        AWS         2026    20.5%
    """

    # df['skills'] is a column where each cell is a LIST.
    # For example:
    #   row 0: ['Python', 'SQL', 'AWS']
    #   row 1: ['JavaScript', 'React']
    #   row 2: ['Python', 'Docker']
    #
    # .explode() "unpacks" those lists so each skill gets
    # its own row:
    #   row 0: 'Python'
    #   row 1: 'SQL'
    #   row 2: 'AWS'
    #   row 3: 'JavaScript'
    #   row 4: 'React'
    #   row 5: 'Python'    ← Python appears again
    #   row 6: 'Docker'
    #
    # This lets us count how many times each skill appears
    # across all job postings.

    skills_exploded = df['skills'].explode()

    # Remove empty values (from jobs where no skills were found)
    skills_exploded = skills_exploded.dropna()
    skills_exploded = skills_exploded[skills_exploded != '']

    # value_counts() counts occurrences of each unique value
    # Returns a Series: index=skill name, value=count
    skill_counts = skills_exploded.value_counts()

    # Convert to DataFrame for easier manipulation
    freq_df = pd.DataFrame({
        'skill': skill_counts.index,
        'count': skill_counts.values
    })

    # Calculate percentage — what % of jobs mention this skill
    # len(df) = total number of jobs
    freq_df['percentage'] = (freq_df['count'] / len(df) * 100).round(1)

    # Keep only top N skills
    freq_df = freq_df.head(top_n).reset_index(drop=True)

    return freq_df


def get_monthly_trends(df, top_skills=10):
    """
    Calculates how skill demand changes month by month.
    Returns a pivot table where:
        rows    = months (1, 2, 3... 12)
        columns = skill names
        values  = count of jobs mentioning that skill that month

    Example:
              Python  SQL   AWS   JavaScript
    month
    1           245   267   189      201
    2           289   301   210      234
    3           312   298   245      267
    """

    # First get the top skills so we only track meaningful ones
    freq_df = get_skill_frequency(df, top_n=top_skills)
    top_skill_names = freq_df['skill'].tolist()
    # .tolist() converts a pandas Series to a plain Python list

    # We need to "explode" the skills column but also keep
    # the month column alongside it.
    # explode() on a DataFrame column keeps all other columns.
    df_exploded = df[['month', 'skills']].explode('skills')

    # Keep only rows where the skill is in our top skills list
    df_exploded = df_exploded[
        df_exploded['skills'].isin(top_skill_names)
    ]
    # .isin() returns True for rows where the value is in
    # the provided list — another core pandas operation

    # Remove any NaN skills
    df_exploded = df_exploded.dropna(subset=['skills'])

    # Now group by month AND skill, count occurrences
    # groupby(['month', 'skills']) groups rows that share
    # the same month AND skill together
    # .size() counts how many rows are in each group
    monthly_counts = df_exploded.groupby(
        ['month', 'skills']
    ).size().reset_index(name='count')

    # pivot_table() reshapes the data from "long" to "wide"
    # format. Think of it like an Excel pivot table.
    # Before pivot (long format):
    #   month  skill    count
    #   1      Python   245
    #   1      SQL      267
    #   2      Python   289
    #
    # After pivot (wide format):
    #   month  Python  SQL
    #   1      245     267
    #   2      289     ...
    #
    # index='month'   → months become rows
    # columns='skills'→ skills become columns
    # values='count'  → fill cells with count
    # fill_value=0    → missing combos get 0 not NaN
    trend_pivot = monthly_counts.pivot_table(
        index='month',
        columns='skills',
        values='count',
        fill_value=0
    )

    return trend_pivot


def get_growth_rates(df, top_skills=15):
    """
    Calculates growth rate for each skill across months.
    Compares first half of the year vs second half.

    Growth rate formula:
        growth = (later_count - earlier_count) / earlier_count × 100

    Returns a DataFrame sorted by growth rate descending.
    """

    trend_pivot = get_monthly_trends(df, top_skills)

    # Split months into two halves
    # First half = months 1-6, Second half = months 7-12
    # We use whatever months are available in our data
    all_months = sorted(trend_pivot.index.tolist())

    if len(all_months) < 2:
        # Not enough months to calculate growth
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=['skill', 'growth_rate', 'trend'])

    # Split months into first half and second half
    mid = len(all_months) // 2
    # // is integer division: 8 // 2 = 4, 7 // 2 = 3
    first_half = all_months[:mid]
    second_half = all_months[mid:]

    # Sum counts across each half
    # .loc[list_of_months] selects specific rows by index value
    first_counts = trend_pivot.loc[first_half].sum()
    second_counts = trend_pivot.loc[second_half].sum()
    # .sum() without axis argument sums down each column
    # giving total count per skill for that half

    growth_data = []
    for skill in trend_pivot.columns:
        early = first_counts[skill]
        late = second_counts[skill]

        if early == 0:
            # Avoid division by zero
            # If a skill had 0 mentions early, skip it
            continue

        # Calculate percentage growth
        growth = ((late - early) / early) * 100

        # Classify the trend direction
        if growth > 5:
            trend = '📈 Growing'
        elif growth < -5:
            trend = '📉 Declining'
        else:
            trend = '➡️  Stable'

        growth_data.append({
            'skill': skill,
            'growth_rate': round(growth, 1),
            'trend': trend
        })

    # Create DataFrame from list of dictionaries
    # Each dictionary becomes one row
    growth_df = pd.DataFrame(growth_data)

    # Sort by growth rate, highest first
    growth_df = growth_df.sort_values(
        'growth_rate', ascending=False
    ).reset_index(drop=True)

    return growth_df


def get_salary_by_skill(df, top_n=15):
    """
    Calculates average salary for jobs requiring each skill.
    Only uses jobs where salary data is available.

    Returns a DataFrame sorted by average salary descending.
    """

    # Filter to only jobs that have salary data
    # notna() returns True where value is NOT NaN
    df_with_salary = df[df['salary_yearly'].notna()].copy()

    if len(df_with_salary) == 0:
        print(Fore.YELLOW + "   ⚠ No salary data available")
        return pd.DataFrame(columns=['skill', 'avg_salary', 'job_count'])

    # Explode skills so each skill gets its own row
    # but salary travels with it
    df_exploded = df_with_salary[
        ['skills', 'salary_yearly']
    ].explode('skills')

    df_exploded = df_exploded.dropna(subset=['skills'])
    df_exploded = df_exploded[df_exploded['skills'] != '']

    # Group by skill, calculate mean salary and count
    # agg() lets you apply multiple aggregation functions
    # at once to different columns
    salary_by_skill = df_exploded.groupby('skills').agg(
        avg_salary=('salary_yearly', 'mean'),
        job_count=('salary_yearly', 'count')
    ).reset_index()
    # avg_salary=('salary_yearly', 'mean') means:
    #   create a column called 'avg_salary' by taking
    #   the 'mean' of the 'salary_yearly' column

    # Rename 'skills' column to 'skill' for consistency
    salary_by_skill = salary_by_skill.rename(
        columns={'skills': 'skill'}
    )

    # Only keep skills with at least 10 salary data points
    # Less than 10 is statistically unreliable
    salary_by_skill = salary_by_skill[
        salary_by_skill['job_count'] >= 10
    ]

    # Round salary to nearest dollar
    salary_by_skill['avg_salary'] = salary_by_skill[
        'avg_salary'
    ].round(0)

    # Sort by salary descending
    salary_by_skill = salary_by_skill.sort_values(
        'avg_salary', ascending=False
    ).head(top_n).reset_index(drop=True)

    return salary_by_skill


def run_analysis(df):
    """
    MAIN FUNCTION — runs all four analyses and returns
    results as a dictionary so visualizer.py and main.py
    can access them easily.

    Returns:
        dict with keys:
            'frequency'  → skill frequency DataFrame
            'trends'     → monthly trend pivot table
            'growth'     → growth rates DataFrame
            'salary'     → salary by skill DataFrame
    """

    print(Fore.YELLOW + Style.BRIGHT + "\n" + "="*50)
    print(Fore.YELLOW + Style.BRIGHT + "   ANALYZING SKILL TRENDS")
    print(Fore.YELLOW + Style.BRIGHT + "="*50)

    # 1. Frequency Analysis
    print(Fore.CYAN + "\n📊 Calculating skill frequencies...")
    freq_df = get_skill_frequency(df, top_n=20)
    print(Fore.GREEN + f"   ✓ Top skill: {freq_df['skill'].iloc[0]} "
          f"({freq_df['count'].iloc[0]:,} jobs, "
          f"{freq_df['percentage'].iloc[0]}%)")

    # 2. Monthly Trends
    print(Fore.CYAN + "\n📅 Calculating monthly trends...")
    trend_pivot = get_monthly_trends(df, top_skills=10)
    print(Fore.GREEN + f"   ✓ Tracking {len(trend_pivot.columns)} "
          f"skills across {len(trend_pivot)} months")

    # 3. Growth Rates
    print(Fore.CYAN + "\n📈 Calculating growth rates...")
    growth_df = get_growth_rates(df, top_skills=15)
    if len(growth_df) > 0:
        top_grower = growth_df.iloc[0]
        print(Fore.GREEN + f"   ✓ Fastest growing: "
              f"{top_grower['skill']} "
              f"({top_grower['growth_rate']:+.1f}%)")
    else:
        print(Fore.YELLOW + "   ⚠ Not enough monthly data for growth analysis")

    # 4. Salary Analysis
    print(Fore.CYAN + "\n💰 Calculating salary insights...")
    salary_df = get_salary_by_skill(df, top_n=15)
    if len(salary_df) > 0:
        top_paying = salary_df.iloc[0]
        print(Fore.GREEN + f"   ✓ Highest paying skill: "
              f"{top_paying['skill']} "
              f"(avg ${top_paying['avg_salary']:,.0f}/year)")

    # Print full summary
    print(Fore.YELLOW + Style.BRIGHT + "\n" + "="*50)
    print(Fore.YELLOW + Style.BRIGHT + "   ANALYSIS COMPLETE")
    print(Fore.YELLOW + Style.BRIGHT + "="*50)

    print(Fore.CYAN + "\n🏆 TOP 10 MOST DEMANDED SKILLS:")
    for i, row in freq_df.head(10).iterrows():
        bar = '█' * int(row['percentage'] / 1.5)
        print(Fore.GREEN +
              f"   {i+1:2}. {row['skill']:<20} "
              f"{row['count']:>5,} jobs  "
              f"({row['percentage']}%)  {bar}")

    if len(salary_df) > 0:
        print(Fore.CYAN + "\n💰 TOP 10 HIGHEST PAYING SKILLS:")
        for i, row in salary_df.head(10).iterrows():
            print(Fore.GREEN +
                  f"   {i+1:2}. {row['skill']:<20} "
                  f"${row['avg_salary']:>9,.0f}/year  "
                  f"({row['job_count']} jobs)")

    print()

    return {
        'frequency': freq_df,
        'trends':    trend_pivot,
        'growth':    growth_df,
        'salary':    salary_df
    }