# import openai
# from openai import AzureOpenAI
# from django.conf import settings
# import time

# # Setting up Azure OpenAI Client
# openai.api_key = settings.OPENAI_API_KEY
# openai.api_base = settings.OPENAI_API_ENDPOINT
# openai.api_type = settings.OPENAI_API_TYPE
# openai.api_version = settings.OPENAI_API_VERSION  

# client = AzureOpenAI(
#     api_key=settings.OPENAI_API_KEY,
#     api_version=settings.OPENAI_API_VERSION,
#     azure_endpoint=settings.OPENAI_API_ENDPOINT
# )

# def detect_language_with_openai(text, max_retries=3):
#     user_prompt = f"You are a language detector. Respond only with the language name (e.g., kamba, kikuyu, dholuo, hindi).\nText: {text}"
    
#     for attempt in range(max_retries):
#         try:
#             response = client.chat.completions.create(
#                 model=settings.OPENAI_DEPLOYMENT_NAME,  
#                 messages=[{"role": "user", "content": user_prompt}],
#                 max_completion_tokens=500, 
#             )
#             print("🔍 Detected language response:", response)  # Debugging

#             detected_language = response.choices[0].message.content.strip().lower()
#             return detected_language
        
#         except openai.error.RateLimitError:
#             print(f"💥 Rate limit reached. Retry {attempt + 1}/{max_retries}...")
#             time.sleep(2 ** attempt)  # Exponential backoff

#         except openai.error.APIError as e:
#             print(f"💥 API error: {e}. Retry {attempt + 1}/{max_retries}...")
#             time.sleep(2 ** attempt)  # Exponential backoff

#         except Exception as e:
#             print(f"💥 Unknown error during language detection: {e}")
#             break

#     return "unknown"


from openai import AzureOpenAI
from django.conf import settings
import openai
import time

openai.api_key = settings.OPENAI_API_KEY
openai.api_base = settings.OPENAI_API_ENDPOINT  
openai.api_type = settings.OPENAI_API_TYPE  
openai.api_version = settings.OPENAI_API_VERSION  

client = AzureOpenAI(
    api_key=settings.OPENAI_API_KEY,
    api_version=settings.OPENAI_API_VERSION,
    azure_endpoint=settings.OPENAI_API_ENDPOINT
)

def detect_language_with_openai(text, max_retries=3):
    user_prompt = (
        "You are a language detector specializing in Kenyan languages, specifically kikuyu, dholuo, swahili, kamba, hindi, somali and english. Identify with 100 percent accuracy the language used in the text provided."
        "Reply with a single word answer. No extra words or explanations.\n"
        f"Text: {text}"
    )

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_DEPLOYMENT_NAME,  
            messages=[{"role": "user", "content": user_prompt}],
            max_completion_tokens=8000,
        )
        
        print("🔍 Detected language response:", response)  
        return response.choices[0].message.content.strip().lower()

    except Exception as e:
        print(f"💥 Language detection error: {e}")
        return "unknown"
