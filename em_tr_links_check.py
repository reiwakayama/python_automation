# Check for broken links within email body

import win32com.client
import requests
import datetime
from bs4 import BeautifulSoup

# Initialize Outlook application
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

# Get the Inbox folder
inbox = outlook.GetDefaultFolder(6)  # 6 corresponds to the Inbox folder

# Define the time range for the past x hours
today = datetime.datetime.today()
past_x_hours = today - datetime.timedelta(hours=48) # Update number of hours as needed

# List of email addresses to check
email_addresses = ["abc123@gmail.com", "xyz890@gmail.com"] # Update

# Retrieve all emails from past x hours in the Inbox folder
emails = inbox.Items.Restrict(f"[ReceivedTime] >= '{past_x_hours.strftime('%m/%d/%Y %H:%M %p')}'")

# Check if any emails match the criteria
trigger_emails_exist = False

# Iterate over the emails
for email in emails:
    sender_address = email.SenderEmailAddress.lower()
    if sender_address in email_addresses:
        trigger_emails_exist = True
        subject = email.Subject
        body = email.HTMLBody

        # Parse HTML content of the email body
        soup = BeautifulSoup(body, 'html.parser')

        # Find all visible text hyperlinks
        hyperlinks = soup.find_all('a')
        visible_hyperlinks = []
        for link in hyperlinks:
            if link.text:
                visible_hyperlinks.append(link['href'])

        # Check the response code of each visible hyperlink
        broken_links = []
        for link in visible_hyperlinks:
            try:
                response = requests.get(link)
                if response.status_code != 200:
                    broken_links.append((link, response.status_code))
            except requests.exceptions.RequestException as e:
                broken_links.append((link, str(e)))

        # Print the subject line and any broken links
        if broken_links:
            print(f"Subject: {subject}")
            for link, code in broken_links:
                print(f"Broken link: {link} - Response Code: {code}")
            print()
        else:
            print(f"Subject: {subject} - No broken links detected")
            print()

# Print message if no eligible emails found
if not trigger_emails_exist:
    print("No eligible trigger emails")
