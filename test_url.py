import requests

ENDPOINT = "https://discjnb22222.cognitiveservices.azure.com"
KEY = "3d7a4fc3a37e49de960d4038bc55bf1f"
MODEL_ID = "modelo_entrega_jnb"

# Variaciones de URL a probar
urls = [
    f"{ENDPOINT}/documentintelligence/document-models/{MODEL_ID}:analyze?api-version=2024-11-30",
    f"{ENDPOINT}/document-intelligence/analyze:build-model/{MODEL_ID}?api-version=2024-11-30",
    f"{ENDPOINT}/document-models/{MODEL_ID}:analyze?api-version=2024-11-30",
    f"{ENDPOINT}/documentintelligence/analyze/{MODEL_ID}?api-version=2024-11-30",
]

headers = {
    "Ocp-Apim-Subscription-Key": KEY,
    "Content-Type": "application/octet-stream"
}

# Leer un PDF pequeño para probar
pdf_path = "REPSOL1.pdf"
with open(pdf_path, "rb") as f:
    pdf_data = f.read()

print("Probando diferentes URLs...\n")
for i, url in enumerate(urls, 1):
    try:
        print(f"{i}. {url}")
        response = requests.post(url, headers=headers, data=pdf_data, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code != 202:
            print(f"   Response: {response.text[:300]}")
        else:
            print(f"   ✓ ÉXITO - Operación aceptada!")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")
