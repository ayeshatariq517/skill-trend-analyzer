# ============================================================
# skill_extractor.py
# PURPOSE: Extract specific tech skills from job description
#          text using NLP techniques and a curated skill
#          dictionary. Adds a 'skills' column to the DataFrame.
# ============================================================

import re                          # regex — pattern matching in text
import pandas as pd
from tqdm import tqdm              # progress bar for loops
from colorama import Fore, Style, init

init(autoreset=True)

# ============================================================
# THE SKILL DICTIONARY
# This is the most important data structure in the project.
# It's a Python dictionary where:
#   KEY   = the canonical skill name (how we display it)
#   VALUE = list of variations/aliases of that skill
#
# Why do we need aliases?
# Job postings are written by humans, inconsistently.
# "JavaScript", "javascript", "JS", "js", "Java Script"
# all mean the same thing. We need to catch all variations.
# ============================================================

SKILLS_DICT = {
    # --- PROGRAMMING LANGUAGES ---
    'Python':       ['python', 'python3', 'python 3'],
    'JavaScript':   ['javascript', 'java script', r'\bjs\b'],
    'TypeScript':   ['typescript', 'type script'],
    'Java':         [r'\bjava\b'],
    'C++':          [r'c\+\+', 'cpp'],
    'C#':           [r'c#', r'\bc sharp\b'],
    'Go':           [r'\bgolang\b', r'\bgo\b(?= programming| lang| developer)'],
    'Rust':         [r'\brust\b(?= programming| lang| developer)'],
    'Swift':        [r'\bswift\b'],
    'Kotlin':       ['kotlin'],
    'R':            [r'\br\b(?= programming| language| studio)'],
    'PHP':          [r'\bphp\b'],
    'Ruby':         [r'\bruby\b'],
    'Scala':        [r'\bscala\b'],
    'MATLAB':       ['matlab'],

    # --- WEB FRAMEWORKS & LIBRARIES ---
    'React':        [r'\breact\b', 'react.js', 'reactjs'],
    'Angular':      ['angular', 'angularjs', 'angular.js'],
    'Vue.js':       [r'\bvue\b', 'vue.js', 'vuejs'],
    'Node.js':      ['node.js', 'nodejs', r'\bnode\b(?= js| developer)'],
    'Django':       ['django'],
    'Flask':        [r'\bflask\b'],
    'FastAPI':      ['fastapi', 'fast api'],
    'Spring Boot':  ['spring boot', 'springboot'],
    'Next.js':      ['next.js', 'nextjs'],

    # --- DATABASES ---
    'SQL':          [r'\bsql\b'],
    'MySQL':        ['mysql'],
    'PostgreSQL':   ['postgresql', 'postgres'],
    'MongoDB':      ['mongodb', 'mongo'],
    'Redis':        [r'\bredis\b'],
    'Oracle':       [r'\boracle\b(?= db| database| sql)'],
    'SQL Server':   ['sql server', 'mssql', 'microsoft sql'],
    'Cassandra':    ['cassandra'],
    'Elasticsearch':['elasticsearch', 'elastic search'],
    'Snowflake':    ['snowflake'],
    'BigQuery':     ['bigquery', 'big query'],

    # --- CLOUD PLATFORMS ---
    'AWS':          [r'\baws\b', 'amazon web services'],
    'Azure':        [r'\bazure\b', 'microsoft azure'],
    'GCP':          [r'\bgcp\b', 'google cloud', 'google cloud platform'],

    # --- ML / AI FRAMEWORKS ---
    'TensorFlow':   ['tensorflow', 'tensor flow'],
    'PyTorch':      ['pytorch', 'py torch'],
    'Scikit-learn': ['scikit-learn', 'sklearn', 'scikit learn'],
    'Keras':        [r'\bkeras\b'],
    'Hugging Face': ['hugging face', 'huggingface'],
    'LangChain':    ['langchain', 'lang chain'],
    'OpenAI':       ['openai', 'open ai', 'chatgpt api', 'gpt-4', 'gpt4'],

    # --- DATA & ML CONCEPTS ---
    'Machine Learning':  ['machine learning', r'\bml\b(?= engineer| model| pipeline)'],
    'Deep Learning':     ['deep learning'],
    'NLP':               [r'\bnlp\b', 'natural language processing'],
    'Computer Vision':   ['computer vision'],
    'Generative AI':     ['generative ai', 'gen ai', 'genai', 'llm', 'large language model'],
    'MLOps':             ['mlops', 'ml ops'],
    'Data Science':      ['data science'],

    # --- DATA ENGINEERING & ANALYTICS ---
    'Apache Spark':  ['apache spark', r'\bspark\b(?= sql| streaming| job)'],
    'Hadoop':        ['hadoop'],
    'Kafka':         [r'\bkafka\b'],
    'Airflow':       ['airflow', 'apache airflow'],
    'dbt':           [r'\bdbt\b'],
    'Pandas':        [r'\bpandas\b'],
    'NumPy':         ['numpy'],
    'Power BI':      ['power bi', 'powerbi'],
    'Tableau':       ['tableau'],
    'Excel':         [r'\bexcel\b'],

    # --- DEVOPS & INFRASTRUCTURE ---
    'Docker':        ['docker'],
    'Kubernetes':    ['kubernetes', r'\bk8s\b'],
    'Terraform':     ['terraform'],
    'Ansible':       ['ansible'],
    'Jenkins':       ['jenkins'],
    'CI/CD':         ['ci/cd', 'cicd', 'continuous integration', 'continuous deployment'],
    'Git':           [r'\bgit\b(?!hub| lab)'],
    'GitHub':        ['github'],
    'GitLab':        ['gitlab'],
    'Linux':         [r'\blinux\b', r'\bunix\b'],

    # --- SECURITY ---
    'Cybersecurity': ['cybersecurity', 'cyber security', 'information security', 'infosec'],
    'Penetration Testing': ['penetration testing', 'pen testing', 'pentesting'],

    # --- MOBILE ---
    'React Native':  ['react native'],
    'Flutter':       ['flutter'],

    # --- OTHER TOOLS ---
    'REST API':      ['rest api', 'restful', 'rest ful', r'\bapi\b(?= development| design| integration)'],
    'GraphQL':       ['graphql', 'graph ql'],
    'Microservices': ['microservices', 'micro services'],
    'Agile':         [r'\bagile\b', r'\bscrum\b'],
    'Jira':          [r'\bjira\b'],
}


