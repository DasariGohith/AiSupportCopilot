import os
from openai import OpenAI

# Check if API key is set
api_key = os.environ.get("OPENAI_API_KEY")
print(f"API Key present: {bool(api_key)}")
print(f"API Key starts with: {api_key[:20] if api_key else 'None'}...")

# Test basic OpenAI client
try:
    client = OpenAI(api_key=api_key)
    print("OpenAI client created successfully")
    
    # Try a simple API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say hello"}
        ],
    )
    print("API Response:", response.choices[0].message.content)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
