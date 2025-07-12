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
    "cancer genomics", 
    "sequencing",
    "mutation",
    "cancer evolution",
    "cancer",
    "evolution",
    "trajectory",
    "tumor",
    "somatic",
    "germline"
]

# Maximum results per search
MAX_RESULTS_PER_SEARCH = 50

# Keyword matching settings
KEYWORD_MATCH_THRESHOLD = 0.0  # Keyword matching threshold (0.0 ~ 1.0) - lowered to 0.0

# Required keyword settings (all keywords must be included)
REQUIRED_KEYWORDS = [
    "breast cancer",
    "cancer", 
    "sequencing",
    "mutation"
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
    "structural"
]

# Keyword weight settings
PRIORITY_KEYWORD_WEIGHT = 2.0  # Weight for priority keywords
REQUIRED_KEYWORD_WEIGHT = 1.0  # Base weight for required keywords

# Score-based classification settings
SCORE_THRESHOLDS = {
    "high": 0.7,    # 0.7 or higher: high relevance
    "medium": 0.4,  # 0.4 or higher: medium relevance  
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
# Date filter settings (adjustable as needed)
# Option 1: Last 7 days (very restrictive)
# seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y/%m/%d")

# Option 2: Last 30 days (recommended)
thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y/%m/%d")

# Option 3: Last 1 year (broad range)
# one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y/%m/%d")

# Option 4: Disable date filter (search all papers)
# date_filter = None

FILTER_SETTINGS = {
    "publication_date_from": thirty_days_ago,  # 30 days ago from current date (for more results)
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
OUTPUT_BASE_DIR = "./output"
MARKDOWN_OUTPUT_DIR = "./output/papers"
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
SCHEDULE_TIME = "09:00"  # 24-hour format (HH:MM)
SCHEDULE_DAYS = ["sunday"]  # List of days (monday, tuesday, ..., sunday)

# Scheduling log settings
SCHEDULE_LOG_FILE = "./logs/schedule.log"

# =============================================================================
# Logging Settings
# =============================================================================

# Log settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "./logs/pubmed_scraper.log"
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
