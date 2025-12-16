# Setup Instructions for India Internship Scraper

This guide will help you set up the automated internship scraper that runs daily via GitHub Actions.

## Prerequisites

- GitHub account (with Student Pack for unlimited Actions minutes)
- Google account for Google Sheets
- Google Cloud Platform project (free tier)

## Step 1: Set Up Google Sheets

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it "India Internship Tracker"
4. Add headers in the first row:
   - Column A: Title
   - Column B: Company
   - Column C: Location
   - Column D: Stipend
   - Column E: Link
   - Column F: Source
   - Column G: Date
   - Column H: Category
5. Copy the Spreadsheet ID from the URL:
   - Example: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
   - Save this ID for later

## Step 2: Create Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project (or create a new one)
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: `internship-scraper`
   - Click "Create and Continue"
   - Skip optional steps, click "Done"
5. Create Service Account Key:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Select "JSON"
   - Download the JSON file
6. Share Google Sheet with Service Account:
   - Open the JSON file
   - Copy the `client_email` value
   - Go back to your Google Sheet
   - Click "Share"
   - Paste the service account email
   - Grant "Editor" access
   - Click "Send" (uncheck "Notify people")

## Step 3: Configure GitHub Secrets

1. Go to your GitHub repository
2. Click "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add two secrets:

### Secret 1: GOOGLE_CREDENTIALS
- Name: `GOOGLE_CREDENTIALS`
- Value: Paste the entire contents of the downloaded JSON file
- Click "Add secret"

### Secret 2: SPREADSHEET_ID
- Name: `SPREADSHEET_ID`
- Value: Paste the Spreadsheet ID from Step 1
- Click "Add secret"

## Step 4: Verify GitHub Actions Setup

1. Go to the "Actions" tab in your repository
2. You should see the workflow "Scrape India Internships Daily"
3. The workflow runs automatically daily at 6 AM UTC (11:30 AM IST)
4. You can also trigger it manually:
   - Click on the workflow
   - Click "Run workflow"
   - Select the branch
   - Click "Run workflow"

## Step 5: Test the Scraper

1. Trigger the workflow manually (as described above)
2. Wait for it to complete (usually 2-3 minutes)
3. Check your Google Sheet for new internship listings
4. View the workflow logs for details:
   - Go to "Actions" tab
   - Click on the latest run
   - Click on the "scrape" job
   - Expand "Run scraper" to see output

## Troubleshooting

### Workflow Fails
- Check the Actions logs for error messages
- Verify that both secrets are correctly set
- Ensure the service account has Editor access to the sheet
- Verify the Spreadsheet ID is correct

### No Data Appears
- The scraper only adds NEW internships (not duplicates)
- Check if internships were found in the logs
- Some websites may have anti-scraping measures
- Try running the workflow again later

### Rate Limiting
- If you see rate limit errors, the scraper includes delays
- The daily schedule prevents excessive requests
- Consider adding more delay between requests if needed

## Customization

### Change Schedule
Edit `.github/workflows/scrape-internships.yml`:
```yaml
schedule:
  - cron: '0 6 * * *'  # Change this cron expression
```

### Modify Search Keywords
Edit `main.py` to change internship categories:
```python
keywords = ['data-analytics', 'machine-learning', 'artificial-intelligence', 'data-science']
queries = ['Data Analytics Intern', 'Machine Learning Intern', 'AI Intern', 'Data Science Intern']
```

## Maintenance

- Monitor the Actions tab weekly for failures
- Update dependencies periodically
- Check for website structure changes if scraping stops working
- Keep your service account credentials secure

## Support

For issues:
1. Check the Actions logs
2. Review this documentation
3. Check if the target websites have changed
4. Verify all credentials are up to date

---

**Note**: This scraper is for educational purposes. Always respect website terms of service and robots.txt files.
