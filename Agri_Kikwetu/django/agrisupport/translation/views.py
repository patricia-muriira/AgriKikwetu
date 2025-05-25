from django.http import JsonResponse
from django.conf import settings
import requests
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from rest_framework.parsers import MultiPartParser, FormParser
from plant_disease.views import get_openai_response, identify_disease, get_farming_advice , generic
from .translation_routes import translate_input, translate_back
from intent_recognition.utils import classify_intent, extract_city
from django.views.decorators.csrf import csrf_exempt

# Load the pre-trained model globally.
MODEL_PATH = 'C:\\Users\\HP\\Desktop\\Project\\Agri_Kikwetu\\models'
model = tf.saved_model.load(MODEL_PATH)
predict_fn = model.signatures["serving_default"]

# Defining the class names
class_names = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot", "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy", "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", "Potato___Early_blight",
    "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy", "Soybean___healthy",
    "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites_Two-spotted_spider_mite", "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus", "Tomato___healthy"
]
#allow non-browser requests
@csrf_exempt
def handle_translation_and_intent(request):
    # print("Request method:", request.method)
    # print("POST keys:", list(request.POST.keys()))
    # print("FILES keys:", list(request.FILES.keys()))
    # print("Raw POST data:", request.body)
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    user_input = request.POST.get('user_input', '').strip()
    image_file = request.FILES.get('image', None)
    
    if not user_input and not image_file:
        return JsonResponse({'error': 'No input provided.'}, status=400)

    final_response = ""
    original_lang = "en"
    translator_used = "None"

    # Step 1: Translate the text if present
    if user_input:
        translation_result = translate_input(user_input)
        english_input = translation_result["translated_input"]
        original_lang = translation_result["detected_language"]
        translator_used = translation_result["translator_used"]

        if not english_input or english_input.lower() in ["translation_failed", ""]:
            return JsonResponse({
                'original_language': original_lang,
                'translator_used': translator_used,
                'intent': '',
                'ai_response': 'Translation to English failed.',
                'final_output': 'Sorry, translation back failed.'
            }, status=400)

        # Step 2: Classify Intent
        intent = classify_intent(english_input).strip().lower()
        print(f"Classified intent: {intent}")

        # Step 3: Handle Text-based Intent
        if intent == 'weather_query':
            city = extract_city(english_input)
            if not city:
                final_response = "City not found in input."
            else:
                try:
                    weatherkey = settings.WEATHER_API_KEY
                    url = f"http://api.weatherapi.com/v1/current.json?key={weatherkey}&q={city}"
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()

                    if "error" in data:
                        final_response = "Unable to fetch weather data."
                    else:
                        weather_info = {
                            "city": city,
                            "temperature": data["current"]["temp_c"],
                            "condition": data["current"]["condition"]["text"],
                            "humidity": data["current"]["humidity"],
                            "wind_speed": data["current"]["wind_kph"],
                        }

                        openai_input = (
                            f"Here is a weather report for {city}: {weather_info}. "
                            "It includes temperature, condition, humidity, and wind speed. "
                            "Give a natural sounding output of not more that 50 words "
                            "with recommendations in point-form on how this can affect farming."
                        )
                        final_response = get_openai_response(openai_input)

                except Exception as e:
                    final_response = f"Error fetching weather data: {str(e)}"

        elif intent.strip().lower() == 'plant_disease':
            final_response = identify_disease(english_input)
        elif intent.strip().lower() == 'farming_advice':
            final_response = get_farming_advice(english_input)
        elif intent.strip().lower() == 'generic_conversation':
            final_response = generic(english_input)
        else:
            final_response = "Generic Intent"

    # Step 4: Process Image if provided
    if image_file:
        try:
            predicted_class_name = process_image(image_file)
            image_response = f"Detected disease: {predicted_class_name}."

            # Enhance with OpenAI insights
            openai_input = f"This is a plant disease prediction result: {predicted_class_name}. Provide more insights.Your output should sound natural and human-like. use no more than 50 words."
            openai_response = get_openai_response(openai_input)
            image_response += f"\n\n{openai_response}"
            final_response += f"\n\n{image_response}" if final_response else image_response

        except Exception as e:
            print(f"Image processing error: {e}")
            final_response += f"\n\nError processing image: {str(e)}"

    # Step 5: Translate response back to user's language
    if original_lang != "en":
        final_output = translate_back(final_response, original_lang, translator_used)
    else:
        final_output = final_response

    # Step 6: Return the response
    return JsonResponse({
        # "original_language": original_lang,
        # "translator_used": translator_used,
        # "intent": intent,
        # "user_input": user_input,
        "ai_response": final_response,
        "final_output": final_output
    })

def process_image(image_file):
    """
    Process the uploaded image and return the predicted class name.
    """
    from io import BytesIO
    img_io = BytesIO(image_file.read())
    img_io.seek(0)

    img = image.load_img(img_io, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    input_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)
    predictions = predict_fn(input_tensor)
    prediction = list(predictions.values())[0].numpy()
    class_idx = np.argmax(prediction, axis=-1)
    return class_names[class_idx[0]]
