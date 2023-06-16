from flask import Flask, render_template
from flask import jsonify
import requests
from bs4 import BeautifulSoup
import openai
import random
import os
import json



app = Flask(__name__)

# Load OpenAI API key from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")
API_ENDPOINT = "https://api.openai.com/v1/chat/completions"

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
    prompts = [
        f"As a poet and an art critic with deep knowledge of art history, imagine you are observing '{title}' by {artist}. Provide a detailed interpretation of the artwork based on the title and the artist's style. Discuss the potential themes, emotions, and artistic techniques that might be present in this piece. Additionally, write three words that you think could describe this artwork. In a concise sentence, explain how this artwork could resonate with our current society, considering the period and location it was created in (if possible or relevant)",
        f"Imagine yourself standing in front of '{title}' by {artist} as a poet and an artist. Describe the emotions that arise within you based on the title and the artist's reputation. Write a short paragraph about how you believe this artwork connects with the viewer on an emotional level. Use your imagination to explore the potential composition, color palette, and subject matter that could be present in this artwork. Consider the period and location it was created in (if possible) and discuss how it might reflect the societal and cultural influences of that time.",
        f"Based on the title and the artist's name, provide an interesting fact or detail about '{title}' by {artist} or similar artworks from the same period and location. Use your knowledge of art history to explain how this fact contributes to our understanding of the piece. Discuss the potential artistic movements, historical events, or cultural influences that might have shaped this artwork. Feel free to speculate on the techniques, subject matter, or symbolism that could be present, considering the context in which it was created.",
    ]

    prompt = random.choice(prompts)

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
    painting_json = json.dumps(painting)
    return render_template('index.html', painting=painting, painting_json=painting_json)

@app.route('/refresh')
def refresh():
    painting = scrape_painting()
    painting_info = generate_artwork_info(painting["artist"], painting["title"])
    painting["info"] = painting_info
    return jsonify(painting)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
