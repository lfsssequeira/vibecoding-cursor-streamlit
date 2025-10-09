#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import sys

def scrape_bamboohr_jobs_selenium():
    """Scrape jobs from BambooHR careers page using Selenium for dynamic content."""
    url = "https://people.bamboohr.com/careers"
    
    print("Setting up browser...")
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        # Initialize Chrome driver (will use Chrome from /Applications)
        driver = webdriver.Chrome(options=chrome_options)
        
        print("Loading BambooHR careers page...")
        driver.get(url)
        
        # Wait for jobs to load (up to 10 seconds)
        print("Waiting for jobs to load...")
        wait = WebDriverWait(driver, 10)
        
        # Wait for the careers root element
        wait.until(EC.presence_of_element_located((By.ID, "js-careers-root")))
        
        # Wait a bit more for dynamic content
        time.sleep(3)
        
        # Try different selectors to find job links
        job_selectors = [
            "a[href*='/careers/']",  # Direct career links
            ".jss-g13",             # The specific class we found
            "ul li div a",          # Links within list items
            "main section ul a"     # Links in main section
        ]
        
        jobs = []
        for selector in job_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    
                    for i, element in enumerate(elements[:15]):  # Limit to 15
                        try:
                            title = element.text.strip()
                            link = element.get_attribute("href")
                            
                            if title and link and "/careers/" in link:
                                # Find the parent container to get location info
                                parent_container = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'fabric-5qovnk-root')]")
                                
                                # Look for location in the structure
                                location = "Location not specified"
                                try:
                                    # Try to find location elements
                                    location_elements = parent_container.find_elements(By.CSS_SELECTOR, ".jss-g16")
                                    if location_elements:
                                        location = location_elements[0].text.strip()
                                except:
                                    pass
                                
                                jobs.append({
                                    'title': title,
                                    'link': link,
                                    'location': location,
                                    'rank': len(jobs) + 1
                                })
                                
                        except Exception as e:
                            print(f"Error processing element {i}: {e}")
                            continue
                    
                    if jobs:
                        break  # Found jobs, stop trying other selectors
                        
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        driver.quit()
        return jobs[:10]  # Return top 10
        
    except Exception as e:
        print(f"Error with Selenium: {e}")
        try:
            driver.quit()
        except:
            pass
        return []

def display_jobs(jobs):
    """Display the job list nicely."""
    if not jobs:
        print("No jobs found!")
        return
    
    print(f"\n🏢 Top {len(jobs)} BambooHR Jobs:")
    print("=" * 60)
    
    for job in jobs:
        print(f"{job['rank']}. {job['title']}")
        print(f"   📍 {job['location']}")
        print(f"   🔗 {job['link']}")
        print()

def main():
    print("BambooHR Job Scraper (Selenium Version)")
    print("=" * 40)
    
    jobs = scrape_bamboohr_jobs_selenium()
    display_jobs(jobs)
    
    if jobs:
        print(f"✅ Found {len(jobs)} jobs successfully!")
    else:
        print("❌ No jobs found. Make sure Chrome/Chromium is installed.")

if __name__ == "__main__":
    main()
