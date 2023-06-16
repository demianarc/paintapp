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
        f"As an art expert and critic, dive into the emotional landscape of '{title}' by {artist}. Imagine yourself immersed in the artwork and describe the emotions it evokes within you. Explore how the composition, color palette, and subject matter contribute to these emotions. Utilize the knowledge base to provide relevant context about the period and location in which the artwork was created. Help the viewer to relate and connect with the artwork's emotional essence.",
        f"Imagine you are an art critic experiencing '{title}' by {artist}. Write a heartfelt description of how this artwork communicates with the viewer on an emotional level. Reflect on the artist's style and techniques used to evoke specific emotions. Utilize the knowledge base to provide information about the period and location in which the artwork was created. Help the viewer immerse themselves in the painting's world by providing vivid emotional context.",
        f"Immerse yourself in the world of '{title}' by {artist} as an art expert. Imagine the emotions that this artwork conveys to the viewer and describe them in detail. Reflect on the artist's techniques and artistic choices that contribute to the emotional impact. Utilize the knowledge base to provide insights about the period and location in which the artwork was created. Provide the viewer with a rich emotional and contextual understanding of the artwork.",
    ]

    prompt = random.choice(prompts)

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=500,  # Adjust the value as per your preference
        temperature=0.7,
        n=1,
        stop=None,
        temperature=0.7,
    )

    text = response.choices[0].text.strip()

    # Ensure the response ends with a complete sentence
    sentences = text.split(".")
    while len(sentences) > 1 and len(".".join(sentences)) > 400:
        sentences = sentences[:-1]

    return ".".join(sentences).strip()


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
