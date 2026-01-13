import requests
from django.conf import settings
from translation.language_codes import NLLB_LANG_CODES, AZURE_LANG_CODES  


class AzureTranslator:
    def __init__(self):
        self.endpoint = settings.AZURE_TRANSLATE_ENDPOINT
        self.api_key = settings.AZURE_TRANSLATOR_KEY
        self.region = settings.AZURE_TRANSLATOR_REGION
        self.version = settings.AZURE_TRANSLATE_API_VERSION

        self.headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Ocp-Apim-Subscription-Region': self.region,
            'Content-Type': 'application/json'
        }

    # Detect the language of input text using Azure
    def detect_language(self, text):
        url = f"{self.endpoint}/detect?api-version={self.version}"
        body = [{'Text': text}]
        
        try:
            response = requests.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            detected_language = response.json()[0]['language']
            return detected_language
        except Exception as e:
            print(f"Azure language detection failed: {e}")
            return "unknown"

    # Translate from any language to English, unless handled by NLLB
    #User query is translated from original language to English for system processing
    def translate_to_english_azure(self, text, source_language=None):
        if not source_language:
            source_language = self.detect_language(text)

        if not source_language:
            print("No source language detected.")
            return "Sorry, translation failed.", None

        # Check if the language is handled by Meta NLLB (skip Azure translation if so)
        if source_language.lower() in NLLB_LANG_CODES:
            print(f"Skipping Azure translation for '{source_language}' (handled by NLLB)")
            return None, None

        # If the language is handled by Azure
        if source_language.lower() in AZURE_LANG_CODES:
            source_language_code = AZURE_LANG_CODES[source_language.lower()]
        else:
            print(f"Translator for '{source_language}' not available in Azure.")
            return "Sorry, translation failed.", None

        url = f"{self.endpoint}/translate?api-version={self.version}&from={source_language_code}&to=en"
        body = [{'Text': text}]
        
        try:
            response = requests.post(url, headers=self.headers, json=body)
            response.raise_for_status()  # Raise an exception for bad responses
            translated_text = response.json()[0]['translations'][0]['text']
            return translated_text, source_language
        except Exception as e:
            print(f"Error translating to English (Azure): {e}")
            return "Sorry, translation failed.", None

    # Translate from English to any target language
    #System response is translated back to user's original language
    def translate_from_english_azure(self, text, target_language):
        if target_language.lower() in AZURE_LANG_CODES:
            target_language_code = AZURE_LANG_CODES[target_language.lower()]
        else:
            print(f"Translator for '{target_language}' not available in Azure.")
            return "Sorry, translation back failed."

        url = f"{self.endpoint}/translate?api-version={self.version}&from=en&to={target_language_code}"
        body = [{'Text': text}]
        
        try:
            response = requests.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            translated_text = response.json()[0]['translations'][0]['text']
            return translated_text
        except Exception as e:
            print(f"Error translating from English (Azure): {e}")
            return "Sorry, translation back failed."
