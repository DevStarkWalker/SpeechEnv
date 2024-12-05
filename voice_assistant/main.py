from dotenv import load_dotenv
import os
import sib_api_v3_sdk
from newsapi import NewsApiClient
from sib_api_v3_sdk.rest import ApiException
import requests

# Load environment variables from .env file
load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
RECIPIENT_EMAIL2 = os.getenv("RECIPIENT_EMAIL2")

# Set up the configuration for Brevo API
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY

# Set up the configuration for News API
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

CATEGORIES = ["business", "technology", "sports", "health", "science"]

def fetch_news_by_category(category):
    """Fetch top news articles for a specific category."""
    url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get("articles", [])
        return articles[:5]  # Get the top 5 articles per category
    else:
        print(f"Failed to fetch news for category '{category}': {response.status_code}")
        return []

def send_email_with_template(params):
    """Send the email using a Brevo template."""
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    # Specify the ID of the Brevo template you created
    TEMPLATE_ID = 2  # Replace with your actual template ID from Brevo

    # Create the email with the template and dynamic content
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": RECIPIENT_EMAIL}],
        sender={"email": SENDER_EMAIL, "name": "Daily Newsletter"},
        template_id=TEMPLATE_ID,
        params=params  # Map dynamic content to Brevo template placeholders
    )

        # Create the email with the template and dynamic content
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": RECIPIENT_EMAIL2}],
        sender={"email": SENDER_EMAIL, "name": "Daily Newsletter"},
        template_id=TEMPLATE_ID,
        params=params  # Map dynamic content to Brevo template placeholders
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent successfully!")
        print(api_response)
    except ApiException as e:
        print(f"Exception when sending email: {e}")

def format_news_for_template(news_by_category):
    """Format the news for Brevo template placeholders, assigning categories to category1, category2, etc."""
    params = {}
    
    # Initialize counters
    count = 1
    category_count = 1
    
    # Iterate through each category and its corresponding articles
    for category, articles in news_by_category.items():
        # Add the category name to params with a numbered key
        params[f"Category{category_count}"] = category.capitalize()  # Add the category name with the appropriate key (category1, category2, etc.)

        # Iterate through the articles for this category
        for article in articles[:5]:  # Limit to top 5 articles
            # Assign title, description, and link with unique keys
            params[f"Title{count}"] = article.get("title", "No Title")
            params[f"Description{count}"] = article.get("description", "No Description")
            params[f"link{count}"] = article.get("url", "#")
            
            # Increment the counter to ensure the keys are unique for articles
            count += 1
        
        # Increment the category counter for the next category
        category_count += 1
    
    return params




def main():
    # Fetch news for all categories
    news_by_category = {}
    for category in CATEGORIES:
        news_by_category[category] = fetch_news_by_category(category)

    # Format the news for the Brevo template placeholders
    params = format_news_for_template(news_by_category)
    print("Sending email with the following dynamic content:")
    #print("Formatted parameters for the email:")
    #for key, value in params.items():
        #print(f"{key}: {value}")

    # Send the email using Brevo template
    send_email_with_template(params)

if __name__ == "__main__":
    main()