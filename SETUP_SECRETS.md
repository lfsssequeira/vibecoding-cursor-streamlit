# 🔐 Secure Configuration Setup

This guide will help you set up secure configuration for your Via Verde app review scraper, so you don't need to copy-paste API keys every time.

## 🚀 Quick Setup

### Step 1: Configure Your Secrets

1. **Open the secrets file:**
   ```bash
   nano .streamlit/secrets.toml
   ```

2. **Replace the placeholder values with your actual credentials:**

   ```toml
   [gemini]
   api_key = "AIzaSyC..." # Your actual Gemini API key

   [google_sheets]
   sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
   
   service_account_json = """
   {
     "type": "service_account",
     "project_id": "your-project-id",
     "private_key_id": "your-private-key-id",
     "private_key": "-----BEGIN PRIVATE KEY-----\\nYour actual private key\\n-----END PRIVATE KEY-----\\n",
     "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
     "client_id": "your-client-id",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
   }
   """
   ```

### Step 2: Get Your API Keys

#### 🤖 Gemini API Key
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in `secrets.toml`

#### 📊 Google Sheets Service Account
1. Go to: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Google Sheets API
4. Go to "Credentials" → "Create Credentials" → "Service Account"
5. Download the JSON key file
6. Copy the entire JSON content to `secrets.toml`

### Step 3: Share Your Google Sheet
1. Open your Google Sheet
2. Click "Share" button
3. Add your service account email (found in the JSON)
4. Give it "Editor" permissions

### Step 4: Run the App
```bash
python3 -m streamlit run app_review_scraper.py
```

## ✅ Verification

When you run the app, you should see:
- ✅ **Gemini API key loaded from configuration**
- ✅ **Google Sheets credentials loaded from configuration**
- 🔑 **Service Account: your-email@project.iam.gserviceaccount.com**

## 🔒 Security Notes

- ✅ The `.streamlit/secrets.toml` file is in `.gitignore` - it won't be committed to git
- ✅ Your API keys are stored locally and never shared
- ✅ Streamlit encrypts secrets when running
- ✅ You can still override secrets by entering them manually in the app

## 🆘 Troubleshooting

### "No Gemini API key found in configuration"
- Check that your API key is in `secrets.toml` under `[gemini]`
- Make sure the key doesn't have extra quotes or spaces

### "No Google Sheets credentials found"
- Verify the JSON is properly formatted in `secrets.toml`
- Make sure the service account has access to your sheet
- Check that the sheet URL is correct

### "Error opening spreadsheet"
- Ensure your service account email is shared with the Google Sheet
- Verify the sheet URL is accessible
- Check that Google Sheets API is enabled in your project

## 🎯 Benefits

- 🚀 **No more copy-pasting** API keys
- 🔒 **Secure storage** of sensitive data
- ⚡ **Faster setup** when running the app
- 🛡️ **Git-safe** - secrets won't be committed
- 🔄 **Easy switching** between manual and configured modes