# ============================================================
# BUILDING THE COMPILED PATTERN
#
# regex (regular expressions) is a language for describing
# text patterns. For example:
#   r'\bpython\b' matches "python" but not "pythonista"
#   \b means "word boundary" — the edge of a word
#
# Compiling all patterns once upfront is much faster than
# recompiling them for every single job description.
# re.compile() turns a pattern string into a compiled
# regex object that can search text very quickly.
# re.IGNORECASE makes matching case-insensitive so we
# catch "Python", "PYTHON", "python" all at once.
# ============================================================

def build_compiled_patterns():
    """
    Pre-compiles all regex patterns for every skill.
    Returns a dict of {skill_name: compiled_regex_pattern}
    """
    compiled = {}
    for skill_name, patterns in SKILLS_DICT.items():
        # Join all aliases with | (OR) into one pattern
        # e.g. ['python', 'python3'] → 'python|python3'
        combined = '|'.join(f'(?:{p})' for p in patterns)
        # (?:...) is a non-capturing group — it groups the
        # pattern but doesn't capture it separately.
        # This is a regex best practice for alternation (|).
        compiled[skill_name] = re.compile(combined, re.IGNORECASE)
    return compiled

# Build once at module load time — not inside any function.
# This means it runs once when the file is imported, not
# repeatedly for every job description. Big performance win.
COMPILED_PATTERNS = build_compiled_patterns()


# ============================================================
# TEXT CLEANING
# Before we search for skills, we clean the text.
# Job descriptions have HTML artifacts, weird characters,
# encoding errors etc. We remove these first.
# ============================================================

def clean_text(text):
    """
    Cleans a single job description string.
    Returns cleaned text ready for skill extraction.
    """
    if not isinstance(text, str):
        # If text is NaN or not a string, return empty string
        return ''

    # Fix encoding errors — these appear as â€™ â€" etc
    # They're caused by UTF-8 characters being read as
    # the wrong encoding (latin-1/windows-1252)
    text = text.encode('utf-8', errors='ignore').decode('utf-8')

    # Remove HTML tags like <br>, <p>, <strong> etc
    # <.*?> matches any HTML tag
    # .*? means "any characters, as few as possible"
    text = re.sub(r'<.*?>', ' ', text)

    # Remove URLs (http://... or https://...)
    text = re.sub(r'http\S+', ' ', text)

    # Remove special characters but keep + # . / - spaces
    # (we need + for C++, # for C#, . for Node.js etc)
    text = re.sub(r'[^\w\s\+\#\.\/\-]', ' ', text)

    # Collapse multiple spaces into one
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# ============================================================
# SKILL EXTRACTION FOR ONE DESCRIPTION
# ============================================================

