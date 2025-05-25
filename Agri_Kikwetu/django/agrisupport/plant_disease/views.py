import tensorflow as tf
import numpy as np
import requests
from django.http import JsonResponse
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from tensorflow.keras.preprocessing import image
from .serializers import PlantImageSerializer
import openai
from openai import AzureOpenAI
from django.views.decorators.csrf import csrf_exempt

# Azure OpenAI settings
openai.api_key = settings.OPENAI_API_KEY
openai.api_base = settings.OPENAI_API_ENDPOINT  # Azure OpenAI endpoint
openai.api_type = settings.OPENAI_API_TYPE  
openai.api_version = settings.OPENAI_API_VERSION  

client = AzureOpenAI(
    api_key=settings.OPENAI_API_KEY,
    api_version=settings.OPENAI_API_VERSION,
    azure_endpoint=settings.OPENAI_API_ENDPOINT
)

def get_openai_response(user_input):
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_DEPLOYMENT_NAME,  
            messages=[{"role": "user", "content": user_input}],
            max_completion_tokens=1500
        )
        print("🔍 RAW Azure Response:", response)  
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"💥 Azure OpenAI Error: {e}")
        return "Sorry, I couldn't process your request right now."

# def get_openai_response(user_input):
#     try:
#         response = client.chat.completions.create(
#             model=settings.OPENAI_DEPLOYMENT_NAME,
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant for farming and plant disease queries."},
#                 {"role": "user", "content": user_input}
#             ],
#             max_completion_tokens=1000  # Reduced for faster, safer responses
#         )
#         print("🔍 RAW Azure Response:", response)  # Debugging the full response structure

        # # Validate response structure and content
        # if "choices" in response and len(response["choices"]) > 0:
        #     message_content = response["choices"][0].get("message", {}).get("content", "").strip()
        #     if message_content:
        #         return message_content
        
        # return "Sorry, I couldn't process your request right now."

    # except Exception as e:
    #     print(f"💥 Azure OpenAI Error: {e}")
    #     return "Sorry, I couldn't process your request right now."



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

# View for uploading images for plant disease prediction
class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Handle file uploads

    def post(self, request, *args, **kwargs):
        serializer = PlantImageSerializer(data=request.data)
        if serializer.is_valid():
            img = serializer.validated_data['image']

            try:
                from io import BytesIO
                img_io = BytesIO(img.read())
                img_io.seek(0)

                img = image.load_img(img_io, target_size=(224, 224))
                img_array = image.img_to_array(img)
                img_array = np.expand_dims(img_array, axis=0)
                img_array = img_array / 255.0

                # Converting the image array to a tensor for prediction
                input_tensor = tf.convert_to_tensor(
                    img_array, dtype=tf.float32)

                # Making the prediction
                predictions = predict_fn(input_tensor)
                prediction = list(predictions.values())[0].numpy()

                # Getting the predicted class index and corresponding class name
                class_idx = np.argmax(prediction, axis=-1)
                predicted_class_name = class_names[class_idx[0]]

                # Passing the prediction to OpenAI to generate a response
                openai_input = f"This is a plant disease prediction result: {predicted_class_name}. Provide more insights.Your output should sound natural and human-like.Limit your response to 50 words."
                openai_response = get_openai_response(openai_input)

                return JsonResponse({'prediction': predicted_class_name, 'openai_response': openai_response})

            except Exception as e:
                return JsonResponse({'error': f'Error processing image: {str(e)}'}, status=400)

        return JsonResponse({'error': 'Invalid image'}, status=400)


# View for getting weather information
def get_weather(request):
    city = request.GET.get('city', 'Nairobi')  # Default to Nairobi if no city is provided
    weatherkey = settings.WEATHER_API_KEY  
    url = f"http://api.weatherapi.com/v1/current.json?key={weatherkey}&q={city}"

    try:
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            return JsonResponse({"error": "Unable to fetch weather data."}, status=400)

        weather_info = {
            "city": city,
            "temperature": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"],
            "wind_speed": data["current"]["wind_kph"],
        }

        # Passing the weather info to OpenAI to generate a response
        openai_input = f"Here is a weather report for {city}: {weather_info}. It indicates the temperature, condition,humidity, and wind speed. Provide a concise, to the point, natural-sounding summary with recommendations in point-form as to how this can affect farming. Your output should be no more than 50 words."
        openai_response = get_openai_response(openai_input)

        return JsonResponse({
            'weather_info': weather_info,
            'openai_response': openai_response
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# Text-based plant disease identification using OpenAI
def identify_disease(user_input):
    """
    This function handles disease-related queries via text using Azure OpenAI.
    """
    prompt = f"A farmer asked this about their crops: '{user_input}'. Provide a helpful, natural-sounding response assuming the user is describing plant disease symptoms. Your response should be no more than 50 words"
    
    try:
        response = get_openai_response(prompt)
        return response
    except Exception as e:
        return f"Sorry, I couldn’t understand the plant issue right now. Error: {str(e)}"
    
def get_farming_advice(user_input):
    prompt = (
            f"The user asked the following farming-related question: \"{user_input}\". "
            "Respond in a natural, helpful tone. Be concise but informative. Use point-form if necessary. "
            "No more than 50 words in your output. "
        )
    try:
        response = get_openai_response(prompt)
        return response
    except Exception as e:
        return "Sorry, I couldn't provide farming advice at the moment."
    
def generic(user_input):
    """
    This function handles generic conversations using Azure OpenAI.
    """
    prompt = f"The user said: '{user_input}'. Respond in a friendly, conversational manner.Identify yourself as AGRI-KIKWETU bot, a helpful assistant for farmers in Kenya. Provide a natural-sounding response.If asked who created you, say Patricia Muriira, a Kenyan software engineer, and that you are a project of the Agri-Kikwetu initiative. Your response should be no more than 50 words." 
    
    try:
        response = get_openai_response(prompt)
        return response
    except Exception as e:
        return f"Sorry, I couldn’t understand your message right now. Error: {str(e)}"

# View for OpenAI chatbot
@csrf_exempt
def chat_with_bot(request):
    if request.method == 'POST':
        user_input = request.POST.get('message', '')  # Get the message from the POST request
        
        if user_input:  # Ensure there's a message from the user
            # Call the Azure OpenAI function to get the response
            response_text = get_openai_response(user_input)
            return JsonResponse({'response': response_text})  # Send back the OpenAI response
        
        else:
            # If no message was provided, return an error
            return JsonResponse({'error': 'No message provided'}, status=400)

    # If the request method is not POST, return a method error
    return JsonResponse({'error': 'Invalid request method'}, status=405)
