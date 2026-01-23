import os
import time
import random
import threading
import queue
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---- Prevent unwanted backends
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from flair.models import SequenceTagger
from flair.data import Sentence


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(page_title="Fast AI Job Scraper", layout="wide")


# ============================================================
# GLOBALS (SAFE FOR THREADS)
# ============================================================

STOP_EVENT = threading.Event()
RAW_RESULTS_QUEUE: queue.Queue[dict] = queue.Queue()

# Shared HTTP session (HUGE SPEEDUP)
SESSION = requests.Session()
SESSION.mount(
    "https://",
    HTTPAdapter(
        max_retries=Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
    ),
)

HEADERS_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]


# ============================================================
# LOAD NLP MODEL (CACHED)
# ============================================================

@st.cache_resource
def load_flair_model():
    return SequenceTagger.load("kaliani/flair-ner-skill")

flair_model = load_flair_model()


# ============================================================
# FILTER MAPPINGS
# ============================================================

experience_level_mapping = {
    "Internship": "f_E=1",
    "Entry Level": "f_E=2",
    "Mid Level": "f_E=3",
    "Senior Level": "f_E=4",
}

work_type_mapping = {
    "On-site": "f_WT=1",
    "Hybrid": "f_WT=2",
    "Remote": "f_WT=3",
}

time_filter_mapping = {
    "Past 24 hours": "f_TPR=r86400",
    "Past week": "f_TPR=r604800",
    "Past month": "f_TPR=r2592000",
}


# ============================================================
# SESSION STATE
# ============================================================

if "scraping" not in st.session_state:
    st.session_state.scraping = False
    st.session_state.data = pd.DataFrame()


# ============================================================
# FAST SCRAPING (NO NLP HERE)
# ============================================================

def fetch_job_details(job, work_type, exp_level, position):
    try:
        title_el = job.find("h3", class_="base-search-card__title")
        company_el = job.find("a", class_="hidden-nested-link")
        location_el = job.find("span", class_="job-search-card__location")
        link_el = job.find("a", class_="base-card__full-link")

        if not all([title_el, company_el, location_el, link_el]):
            return None

        link = link_el["href"].split("?")[0]

        time.sleep(random.uniform(0.15, 0.35))  # lighter throttle

        resp = SESSION.get(
            link,
            headers={
                "User-Agent": random.choice(HEADERS_POOL),
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=10,
        )

        soup = BeautifulSoup(resp.text, "html.parser")

        desc = ""
        for sel in (
            "div.show-more-less-html__markup",
            "div.description__text",
            "section.core-section-container",
        ):
            el = soup.select_one(sel)
            if el:
                desc = el.get_text("\n").strip()
                break

        return {
            "Position": position,
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Work Type": work_type,
            "Experience Level": exp_level,
            "Location": location_el.text.strip(),
            "Company": company_el.text.strip(),
            "Title": title_el.text.strip(),
            "Description": desc[:800],
            "Skills": None,
            "Link": link,
        }

    except Exception:
        return None


def scrape_jobs(location, position, work_types, exp_levels, time_filter):
    for wt in work_types:
        for el in exp_levels:
            if STOP_EVENT.is_set():
                return

            url = (
                "https://www.linkedin.com/jobs/search/"
                f"?keywords={position}"
                f"&location={location}"
                f"&{work_type_mapping[wt]}"
                f"&{experience_level_mapping[el]}"
                f"&{time_filter_mapping[time_filter]}"
                "&radius=0"
            )

            resp = SESSION.get(url, headers={"User-Agent": random.choice(HEADERS_POOL)})
            soup = BeautifulSoup(resp.text, "html.parser")
            jobs = soup.find_all("div", class_="base-card")[:5]  # Limit to top 5 jobs

            with ThreadPoolExecutor(max_workers=6) as pool:
                futures = [
                    pool.submit(fetch_job_details, job, wt, el, position)
                    for job in jobs
                ]

                for f in as_completed(futures):
                    if STOP_EVENT.is_set():
                        return
                    res = f.result()
                    if res:
                        RAW_RESULTS_QUEUE.put(res)


# ============================================================
# BATCH NLP (VERY FAST)
# ============================================================

def batch_extract_skills(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Description" not in df:
        return df

    sentences = [Sentence(text) for text in df["Description"].fillna("")]
    flair_model.predict(sentences, mini_batch_size=8)

    df["Skills"] = [
        ", ".join({ent.text for ent in sent.get_spans("ner")})
        for sent in sentences
    ]
    return df


# ============================================================
# BACKGROUND WORKER
# ============================================================

def start_scraping(cities, states, positions, work_types, exp_levels, time_filter):
    st.session_state.data = pd.DataFrame()
    STOP_EVENT.clear()
    st.session_state.scraping = True

    cities = [c.strip() for c in cities.split(",") if c.strip()]
    states = [s.strip() for s in states.split(",") if s.strip()]
    positions = [p.strip().replace(" ", "%20") for p in positions.split(",") if p.strip()]
    locations = [f"{c},{s}" for c in cities for s in states]

    def worker():
        for loc in locations:
            for pos in positions:
                scrape_jobs(loc, pos, work_types, exp_levels, time_filter)

        st.session_state.scraping = False

    threading.Thread(target=worker, daemon=True).start()


def flush_queue():
    updated = False
    while not RAW_RESULTS_QUEUE.empty():
        item = RAW_RESULTS_QUEUE.get()
        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([item])], ignore_index=True
        )
        updated = True
    return updated


# ============================================================
# STREAMLIT UI
# ============================================================

st.title("⚡ Fast AI-Powered LinkedIn Job Scraper")

flush_queue()

with st.sidebar:
    cities = st.text_input("Cities")
    states = st.text_input("States / Countries")
    positions = st.text_input("Job Roles")

    work_types = st.multiselect("Work Type", list(work_type_mapping.keys()))
    exp_levels = st.multiselect("Experience Level", list(experience_level_mapping.keys()))
    time_filter = st.selectbox("Time Filter", list(time_filter_mapping.keys()))

    if st.button("Start Scraping") and not st.session_state.scraping:
        start_scraping(cities, states, positions, work_types, exp_levels, time_filter)

    if st.button("Stop"):
        STOP_EVENT.set()
        st.session_state.scraping = False


status = "Scraping in progress..." if st.session_state.scraping else "Idle"
st.info(status)

col1, col2 = st.columns(2)
with col1:
    st.metric("Jobs Found", len(st.session_state.data))
with col2:
    if not RAW_RESULTS_QUEUE.empty():
        st.metric("In Queue", RAW_RESULTS_QUEUE.qsize())

st.subheader("Results")

# Auto-refresh while scraping
if st.session_state.scraping:
    time.sleep(0.5)
    st.rerun()

st.dataframe(st.session_state.data, use_container_width=True)

if not st.session_state.data.empty and not st.session_state.scraping:
    df = batch_extract_skills(st.session_state.data.copy())
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV (with Skills)", csv, "jobs.csv", "text/csv")
