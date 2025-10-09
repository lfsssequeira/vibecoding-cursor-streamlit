# Google Form Automation
# This script automatically fills out the survey with a prefix

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def fill_survey():
    """
    This program opens a browser, goes to the survey,
    and fills out all the fields with the prefix 'vibe-coding-20251009'
    """
    
    # List of random words to use before the prefix
    random_words = ["amazing", "awesome", "brilliant", "creative", "dynamic", 
                   "excellent", "fantastic", "great", "incredible", "perfect",
                   "super", "wonderful", "cool", "nice", "sweet", "epic"]
    
    # The prefix we want to add to all fields
    prefix = "vibe-coding-20251009"
    
    print("Starting browser...")
    
    # Open Chrome browser
    driver = webdriver.Chrome()
    
    try:
        # Go to the survey
        print("Going to the survey...")
        driver.get("https://forms.gle/uXPeoEpXkdFEfRw49")
        
        # Wait for the page to load
        time.sleep(3)
        
        # Find all text input fields and fill them
        print("Looking for form fields...")
        
        # Find input fields by different possible selectors
        input_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], textarea")
        
        print(f"Found {len(input_fields)} input fields")
        
        # Fill each field with a random word + prefix
        for i, field in enumerate(input_fields):
            try:
                # Pick a random word for this field
                random_word = random.choice(random_words)
                # Combine random word with prefix
                field_text = f"{random_word}-{prefix}"
                
                # Clear any existing text and add our text
                field.clear()
                field.send_keys(field_text)
                print(f"Filled field {i+1} with: {field_text}")
                time.sleep(0.5)  # Small delay between fields
            except Exception as e:
                print(f"Could not fill field {i+1}: {e}")
        
        print("All fields filled! Now looking for the submit button...")
        
        # Look for the submit button (Enviar)
        try:
            # Try different possible selectors for the submit button
            submit_button = None
            
            # Try to find button with text "Enviar" or "Submit"
            try:
                submit_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Enviar')]/parent::*")
            except:
                try:
                    submit_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Submit')]/parent::*")
                except:
                    # Try finding by button type
                    submit_button = driver.find_element(By.CSS_SELECTOR, "div[role='button']")
            
            if submit_button:
                print("Found submit button! Clicking it now...")
                submit_button.click()
                print("Form submitted successfully!")
                time.sleep(5)  # Wait a moment to see the confirmation
            else:
                print("Could not find the submit button. You may need to submit manually.")
                
        except Exception as e:
            print(f"Could not submit the form automatically: {e}")
            print("The form is filled but you'll need to submit it manually.")
        
        print("The browser will stay open for 10 seconds so you can see the result...")
        time.sleep(10)
        
    except Exception as e:
        print(f"Something went wrong: {e}")
    
    finally:
        # Close the browser
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    fill_survey()
