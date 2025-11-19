import requests
import json

url = "http://127.0.0.1:8000/api/v1/genres/variations"
payload = {
    "super_genre": "Electronic",
    "num_variations": 5
}

try:
    print(f"Testing API: {url}")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        variations = data.get("data", [])
        print(f"✅ Success! Got {len(variations)} variations.")
        for v in variations:
            print(f"- {v.get('subgenre')}: {v.get('description')}")
            
        # Check if generic
        if "Style 1" in str(variations):
            print("\n❌ FAILURE: Still receiving generic 'Style X' names.")
        else:
            print("\n✅ SUCCESS: Received real subgenre names.")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"❌ Exception: {e}")
