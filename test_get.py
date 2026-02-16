import requests
import json

ENDPOINT = "https://discjnb22222.cognitiveservices.azure.com"
KEY = "3d7a4fc3a37e49de960d4038bc55bf1f"
MODEL_ID = "modelo_entrega_jnb"

headers = {
    "Ocp-Apim-Subscription-Key": KEY
}

# Pruebas diversas de GET para verificar el recurso
urls_get = [
    f"{ENDPOINT}/documentintelligence/document-models/{MODEL_ID}?api-version=2024-11-30",
    f"{ENDPOINT}/documentintelligence/document-models?api-version=2024-11-30",
    f"{ENDPOINT}/document-models/{MODEL_ID}?api-version=2024-11-30",
]

print("Probando GET requests...\n")
for i, url in enumerate(urls_get, 1):
    try:
        print(f"{i}. {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        try:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:400]}")
        except:
            print(f"   Response: {response.text[:300]}")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")
