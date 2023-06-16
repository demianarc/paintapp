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
        f"As an art historian with access to a vast knowledge base, explore the historical and cultural context surrounding '{title}' by {artist}. Discuss the artist's background and the broader artistic movement of that period. Uncover the societal influences and prevailing themes of the time, offering valuable insights into the artwork's significance and its connection to the artist's overall body of work.",
        f"Delve into the historical and cultural significance of '{title}' by {artist}. Explore the artist's background, the prevailing artistic trends of the time, and the social context in which the artwork was created. Provide insights into how this piece reflects or challenges the conventions of its era, shedding light on the artist's intentions and the audience's reception. If the artist is unknown, speculate on the possible influences and cultural implications of the artwork. Help the viewer immerse themselves in the painting's world by providing vivid emotional context.",
        f"Explore the artistic legacy of {artist} through their notable works. While '{title}' may not be their most iconic piece, it offers an opportunity to discuss the recurring themes, techniques, and distinctive characteristics found in the artist's body of work. Examine how this artwork aligns with their oeuvre, discussing the influence and significance of their other renowned works. Imagine the emotions that this artwork conveys to the viewer and describe them in detail.",
    ]

    prompt = random.choice(prompts)

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=400,
        n=1,
        stop=None,
        temperature=0.7,
    )

    text = response.choices[0].text.strip()

    # Check if the last sentence is incomplete and remove it if necessary
    sentences = text.split(".")
    if len(sentences) > 1 and not sentences[-1]:
        text = ".".join(sentences[:-1]).strip()

    return text


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
