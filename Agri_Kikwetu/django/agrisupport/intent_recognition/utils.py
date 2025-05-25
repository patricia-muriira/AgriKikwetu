from django.conf import settings
from openai import AzureOpenAI

# Configure Azure OpenAI client
client = AzureOpenAI(
    api_key=settings.OPENAI_API_KEY,
    api_version=settings.OPENAI_API_VERSION,
    azure_endpoint=settings.OPENAI_API_ENDPOINT
)

def classify_intent(text):
    prompt = (
        "You are an intent classifier. Classify the user input into one of the following intents: "
        "'weather_query', 'plant_disease', 'farming_advice', 'generic_conversation'. "
        "Your response must be exactly one of these four. Nothing else.\n\n"
        f"Text: \"{text}\"\nIntent:"
    )
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=5000
        )
        print("🔍 Intent Response:", response)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"💥 Intent classification error: {e}")
        return "generic"


# Extract city from the user's message
def extract_city(text):
    prompt = (
        "Extract only the city name from the following sentence. The name may start with a lowercase or uppercase letter. "
        "If no city is mentioned, respond with 'None'.\n\n"
        f"Sentence: \"{text}\"\nCity:"
    )
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=7000
        )
        print("🌍 City Extraction Response:", response)
        city = response.choices[0].message.content.strip()
        return None if city.lower() == "none" else city
    except Exception as e:
        print(f"💥 City extraction error: {e}")
        return None
