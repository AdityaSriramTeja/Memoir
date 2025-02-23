import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from spacy.lang.en import English
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from bertopic.representation import MaximumMarginalRelevance
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic import BERTopic
import json
import requests
import re
import models
from database import engine, SessionLocal

load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
API_KEY = os.getenv("API_KEY")

app = FastAPI()

# IF YOU MODIFY TABLES, DROP ALL TABLES FIRST
# models.Base.metadata.drop_all(bind=engine)

# creates tables and cols in database
models.Base.metadata.create_all(bind=engine, checkfirst=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TextInput(BaseModel):
    text: str

def initialize_nlp_pipeline():
    nlp = English()
    nlp.add_pipe("sentencizer")
    return nlp

def initialize_models():
    embedding_model_name = "all-mpnet-base-v2"
    embedding_model = SentenceTransformer(embedding_model_name)
    umap_model = UMAP(n_neighbors=3, n_components=2, min_dist=0.0, metric='cosine', random_state=42)
    hdbscan_model = HDBSCAN(min_cluster_size=2, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    vectorizer_model = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    representation_model = MaximumMarginalRelevance(diversity=0.4)
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)

    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        representation_model=representation_model,
        ctfidf_model=ctfidf_model,
        language="english",
        calculate_probabilities=True,
        verbose=True
    )

    return topic_model, embedding_model


def get_topic_number_and_keywords(topic_model):
    data =[]
    topic_info = topic_model.get_topic_info()

    for topic in topic_info[topic_info["Count"] > 0].itertuples():  # Filter significant topics
        if topic.Topic == -1:
            continue
        data.append(
            {"Topic": f"{topic.Topic}: {topic.Name}",
             "Keywords": topic_model.get_topic(topic.Topic)
             })
    return data

def get_topics_taxonomy(all_topic_names, topic_keywords, API_KEY):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={API_KEY}"

    payload = json.dumps({
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""
Generate a hierarchical sequence of topics, moving from a broad root category to a specific subcategory that aligns with a given topic and its associated keywords.

Each topic index must be assigned exactly one structured hierarchy, ensuring coherence, depth, and a logical transition from general to specific.

### Rules & Requirements:

1. **General to Specific Flow**
   - Each sequence must start with a broad category and progressively narrow down to a specific subcategory that represents the topic’s keywords.
   - The final level must be highly relevant to the keywords but not overly specific (no random numbers or unrelated words).

2. **One Hierarchy Per Topic (Strict Enforcement)**
   - Each topic index must appear exactly once in the output.
   - No duplicates, no missing topics, no extra sequences.

3. **Logical & Coherent Structure**
   - The hierarchy must follow a natural progression (e.g., "Computer Networks > Network Troubleshooting > Traceroute Analysis" is valid; "Networking > Computers > Analysis" is not).
   - Each sublevel must be a logical subcategory of the previous level.

4. **Balanced Depth (3 to 5 Levels)**
   - The hierarchy must be neither too shallow nor excessively deep.
   - Aim for 3 to 5 levels before reaching the topic index.

5. **Reuse Existing Topics for Consistency**
   - If a similar broad topic already exists, reuse it instead of creating a redundant one.
   - Example: If "Cybersecurity" exists, use it instead of "Information Security."

6. **Meaningful & Relevant Leaf Nodes**
   - The final category before the topic index must be specific but general enough to capture the essence of the keywords.
   - Avoid numbers, overly specific terms, or meaningless end nodes.

7. **Output Format (Strict JSON Array Format)**
   - The output must be a structured JSON array with each hierarchy as a single string, separated by " > ".
   - Example output:
     ```json
     [
       "Computer Science > Networking > Network Troubleshooting > Traceroute Analysis > 0_orbis_net_traceroute_tracert",
       "Computer Science > Networking > Network Diagnostics > Ping & Connectivity Issues > 1_interface_ping_default_subnet"
     ]
     ```
   - Each sequence must align perfectly with the provided keywords while maintaining logical structure and consistency.

### Input Data:
**Existing Topics List:**
{all_topic_names}

**Keywords and Their Indexes:**
{topic_keywords}

### Final Notes:
- The taxonomies must be robust, meaningful, and comprehensive.
- Each topic must be categorized in the best possible hierarchy.
- Ensure perfect balance and alignment between the topic’s broader field and its keywords while maintaining a logical structure.
"""
                    }
                ]
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    # print("LLM response:", data)
    raw_text = data["candidates"][0]['content']['parts'][0]['text']
    clean_text = raw_text.strip("```json").strip("```").strip()
    return clean_text

def format_json_string(json_string: str):
    """Formats a given JSON-like string into a Python list."""
    match = re.search(r'\[.*\]', json_string, re.DOTALL)
    if match:
        clean_text = match.group(0)
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            print("Warning: Could not parse JSON, returning as a string.")
            return clean_text
    else:
        print("No valid list found.")
        return []

def generate_keywords_and_topic_identity(formatted_list):
    keywords = set()
    identity = {}
    keywords_layer = []
    for i, val in enumerate(formatted_list):
        temp = val.split(" > ")
        keywords_layer.append(temp[:-1])
        for idx in range(len(temp)-1):
            keywords.add(temp[idx])
        identity[i] = temp[-2]
    return keywords, identity, keywords_layer
