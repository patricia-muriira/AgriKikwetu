# Multilingual Agri-Support & Crop Disease Detection Bot

An advanced Django-based backend for an AI-powered agricultural assistant. This system provides farmers with **real-time disease detection**, **localized weather forecasts**, and **tailored farming advice**. 
By integrating **Azure Translate** and **NLLB**, it bridges the language gap for rural communities in Kenya and beyond.

---

## System Logic

The system follows a structured pipeline to process user queries (Text or Image) via the **Telegram** interface:

1. **Input Detection:** Supports text queries and image uploads.
2. **Multilingual Translation (Inbound):** * Automatically detects the language.
* Translates non-English text to English for processing.
* *Default:* If an image is sent without text, the system defaults to English.

3. **Intent Classification:** Determines if the user needs **Disease Detection**, **Weather Updates**, or **Farming Advice**.
4. **Specialized View Routing:**
* **Disease Detection:** Runs a Vision model inference on uploaded images.
* **Weather Info:** Fetches timely, localized weather data and augments with related farming tips
* **Farming Advice:** Provides general or specific agricultural best practices.

5. **Azure OpenAI Augmentation:** Raw data (like a disease class or weather metrics) is converted into a natural, conversational response.
6. **Translation (Outbound):** The conversational response is translated back to the user's original language.
7. **Final Response:** Delivered directly to the user's Telegram chat.

---

## Supported Languages

The bot supports a wide range of local and international languages to ensure inclusivity:

### **Azure Translator Support**

* **English** (`en`)
* **Swahili** (`sw`)
* **Somali** (`so`)

### **Meta NLLB (No Language Left Behind) Support**

* **Kamba:** `kab_Latn`
* **Kikuyu:** `kik_Latn`
* **Dholuo:** `luo_Latn`
* **Hindi:** `hin_Deva`

* More languages can be added by editing the language codes file and the router logic. These were the Kenyan languages available as of 2025
---

##  Tech Stack

* **Backend:** [Django](https://www.djangoproject.com/)
* **Chatbot API:** Telegram Bot API
* **Translation Engines:** Azure Translate & NLLB with a custom routing engine
* **Conversational AI:** Azure OpenAI
* **Inference:** Disease Detection Vision Model[1]

---

## Setup & Installation

1. **Clone the Repo**
```bash
git clone https://github.com/patricia-muriira/AgriKikwetu.git
cd AgriKikwetu

```


2. **Install Requirements**
```bash
pip install -r requirements.txt

```


3. **Environment Configuration**
Create a `.env` file and add your credentials:
```env
TELEGRAM_BOT_TOKEN=your_token
AZURE_TRANSLATE_KEY=your_key
AZURE_OPENAI_KEY=your_openai_key
AZURE_OPENAI_ENDPOINT=your_endpoint
WEATHER_API_KEY=your_weather_api_key
** not exhaustive
```

---

##  Feature Usage

* **Disease Analysis:** Send a photo of a crop. The bot will identify the disease and provide treatment steps in your local language.
* **Weather Updates:** Ask "What is the weather like today in <city> ?" to receive local forecasts. Default city is Nairobi
* **Farming Advice:** Ask questions like "When should I plant maize?" or "How do I manage pests?" for localized agricultural guidance.

**Model Source:** 
1. [Plant Disease Detection Model](https://www.kaggle.com/models/rishitdagli/plant-disease) by [Rishit Dagli](https://github.com/Rishit-dagli). 
Based on the **PlantVillage Dataset** by Hughes et al.
