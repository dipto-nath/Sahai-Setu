import asyncio
import os
from google import genai

async def test():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    try:
        response = await client.aio.models.generate_content(
            model="gemini-1.5-flash",
            contents="test"
        )
        print("1.5-flash OK", response.text)
    except Exception as e:
        print("1.5-flash ERROR:", e)

    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents="test"
        )
        print("2.5-flash OK", response.text)
    except Exception as e:
        print("2.5-flash ERROR:", e)

asyncio.run(test())
