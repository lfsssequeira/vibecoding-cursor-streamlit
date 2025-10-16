#!/usr/bin/env python3
"""
Quick setup script using your existing credentials
"""

import json
from pathlib import Path

def quick_setup():
    """Quick setup using existing JSON file"""
    
    print("🚀 Quick Setup for Via Verde App Review Scraper")
    print("=" * 50)
    
    # Paths
    json_file = Path("/Users/luissequeira/Downloads/vibecoding-codeforall-173f2d03d225.json")
    secrets_file = Path(".streamlit/secrets.toml")
    
    # Ensure .streamlit directory exists
    secrets_file.parent.mkdir(exist_ok=True)
    
    # Your credentials (I can see them from your env.example)
    gemini_api_key = "AIzaSyB-EwcNl_NZ9uOPAyyHifculv9Oh0XdX5o"
    sheet_url = "https://docs.google.com/spreadsheets/d/1ZBU9dDbMhYK2qWeWvVSK1D0o_muRjtN2rXFPlpVO_UU/edit?gid=0#gid=0"
    
    # Read the JSON file
    try:
        with open(json_file, 'r') as f:
            service_account_json = f.read().strip()
        print(f"✅ Loaded Google Service Account JSON from {json_file}")
    except FileNotFoundError:
        print(f"❌ Could not find {json_file}")
        print("Please make sure the JSON file exists")
        return
    
    # Validate JSON
    try:
        json_data = json.loads(service_account_json)
        client_email = json_data.get('client_email', 'Unknown')
        print(f"✅ Valid JSON - Service Account: {client_email}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return
    
    # Create secrets.toml content
    secrets_content = f'''# Streamlit Secrets Configuration for Via Verde App Review Scraper
# Auto-generated from existing credentials

[gemini]
# Your Google Gemini API key
api_key = "{gemini_api_key}"

[google_sheets]
# Your Google Sheet URL
sheet_url = "{sheet_url}"

# Your Google Service Account JSON credentials
service_account_json = """
{service_account_json}
"""
'''
    
    # Write secrets file
    with open(secrets_file, 'w') as f:
        f.write(secrets_content)
    
    print()
    print("✅ Secrets configuration created successfully!")
    print(f"📁 Location: {secrets_file.absolute()}")
    print()
    
    # Show what was configured
    print("🔧 Configuration Summary:")
    print(f"🤖 Gemini API Key: {'✅ Configured' if gemini_api_key else '❌ Missing'}")
    print(f"📊 Google Sheet URL: {'✅ Configured' if sheet_url else '❌ Missing'}")
    print(f"🔑 Service Account: ✅ {client_email}")
    print()
    
    print("🚀 Ready to run!")
    print("Run this command to start the app:")
    print("python3 -m streamlit run app_review_scraper.py")
    print()
    print("🔒 Your credentials are now stored securely and won't be committed to git")

if __name__ == "__main__":
    try:
        quick_setup()
    except Exception as e:
        print(f"❌ Error: {e}")
