from __future__ import print_function
import os
import openai
import requests
import sib_api_v3_sdk
from dotenv import load_dotenv
from pprint import pprint
from sib_api_v3_sdk.rest import ApiException

# Load environment variables from .env file
load_dotenv()

# Get API keys and email credentials from environment
api_key = os.getenv("OPENAI_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
email_user = os.getenv("EMAIL_USER")  # Brevo email user
brevo_api_key = os.getenv("BREVO_API_KEY")  # Brevo API key

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

# Configure Brevo API key authorization
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = brevo_api_key

# Create an instance of the API class
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# Function to fetch top news headlines for a given category with a limit
def get_news_headlines(category="general", country="us", limit=10):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&country={country}&apiKey={news_api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get("articles", [])
        headlines = []
        for i, article in enumerate(articles[:limit]):
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
    return markdown_content



# Function to send the email via Brevo API
def send_email(subject, body, recipient):
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
    to=[{"email": "dejvonwalker@gmail.com", "name": "Dejvon Walker"}],
    sender={"email": "devonwalker@novaehstudios.com", "name": "Novaeh Studios"},
    template_id=2,
    params={"name": "John", "surname": "Doe"},
    headers={"X-Mailin-custom": "custom_header_1:custom_value_1|custom_header_2:custom_value_2|custom_header_3:custom_value_3", "charset": "iso-8859-1"}
)

    try:
        # Send the email using Brevo API
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
    except ApiException as e:
        print(f"Exception when calling SMTPApi->send_transac_email: {e}\n")

# Function to create a Brevo email campaign
def create_brevo_campaign(campaign_name, subject, sender_name, sender_email, html_content, list_ids, schedule_time=None):
    api_instance = sib_api_v3_sdk.EmailCampaignsApi(sib_api_v3_sdk.ApiClient(configuration))

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

    try:
        # Create the campaign
        api_response = api_instance.create_email_campaign(email_campaign)
        pprint(api_response)
    except ApiException as e:
        print(f"Exception when creating email campaign: {e}")

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
        campaign_name = "Nathaniel's News"
        subject = "Nathaniel's Daily News"
        sender_name = "Novaeh Studios"
        sender_email = email_user
        html_content = markdown_content.replace("\n", "<br>")  # Convert Markdown to basic HTML
        list_ids = [2, 7]  # Example list IDs; replace with your actual list IDs
        schedule_time = None  # Example: "2024-11-15 21:45:00" for scheduled sending

        create_brevo_campaign(campaign_name, subject, sender_name, sender_email, html_content, list_ids, schedule_time)

if __name__ == "__main__":
    main()
