"""
Paper scraper scheduler module
Regularly collect and save papers using PubMed API
"""

import schedule
import time
import threading
import logging
from datetime import datetime
from typing import List, Optional

# Local module imports
from modules.pubmed_scraper import PubMedScraper
from modules.markdown_saver import MarkdownSaver
import config

class PaperScrapperScheduler:
    """Paper scraper scheduler"""
    
    def __init__(self):
        """Initialize scheduler"""
        self.logger = logging.getLogger(__name__)
        self.scraper = PubMedScraper()
        self.markdown_saver = MarkdownSaver()
        self.is_running = False
        self.scheduler_thread = None
        
        # Load configuration
        self.schedule_enabled = getattr(config, 'SCHEDULE_ENABLED', True)
        self.schedule_time = getattr(config, 'SCHEDULE_TIME', "09:00")
        self.schedule_days = getattr(config, 'SCHEDULE_DAYS', ["sunday"])
        self.search_keywords = getattr(config, 'SEARCH_KEYWORDS', ["machine learning"])
        self.max_results = getattr(config, 'MAX_RESULTS_PER_SEARCH', 50)
        
        self.logger.info("Paper scraper scheduler initialized")
    
    def setup_schedule(self):
        """Setup schedule"""
        if not self.schedule_enabled:
            self.logger.info("Scheduling is disabled")
            return
        
        # Clear existing schedule
        schedule.clear()
        
        # Set schedule for each day
        for day in self.schedule_days:
            day_lower = day.lower()
            
            if day_lower == "monday":
                schedule.every().monday.at(self.schedule_time).do(self.run_scraping_job)
            elif day_lower == "tuesday":
                schedule.every().tuesday.at(self.schedule_time).do(self.run_scraping_job)
            elif day_lower == "wednesday":
                schedule.every().wednesday.at(self.schedule_time).do(self.run_scraping_job)
            elif day_lower == "thursday":
                schedule.every().thursday.at(self.schedule_time).do(self.run_scraping_job)
            elif day_lower == "friday":
                schedule.every().friday.at(self.schedule_time).do(self.run_scraping_job)
            elif day_lower == "saturday":
                schedule.every().saturday.at(self.schedule_time).do(self.run_scraping_job)
            elif day_lower == "sunday":
                schedule.every().sunday.at(self.schedule_time).do(self.run_scraping_job)
            else:
                self.logger.warning(f"Unknown day: {day}")
        
        self.logger.info(f"Schedule setup complete: {', '.join(self.schedule_days)} {self.schedule_time}")
    
    def run_scraping_job(self):
        """Execute scraping job"""
        self.logger.info("Scheduled paper collection job started")
        start_time = datetime.now()
        
        try:
            # Search papers
            self.logger.info(f"Searching papers with keywords: {self.search_keywords}")
            papers = self.scraper.search_papers(self.search_keywords, self.max_results)
            
            if not papers:
                self.logger.warning("No papers found")
                return
            
            # Save as markdown files
            self.logger.info(f"Saving {len(papers)} papers to markdown...")
            saved_count = 0
            
            for paper in papers:
                try:
                    # Convert paper info to dictionary
                    paper_data = {
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
                        'keyword_score': f"{paper.keyword_score:.2f}",
                        'relevance_category': paper.relevance_category,
                        'korean_summary': paper.korean_summary,
                        'language': paper.language,
                        'publication_type': paper.publication_type,
                        'mesh_terms': ', '.join(paper.mesh_terms),
                        'grants': ', '.join(paper.grants)
                    }
                    
                    # Save markdown file
                    success = self.markdown_saver.save_paper(paper_data)
                    if success:
                        saved_count += 1
                        
                except Exception as e:
                    self.logger.error(f"Error saving paper (PMID: {paper.pmid}): {str(e)}")
                    continue
            
            # Log execution results
            end_time = datetime.now()
            duration = end_time - start_time
            
            self.logger.info(f"Paper collection job completed:")
            self.logger.info(f"- Papers found: {len(papers)}")
            self.logger.info(f"- Papers saved: {saved_count}")
            self.logger.info(f"- Duration: {duration.total_seconds():.2f} seconds")
            
        except Exception as e:
            self.logger.error(f"Error during scraping job: {str(e)}")
    
    def start_scheduler(self):
        """Start scheduler"""
        if not self.schedule_enabled:
            self.logger.info("Scheduling is disabled")
            return
        
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.setup_schedule()
        self.is_running = True
        
        # Run scheduler in separate thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Scheduler started")
    
    def stop_scheduler(self):
        """Stop scheduler"""
        if not self.is_running:
            self.logger.info("Scheduler is not running")
            return
        
        self.is_running = False
        schedule.clear()
        
        # Wait for thread to finish
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Scheduler stopped")
    
    def _scheduler_loop(self):
        """Scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check schedule every minute
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {str(e)}")
                time.sleep(60)
    
    def run_once(self):
        """Run once"""
        self.logger.info("One-time paper collection job execution")
        self.run_scraping_job()
    
    def get_next_run_time(self) -> Optional[str]:
        """Get next run time"""
        if not self.schedule_enabled or not schedule.jobs:
            return None
        
        try:
            next_run = schedule.next_run()
            if next_run:
                return next_run.strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass
        
        return None
    
    def get_schedule_info(self) -> dict:
        """Get schedule information"""
        return {
            'enabled': self.schedule_enabled,
            'time': self.schedule_time,
            'days': self.schedule_days,
            'keywords': self.search_keywords,
            'max_results': self.max_results,
            'is_running': self.is_running,
            'next_run': self.get_next_run_time(),
            'job_count': len(schedule.jobs)
        }

# Usage example
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run scheduler
    scheduler = PaperScrapperScheduler()
    
    print("Scheduler information:")
    info = scheduler.get_schedule_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # One-time execution test
    print("\nOne-time execution test...")
    scheduler.run_once() 