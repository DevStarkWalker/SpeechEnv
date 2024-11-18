from dotenv import load_dotenv
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import requests

# Load environment variables from .env file
load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

print(f"Brevo API Key: {BREVO_API_KEY}")
print(f"News API Key: {NEWS_API_KEY}")
print(f"Sender Email: {SENDER_EMAIL}")
print(f"Receipent Email: {RECIPIENT_EMAIL}")

# Set up the configuration for Brevo API
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY

CATEGORIES = ["business", "technology", "sports", "health", "entertainment"]

def fetch_news_by_category(category):
    """Fetch top news articles for a specific category."""
    url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get("articles", [])
        return articles[:5]  # Get the top 3 articles per category
    else:
        print(f"Failed to fetch news for category '{category}': {response.status_code}")
        return []

def format_news_for_template(news_by_category):
    """Format the news for template placeholders."""
    formatted_news = ""
    for category, articles in news_by_category.items():
        formatted_news += f"<h2>{category.capitalize()}</h2>"
        if not articles:
            formatted_news += "<p>No articles available for this category.</p>"
        for article in articles:
            title = article.get("title", "No Title")
            url = article.get("url", "#")
            description = article.get("description", "No Description")
            formatted_news += f"<p><strong><a href='{url}'>{title}</a></strong>: {description}</p>"
        formatted_news += "<hr>"
    return formatted_news


def send_email_with_template(content):
    """Send the email using a Brevo template."""
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    # Specify the ID of the Brevo template you created
    TEMPLATE_ID = 2  # Replace with your actual template ID from Brevo

    # Create the email with the template and dynamic content
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
    to=[{"email": RECIPIENT_EMAIL}],  # Ensure RECIPIENT_EMAIL is being set correctly
    sender={"email": SENDER_EMAIL, "name": "Daily Newsletter"},
    template_id=TEMPLATE_ID,
    params={"categories": content}  # Map dynamic content to Brevo template placeholders
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Sending Email with Content: ")
        print(content) 
        print("Email sent successfully!")
        print(api_response)
    except ApiException as e:
        print(f"Exception when sending email: {e}")

def main():
    # Fetch news for all categories
    news_by_category = {}
    for category in CATEGORIES:
        news_by_category[category] = fetch_news_by_category(category)

    # Format the news for the email template
    formatted_news = format_news_for_template(news_by_category)

    # Print the formatted news to check the content
    print("Formatted News Content:")
    print(formatted_news)  # This will print the HTML content of the categories

    # Send the email using Brevo template
    send_email_with_template(formatted_news)

if __name__ == "__main__":
    main()
