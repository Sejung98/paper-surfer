# Paper Surfer Configuration
# PubMed API-based paper search and storage system

from datetime import datetime, timedelta

# =============================================================================
# PubMed API Settings
# =============================================================================

# PubMed API base URL
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# PubMed API key (optional but recommended)
# You can get it from your NCBI account: https://www.ncbi.nlm.nih.gov/account/
# Without API key: 3 requests/second, with API key: 10 requests/second
PUBMED_API_KEY = ""  # Example: "YOUR_API_KEY_HERE"

# Request limit settings
MAX_REQUESTS_PER_SECOND = 10  # 3 without API key, 10 with API key
REQUEST_DELAY = 1.0  # Minimum delay between requests (seconds)

# Email address (required: contact information must be provided when using PubMed API)
CONTACT_EMAIL = ""  # Change to your actual email address

# Tool name (for application identification when using PubMed API)
TOOL_NAME = "PaperSurfer"

# =============================================================================
# Search Settings
# =============================================================================

# Paper search keywords (using PubMed search syntax)
# Search broadly first, then filter with required/priority keywords
SEARCH_KEYWORDS = [
    "breast cancer",
    "cancer",
    "genomics",
    "sequencing",
    "mutation",
    "evolution",
    "trajectory",
    "tumor",
    "somatic",
    "germline",
    "signature",
    "copy number",
    "structural variation",
    "chromosomal instability",
    "resistance",
    "prognosis",
    "early detection",
    "clonal",
    "ecDNA"
]

# Author search examples (you can add specific author names)
# To search for specific authors, add their names to SEARCH_KEYWORDS above
# Examples:
# "John Smith"     - searches for papers by John Smith
# "Smith J"        - searches for papers by J. Smith
# "Smith"          - searches for papers by anyone with surname Smith

# Maximum results per search
MAX_RESULTS_PER_SEARCH = 50

# Keyword matching settings
KEYWORD_MATCH_THRESHOLD = 0.0  # Keyword matching threshold (0.0 ~ 1.0) - lowered to 0.0

# Required keyword settings (all keywords must be included)
REQUIRED_KEYWORDS = [
    "breast cancer",
    "sequencing"

]

# Priority keyword settings (gives score weight if included)
PRIORITY_KEYWORDS = [
    "cancer evolution",
    "evolution", 
    "clonal",
    "whole genome duplication",
    "whole genome doubling",
    "giant tumor cell",
    "WGD",
    "WGS", 
    "SNV",
    "SV",
    "CNV",
    "CNA",
    "copy number alteration",
    "copynumber alteration", 
    "structural",
    "structural variation",
    "chromosomal instability",
    "evolution",
    "clonal",
    "trajectory",
    "signature",
    "driver mutation",
    "prognosis",
    "resistance",
    "early detection",
    "immune escape",
    "metastasis",
    "heterogeneity",
    "ecDNA",
    "extra chromosomal DNA"
]

# Keyword weight settings
PRIORITY_KEYWORD_WEIGHT = 2.0  # Weight for priority keywords
REQUIRED_KEYWORD_WEIGHT = 1.0  # Base weight for required keywords

# Score-based classification settings
SCORE_THRESHOLDS = {
    "high": 0.8,    # 0.8 or higher: high relevance (increased from 0.7)
    "medium": 0.5,  # 0.5 or higher: medium relevance (increased from 0.4)
    "low": 0.0      # 0.0 or higher: low relevance
}

# Storage directories by category
CATEGORY_FOLDERS = {
    "high": "high_relevance",
    "medium": "medium_relevance", 
    "low": "low_relevance"
}

# High-impact journal priority settings
HIGH_IMPACT_JOURNALS = [
    "nature",
    "cell", 
    "science"
]

# Korean summary feature settings
ENABLE_KOREAN_SUMMARY = True  # Whether to generate Korean summary
SUMMARY_MAX_LENGTH = 150      # Maximum summary length (characters)

# Search result filtering
# =============================================================================
# Date Filter Settings
# =============================================================================

# Enable/disable date filtering
ENABLE_DATE_FILTER = True  # Set to False to search all papers regardless of date

# Number of days back to search (from current date)
SEARCH_DAYS_BACK = 7  # Options: 7, 30, 90, 365, or any number of days

# Preset options for common use cases:
# SEARCH_DAYS_BACK = 7     # Last week (very restrictive, few results)
# SEARCH_DAYS_BACK = 30    # Last month (recommended, balanced results)
# SEARCH_DAYS_BACK = 90    # Last 3 months (more results)
# SEARCH_DAYS_BACK = 365   # Last year (very broad, many results)

# Calculate date_from dynamically based on settings
def get_date_from():
    if not ENABLE_DATE_FILTER:
        return None
    return (datetime.now() - timedelta(days=SEARCH_DAYS_BACK)).strftime("%Y/%m/%d")

