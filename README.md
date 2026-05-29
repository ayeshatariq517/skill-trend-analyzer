# AI Skill Trend & Career Insight System

A Python-based AI system that analyzes **9,864 real LinkedIn job postings** 
to extract tech skill trends, salary insights, and career recommendations 
using Natural Language Processing (NLP).

---

## Project Overview

The tech job market evolves rapidly. Students and professionals often struggle 
to identify which skills are in demand — spending hours reading blog posts based 
on opinions rather than data.

This system solves that by going directly to the source — real LinkedIn job 
postings — and automatically extracting what employers are actually asking for.

Instead of telling you what we think the market wants, our system tells you 
what **9,864 hiring managers wrote** in their actual job descriptions.

---

## Features

- **Skill Extraction** — Automatically extracts 80+ tech skills from job descriptions using NLP and regex pattern matching
- **Demand Analysis** — Ranks skills by how frequently they appear across all job postings
- **Salary Insights** — Shows average salary for jobs requiring each specific skill
- **Role Search** — Filter and analyze skills for a specific job role (e.g. Data Scientist, DevOps Engineer)
- **Career Recommender** — Enter your current skills and get personalized learning recommendations
- **Data Visualizations** — Generates professional charts saved as PNG files

---

## Sample Output
╔══════════════════════════════════════════════════════╗
║       AI SKILL TREND & CAREER INSIGHT SYSTEM                    ║
║              LinkedIn Job Market 2024                           ║
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
1    Deep Learning       $192,330/year
2    NLP                 $180,449/year
3    PyTorch             $178,706/year
4    MLOps               $174,519/year
5    Machine Learning    $169,498/year

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| Python | Core programming language |
| Pandas | Data loading and manipulation |
| NLTK | Natural Language Processing |
| Scikit-learn | Machine learning utilities |
| Matplotlib | Chart generation |
| Seaborn | Chart styling |
| WordCloud | Word cloud visualization |
| Colorama | Colored terminal output |
| tqdm | Progress bars |

---

## Project Structure

**Source Code** (`src/`)
- `data_loader.py` — Loads, cleans and filters 124k job postings down to 9,864 tech jobs
- `skill_extractor.py` — NLP pipeline that extracts 80+ skills from job descriptions
- `trend_analyzer.py` — Calculates skill frequency, salary insights and trends
- `visualizer.py` — Generates professional charts as PNG files

**Entry Point**
- `main.py` — Run this to start the interactive CLI

**Other**
- `requirements.txt` — Install all dependencies with one command
- `data/` — Place your dataset files here (see Dataset section below)
- `output/charts/` — Generated charts are saved here automatically

---

## Dataset

This project uses the **LinkedIn Job Postings (2023-2024)** dataset from Kaggle.

Download here:
https://www.kaggle.com/datasets/arshkon/linkedin-job-postings

After downloading, extract the zip and place these two files in the `data/` folder:

- `postings.csv`
- `salaries.csv`

---

## Installation & Setup

**1. Clone the repository**
git clone https://github.com/YOUR_USERNAME/skill-trend-analyzer.git
cd skill-trend-analyzer

**2. Install dependencies**
pip install -r requirements.txt

**3. Download the dataset**

Follow the dataset instructions above and place files in `data/`

**4. Run the program**
python main.py

---

## How It Works

**Step 1 — Data Loading**

Raw CSV files are loaded using pandas. The dataset is cleaned by removing
empty descriptions, fixing date formats, and normalizing salary data to
yearly figures. Jobs are filtered to tech roles only using a curated list
of 40+ job title keywords — reducing 123,849 total postings to 9,864
relevant tech jobs. Salary data is joined using a LEFT JOIN so all jobs
are kept even when salary is not disclosed.

**Step 2 — Skill Extraction (NLP)**

Each job description goes through a four-stage NLP pipeline.
First, text cleaning removes HTML tags, encoding errors, and URLs.
Second, all 80+ skill patterns are pre-compiled into regex objects
for performance. Third, each description is scanned for skill matches
using word boundary markers to avoid false positives — for example
preventing the word "scalable" from matching "Scala".
Fourth, matched skills are recorded per job.

**Step 3 — Analysis**

Skill frequency is calculated by exploding the skills lists and counting
occurrences across all jobs. Salary analysis groups jobs by skill and
calculates average yearly compensation. Only skills with at least 10
salary data points are included for statistical reliability.

**Step 4 — Interactive CLI**

Results are presented through a colored, menu-driven terminal interface.
Users can explore top skills, salary data, search by job role, and get
personalized career path recommendations.

---

## Limitations

- Dataset covers March–April 2024 only — multi-year trend analysis requires a longitudinal dataset
- Salary data is available for 27% of jobs — only companies that publicly disclosed compensation
- Skill extraction is rule-based using a predefined dictionary — skills not in the dictionary will not be detected

---

## Future Improvements

- Integrate multi-year salary data to enable year-over-year trend prediction using Linear Regression
- Add a salary prediction model — input your skillset, get a predicted salary using Random Forest
- Build a web interface using Flask or Streamlit for broader accessibility

---


FAST NUCES — Artificial Intelligence Lab Project — 2024