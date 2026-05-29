# AI Skill Trend & Career Insight System

A Python-based AI system that analyzes **9,864 real LinkedIn job postings**
to extract tech skill trends, salary insights, and career recommendations
using Natural Language Processing (NLP).

---

## Project Overview

The tech job market evolves rapidly. Students and professionals often struggle
to identify which skills are in demand — spending hours reading blog posts
based on opinions rather than data.

This system solves that by going directly to the source — real LinkedIn job
postings — and automatically extracting what employers are actually asking for.

Instead of telling you what we think the market wants, our system tells you
what **9,864 hiring managers wrote** in their actual job descriptions.

---

## Features

- **Automated Skill Extraction** — NLP pipeline extracts 80+ specific tech skills from raw job description text
- **Demand Ranking** — Ranks skills by frequency across all job postings with percentage market share
- **Salary Intelligence** — Calculates average yearly salary per skill from disclosed compensation data
- **Role-Based Search** — Filter the entire dataset by job role and get role-specific skill rankings and salary figures
- **Career Path Recommender** — Enter your current skills and receive personalized recommendations for what to learn next based on skill co-occurrence patterns
- **Data Visualizations** — Generates three professional charts: skill frequency bar chart, salary bar chart, and word cloud
- **Interactive CLI** — Fully menu-driven terminal interface with colored output and formatted tables

---

## Sample Output
╔══════════════════════════════════════════════════════╗
║       AI SKILL TREND & CAREER INSIGHT SYSTEM        ║
║              LinkedIn Job Market 2024               ║
╚══════════════════════════════════════════════════════╝
TOP 15 MOST IN-DEMAND TECH SKILLS (2024)
Skill                  Jobs      %    Chart

1    SQL                   2,971   30.1%  ###############
2    Python                2,917   29.6%  ##############
3    Agile                 2,773   28.1%  #############
4    AWS                   2,026   20.5%  ##########
5    Java                  1,854   18.8%  #########
6    JavaScript            1,853   18.8%  #########
7    Azure                 1,732   17.6%  ########
8    CI/CD                 1,375   13.9%  ######
9    Linux                 1,026   10.4%  #####
10   REST API                967    9.8%  ####
TOP 10 HIGHEST PAYING SKILLS
1    Deep Learning       $192,330/year   (60 jobs)
2    NLP                 $180,449/year   (80 jobs)
3    PyTorch             $178,706/year   (61 jobs)
4    MLOps               $174,519/year   (31 jobs)
5    Machine Learning    $169,498/year  (335 jobs)
6    Go                  $168,984/year   (55 jobs)
7    Scikit-learn        $168,914/year   (18 jobs)
8    dbt                 $168,250/year   (26 jobs)
9    Computer Vision     $167,336/year   (57 jobs)
10   TensorFlow          $166,056/year   (62 jobs)

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| Python | Core programming language |
| Pandas | Data loading, cleaning, merging, groupby, explode, pivot |
| re (regex) | Pattern matching for skill extraction |
| Scikit-learn | Machine learning utilities |
| Matplotlib | Chart generation and dark theme styling |
| Seaborn | Chart aesthetics |
| WordCloud | Frequency-weighted word cloud generation |
| Colorama | Colored terminal output |
| tqdm | Real-time progress bars |
| collections.Counter | Skill frequency counting |

---

## Project Structure

**Source Code** (`src/`)
- `data_loader.py` — Loads, cleans and filters 124k job postings to 9,864 tech jobs
- `skill_extractor.py` — NLP pipeline extracting 80+ skills from job descriptions
- `trend_analyzer.py` — Frequency ranking, salary analysis, trend calculations
- `visualizer.py` — Generates 3 professional charts as PNG files

**Entry Point**
- `main.py` — Run this to start the interactive CLI

**Other**
- `requirements.txt` — Install all dependencies with one command
- `data/` — Place dataset files here (see Dataset section)
- `output/charts/` — Generated charts saved here automatically

---

## Dataset

This project uses the **LinkedIn Job Postings (2023-2024)** dataset from Kaggle.

Download here:
https://www.kaggle.com/datasets/arshkon/linkedin-job-postings

After downloading place these two files in the `data/` folder:
- `postings.csv`
- `salaries.csv`

---

## Installation & Setup

**1. Clone the repository**
git clone https://github.com/ayeshatariq517/skill-trend-analyzer.git
cd skill-trend-analyzer

**2. Install dependencies**
pip install -r requirements.txt

**3. Download the dataset**

Follow the dataset instructions above and place files in `data/`

**4. Run the program**
python main.py

---

## How It Works — Technical Detail

### Module 1 — Data Loader (`data_loader.py`)

**Column Selection**
From 31 raw columns, only 7 are kept — job_id, title, company_name,
location, description, listed_time, formatted_experience_level.
This reduces memory usage significantly.

**Unix Timestamp Conversion**
The posted date is stored as Unix milliseconds (e.g. 1.7134E+12).
This is converted using `pd.to_datetime(unit='ms')` and split into
separate year and month columns for trend analysis.

**Tech Job Filtering**
A curated list of 40+ multi-word job title patterns is used with
`str.contains()` and regex OR matching to filter 123,849 total
postings down to 9,864 genuine tech jobs. Multi-word phrases
(e.g. "software engineer" not just "engineer") were deliberately
used to avoid false positives like "Building Engineer".

**Salary Normalization**
Salaries come in three pay periods — HOURLY, MONTHLY, YEARLY.
All are normalized to yearly equivalents:
- HOURLY × 2080 (40 hours × 52 weeks)
- MONTHLY × 12
- YEARLY used as-is

Outliers below $10,000 and above $500,000 are removed as data errors.