# Get the calculated date (will be None if date filter is disabled)
calculated_date_from = get_date_from() if ENABLE_DATE_FILTER else None

FILTER_SETTINGS = {
    "publication_date_from": calculated_date_from,  # Calculated based on SEARCH_DAYS_BACK setting
    "publication_date_to": None,  # None means up to current date
    "min_abstract_length": 50,  # Minimum abstract length - lowered from 100 to 50
    "languages": ["english"],  # Language filter (english: English)
    "publication_types": [
        "Journal Article",
        "Review",
        "Meta-Analysis",
        "Systematic Review",
        "Research Support, N.I.H., Extramural",
        "Case Reports"  # Added more diverse publication types
    ]
}

# =============================================================================
# Storage Settings
# =============================================================================

# Output directory settings
OUTPUT_BASE_DIR = "C:/iCloudDrive/iCloud~md~obsidian/auto논문"
MARKDOWN_OUTPUT_DIR = "C:/iCloudDrive/iCloud~md~obsidian/auto논문"
ENABLE_DATE_FOLDERS = True  # Whether to create date-based folders

# Markdown file settings
MARKDOWN_FILE_PREFIX = "paper"
MARKDOWN_FILE_SUFFIX = ".md"
MARKDOWN_TEMPLATE = """# {title}

## 📝 Summary (Korean)
{korean_summary}

## Paper Information
- **Title**: {title}
- **Authors**: {authors}
- **Journal**: {journal}
- **Publication Date**: {pub_date}
- **DOI**: {doi}
- **PMID**: {pmid}
- **PMC ID**: {pmc_id}
- **Keywords**: {keywords}

## Abstract
{abstract}

## Collection Information
- **Collection Date**: {collection_date}
- **Search Keywords**: {search_keyword}
- **Keyword Matching Score**: {keyword_score:.2f}
- **Relevance Category**: {relevance_category}
- **PubMed URL**: https://pubmed.ncbi.nlm.nih.gov/{pmid}/

## Metadata
- **Language**: {language}
- **Publication Type**: {publication_type}
- **MeSH Terms**: {mesh_terms}
- **Grant Information**: {grants}

---
*This document was automatically generated by Paper Surfer.*
"""

# =============================================================================
# Scheduling Settings
# =============================================================================

# Automatic execution schedule settings
SCHEDULE_ENABLED = True
SCHEDULE_TIME = "02:00"  # 24-hour format (HH:MM) - 새벽 2시
SCHEDULE_DAYS = ["saturday"]  # 매주 토요일 실행

# Alternative schedule options:
# SCHEDULE_DAYS = ["monday", "wednesday", "friday"]  # 3 times per week
# SCHEDULE_DAYS = ["sunday"]  # Weekly (original setting)
# SCHEDULE_DAYS = ["monday", "thursday"]  # Twice per week
# SCHEDULE_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]  # Daily execution

# Scheduling log settings
SCHEDULE_LOG_FILE = "C:/iCloudDrive/iCloud~md~obsidian/auto논문/logs/schedule.log"

# =============================================================================
# Logging Settings
# =============================================================================

# Log settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "C:/iCloudDrive/iCloud~md~obsidian/auto논문/logs/pubmed_scraper.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Maximum log file size (MB)
LOG_MAX_SIZE = 10
LOG_BACKUP_COUNT = 5

# =============================================================================
# Error Handling Settings
# =============================================================================

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
EXPONENTIAL_BACKOFF = True  # Whether to use exponential backoff

# Timeout settings
REQUEST_TIMEOUT = 30  # seconds
PARSE_TIMEOUT = 60  # seconds

# Error handling options
CONTINUE_ON_ERROR = True  # Whether to continue on error
SAVE_ERROR_LOG = True  # Whether to save error log

# =============================================================================
# Development and Debugging Settings
# =============================================================================

# Debug mode
DEBUG_MODE = True
VERBOSE_LOGGING = True

# Test mode (test without actually saving files)
TEST_MODE = False
DRY_RUN = False

# Cache settings
ENABLE_CACHING = True
CACHE_DIR = "./cache"
CACHE_DURATION = 3600  # seconds (1 hour)

print("PubMed API-based Paper Surfer configuration loaded.")
print(f"- Search keywords: {len(SEARCH_KEYWORDS)} keywords")
print(f"- Output directory: {MARKDOWN_OUTPUT_DIR}")
print(f"- Scheduling: {'Enabled' if SCHEDULE_ENABLED else 'Disabled'}")
print(f"- API key: {'Set' if PUBMED_API_KEY else 'Not set'}")
print(f"- Contact: {CONTACT_EMAIL}") 
print(f"- Date filter: {'Enabled' if ENABLE_DATE_FILTER else 'Disabled'}")
if ENABLE_DATE_FILTER:
    print(f"- Search range: Last {SEARCH_DAYS_BACK} days (from {calculated_date_from} to today)")
