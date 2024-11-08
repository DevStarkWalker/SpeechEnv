from __future__ import print_function
import os
import openai
import requests
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables from .env file
load_dotenv()

# Get API keys and email credentials
api_key = os.getenv("OPENAI_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
email_user = os.getenv("EMAIL_USER")  # Brevo email user
email_pass = os.getenv("BREVO_API_KEY")  # Brevo API key used as the password for SMTP and API authentication

# Predefined categories for the newsletter
CATEGORIES = ["technology", "business", "health", "sports", "general", "science"]

# Category limits (number of articles per category)
CATEGORY_LIMITS = {
    "sports": 5,
    "technology": 5,
    "business": 7,
    "health": 3,
    "general": 5,
    "science": 5,
}

# Function to fetch top news headlines for a given category with a limit
def get_news_headlines(category="general", country="us", limit=10):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&country={country}&apiKey={news_api_key}"
    response = requests.get(url)
    
    print(f"Response for {category}: {response.status_code}")
    print(response.json())  # Debugging: print response structure

    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get("articles", [])
        headlines = []
        for i, article in enumerate(articles[:limit]):  # Limit the number of articles
            title = article.get("title")
            url = article.get("url")
            
            if title and url:
                headlines.append(f"- [{title}]({url})")
        return headlines
    else:
        return [f"Error fetching news for {category}. Status code: {response.status_code}"]

# Function to create the newsletter content in Markdown format
def create_markdown_newsletter():
    markdown_content = "# Daily News Digest\n\n"
    for category in CATEGORIES:
        markdown_content += f"## {category.capitalize()} News\n\n"
        limit = CATEGORY_LIMITS.get(category, 10)
        headlines = get_news_headlines(category, limit=limit)
        markdown_content += "\n".join(headlines) + "\n\n"
    with open("newsletter.md", "w") as file:
        file.write(markdown_content)
    return markdown_content

# Function to send the Markdown content via Brevo SMTP
def send_email(subject, body, recipient):
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = recipient
    msg['Subject'] = subject
    
    # Attach the body as plain text
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Brevo SMTP server setup
        server = smtplib.SMTP("smtp-relay.sendinblue.com", 587)
        server.starttls()
        
        # Login with Brevo email and API key as password
        server.login(email_user, email_pass)  # Use API key as password
        server.sendmail(email_user, recipient, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to create a Brevo email campaign
def create_brevo_campaign(campaign_name, subject, sender_name, sender_email, html_content, list_ids, schedule_time):
    # Configure Brevo client for the API
    sib_api_v3_sdk.configuration.api_key['api-key'] = email_pass  # Use Brevo API key from environment
    api_instance = sib_api_v3_sdk.EmailCampaignsApi()

    # Define the email campaign
    email_campaign = sib_api_v3_sdk.CreateEmailCampaign(
        name=campaign_name,
        subject=subject,
        sender={"name": sender_name, "email": sender_email},
        type="classic",
        html_content=html_content,
        recipients={"listIds": list_ids},
        scheduled_at=schedule_time
    )

    # Create the campaign
    try:
        api_response = api_instance.create_email_campaign(email_campaign)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling EmailCampaignsApi->create_email_campaign: %s\n" % e)

# Main function to generate and send the newsletter
def main():
    print("Generating newsletter...")
    markdown_content = create_markdown_newsletter()
    
    # Preview content
    print("Markdown Content:\n", markdown_content)

    # Option to send the email directly
    recipient = input("Enter the email address to send the newsletter directly: ")
    send_email("Daily News Digest", markdown_content, recipient)

    # Option to create a Brevo campaign
    create_campaign = input("Would you like to create a Brevo campaign? (yes/no): ").lower()
    if create_campaign == 'yes':
        campaign_name = "Daily News Digest Campaign"
        subject = "Your Daily News Digest"
        sender_name = "Your Sender Name"
        sender_email = email_user
        html_content = markdown_content  # Use the same content for the campaign
        list_ids = [2, 7]  # Example list IDs
        schedule_time = "2024-11-08 00:00:01"  # Example scheduled time

        create_brevo_campaign(campaign_name, subject, sender_name, sender_email, html_content, list_ids, schedule_time)

if __name__ == "__main__":
    main()
