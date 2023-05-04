from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import openai
import requests
import random
import os
import json



app = Flask(__name__)

# Load OpenAI API key from environment variables
gpt4_api_key = os.environ.get("GPT4_API_KEY")

def scrape_painting():
    api_key = os.environ.get("HARVARD_API_KEY")
    url = f"https://api.harvardartmuseums.org/object?apikey={api_key}&size=100&sort=random&classification=Paintings&hasimage=1&sortorder=asc"
    response = requests.get(url)
    print(f"URL: {url}")
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")
    data = response.json()

    if "records" not in data or not data["records"]:
        return {
            "image_url": None,
            "title": None,
            "artist": None,
            "date": None
        }

    painting = random.choice(data["records"])

    image_url = painting["primaryimageurl"]
    title = painting["title"]
    artist = painting["people"][0]["name"] if "people" in painting and painting["people"] else "Unknown artist"
    date = painting["dated"]

    return {
        "image_url": image_url,
        "title": title,
        "artist": artist,
        "date": date
    }

def generate_chat_completion(messages, model="gpt-4", temperature=1, max_tokens=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GPT4_API_KEY}",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def generate_artwork_info(artist, title):
    prompts = [
        f"You are an art critic and poet, make a deep interpretation of '{title}' by {artist}. Write 3 words this artwork inspires you. Make it short if possible in bullet points. Include a short section that explains how it could resonate with our current society.",
        f"Describe the emotions that '{title}' by {artist} evokes in you. Write a short paragraph about how this artwork connects with the viewer on an emotional level.",
        f"Provide a random fact or interesting detail about '{title}' by {artist} or similar artworks. Explain how this fact contributes to the overall understanding of the piece.",
    ]

    prompt = random.choice(prompts)

    # Call the GPT-4 API
    def gpt4_request(prompt, max_tokens=150, temperature=0.7):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {gpt4_api_key}",
        }
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

    response_text = gpt4_request(prompt)
    return response_text


@app.route('/')
def painting_of_the_day():
    painting = scrape_painting()
    painting_info = generate_artwork_info(painting["artist"], painting["title"])
    painting["info"] = painting_info
    return render_template("index.html", painting=painting)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
