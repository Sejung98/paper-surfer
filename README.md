# Paper Surfer 📚

A Python program that automatically collects and analyzes papers from PubMed and saves them in Markdown format.

## Key Features ✨

1. **PubMed Search**: Keyword-based paper search
2. **Content Analysis**: Verify keyword matching in actual paper content
3. **Markdown Storage**: Save collected paper information in structured Markdown format
4. **Automatic Scheduling**: Automatically execute paper collection at specified times weekly

## Installation 🔧

### 1. Clone Repository
```bash
git clone <repository-url>
cd paper_surfer
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage 📖

### 1. Interactive Mode (Default)
```bash
python main.py
```

### 2. Run Once
```bash
# Run with default keywords
python main.py --once

# Run with specific keywords
python main.py --once --keywords "machine learning, deep learning"

# Specify maximum number of papers
python main.py --once --max-papers 20
```

### 3. Run Scheduler
```bash
# Default schedule (every Sunday at 09:00)
python main.py --scheduler

# Set specific schedule
python main.py --scheduler --day monday --time "08:00"
```

### 4. Help
```bash
python main.py --help
```

## Configuration 🛠️

You can modify the following settings in the `config.py` file:

### Default Search Keywords
```python
SEARCH_KEYWORDS = [
    "machine learning",
    "artificial intelligence",
    "deep learning"
]
```

### Schedule Settings
```python
SCHEDULE_DAY = "sunday"    # Execution day
SCHEDULE_TIME = "09:00"    # Execution time (24-hour format)
```

### Search Settings
```python
MAX_PAPERS_PER_SEARCH = 10        # Maximum papers per search
REQUIRED_KEYWORD_MATCHES = 3      # Relevance criteria
```

## Output Results 📁

### Directory Structure
```
paper_surfer/
├── output/
│   └── YYYY-MM-DD/           # Date-based directory
│       ├── paper1.md         # Individual paper files
│       ├── paper2.md
│       ├── summary_*.md      # Summary reports
│       └── metadata_*.json   # Metadata
├── logs/                     # Log files
└── modules/                  # Module files
```

### Markdown File Example
```markdown
# Paper Title

## Paper Information
- **Title**: Paper Title
- **Authors**: Author Names
- **Publication Year**: 2023
- **Source**: Journal/Conference Name
- **URL**: Paper URL

## Abstract
Paper abstract content...

## Keyword Matching
### Keyword Matching Results
- **machine learning**: 5 matches
- **deep learning**: 3 matches

## Additional Information
- **Citation Count**: 42
- **PDF Link**: PDF URL
- **PubMed**: PubMed URL
```

## Module Structure 🏗️

```
modules/
├── pubmed_scraper.py     # PubMed search
├── markdown_saver.py     # Markdown storage
└── scheduler.py          # Scheduling management
```

### Module Roles

1. **pubmed_scraper.py**: Search papers from PubMed and collect basic information
2. **markdown_saver.py**: Save collected information in Markdown format
3. **scheduler.py**: Automatic scheduling and overall task management

## Main Classes 📋

### PubMedScraper
```python
scraper = PubMedScraper()
papers = scraper.search_papers(["machine learning"], max_results=5)
```

### MarkdownSaver
```python
saver = MarkdownSaver()
filepath = saver.save_paper(paper_data)
```

### PaperScrapperScheduler
```python
scheduler = PaperScrapperScheduler()
scheduler.start_scheduler()
```

## Precautions ⚠️

1. **PubMed API Limits**: Respect rate limits to avoid IP blocking
2. **Paper Access**: Some papers may have access restrictions
3. **Storage Space**: Collected files accumulate, so periodic cleanup is needed
4. **Internet Connection**: Stable internet connection required

## Troubleshooting 🔍

### Common Errors

1. **ImportError**: Check library installation
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission Error**: Check file permissions
   ```bash
   chmod +x main.py
   ```

3. **API Request Failure**: Check network connection and API key validity

4. **Scheduler Error**: Check time format (HH:MM format)

### Check Logs
```bash
tail -f logs/paper_scrapper_YYYYMMDD.log
```

## Development Environment 🔧

- **Python**: 3.8 or higher
- **Required Libraries**:
  - requests
  - beautifulsoup4
  - lxml
  - schedule
  - python-dateutil

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License 📄

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact 📧

Please register issues for questions or bug reports.

---

**Note**: This tool should be used for research purposes and must respect paper copyrights. 