def extract_skills_from_text(text):
    """
    Takes one job description string.
    Returns a list of skill names found in that text.
    
    Example:
        Input:  "We need Python, AWS and React experience"
        Output: ['Python', 'AWS', 'React']
    """
    cleaned = clean_text(text)

    found_skills = []
    for skill_name, pattern in COMPILED_PATTERNS.items():
        # pattern.search() looks for the pattern anywhere
        # in the text. Returns a match object if found,
        # None if not found.
        if pattern.search(cleaned):
            found_skills.append(skill_name)

    return found_skills


# ============================================================
# MAIN FUNCTION — EXTRACT SKILLS FOR ENTIRE DATAFRAME
# ============================================================

def extract_skills(df):
    """
    Takes the full DataFrame.
    Adds a 'skills' column where each cell contains
    a list of skills found in that job's description.
    
    Example of what the skills column looks like:
        row 0: ['Python', 'SQL', 'Machine Learning']
        row 1: ['JavaScript', 'React', 'Node.js']
        row 2: ['AWS', 'Docker', 'Kubernetes']
    """

    print(Fore.YELLOW + Style.BRIGHT + "\n" + "="*50)
    print(Fore.YELLOW + Style.BRIGHT + "   EXTRACTING SKILLS FROM JOB DESCRIPTIONS")
    print(Fore.YELLOW + Style.BRIGHT + "="*50)
    print(Fore.CYAN + f"\n🔍 Processing {len(df):,} job descriptions...")
    print(Fore.CYAN + "   (This may take 1-2 minutes)\n")

    # tqdm() wraps any iterable and shows a progress bar.
    # desc= sets the label shown next to the bar.
    # We iterate over df['description'] — the Series of
    # all job description strings — and apply
    # extract_skills_from_text() to each one.
    skills_list = []
    for description in tqdm(df['description'],
                            desc='Extracting skills',
                            colour='green'):
        skills = extract_skills_from_text(description)
        skills_list.append(skills)

    # Add the results as a new column in the DataFrame
    df = df.copy()
    df['skills'] = skills_list

    # --- STATS ---
    # Count how many jobs had at least one skill found
    has_skills = df['skills'].apply(lambda x: len(x) > 0).sum()
    # lambda x: len(x) > 0 returns True if the list has
    # at least one skill, False if it's empty []
    # .sum() counts all the True values

    # Calculate average skills per job
    avg_skills = df['skills'].apply(len).mean()
    # .apply(len) runs len() on every list in the column
    # giving us the count of skills per job
    # .mean() averages those counts

    # Find the most common skills for a quick preview
    from collections import Counter
    # Counter counts occurrences of items in a list
    all_skills = []
    for skill_list in df['skills']:
        all_skills.extend(skill_list)
    # .extend() adds all items from a list into another list
    # so [['Python','SQL'], ['Python','AWS']] becomes
    # ['Python', 'SQL', 'Python', 'AWS']

    top_10 = Counter(all_skills).most_common(10)
    # .most_common(10) returns the 10 most frequent items
    # as a list of (skill, count) tuples

    print(Fore.GREEN + f"\n   ✓ Jobs with at least 1 skill found: "
          f"{has_skills:,} ({has_skills/len(df)*100:.1f}%)")
    print(Fore.GREEN + f"   ✓ Average skills per job: {avg_skills:.1f}")

    print(Fore.CYAN + "\n📊 Quick Preview — Top 10 Skills Found:")
    for i, (skill, count) in enumerate(top_10, 1):
        # enumerate(top_10, 1) gives us (1, item), (2, item)...
        # starting from 1 instead of 0
        bar = '█' * (count // 50)  # simple text bar
        print(Fore.GREEN + f"   {i:2}. {skill:<20} {count:>5,}  {bar}")

    print(Fore.YELLOW + Style.BRIGHT + "="*50 + "\n")

    return df