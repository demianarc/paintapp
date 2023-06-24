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
        f"As an art historian, you have the unique opportunity to provide context and insights into '{title}' by {artist}. Explore the artist's background, their artistic style, and any significant events or influences that shaped their work. Describe the themes, subjects, and techniques employed in this artwork, and speculate on their significance. Share your expertise and enlighten the viewer about the artist's intentions and the artwork's place within their body of work.",
        f"Transport yourself to the world of {artist} as you analyze '{title}'. While some details about the artwork may be unknown, use your expertise to draw connections between the artist's known works and this piece. Discuss the potential inspirations, cultural influences, or personal experiences that could have informed the creation of this artwork. Provide a thoughtful interpretation that considers the artist's broader context and their unique artistic journey.",
        f"Step into the realm of '{title}', a captivating creation by {artist}. Acknowledge the limitations of the available information and approach the artwork with an open mind. Share your interpretation, exploring potential narratives, emotions, and symbolic elements present in the artwork. Consider how this artwork fits into the artist's larger body of work and discuss any intriguing or unique aspects that set it apart. Engage the viewer with your thoughtful analysis and invite them to discover their own connection.",
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
