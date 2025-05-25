from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import requests
from .utils import classify_intent, extract_city  
from plant_disease.views import get_openai_response

from plant_disease.views import identify_disease
# from plant_disease.views import get_weather  
from plant_disease.views import get_farming_advice


def handle_intent(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')

        if not user_input:
            return JsonResponse({'response': 'No input provided.'}, status=400)

        # Classify the intent using Azure OpenAI
        intent = classify_intent(user_input)
        print(f"Classified intent: {intent}")

        if intent.strip().lower() == 'weather_query':
            print("Intent is weather_query")
            city = extract_city(user_input)
            print("Extracted city:", city)
            if city:
                weatherkey = settings.WEATHER_API_KEY
                url = f"http://api.weatherapi.com/v1/current.json?key={weatherkey}&q={city}"

                try:
                    response = requests.get(url)
                    response.raise_for_status()  # Raise an exception for bad status codes
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

                    # Assuming get_openai_response is defined elsewhere
                    openai_input = f"Here is a weather report for {city}: {weather_info}. It indicates the temperature, condition,humidity, and wind speed. Provide a concise, to the point, natural-sounding summary with recommendations in point-form as to how this can affect farming."
                    openai_response = get_openai_response(openai_input)

                    return JsonResponse({
                        'weather_info': weather_info,
                        'openai_response': openai_response
                    })

                except requests.exceptions.RequestException as e:
                    return JsonResponse({"error": f"Error fetching weather data: {str(e)}"}, status=500)
            else:
                return JsonResponse({'response': 'City not found in input.'})
        elif intent.strip().lower() == 'plant_disease':
            print("Intent is plant_disease")
            disease_info = identify_disease(user_input)
            return JsonResponse({'response': disease_info})
        elif intent.strip().lower() == 'farming_advice':
            print("Intent is farming_advice")
            farming_advice = get_farming_advice(user_input)
            return JsonResponse({'response': farming_advice})
        else:
            print("Intent not recognized")
            return JsonResponse({'response': 'Intent not recognized.'})

    return JsonResponse({'response': 'Invalid request method.'}, status=405)