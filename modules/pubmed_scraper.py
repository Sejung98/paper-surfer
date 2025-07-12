"""
PubMed API scraper module
Search for papers using PubMed API and collect metadata
"""

import requests
import time
import re
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Import config file
try:
    import config
except ImportError:
    print("Warning: config.py not found. Using default settings.")
    config = None

@dataclass
class PubMedPaper:
    """Data class to store PubMed paper information"""
    pmid: str
    title: str
    authors: List[str]
    abstract: str
    journal: str
    pub_date: str
    doi: str
    pmc_id: str
    keywords: List[str]
    mesh_terms: List[str]
    publication_type: str
    language: str
    grants: List[str]
    url: str
    collection_date: str
    search_keyword: str
    keyword_score: float
    korean_summary: str = ""
    relevance_category: str = ""

class PubMedScraper:
    """Class to search and collect papers using PubMed API"""
    
    def __init__(self):
        """Initialize PubMed scraper"""
        self.logger = logging.getLogger(__name__)
        self.base_url = getattr(config, 'PUBMED_BASE_URL', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/')
        self.api_key = getattr(config, 'PUBMED_API_KEY', None)
        self.email = getattr(config, 'CONTACT_EMAIL', 'user@example.com')
        self.tool_name = getattr(config, 'TOOL_NAME', 'PaperSurfer')
        self.request_delay = getattr(config, 'REQUEST_DELAY', 1.0)
        self.max_retries = getattr(config, 'MAX_RETRIES', 3)
        self.timeout = getattr(config, 'REQUEST_TIMEOUT', 30)
        
        # Session settings
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'{self.tool_name}/1.0 ({self.email})',
            'Accept': 'application/xml,application/json,text/xml,text/plain'
        })
        
        self.logger.info(f"PubMed scraper initialization complete")
        self.logger.info(f"API key configured: {'Yes' if self.api_key else 'No'}")
    
    def search_papers(self, keywords: List[str], max_results: int = 50) -> List[PubMedPaper]:
        """
        Search papers with keyword list
        
        Args:
            keywords: List of search keywords
            max_results: Maximum results per search
            
        Returns:
            List of found papers
        """
        all_papers = []
        
        for keyword in keywords:
            self.logger.info(f"Starting search with keyword '{keyword}'")
            try:
                papers = self._search_single_keyword(keyword, max_results)
                all_papers.extend(papers)
                self.logger.info(f"Keyword '{keyword}': {len(papers)} papers found")
                
                # Respect API rate limits
                time.sleep(self.request_delay)
                
            except Exception as e:
                self.logger.error(f"Error searching keyword '{keyword}': {str(e)}")
                continue
        
        # Remove duplicates (based on PMID)
        unique_papers = {}
        for paper in all_papers:
            if paper.pmid not in unique_papers:
                unique_papers[paper.pmid] = paper
        
        result_papers = list(unique_papers.values())
        self.logger.info(f"Total {len(result_papers)} unique papers found")
        
        return result_papers
    
    def _search_single_keyword(self, keyword: str, max_results: int) -> List[PubMedPaper]:
        """
        Search papers with single keyword
        
        Args:
            keyword: Search keyword
            max_results: Maximum results
            
        Returns:
            List of found papers
        """
        # Step 1: Get PMID list with ESearch
        pmids = self._search_pmids(keyword, max_results)
        if not pmids:
            return []
        
        # Step 2: Get detailed information with EFetch
        papers = self._fetch_paper_details(pmids, keyword)
        
        # Step 3: Calculate keyword matching scores and filter
        filtered_papers = self._filter_and_score_papers(papers, keyword)
        
        return filtered_papers
    
    def _search_pmids(self, keyword: str, max_results: int) -> List[str]:
        """
        Search PMID list using ESearch API
        
        Args:
            keyword: Search keyword
            max_results: Maximum results
            
        Returns:
            List of PMIDs
        """
        # Build search query
        query = self._build_search_query(keyword)
        
        # Call ESearch API
        esearch_url = f"{self.base_url}esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml',
            'sort': 'relevance',
            'tool': self.tool_name,
            'email': self.email
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
        
        # Apply date filter
        if config and hasattr(config, 'FILTER_SETTINGS'):
            filter_settings = config.FILTER_SETTINGS
            if filter_settings:
                date_from = filter_settings.get('publication_date_from')
                date_to = filter_settings.get('publication_date_to')
                
                if date_from:
                    params['datetype'] = 'pdat'
                    params['mindate'] = date_from
                    if date_to:
                        params['maxdate'] = date_to
        
        try:
            response = self._make_request(esearch_url, params)
            pmids = self._parse_esearch_response(response)
            self.logger.debug(f"ESearch result: {len(pmids)} PMIDs")
            return pmids
            
        except Exception as e:
            self.logger.error(f"ESearch request failed: {str(e)}")
            return []
    
    def _build_search_query(self, keyword: str) -> str:
        """
        Build PubMed search query (including date filtering)
        
        Args:
            keyword: Base keyword
            
        Returns:
            PubMed search query
        """
        # Search broadly (all fields including title, abstract, keywords, MeSH terms)
        # Changed to [All Fields] for broader search
        base_query = f'{keyword}[All Fields]'
        
        # Apply additional filters
        filters = []
        
        if config and hasattr(config, 'FILTER_SETTINGS'):
            filter_settings = config.FILTER_SETTINGS
            if filter_settings:
                # Date filter (most important filter)
                date_from = filter_settings.get('publication_date_from')
                date_to = filter_settings.get('publication_date_to')
                
                if date_from:
                    # PubMed date format: YYYY/MM/DD
                    if date_to:
                        # Date range specification
                        date_filter = f'("{date_from}"[Publication Date] : "{date_to}"[Publication Date])'
                    else:
                        # From start date to current
                        from datetime import datetime
                        current_date = datetime.now().strftime("%Y/%m/%d")
                        date_filter = f'("{date_from}"[Publication Date] : "{current_date}"[Publication Date])'
                    
                    filters.append(date_filter)
                    self.logger.info(f"Date filter applied: {date_filter}")
                
                # Language filter
                if filter_settings.get('languages'):
                    lang_filter = ' OR '.join([f'"{lang}"[Language]' for lang in filter_settings['languages']])
                    filters.append(f'({lang_filter})')
                
                # Publication type filter (temporarily removed for testing)
                # if filter_settings.get('publication_types'):
                #     pub_types = filter_settings['publication_types']
                #     type_filter = ' OR '.join([f'"{pt}"[Publication Type]' for pt in pub_types])
                #     filters.append(f'({type_filter})')
        
        # Final query construction
        if filters:
            final_query = f'{base_query} AND {" AND ".join(filters)}'
        else:
            final_query = base_query
        
        self.logger.debug(f"Search query: {final_query}")
        return final_query
    
    def _fetch_paper_details(self, pmids: List[str], search_keyword: str) -> List[PubMedPaper]:
        """
        Fetch detailed paper information using EFetch API
        
        Args:
            pmids: List of PMIDs
            search_keyword: Search keyword
            
        Returns:
            List of detailed paper information
        """
        if not pmids:
            return []
        
        # Process PMIDs in chunks (maximum 200 at a time)
        chunk_size = 200
        all_papers = []
        
        for i in range(0, len(pmids), chunk_size):
            chunk_pmids = pmids[i:i + chunk_size]
            
            # Call EFetch API
            efetch_url = f"{self.base_url}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(chunk_pmids),
                'retmode': 'xml',
                'rettype': 'abstract',
                'tool': self.tool_name,
                'email': self.email
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            try:
                response = self._make_request(efetch_url, params)
                chunk_papers = self._parse_efetch_response(response, search_keyword)
                all_papers.extend(chunk_papers)
                
                # Respect API rate limits
                time.sleep(self.request_delay)
                
            except Exception as e:
                self.logger.error(f"EFetch request failed (PMID chunk {i//chunk_size + 1}): {str(e)}")
                continue
        
        return all_papers
    
    def _make_request(self, url: str, params: Dict[str, Any]) -> requests.Response:
        """
        Execute HTTP request (with retry logic)
        
        Args:
            url: Request URL
            params: Request parameters
            
        Returns:
            Response object
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt == self.max_retries - 1:
                    break
                
                wait_time = (2 ** attempt) * self.request_delay
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}), retrying in {wait_time} seconds: {str(e)}")
                time.sleep(wait_time)
        
        # Raise exception if all retries fail
        raise last_exception or requests.exceptions.RequestException("Unknown error")
    
    def _parse_esearch_response(self, response: requests.Response) -> List[str]:
        """
        Parse ESearch response
        
        Args:
            response: ESearch response
            
        Returns:
            List of PMIDs
        """
        try:
            # Log response content for debugging
            self.logger.debug(f"ESearch response content: {response.text[:1000]}...")
            
            root = ET.fromstring(response.text)
            pmids = []
            
            for id_elem in root.findall('.//IdList/Id'):
                pmid = id_elem.text
                if pmid:
                    pmids.append(pmid)
            
            # Debug log
            self.logger.debug(f"Parsed {len(pmids)} PMID(s)")
            if pmids:
                self.logger.debug(f"First PMID: {pmids[0]}")
            
            return pmids
            
        except ET.ParseError as e:
            self.logger.error(f"ESearch response parsing error: {str(e)}")
            return []
    
    def _parse_efetch_response(self, response: requests.Response, search_keyword: str) -> List[PubMedPaper]:
        """
        Parse EFetch response
        
        Args:
            response: EFetch response
            search_keyword: Search keyword
            
        Returns:
            List of paper information
        """
        try:
            root = ET.fromstring(response.text)
            papers = []
            
            for article in root.findall('.//PubmedArticle'):
                try:
                    paper = self._parse_single_article(article, search_keyword)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    self.logger.warning(f"Error parsing individual paper: {str(e)}")
                    continue
            
            return papers
            
        except ET.ParseError as e:
            self.logger.error(f"EFetch response parsing error: {str(e)}")
            return []
    
    def _parse_single_article(self, article_elem: ET.Element, search_keyword: str) -> Optional[PubMedPaper]:
        """
        Parse individual paper information
        
        Args:
            article_elem: Paper XML element
            search_keyword: Search keyword
            
        Returns:
            Paper information object
        """
        try:
            # Extract PMID
            pmid_elem = article_elem.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else ""
            
            # Extract title
            title_elem = article_elem.find('.//ArticleTitle')
            title = self._clean_text(title_elem.text if title_elem is not None and title_elem.text else "")
            
            # Extract abstract
            abstract_elems = article_elem.findall('.//Abstract/AbstractText')
            abstract_parts = []
            for abs_elem in abstract_elems:
                label = abs_elem.get('Label', '')
                text = abs_elem.text or ""
                if label:
                    abstract_parts.append(f"{label}: {text}")
                else:
                    abstract_parts.append(text)
            abstract = self._clean_text(" ".join(abstract_parts))
            
            # Extract authors
            authors = []
            author_elems = article_elem.findall('.//AuthorList/Author')
            for author_elem in author_elems:
                last_name = author_elem.find('LastName')
                first_name = author_elem.find('ForeName')
                if last_name is not None and first_name is not None:
                    last_name_text = last_name.text or ""
                    first_name_text = first_name.text or ""
                    if last_name_text and first_name_text:
                        authors.append(f"{first_name_text} {last_name_text}")
            
            # Extract journal information
            journal_elem = article_elem.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None and journal_elem.text else ""
            
            # Extract publication date
            pub_date = self._extract_publication_date(article_elem)
            
            # Extract DOI
            doi = ""
            doi_elems = article_elem.findall('.//ArticleId')
            for doi_elem in doi_elems:
                if doi_elem.get('IdType') == 'doi':
                    doi = doi_elem.text or ""
                    break
            
            # Extract PMC ID
            pmc_id = ""
            for pmc_elem in doi_elems:
                if pmc_elem.get('IdType') == 'pmc':
                    pmc_id = pmc_elem.text or ""
                    break
            
            # Extract MeSH terms
            mesh_terms = []
            mesh_elems = article_elem.findall('.//MeshHeadingList/MeshHeading/DescriptorName')
            for mesh_elem in mesh_elems:
                mesh_text = mesh_elem.text
                if mesh_text:
                    mesh_terms.append(mesh_text)
            
            # Extract keywords
            keywords = []
            keyword_elems = article_elem.findall('.//KeywordList/Keyword')
            for keyword_elem in keyword_elems:
                keyword_text = keyword_elem.text
                if keyword_text:
                    keywords.append(keyword_text)
            
            # Extract publication type
            pub_type_elems = article_elem.findall('.//PublicationType')
            pub_types = [pt.text for pt in pub_type_elems if pt.text]
            publication_type = ", ".join(pub_types) if pub_types else ""
            
            # Extract language
            language_elem = article_elem.find('.//Language')
            language = language_elem.text if language_elem is not None and language_elem.text else "eng"
            
            # Extract grants
            grants = []
            grant_elems = article_elem.findall('.//GrantList/Grant/GrantID')
            for grant_elem in grant_elems:
                grant_text = grant_elem.text
                if grant_text:
                    grants.append(grant_text)
            
            # Validate required fields
            if not pmid or not title:
                return None
            
            # Check abstract length
            if config and hasattr(config, 'FILTER_SETTINGS'):
                filter_settings = config.FILTER_SETTINGS
                if filter_settings:
                    min_abstract_length = filter_settings.get('min_abstract_length', 0)
                    if len(abstract) < min_abstract_length:
                        return None
            
            # Create PubMedPaper object
            paper = PubMedPaper(
                pmid=pmid,
                title=title,
                authors=authors,
                abstract=abstract,
                journal=journal,
                pub_date=pub_date,
                doi=doi,
                pmc_id=pmc_id,
                keywords=keywords,
                mesh_terms=mesh_terms,
                publication_type=publication_type,
                language=language,
                grants=grants,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                collection_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                search_keyword=search_keyword,
                keyword_score=0.0,  # Calculate later
                korean_summary="",  # Generate later
                relevance_category=""  # Set later
            )
            
            return paper
            
        except Exception as e:
            self.logger.error(f"Error parsing paper: {str(e)}")
            return None
    
    def _extract_publication_date(self, article_elem: ET.Element) -> str:
        """
        Extract publication date
        
        Args:
            article_elem: Paper XML element
            
        Returns:
            Publication date string
        """
        # Extract date from PubDate element
        pub_date_elem = article_elem.find('.//PubDate')
        if pub_date_elem is not None:
            year_elem = pub_date_elem.find('Year')
            month_elem = pub_date_elem.find('Month')
            day_elem = pub_date_elem.find('Day')
            
            year = year_elem.text if year_elem is not None else ""
            month = month_elem.text if month_elem is not None else ""
            day = day_elem.text if day_elem is not None else ""
            
            # Convert month name to number
            month_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            
            if month and month in month_map:
                month = month_map[month]
            elif month and month.isdigit():
                month = month.zfill(2)
            
            if day and day.isdigit():
                day = day.zfill(2)
            
            if year:
                if month and day:
                    return f"{year}-{month}-{day}"
                elif month:
                    return f"{year}-{month}"
                else:
                    return year
        
        return ""
    
    def _filter_and_score_papers(self, papers: List[PubMedPaper], search_keyword: str) -> List[PubMedPaper]:
        """
        Filter papers and calculate keyword matching scores (including date filtering)
        
        Args:
            papers: List of papers
            search_keyword: Search keyword
            
        Returns:
            Filtered list of papers
        """
        filtered_papers = []
        threshold = getattr(config, 'KEYWORD_MATCH_THRESHOLD', 0.0)
        
        for paper in papers:
            # Check date filter
            if not self._check_date_filter(paper):
                continue  # Exclude if date condition is not met
            
            # Check required keywords
            if not self._check_required_keywords(paper):
                continue  # Exclude if required keywords are missing
            
            # Calculate keyword matching score
            score = self._calculate_keyword_score(paper, search_keyword)
            paper.keyword_score = score
            
            # Set relevance category
            paper.relevance_category = self._categorize_paper(score, paper)
            
            # Generate Korean summary
            paper.korean_summary = self._generate_korean_summary(paper)
            
            # Include only papers above threshold
            if score >= threshold:
                filtered_papers.append(paper)
        
        # Sort by score
        filtered_papers.sort(key=lambda x: x.keyword_score, reverse=True)
        
        return filtered_papers
    
    def _check_date_filter(self, paper: PubMedPaper) -> bool:
        """
        Check if the publication date of the paper falls within the set date range
        
        Args:
            paper: Paper information
            
        Returns:
            Whether date condition is met
        """
        if not config or not hasattr(config, 'FILTER_SETTINGS'):
            return True
        
        filter_settings = config.FILTER_SETTINGS
        if not filter_settings:
            return True
        
        date_from = filter_settings.get('publication_date_from')
        date_to = filter_settings.get('publication_date_to')
        
        if not date_from:
            return True  # No date filter set, allow all papers
        
        # Parse paper's publication date
        paper_date = paper.pub_date
        if not paper_date:
            return True  # No publication date, allow
        
        try:
            from datetime import datetime
            
            # Convert paper publication date to datetime object
            if len(paper_date) == 10:  # YYYY-MM-DD format
                paper_datetime = datetime.strptime(paper_date, "%Y-%m-%d")
            elif len(paper_date) == 7:  # YYYY-MM format
                paper_datetime = datetime.strptime(paper_date, "%Y-%m")
            elif len(paper_date) == 4:  # YYYY format
                paper_datetime = datetime.strptime(paper_date, "%Y")
            else:
                return True  # Cannot determine format, allow
            
            # Convert filter dates to datetime objects
            date_from_datetime = datetime.strptime(date_from, "%Y/%m/%d")
            
            # Compare dates
            if paper_datetime < date_from_datetime:
                self.logger.debug(f"Paper {paper.pmid} date filtering: {paper_date} < {date_from}")
                return False
            
            if date_to:
                date_to_datetime = datetime.strptime(date_to, "%Y/%m/%d")
                if paper_datetime > date_to_datetime:
                    self.logger.debug(f"Paper {paper.pmid} date filtering: {paper_date} > {date_to}")
                    return False
            
            return True
            
        except ValueError as e:
            self.logger.warning(f"Paper {paper.pmid} date parsing error: {paper_date}, {str(e)}")
            return True  # Allow on parsing error
    
    def _check_required_keywords(self, paper: PubMedPaper) -> bool:
        """
        Check if all required keywords are included
        
        Args:
            paper: Paper information
            
        Returns:
            Whether all required keywords are included
        """
        required_keywords = getattr(config, 'REQUIRED_KEYWORDS', [])
        if not required_keywords:
            return True  # No required keywords set, allow all papers
        
        # Combine all text from the paper (lowercase)
        all_text = " ".join([
            paper.title,
            paper.abstract,
            " ".join(paper.keywords),
            " ".join(paper.mesh_terms)
        ]).lower()
        
        # Check if all required keywords are included
        for required_keyword in required_keywords:
            if required_keyword.lower() not in all_text:
                return False
        
        return True
    
    def _generate_korean_summary(self, paper: PubMedPaper) -> str:
        """
        Generate Korean summary for the paper
        
        Args:
            paper: Paper information
            
        Returns:
            Korean summary string
        """
        if not getattr(config, 'ENABLE_KOREAN_SUMMARY', True):
            return ""
        
        max_length = getattr(config, 'SUMMARY_MAX_LENGTH', 150)
        
        # Generate simple keyword-based summary
        title = paper.title.lower()
        abstract = paper.abstract.lower()
        
        # Translate important keywords and Korean
        keyword_translations = {
            "breast cancer": "Breast Cancer",
            "cancer": "Cancer",
            "tumor": "Tumor", 
            "mutation": "Mutation",
            "sequencing": "Sequencing",
            "genomics": "Genomics",
            "genome": "Genome",
            "gene": "Gene",
            "therapy": "Therapy",
            "treatment": "Treatment",
            "diagnosis": "Diagnosis",
            "prognosis": "Prognosis",
            "biomarker": "Biomarker",
            "evolution": "Evolution",
            "clonal": "Clonal",
            "structural variation": "Structural Variation",
            "copy number": "Copy Number",
            "somatic": "Somatic",
            "germline": "Germline",
            "whole genome": "Whole Genome",
            "duplication": "Duplication",
            "analysis": "Analysis",
            "study": "Study",
            "patient": "Patient"
        }
        
        # Generate summary
        summary_parts = []
        
        # Determine research topic
        if "breast cancer" in title:
            summary_parts.append("Breast Cancer")
        elif "cancer" in title:
            summary_parts.append("Cancer")
            
        # Determine research method
        if "sequencing" in title or "sequencing" in abstract:
            summary_parts.append("Sequencing")
        if "genomics" in title or "genomic" in title:
            summary_parts.append("Genomics")
        if "mutation" in title or "mutation" in abstract:
            summary_parts.append("Mutation")
            
        # Determine research purpose
        research_purpose = ""
        if "treatment" in abstract or "therapy" in abstract:
            research_purpose = "Treatment Method"
        elif "diagnosis" in abstract:
            research_purpose = "Diagnosis Method"
        elif "analysis" in title or "analysis" in abstract:
            research_purpose = "Analysis"
        elif "study" in title:
            research_purpose = "Study"
            
        # Generate summary sentence
        if summary_parts:
            base_summary = f"This study is about {', '.join(summary_parts)}."
            if research_purpose:
                base_summary += f" {research_purpose} "
            base_summary += "research."
        else:
            base_summary = "A research paper in the field of medicine and life sciences."
            
        # Add additional information
        additional_info = []
        
        if "patient" in abstract:
            additional_info.append("Utilized patient data")
        if "clinical" in abstract:
            additional_info.append("Clinical study")
        if "genomic" in abstract or "genetic" in abstract:
            additional_info.append("Genetic approach")
        if "therapeutic" in abstract:
            additional_info.append("Therapeutic approach")
            
        if additional_info:
            base_summary += f" Providing new insights through {', '.join(additional_info)}."
            
        # Truncate length
        if len(base_summary) > max_length:
            base_summary = base_summary[:max_length-3] + "..."
            
        return base_summary
    
    def _categorize_paper(self, score: float, paper: PubMedPaper) -> str:
        """
        Categorize paper based on score (applying advanced journal priority)
        
        Args:
            score: Keyword matching score
            paper: Paper information
            
        Returns:
            Category (high/medium/low)
        """
        # Check for high-impact journals (Nature, Cell, Science, etc.)
        high_impact_journals = getattr(config, 'HIGH_IMPACT_JOURNALS', [])
        if high_impact_journals and paper.journal:
            journal_lower = paper.journal.lower()
            for high_journal in high_impact_journals:
                if high_journal.lower() in journal_lower:
                    self.logger.info(f"Paper published in high-impact journal {paper.journal} - automatically categorized as high relevance")
                    return "high"
        
        # General score-based categorization
        thresholds = getattr(config, 'SCORE_THRESHOLDS', {
            "high": 0.7, "medium": 0.4, "low": 0.0
        })
        
        if score >= thresholds["high"]:
            return "high"
        elif score >= thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _calculate_keyword_score(self, paper: PubMedPaper, search_keyword: str) -> float:
        """
        Calculate keyword matching score (based on required keywords + priority keywords)
        
        Args:
            paper: Paper information
            search_keyword: Search keyword
            
        Returns:
            Matching score (0.0 ~ 1.0)
        """
        # Combine all text from the paper
        title_lower = paper.title.lower()
        abstract_lower = paper.abstract.lower()
        keywords_lower = " ".join(paper.keywords).lower()
        mesh_lower = " ".join(paper.mesh_terms).lower()
        all_text = " ".join([title_lower, abstract_lower, keywords_lower, mesh_lower])
        
        # Basic score (keyword matching)
        search_words = search_keyword.lower().split()
        base_score = self._calculate_text_score(all_text, search_words)
        
        # Required keyword score
        required_keywords = getattr(config, 'REQUIRED_KEYWORDS', [])
        required_weight = getattr(config, 'REQUIRED_KEYWORD_WEIGHT', 1.0)
        required_score = 0.0
        if required_keywords:
            required_matches = sum(1 for keyword in required_keywords 
                                 if keyword.lower() in all_text)
            required_score = (required_matches / len(required_keywords)) * required_weight
        
        # Priority keyword score
        priority_keywords = getattr(config, 'PRIORITY_KEYWORDS', [])
        priority_weight = getattr(config, 'PRIORITY_KEYWORD_WEIGHT', 2.0)
        priority_score = 0.0
        if priority_keywords:
            priority_matches = sum(1 for keyword in priority_keywords 
                                 if keyword.lower() in all_text)
            priority_score = (priority_matches / len(priority_keywords)) * priority_weight
        
        # Apply field-specific weights
        title_bonus = 0.0
        abstract_bonus = 0.0
        
        # Add bonus if important keywords are in the title
        for keyword in required_keywords + priority_keywords:
            if keyword.lower() in title_lower:
                title_bonus += 0.5
        
        # Add bonus if important keywords are in the abstract
        for keyword in required_keywords + priority_keywords:
            if keyword.lower() in abstract_lower:
                abstract_bonus += 0.2
        
        # Final score calculation
        total_score = base_score + required_score + priority_score + title_bonus + abstract_bonus
        
        # Normalize score (0.0 ~ 1.0)
        return min(total_score / 5.0, 1.0)  # Normalize by max score
    
    def _calculate_text_score(self, text: str, keywords: List[str]) -> float:
        """
        Calculate keyword matching score from text
        
        Args:
            text: Text to analyze
            keywords: List of keywords
            
        Returns:
            Matching score
        """
        if not text or not keywords:
            return 0.0
        
        matches = 0
        for keyword in keywords:
            if keyword in text:
                matches += 1
        
        return matches / len(keywords)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text (remove HTML tags, etc.)
        
        Args:
            text: Original text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove consecutive spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def paper_to_dict(self, paper: PubMedPaper) -> dict:
        """
        Convert PubMedPaper object to Dictionary
        
        Args:
            paper: PubMedPaper object
            
        Returns:
            Dictionary of paper data
        """
        return {
            'title': paper.title,
            'authors': ', '.join(paper.authors),
            'journal': paper.journal,
            'pub_date': paper.pub_date,
            'doi': paper.doi,
            'pmid': paper.pmid,
            'pmc_id': paper.pmc_id,
            'keywords': ', '.join(paper.keywords),
            'abstract': paper.abstract,
            'collection_date': paper.collection_date,
            'search_keyword': paper.search_keyword,
            'keyword_score': paper.keyword_score,
            'language': paper.language,
            'publication_type': paper.publication_type,
            'mesh_terms': ', '.join(paper.mesh_terms),
            'grants': ', '.join(paper.grants),
            'korean_summary': paper.korean_summary,
            'relevance_category': paper.relevance_category
        }

# Example usage
if __name__ == "__main__":
    # Logging settings
    logging.basicConfig(level=logging.INFO)
    
    # Create scraper
    scraper = PubMedScraper()
    
    # Test search
    test_keywords = ["machine learning", "artificial intelligence"]
    papers = scraper.search_papers(test_keywords, max_results=5)
    
    print(f"Total {len(papers)} papers found.")
    for i, paper in enumerate(papers[:3], 1):
        print(f"\n{i}. {paper.title}")
        print(f"    Authors: {', '.join(paper.authors[:3])}")
        print(f"    Journal: {paper.journal}")
        print(f"   PMID: {paper.pmid}")
        print(f"    Keyword Score: {paper.keyword_score:.2f}") 