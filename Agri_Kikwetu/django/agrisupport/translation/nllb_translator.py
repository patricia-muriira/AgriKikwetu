from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from translation.language_codes import NLLB_LANG_CODES
import torch

class NLLBTranslator:
    def __init__(self):
        print("Loading NLLB model...")
        self.model_name = "facebook/nllb-200-distilled-600M"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

    #User query translation to English
    def translate_to_english_nllb(self, text, source_language):
        source_lang_code = NLLB_LANG_CODES.get(source_language.lower())
        if not source_lang_code:
            print(f"NLLB: Unsupported language for translation to English: '{source_language}'")
            return "Sorry, translation failed."

        self.tokenizer.src_lang = source_lang_code

        try:
            encoded = self.tokenizer(text, return_tensors="pt")

            generated_tokens = self.model.generate(
                **encoded,
                forced_bos_token_id=self.tokenizer.convert_tokens_to_ids("eng_Latn")
            )

            return self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

        except Exception as e:
            print(f"NLLB translation error: {e}")
            return "Sorry, translation failed."

    #System output is translated back to user's original language
    def translate_from_english_nllb(self, text, target_language):
        target_lang_code = NLLB_LANG_CODES.get(target_language.lower())
        if not target_lang_code:
            print(f"NLLB: Unsupported language for translation from English: '{target_language}'")
            return "Sorry, translation failed."

        self.tokenizer.src_lang = "eng_Latn"

        try:
            encoded = self.tokenizer(text, return_tensors="pt")

            generated_tokens = self.model.generate(
                **encoded,
                forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(target_lang_code)
            )

            return self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

        except Exception as e:
            print(f"NLLB translation error: {e}")
            return "Sorry, translation failed."
