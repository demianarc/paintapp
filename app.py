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
    century = painting.get("century", "Unknown century")
    culture = painting.get("culture", "Unknown culture")
    medium = painting.get("medium", "Unknown medium")
    dimensions = painting.get("dimensions", "Unknown dimensions")
    exhibitionhistory = painting.get("exhibitionhistory", "No known exhibition history")
    creditline = painting.get("creditline", "Unknown credit line")

    return {
        "image_url": image_url,
        "title": title,
        "artist": artist,
        "date": date,
        "century": century,
        "culture": culture,
        "medium": medium,
        "dimensions": dimensions,
        "exhibitionhistory": exhibitionhistory,
        "creditline": creditline
    }

def generate_artwork_info(artist, title, century, culture, medium, dimensions, exhibitionhistory, creditline):
    prompts = [
        f"As an art historian with access to a vast knowledge base, explore the historical and cultural context surrounding '{title}' by {artist}. Discuss the artist's background, the broader artistic movement of the {century}, and the influence of the {culture}. Discuss the artist's choice of {medium} and the implications of the artwork's {dimensions}. Uncover the societal influences and prevailing themes of the time, offering valuable insights into the artwork's significance and its connection to the artist's overall body of work. Reflect on its {exhibitionhistory} and its {creditline}.",
        f"Delve into the historical and cultural significance of '{title}' by {artist}. Explore the artist's background, the prevailing artistic trends of the {century}, and the social context in which the artwork was created. Discuss the use of {medium} and the impact of the artwork's {dimensions}. Reflect on the artwork's {exhibitionhistory} and its {creditline}. Provide insights into how this piece reflects or challenges the conventions of its era, shedding light on the artist's intentions and the audience'sresponse at the time. Consider the influence of the {culture} on the artwork.",
        f"Analyze '{title}' by {artist}, a work of art from the {century}. Explore the historical and cultural context, focusing on the influence of the {culture}. Discuss the artist's use of {medium} and the impact of the {dimensions}. Reflect on its {exhibitionhistory} and consider its {creditline}. What does this piece reveal about the artistic, social, and political currents of its time? How does it reflect the artist's perspective and intent?"
    ]

    prompt = random.choice(prompts)

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=230,
        n=1,
        stop=None,
        temperature=0.7,
    )

    text = response.choices[0].text.strip()

    # Check if the last sentence is incomplete and remove it if necessary
    sentences = text.split(".")
    if len(sentences) > 1 and not sentences[-1]:
        text = ".".join(sentences[:-1]).strip()

    # Limit the maximum number of sentences to avoid cutoffs
    MAX_SENTENCES = 4
    if len(sentences) > MAX_SENTENCES:
        text = ".".join(sentences[:MAX_SENTENCES]).strip()

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
