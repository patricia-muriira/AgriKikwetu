from .nllb_translator import NLLBTranslator
from .azure_translator import AzureTranslator
from .language_detector import detect_language_with_openai

#This translation router decides which langauges are sent to which translator. It also stores the original language for the back translation

# Instantiate the translators
nllb_translator = NLLBTranslator()
azure_translator = AzureTranslator()

# #User input translation function
# def translate_input(user_input):
#     detected_lang = detect_language_with_openai(user_input)

#     if not detected_lang:
#         return {
#             "translated_input": "translation_failed",
#             "detected_language": None,
#             "translator_used": "none"
#         }

#     detected_lang = detected_lang.lower()

#     # NLLB path
#     if detected_lang in ["kamba", "kikuyu", "dholuo", "hindi"]:
#         translated_input = nllb_translator.translate_to_english_nllb(user_input, detected_lang)
#         if not translated_input:
#             return {
#                 "translated_input": "translation_failed",
#                 "detected_language": detected_lang,
#                 "translator_used": "nllb"
#             }
#         return {
#             "translated_input": translated_input,
#             "detected_language": detected_lang,
#             "translator_used": "nllb"
#         }

#     # Azure path
#     elif detected_lang != "english":
#         translated_input, detected_from_api = azure_translator.translate_to_english_azure(user_input, detected_lang)

#         if not detected_from_api:
#             return {
#                 "translated_input": "translation_failed",
#                 "detected_language": None,
#                 "translator_used": "azure"
#             }

#         return {
#             "translated_input": translated_input,
#             "detected_language": detected_from_api.lower(),
#             "translator_used": "azure"
#         }

#     # No translation needed
#     else:
#         return {
#             "translated_input": user_input,
#             "detected_language": detected_lang,
#             "translator_used": "none"
#         }

# #System output back-translation function
# def translate_back(output_text, detected_language, translator_used):
#     if not detected_language or detected_language.lower() == "english" or translator_used == "none":
#         return output_text

#     try:
#         if translator_used == "nllb":
#             return nllb_translator.translate_from_english_nllb(output_text, detected_language)
#         elif translator_used == "azure":
#             return azure_translator.translate_from_english_azure(output_text, detected_language)
#     except Exception as e:
#         print(f"Error translating back: {e}")
#         return "Sorry, translation back failed."

#     return output_text

#User input translated to English for system compatibility

def translate_input(user_input):
    detected_lang = detect_language_with_openai(user_input)

    if not detected_lang:
        return {
            "translated_input": "translation_failed",
            "detected_language": None,
            "translator_used": "none"
        }

    detected_lang = detected_lang.lower()
    
# NLLB supported languages
    if detected_lang in ["kamba", "kikuyu", "dholuo", "hindi"]:
        translated_input = nllb_translator.translate_to_english_nllb(user_input, detected_lang)
        if not translated_input:
            return {
                "translated_input": "translation_failed",
                "detected_language": detected_lang,
                "translator_used": "nllb"
            }
        return {
            "translated_input": translated_input,
            "detected_language": detected_lang,
            "translator_used": "nllb"
        }

    #Azure supported languages
    elif detected_lang != "english":
        translated_input, detected_from_api = azure_translator.translate_to_english_azure(user_input, detected_lang)
        if not detected_from_api:
            return {
                "translated_input": "translation_failed",
                "detected_language": None,
                "translator_used": "azure"
            }

        return {
            "translated_input": translated_input,
            "detected_language": detected_from_api.lower(),
            "translator_used": "azure"
        }

    #Original input in English
    else:
        return {
            "translated_input": user_input,
            "detected_language": detected_lang,
            "translator_used": "none"
        }


#Translation of system output to original language
def translate_back(output_text, detected_language, translator_used):
    if not detected_language or detected_language.lower() == "english" or translator_used == "none":
        return output_text

    # Check if detected_language is None before trying to call .lower()
    if detected_language is None:
        print("Detected language is None. Skipping translation back.")
        return output_text

    try:
        # Proceed with translation if detected_language is not None
        if translator_used == "nllb":
            return nllb_translator.translate_from_english_nllb(output_text, detected_language)
        elif translator_used == "azure":
            return azure_translator.translate_from_english_azure(output_text, detected_language)
    except Exception as e:
        print(f" Error translating back: {e}")
        return "Sorry, translation back failed."

    return output_text