**LEFT JOIN**
Salary data is merged onto job postings using `pd.merge(how='left')`
so all 9,864 jobs are preserved even when salary is not disclosed.
This results in 2,680 jobs (27.2%) with salary data.

---

### Module 2 — Skill Extractor (`skill_extractor.py`)

**Skill Dictionary**
A dictionary of 80+ tech skills is defined where each skill has
multiple aliases to handle real-world inconsistency:
- Python → ['python', 'python3', 'python 3']
- JavaScript → ['javascript', 'java script', r'\bjs\b']
- AWS → [r'\baws\b', 'amazon web services']

Skills cover programming languages, web frameworks, databases,
cloud platforms, ML/AI frameworks, DevOps tools, and methodologies.

**Regex Compilation**
All patterns are pre-compiled using `re.compile()` with `re.IGNORECASE`
before any processing begins. This is a performance optimization —
compiling once is significantly faster than compiling per description.
Non-capturing groups `(?:...)` are used for clean alternation.

**Word Boundary Matching**
`\b` word boundary markers prevent false positives — for example
preventing "scalable" from matching "Scala" which was caught and
fixed during development.

**Text Cleaning Pipeline**
Each description goes through:
1. UTF-8 encoding fix (removes â€™ artifacts)
2. HTML tag removal with `re.sub(r'<.*?>', ' ', text)`
3. URL removal
4. Special character removal (preserving + # . / - for C++, C#, Node.js)
5. Whitespace normalization

**Extraction**
`pattern.search()` scans each cleaned description for every skill.
Results are stored as a list per job giving a final skills column
where each cell contains a list like ['Python', 'SQL', 'AWS'].

---

### Module 3 — Trend Analyzer (`trend_analyzer.py`)

**Skill Frequency**
`df['skills'].explode()` unpacks skill lists so each skill gets
its own row. `value_counts()` then counts occurrences across all
jobs. Percentage is calculated as count divided by total jobs.

**Monthly Trends**
Jobs are grouped by month and skill using `groupby()` then
reshaped into a pivot table using `pivot_table()` where rows
are months and columns are skill names.

**Growth Rate Calculation**
Available months are split into two halves. Growth is calculated as:
`(later_count - earlier_count) / earlier_count × 100`
Results are classified as Growing (+5%), Stable, or Declining (-5%).

**Salary By Skill**
Jobs with salary data are exploded by skill then grouped using
`groupby().agg()` to calculate both mean salary and job count
per skill simultaneously. Only skills with at least 10 salary
data points are included for statistical reliability.

---

### Module 4 — Visualizer (`visualizer.py`)

**Dark Theme**
`plt.rcParams` is updated globally with a dark color scheme
(background #1e1e2e, text #cdd6f4) applied to all charts.

**Skill Frequency Chart**
Horizontal bar chart with a blue gradient using `plt.cm.Blues`
colormap. Count and percentage labels are added to each bar
using `ax.text()`. Unnecessary spines are removed for clean design.

**Salary Chart**
Horizontal bar chart with a green gradient using `plt.cm.Greens`.
X-axis formatted as dollar amounts using `FuncFormatter`.

**Word Cloud**
Generated using `WordCloud.generate_from_frequencies()` with skill
counts as weights so more demanded skills appear larger.
Dark background with Blues colormap for visual consistency.

---

### Module 5 — Main CLI (`main.py`)

**Startup Pipeline**
Data loading, skill extraction, and analysis all run once at
startup. Results are stored in memory so menu options respond
instantly without reprocessing.

**Menu Options**
1. Top 15 skills with color-coded ranking (gold/silver/bronze for top 3)
2. Salary insights color-coded by tier (yellow above $160k, green above $130k)
3. Role search — filters dataset by job title and re-runs frequency analysis on the subset
4. Career recommender — rule-based system using skill co-occurrence logic to suggest next skills to learn
5. Generate and open charts — creates all 3 PNG files and opens the folder
6. Dataset summary — shows job counts, experience level distribution, and salary statistics

---

## Key Technical Decisions

| Decision | Reason |
|----------|--------|
| Regex over spaCy NER | Known fixed vocabulary — regex is faster and more accurate for this use case |
| Word boundary markers | Prevents false positives like "scalable" matching "Scala" |
| Pre-compiled patterns | Compile once at import time not per description — major performance gain |
| Multi-word title keywords | "software engineer" not "engineer" — avoids matching construction/civil roles |
| LEFT JOIN for salary | Preserves all 9,864 jobs instead of dropping 73% with no salary data |
| Minimum 10 jobs for salary | Statistically unreliable averages from 1-2 data points excluded |

---

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Raw job postings | 123,849 |
| Tech jobs after filtering | 9,864 |
| Jobs with salary data | 2,680 (27.2%) |
| Unique companies | 3,743 |
| Unique locations | 1,186 |
| Skills tracked | 80+ |
| Average skills per job | 4.3 |
| Jobs with skills detected | 8,446 (85.6%) |
| Date range | March – April 2024 |

---

## Limitations

- Dataset covers March–April 2024 only — multi-year trend analysis requires a longitudinal dataset
- Salary data available for 27% of jobs — only companies that publicly disclosed compensation
- Skill extraction is rule-based using a predefined dictionary — skills outside the dictionary will not be detected
- Career recommender uses rule-based co-occurrence logic rather than a trained ML model

---

## Future Improvements

- Integrate multi-year salary data to enable year-over-year trend prediction using Linear Regression
- Add a salary prediction model — input your skillset, get a predicted salary using Random Forest Regression
- Build a web interface using Flask or Streamlit for broader accessibility
- Expand skill dictionary automatically using unsupervised clustering on job description text

---

FAST NUCES — Artificial Intelligence Lab Project — 2024
