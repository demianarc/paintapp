from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import openai
import random
import os


app = Flask(__name__)

# Load OpenAI API key from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")

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

def generate_artwork_info(artist, title):
    prompt = f"You are an art critic and poet, make a deep interpretation of '{title}' by {artist}. Write 3 words this artworks inspires you. Make it short if possible in bullet points. Include a short section that explains how it could resonate with our current society"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )

    return response.choices[0].text.strip()


@app.route('/')
def painting_of_the_day():
    painting = scrape_painting()
    painting_info = generate_artwork_info(painting["artist"], painting["title"])
    painting["info"] = painting_info
    return render_template('index.html', painting=painting)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
