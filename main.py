#!/usr/bin/env python3
"""
Paper Surfer - PubMed API-based automatic paper collection tool
Search for papers using PubMed API and save them in markdown format based on keywords
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import List, Dict, Optional

# Logging setup
def setup_logging():
    """Setup logging configuration"""
    try:
        import config
        log_file = getattr(config, 'LOG_FILE', './logs/pubmed_scraper.log')
        log_level = getattr(config, 'LOG_LEVEL', 'INFO')
        log_format = getattr(config, 'LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_date_format = getattr(config, 'LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
    except ImportError:
        log_file = './logs/pubmed_scraper.log'
        log_level = 'INFO'
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_date_format = '%Y-%m-%d %H:%M:%S'
    
    # Create log directory
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=log_date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

# Import settings and modules
try:
    import config
    setup_logging()
    
    from modules.pubmed_scraper import PubMedScraper
    from modules.markdown_saver import MarkdownSaver
    from modules.scheduler import PaperScrapperScheduler
    
    logger = logging.getLogger(__name__)
    logger.info("Paper Surfer started - PubMed API version")
    
except ImportError as e:
    print(f"Module import error: {e}")
    print("Please install required packages: pip install -r requirements.txt")
    sys.exit(1)

def display_banner():
    """Display program banner"""
    banner = """
    ====================================================
    🔬 Paper Surfer - PubMed API-based Paper Collection Tool
    ====================================================
    
    ✨ Key Features:
    • Reliable paper search using PubMed API
    • Keyword-based relevance analysis
    • Automatic saving in markdown format
    • Automatic scheduling functionality
    
    📧 Contact: {contact_email}
    ====================================================
    """.format(
        contact_email=getattr(config, 'CONTACT_EMAIL', 'your.email@example.com')
    )
    print(banner)

def run_interactive_mode():
    """Run interactive mode"""
    print("\n🔍 Interactive Paper Collection Mode")
    print("=" * 50)
    
    # Get user input
    print("\nSearch Settings:")
    
    # Keyword input
    print(f"Default keywords: {', '.join(config.SEARCH_KEYWORDS)}")
    custom_keywords = input("Enter custom keywords (comma-separated, press Enter for defaults): ").strip()
    
    if custom_keywords:
        keywords = [k.strip() for k in custom_keywords.split(',') if k.strip()]
    else:
        keywords = config.SEARCH_KEYWORDS
    
    # Maximum results input
    default_max_results = getattr(config, 'MAX_RESULTS_PER_SEARCH', 50)
    max_results_input = input(f"Maximum results (default: {default_max_results}): ").strip()
    
    try:
        max_results = int(max_results_input) if max_results_input else default_max_results
    except ValueError:
        max_results = default_max_results
        print(f"Invalid input, using default: {default_max_results}")
    
    # Execute search
    print(f"\n🔍 Starting search...")
    print(f"Keywords: {', '.join(keywords)}")
    print(f"Maximum results: {max_results}")
    
    try:
        # Initialize scraper and saver
        scraper = PubMedScraper()
        saver = MarkdownSaver()
        
        # Search papers
        papers = scraper.search_papers(keywords, max_results)
        
        if not papers:
            print("❌ No search results found.")
            return
        
        print(f"\n✅ Found {len(papers)} papers.")
        
        # Preview top 5 papers
        print("\n📄 Top 5 papers preview:")
        print("-" * 80)
        
        for i, paper in enumerate(papers[:5], 1):
            # Category emoji based on relevance
            category_emoji = {
                "high": "🔥",
                "medium": "📊", 
                "low": "📄"
            }
            emoji = category_emoji.get(paper.relevance_category, "📄")
            
            print(f"{i}. {emoji} {paper.title[:60]}...")
            print(f"   Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
            print(f"   Journal: {paper.journal}")
            print(f"   Score: {paper.keyword_score:.2f} | Category: {paper.relevance_category}")
            print(f"   PMID: {paper.pmid}")
            if paper.korean_summary:
                print(f"   Summary: {paper.korean_summary[:80]}...")
            print()
        
        # Save confirmation
        save_confirm = input("Do you want to save these papers to markdown files? (y/n): ").strip().lower()
        
        if save_confirm == 'y':
            print("\n💾 Saving papers...")
            
            saved_count = 0
            for paper in papers:
                try:
                    # Convert paper info to dictionary (using new method)
                    paper_data = scraper.paper_to_dict(paper)
                    
                    # Save markdown file
                    success = saver.save_paper(paper_data)
                    if success:
                        saved_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to save paper (PMID: {paper.pmid}): {e}")
                    continue
            
            print(f"✅ Total {saved_count} papers saved.")
            
            # Category statistics
            category_counts = {"high": 0, "medium": 0, "low": 0}
            for paper in papers:
                if paper.relevance_category in category_counts:
                    category_counts[paper.relevance_category] += 1
            
            print(f"\n📊 Category classification:")
            print(f"🔥 High relevance: {category_counts['high']} papers")
            print(f"📊 Medium relevance: {category_counts['medium']} papers") 
            print(f"📄 Low relevance: {category_counts['low']} papers")
            
            # Saved file information
            files_info = saver.get_saved_files_info()
            print(f"\n📁 Save location: {files_info['output_directory']}")
            print(f"📄 Saved files: {files_info['total_files']}")
            
        else:
            print("❌ Save cancelled.")
            
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"Interactive mode execution error: {e}")
        print(f"❌ Error occurred: {e}")

def run_once_mode():
    """Run once mode"""
    print("\n🚀 One-time Execution Mode")
    print("=" * 50)
    
    try:
        # Display configuration values
        print(f"Search keywords: {', '.join(config.SEARCH_KEYWORDS)}")
        print(f"Maximum results: {getattr(config, 'MAX_RESULTS_PER_SEARCH', 50)}")
        print(f"API key configured: {'Yes' if getattr(config, 'PUBMED_API_KEY', None) else 'No'}")
        
        # Initialize scraper and saver
        scraper = PubMedScraper()
        saver = MarkdownSaver()
        
        # Search papers
        print("\n🔍 Searching papers...")
        papers = scraper.search_papers(
            config.SEARCH_KEYWORDS, 
            getattr(config, 'MAX_RESULTS_PER_SEARCH', 50)
        )
        
        if not papers:
            print("❌ No search results found.")
            return
        
        print(f"✅ Found {len(papers)} papers.")
        
        # Save papers
        print("\n💾 Saving papers...")
        saved_count = 0
        
        for paper in papers:
            try:
                # Convert paper info to dictionary (using new method)
                paper_data = scraper.paper_to_dict(paper)
                
                # Save markdown file
                success = saver.save_paper(paper_data)
                if success:
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to save paper (PMID: {paper.pmid}): {e}")
                continue
        
        print(f"✅ Total {saved_count} papers saved.")
        
        # Category statistics
        category_counts = {"high": 0, "medium": 0, "low": 0}
        for paper in papers:
            if paper.relevance_category in category_counts:
                category_counts[paper.relevance_category] += 1
        
        print(f"\n📊 Category classification:")
        print(f"🔥 High relevance: {category_counts['high']} papers")
        print(f"📊 Medium relevance: {category_counts['medium']} papers") 
        print(f"📄 Low relevance: {category_counts['low']} papers")
        
        # Saved file information
        files_info = saver.get_saved_files_info()
        print(f"\n📁 Save location: {files_info['output_directory']}")
        print(f"📄 Saved files: {files_info['total_files']}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"One-time execution error: {e}")
        print(f"❌ Error occurred: {e}")

def run_scheduler_mode():
    """Run scheduler mode"""
    print("\n⏰ Scheduler Mode")
    print("=" * 50)
    
    try:
        # Initialize scheduler
        scheduler = PaperScrapperScheduler()
        
        # Display schedule information
        schedule_info = scheduler.get_schedule_info()
        print(f"Schedule enabled: {schedule_info['enabled']}")
        print(f"Execution time: {schedule_info['time']}")
        print(f"Execution days: {', '.join(schedule_info['days'])}")
        print(f"Search keywords: {', '.join(schedule_info['keywords'])}")
        print(f"Maximum results: {schedule_info['max_results']}")
        
        if schedule_info['next_run']:
            print(f"Next execution: {schedule_info['next_run']}")
        
        if not schedule_info['enabled']:
            print("⚠️  Scheduling is disabled.")
            return
        
        # Start scheduler
        print("\n🚀 Starting scheduler...")
        print("Press Ctrl+C to stop.")
        
        scheduler.start_scheduler()
        
        # Main loop
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        finally:
            scheduler.stop_scheduler()
            print("✅ Scheduler stopped safely.")
            
    except Exception as e:
        logger.error(f"Scheduler mode execution error: {e}")
        print(f"❌ Error occurred: {e}")

def show_status():
    """Display system status"""
    print("\n📊 System Status")
    print("=" * 50)
    
    try:
        # Configuration information
        print("📋 Configuration:")
        print(f"  - PubMed API key: {'Set' if getattr(config, 'PUBMED_API_KEY', None) else 'Not set'}")
        print(f"  - Contact email: {getattr(config, 'CONTACT_EMAIL', 'your.email@example.com')}")
        print(f"  - Search keywords: {len(config.SEARCH_KEYWORDS)} keywords")
        print(f"  - Maximum results: {getattr(config, 'MAX_RESULTS_PER_SEARCH', 50)}")
        
        # Output directory information
        output_dir = getattr(config, 'MARKDOWN_OUTPUT_DIR', './output/papers')
        print(f"\n📁 Output directory: {output_dir}")
        
        if os.path.exists(output_dir):
            # Count files
            total_files = 0
            md_files = 0
            for root, dirs, files in os.walk(output_dir):
                total_files += len(files)
                md_files += len([f for f in files if f.endswith('.md')])
            
            print(f"  - Total files: {total_files}")
            print(f"  - Markdown files: {md_files}")
        else:
            print("  - Directory not yet created.")
        
        # Scheduler information
        try:
            scheduler = PaperScrapperScheduler()
            schedule_info = scheduler.get_schedule_info()
            
            print(f"\n⏰ Scheduler information:")
            print(f"  - Enabled: {schedule_info['enabled']}")
            print(f"  - Execution time: {schedule_info['time']}")
            print(f"  - Execution days: {', '.join(schedule_info['days'])}")
            print(f"  - Running: {schedule_info['is_running']}")
            
            if schedule_info['next_run']:
                print(f"  - Next execution: {schedule_info['next_run']}")
                
        except Exception as e:
            print(f"  - Failed to load scheduler info: {e}")
            
    except Exception as e:
        print(f"❌ Failed to load status information: {e}")

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="PubMed API-based automatic paper collection tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python main.py                     # Interactive mode
  python main.py --interactive       # Interactive mode (explicit)
  python main.py --once              # One-time execution
  python main.py --scheduler         # Scheduler mode
  python main.py --status            # Status check
        """
    )
    
    parser.add_argument(
        '--interactive', '-i', 
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--once', '-o',
        action='store_true', 
        help='Run once (based on config file)'
    )
    
    parser.add_argument(
        '--scheduler', '-s',
        action='store_true',
        help='Run in scheduler mode'
    )
    
    parser.add_argument(
        '--status', '-st',
        action='store_true',
        help='Check system status'
    )
    
    args = parser.parse_args()
    
    # Display banner
    display_banner()
    
    # Select and run mode
    if args.once:
        run_once_mode()
    elif args.scheduler:
        run_scheduler_mode()
    elif args.status:
        show_status()
    elif args.interactive:
        run_interactive_mode()
    else:
        # Default: interactive mode
        run_interactive_mode()

if __name__ == "__main__":
    main() 