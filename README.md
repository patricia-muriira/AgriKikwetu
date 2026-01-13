# Multilingual Agri-Support & Crop Disease Detection System With Telegram Bot Integration

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

NLLB model - facebook/nllb-200-distilled-600M
* More languages can be added by editing the language codes file and the router logic. These were the Kenyan languages available as of April 2025
---

##  Tech Stack

* **Backend:** [Django](https://www.djangoproject.com/)
* **Chatbot API:** Telegram Bot API
* **Translation Engines:** Azure Translate & NLLB with a custom routing engine
* **Conversational AI:** Azure OpenAI
* **Inference:** Disease Detection Vision Model[1]
---
  
## Modular Architecture & Extensibility
The system is designed with a separation between the Intelligence Engine and the Communication Interface. This modularity ensures that the backend can be plugged into any frontend or endpoint, not just Telegram.

Decoupled Components
Standalone Backend (Agri_Kikwetu): A centralized Django service that handles translation, intent classification, and disease detection. It is completely independent of the chatbot's UI.

Independent Bot Client (Telegram_bot): A standalone module that communicates with the backend. This can be easily replaced or supplemented with other interfaces.

---
## Project Structure
```
AgriKikwetu
├──Agri_Kikwetu
│   ├──django
│   │   └──agrisupport
│   │   │   ├──agrisupport
│   │   │   │   ├──__init__.py
│   │   │   │   ├──asgi.py
│   │   │   │   ├──settings.py
│   │   │   │   ├──urls.py
│   │   │   │   └──wsgi.py
│   │   │   ├──intent_recognition           ## Intent recognition and classification
│   │   │   │   ├──migrations
│   │   │   │   │   └──__init__.py
│   │   │   │   ├──__init__.py
│   │   │   │   ├──admin.py
│   │   │   │   ├──apps.py
│   │   │   │   ├──models.py
│   │   │   │   ├──tests.py
│   │   │   │   ├──urls.py
│   │   │   │   ├──utils.py
│   │   │   │   └──views.py
│   │   │   ├──plant_disease                ## Crop disease detection handling
│   │   │   │   ├──migrations
│   │   │   │   │   ├──__init__.py
│   │   │   │   │   └──0001_initial.py
│   │   │   │   ├──__init__.py
│   │   │   │   ├──admin.py
│   │   │   │   ├──apps.py
│   │   │   │   ├──models.py
│   │   │   │   ├──serializers.py
│   │   │   │   ├──tests.py
│   │   │   │   ├──urls.py
│   │   │   │   └──views.py
│   │   │   ├──templates                   ## Defines the image upload template
│   │   │   │   └──plant_disease
│   │   │   │   │   └──upload.html
│   │   │   ├──translation
│   │   │   │   ├──azure_translator.py     ## Azure translate engine
│   │   │   │   ├──language_codes.py       ## Contains the supported language codes (can be modifies to support more languages)
│   │   │   │   ├──language_detector.py    ## Detects original input language
│   │   │   │   ├──nllb_translator.py      ## Meta NLLB (No language left Behind) engine
│   │   │   │   ├──translation_routes.py   ## routes translation tasks to the translation engines
│   │   │   │   ├──urls.py
│   │   │   │   └──views.py                ## Contains overall system logic
│   │   │   ├──config.yml
│   │   │   ├──db.sqlite3
│   │   │   └──manage.py
│   ├──models
│   │   ├──variables
│   │   │   ├──variables.data-00000-of-00001
│   │   │   └──variables.index
│   │   └──saved_model.pb                   ## Crop disease dtection model
│   ├──freezeviews.py
│   ├──requirements.txt                     ## Requirements file
│   └──.gitignore
├──Telegram_bot                             ## Connects the system to the telegram bot interface
│   ├──bot.py                               ## Chatbot logic 
│   ├──None
│   ├──requirements.txt                     ## Requirements file for telegram bot integration
│   └──.gitignore
└──README.md
```
---
## 🛠️ Setup and Installation

The system is split into two independent components. You must configure and run the backend engine (Part A) before starting the communication interface (Part B).

### **Part A: The Agri-Support Engine (Backend)**

This contains the Django server, NLLB/Azure translation logic, and the disease detection model.

1. **Navigate to the Django Root:**
```bash
cd AgriKikwetu-main/Agri_Kikwetu/django/agrisupport

```
2. **Environment Configuration:**
Create a `.env` file in the `AgriKikwetu-main/Agri_Kikwetu/django/agrisupport` directory:

```env
# Django Settings
SECRET_KEY=your_secret_key

# Azure Translator Settings
AZURE_TRANSLATOR_KEY=your_key
AZURE_TRANSLATOR_REGION=your_region
AZURE_TRANSLATOR_ENDPOINT=your_endpoint
AZURE_TRANSLATE_API_VERSION=version_in_use

# Weather API Settings
WEATHER_API_KEY=your_weather_key

# Azure OpenAI Settings
OPENAI_API_KEY=your_key
OPENAI_API_ENDPOINT=your_endpoint
OPENAI_REGION=your_region
OPENAI_API_TYPE=azure
OPENAI_API_VERSION=version_in_use
OPENAI_DEPLOYMENT_NAME=your_deployment_name
```
3. **Install Dependencies:**
*(Note: Use the requirements file located in the Agri_Kikwetu root)*
```bash
pip install -r ../../requirements.txt

```

4. **Initialize & Launch django server:**
```bash
python manage.py migrate
python manage.py runserver

```
---

### **Part B: The Telegram Interface (Frontend)**

This is the standalone client that connects users to the backend.
*(Note: The backend can be connected to any other frontend not necessarily Telegram)*

1. **Navigate to the Bot Directory:**
```bash
cd AgriKikwetu-main/Telegram_bot

```

2. **Install Interface Dependencies:**
*(Note: Use the requirements file located in the Telegram_bot root)*

```bash
pip install -r requirements.txt

```

3. **Configure .env file:**
Create a `.env` file in the `AgriKikwetu-main/Telegram_bot` directory(for modularity).
```env
# Telegram Credentials
TELEGRAM_TOKEN =your_telegram_bot_token

# Connection to Backend
DJANGO_BACKEND_URL= your_url #http://127.0.0.1:port_number if local
```

5. **Launch the Bot:**
```bash
python bot.py

```
---
##  Feature Usage

* **Disease Analysis:** Send a photo of a crop. The bot will identify the disease and provide treatment steps in your local language.
* **Weather Updates:** Ask "What is the weather like today in *city* ?" to receive local forecasts. Default city is Nairobi
* **Farming Advice:** Ask questions like "When should I plant maize?" or "How do I manage pests?" for localized agricultural guidance.

**Model Source:** 
1. [Plant Disease Detection Model](https://www.kaggle.com/models/rishitdagli/plant-disease) by [Rishit Dagli](https://github.com/Rishit-dagli). 
Based on the **PlantVillage Dataset** by Hughes et al.
