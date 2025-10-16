#!/usr/bin/env python3
"""
Quick setup script for Via Verde App Review Scraper secrets
This script helps you configure your API keys securely
"""

import os
import json
from pathlib import Path

def create_secrets_file():
    """Create or update the secrets.toml file"""
    
    secrets_path = Path(".streamlit/secrets.toml")
    
    # Ensure .streamlit directory exists
    secrets_path.parent.mkdir(exist_ok=True)
    
    print("🔐 Via Verde App Review Scraper - Secrets Setup")
    print("=" * 50)
    print()
    
    # Get Gemini API key
    print("🤖 Gemini AI Configuration")
    print("-" * 30)
    gemini_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
    
    if not gemini_key:
        gemini_key = "your_gemini_api_key_here"
        print("⚠️  Skipped Gemini API key - you can add it later")
    
    print()
    
    # Get Google Sheets configuration
    print("📊 Google Sheets Configuration")
    print("-" * 30)
    
    # Sheet URL
    sheet_url = input("Enter your Google Sheet URL (or press Enter for default): ").strip()
    if not sheet_url:
        sheet_url = "https://docs.google.com/spreadsheets/d/1ZBU9dDbMhYK2qWeWvVSK1D0o_muRjtN2rXFPlpVO_UU/edit?gid=0#gid=0"
        print("📝 Using default sheet URL")
    
    print()
    print("📄 Google Service Account JSON")
    print("You have two options:")
    print("1. Paste JSON manually (type 'paste' and press Enter)")
    print("2. Use the JSON file you already have (type 'file' and press Enter)")
    print("3. Skip for now (type 'skip' and press Enter)")
    
    choice = input("Choose option (1/2/3): ").strip().lower()
    
    if choice == "file":
        # Try to read from the existing JSON file
        json_file_path = "/Users/luissequeira/Downloads/vibecoding-codeforall-173f2d03d225.json"
        try:
            with open(json_file_path, 'r') as f:
                service_account_json = f.read().strip()
            print(f"✅ Loaded JSON from {json_file_path}")
        except FileNotFoundError:
            print(f"❌ File not found: {json_file_path}")
            print("Please provide the correct path or use option 1 to paste manually")
            service_account_json = '{"type": "service_account", ...}'
    elif choice == "paste":
        print("Paste your service account JSON below (press Ctrl+D when done on Mac/Linux or Ctrl+Z on Windows):")
        print("(Get this from: https://console.cloud.google.com/)")
        
        try:
            # Read all lines until EOF
            json_lines = []
            while True:
                try:
                    line = input()
                    json_lines.append(line)
                except EOFError:
                    break
            
            service_account_json = "\n".join(json_lines).strip()
        except KeyboardInterrupt:
            print("\n⚠️ Input cancelled")
            service_account_json = '{"type": "service_account", ...}'
    else:
        # Skip option
        service_account_json = '{"type": "service_account", ...}'
        print("⚠️ Skipped service account JSON - you can add it later")
    
    # Validate JSON
    if service_account_json and service_account_json != "":
        try:
            json.loads(service_account_json)
            print("✅ Valid JSON format")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            print("⚠️  You can fix this later in the secrets.toml file")
            service_account_json = '{"type": "service_account", ...}'
    else:
        service_account_json = '{"type": "service_account", ...}'
        print("⚠️  Skipped service account JSON - you can add it later")
    
    # Create secrets.toml content
    secrets_content = f'''# Streamlit Secrets Configuration for Via Verde App Review Scraper
# Generated on {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[gemini]
# Your Google Gemini API key from https://makersuite.google.com/app/apikey
api_key = "{gemini_key}"

[google_sheets]
# Your Google Sheet URL
sheet_url = "{sheet_url}"

# Your Google Service Account JSON credentials
service_account_json = """
{service_account_json}
"""
'''
    
    # Write secrets file
    with open(secrets_path, 'w') as f:
        f.write(secrets_content)
    
    print()
    print("✅ Secrets configuration created!")
    print(f"📁 Location: {secrets_path.absolute()}")
    print()
    
    # Show next steps
    print("🚀 Next Steps:")
    print("1. Run the app: python3 -m streamlit run app_review_scraper.py")
    print("2. Check that your credentials are loaded automatically")
    print("3. Test the Gemini AI analysis and Google Sheets saving")
    print()
    
    if gemini_key == "your_gemini_api_key_here":
        print("⚠️  Remember to add your Gemini API key to secrets.toml")
    
    if service_account_json == '{"type": "service_account", ...}':
        print("⚠️  Remember to add your Google Service Account JSON to secrets.toml")
    
    print()
    print("🔒 Security: Your secrets are stored locally and won't be committed to git")

if __name__ == "__main__":
    try:
        create_secrets_file()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
