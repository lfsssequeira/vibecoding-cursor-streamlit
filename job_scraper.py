#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import sys
import time

def scrape_bamboohr_jobs():
    """Scrape jobs from BambooHR careers page."""
    url = "https://people.bamboohr.com/careers"
    
    print("Fetching BambooHR careers page...")
    
    try:
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for job listings - common selectors for job boards
        jobs = []
        
        # Try different selectors that BambooHR might use
        job_selectors = [
            '.jss-g13',             # The specific class for job links (most specific)
            'a[href*="/careers/"]', # BambooHR uses /careers/ not /jobs/
            '.fabric-5qovnk-root',  # The container div class
            '#js-careers-root main section ul li div',  # The specific path you found
            'main section ul li div',                   # Simplified version
            'ul li div',                               # Even more simplified
            'a[href*="/jobs/"]',
            '.job-title',
            '.position-title', 
            '[data-testid*="job"]',
            'h3 a',
            'h4 a',
            '.job-listing a'
        ]
        
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} jobs using selector: {selector}")
                break
        
        if not elements:
            # Fallback: look for any links that might be jobs
            elements = soup.find_all('a', href=True)
            elements = [e for e in elements if any(word in e.get_text().lower() 
                      for word in ['engineer', 'developer', 'manager', 'analyst', 'coordinator'])]
            print(f"Fallback: found {len(elements)} potential job links")
        
        # Extract job info
        for i, element in enumerate(elements[:15]):  # Get more than 10 to filter
            try:
                # If element is already a link (like .jss-g13), use it directly
                if element.name == 'a' and element.get('href'):
                    job_link = element
                else:
                    # Look for the job link within this element
                    job_link = element.find('a', href=True)
                    if not job_link:
                        continue
                        
                title = job_link.get_text().strip()
                link = job_link.get('href', '')
                
                # Make sure it's a job link
                if not title or len(title) < 3:
                    continue
                    
                # Clean up the link
                if link.startswith('/'):
                    link = f"https://people.bamboohr.com{link}"
                elif not link.startswith('http'):
                    continue
                    
                # Skip non-job links
                if not any(word in link.lower() for word in ['/careers/', '/jobs/']):
                    continue
                
                jobs.append({
                    'title': title,
                    'link': link,
                    'rank': len(jobs) + 1
                })
                
            except Exception as e:
                print(f"Error processing job {i}: {e}")
                continue
        
        return jobs[:10]  # Return top 10
        
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return []
    except Exception as e:
        print(f"Error parsing page: {e}")
        return []

def display_jobs(jobs):
    """Display the job list nicely."""
    if not jobs:
        print("No jobs found!")
        return
    
    print(f"\n🏢 Top {len(jobs)} BambooHR Jobs:")
    print("=" * 50)
    
    for job in jobs:
        print(f"{job['rank']}. {job['title']}")
        print(f"   🔗 {job['link']}")
        print()

def main():
    print("BambooHR Job Scraper")
    print("=" * 30)
    
    jobs = scrape_bamboohr_jobs()
    display_jobs(jobs)
    
    if jobs:
        print(f"✅ Found {len(jobs)} jobs successfully!")
    else:
        print("❌ No jobs found. The page structure might have changed.")

if __name__ == "__main__":
    main()
