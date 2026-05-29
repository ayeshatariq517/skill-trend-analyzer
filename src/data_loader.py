import pandas as pd          # pandas handles all our tabular data
import os                    # os lets us work with file paths
from colorama import Fore, Style, init  # for colored terminal output

# init() activates colorama on Windows.
init(autoreset=True)

TECH_KEYWORDS = [
    # Core tech job words 
    'software engineer', 'software developer', 'software architect',
    'frontend', 'back-end', 'backend', 'full stack', 'fullstack',
    'web developer', 'web engineer',

    # Data roles
    'data scientist', 'data analyst', 'data engineer',
    'data architect', 'database administrator', 'database developer',
    'business analyst', 'business intelligence', 'bi developer',
    'analytics engineer',

    # AI/ML roles
    'machine learning', 'deep learning', 'nlp engineer',
    'ai engineer', 'ml engineer', 'computer vision',
    'artificial intelligence',

    'devops', 'cloud engineer', 'cloud architect',
    'site reliability', 'sre engineer',
    'platform engineer', 'infrastructure engineer',
    'solutions architect', 'aws engineer', 'azure engineer',

    'cybersecurity', 'security engineer', 'security analyst',
    'information security',

    'ios developer', 'android developer', 'mobile developer',
    'mobile engineer',


    'python developer', 'python engineer',
    'java developer', 'java engineer',
    'javascript developer', 'react developer',
    'node developer', 'node.js', '.net developer',
    'c++ developer', 'golang', 'rust developer',


    'network engineer', 'systems engineer', 'it analyst',
    'it specialist', 'it manager', 'technical lead', 'tech lead',
    'blockchain developer', 'qa engineer', 'qa analyst',
    'test engineer', 'automation engineer', 'embedded engineer',
    'firmware engineer', 'hardware engineer', 'robotics engineer',
    'product manager', 'technical program manager',
    'scrum master', 'agile coach',


    'developer', 'programmer',
]

POSTINGS_COLUMNS = [
    'job_id',
    'title',
    'company_name',
    'location',
    'description',
    'listed_time',
    'formatted_experience_level'
]


SALARY_COLUMNS = [
    'job_id',
    'min_salary',
    'max_salary',
    'pay_period'
]


def load_postings(data_path):
    
    print(Fore.CYAN + "\n📂 Loading postings.csv...")
    
    filepath = os.path.join(data_path, 'postings.csv')
    
    # We use low_memory=False because our CSV has mixed data types in some columns. Without this, pandas sometimes guesses the wrong type and gives a warning.
    df = pd.read_csv(filepath, low_memory=False)
    
    print(Fore.GREEN + f"   ✓ Loaded {len(df):,} total job postings")
    # len(df) gives number of rows.
    
    # Keep only the columns we actually need.
    df = df[POSTINGS_COLUMNS]
    
    # listed_time is stored as Unix milliseconds (e.g. 1.7134E+12)
    df['date'] = pd.to_datetime(df['listed_time'], unit='ms')
    
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
   
    df = df.drop(columns=['listed_time', 'date'])
    
    df = df.dropna(subset=['description'])
    
    print(Fore.GREEN + f"   ✓ After removing empty descriptions: {len(df):,} rows")
    
    return df


def load_salaries(data_path):
    
    print(Fore.CYAN + "\n📂 Loading salaries.csv...")
    
    filepath = os.path.join(data_path, 'salaries.csv')
    df = pd.read_csv(filepath, low_memory=False)
    
    print(Fore.GREEN + f"   ✓ Loaded {len(df):,} salary records")

    df = df[SALARY_COLUMNS]

    # (axis=1 = across columns, axis=0 = across rows).
    # This gives us one salary number per row.
    df['salary_avg'] = df[['min_salary', 'max_salary']].mean(axis=1)
    
    # Now normalize to yearly based on pay_period.
    def normalize_salary(row):
        if pd.isna(row['salary_avg']):
            return pd.NA
        if row['pay_period'] == 'HOURLY':
            return row['salary_avg'] * 2080
        elif row['pay_period'] == 'MONTHLY':
            return row['salary_avg'] * 12
        else:
            return row['salary_avg']
    
    # apply() runs normalize_salary() on every row.
    # axis=1 means "apply this function row by row."
    df['salary_yearly'] = df.apply(normalize_salary, axis=1)

    df = df[['job_id', 'salary_yearly']]
    df = df.dropna(subset=['salary_yearly'])
    df = df[
        (df['salary_yearly'] >= 10000) &
        (df['salary_yearly'] <= 500000)
    ]
    
    print(Fore.GREEN + f"   ✓ Clean salary records: {len(df):,}")
    
    return df


def filter_tech_jobs(df):
    
    print(Fore.CYAN + "\n🔍 Filtering for tech jobs...")
 
    title_lower = df['title'].str.lower()
    pattern = '|'.join(TECH_KEYWORDS)
    tech_mask = title_lower.str.contains(pattern, na=False)

    df_tech = df[tech_mask].copy()
    
    print(Fore.GREEN + f"   ✓ Tech jobs found: {len(df_tech):,} "
          f"(from {len(df):,} total)")
    
    return df_tech


def join_salaries(df_postings, df_salaries):
    
    print(Fore.CYAN + "\n🔗 Joining salary data...")
 
    df_merged = pd.merge(df_postings, df_salaries,
                     on='job_id', how='left')

    df_merged['salary_yearly'] = pd.to_numeric(
        df_merged['salary_yearly'], errors='coerce'
    )
        
    has_salary = df_merged['salary_yearly'].notna().sum()
    pct = (has_salary / len(df_merged)) * 100
    
    print(Fore.GREEN + f"   ✓ Jobs with salary data: "
          f"{has_salary:,} ({pct:.1f}%)")
    
    return df_merged


def load_data(data_path='data'):
    """
    MAIN FUNCTION of this module.
    Calls all the helper functions above in order
    and returns the final clean master DataFrame.
    
    This is the only function that main.py will call.
    Everything else is internal to this module.
    """
    
    print(Fore.YELLOW + Style.BRIGHT +
          "\n" + "="*50)
    print(Fore.YELLOW + Style.BRIGHT +
          "   LOADING AND PREPARING DATA")
    print(Fore.YELLOW + Style.BRIGHT +
          "="*50)
    
    # Step 1: Load raw postings
    df_postings = load_postings(data_path)
    
    # Step 2: Filter to tech jobs only
    df_tech = filter_tech_jobs(df_postings)
    
    # Step 3: Load salary data
    df_salaries = load_salaries(data_path)
    
    # Step 4: Join salaries onto tech jobs
    df_final = join_salaries(df_tech, df_salaries)
    
    # Step 5: Reset the index
    # After filtering rows, the index (row numbers) has gaps:
    # e.g. 0, 1, 5, 9, 12... (because rows 2,3,4,6,7,8,10,11
    # were filtered out). reset_index() renumbers them cleanly
    # from 0, 1, 2, 3...
    # drop=True means don't add the old index as a column.
    df_final = df_final.reset_index(drop=True)
    

    
    return df_final