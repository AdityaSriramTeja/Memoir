from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from spacy.lang.en import English
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from bertopic import BERTopic
from bertopic.representation import MaximalMarginalRelevance
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic import BERTopic
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
import json
import requests
import numpy as np
import re
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session


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
    representation_model = MaximalMarginalRelevance(diversity=0.4)
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



def store_topics_in_db(db, topic_keywords, all_topic_names):
    for topic in topic_keywords:
        if topic not in all_topic_names:
            db_topic = models.Topics(name=topic)
            db.add(db_topic)
            db.commit()
            db.refresh(db_topic)

def store_connections_in_db(db, keywords_layer, all_topic_names, all_topics):

    for layer in keywords_layer:
        for source_idx in range(len(layer)-1):
            target_idx = source_idx + 1
            if (layer[source_idx] not in all_topic_names or layer[target_idx] not in all_topic_names):
                continue

            query_source = [topic for topic in all_topics if topic.name == layer[source_idx]][0]
            query_target = [topic for topic in all_topics if topic.name == layer[target_idx]][0]

            insert_stmt = insert(models.Connections).values(source_topic=query_source.id, target_topic=query_target.id)
            do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['source_topic', 'target_topic'])
            db.execute(do_nothing_stmt)

def store_sources_in_db(db, documents, topics, embeddings, reduced_embeddings, identity, url, page_type):
    data = []
    for doc, topic, embedding, vector_2d in zip(documents, topics, embeddings, reduced_embeddings):
        if topic == -1 or topic not in identity:
            continue

        data.append({"Document": doc, "Assigned Topic": identity[topic]})

        queried_topic = db.query(models.Topics).filter(models.Topics.name == identity[topic]).first()

        new_sources = models.Sources(topic_id=queried_topic.id, vector_2d=vector_2d, vector_768d=embedding, url=url, page_type=page_type, content=doc)
        db.add(new_sources)
        db.commit()
        db.refresh(new_sources)
    return data

def split_into_chunks(sentences, slice_size) -> list[list[str]]:
    return [sentences[i:i + slice_size] for i in range(0, len(sentences), slice_size)]


@app.get("/get_relevant_articles")
async def get_articles(text: str, db: Session = Depends(get_db)):
    embedding_model = SentenceTransformer("all-mpnet-base-v2")
    embedding = embedding_model.encode([text])[0]
    similar_document = db.scalars(select(models.Sources).order_by(models.Sources.vector_768d.cosine_distance(embedding)).limit(5))
    documents = []
    for document in similar_document:
        documents.append({
            "content": document.content,
            "url": document.url,
            "page_type": document.page_type,
            "vector_2d": document.vector_2d.tolist() if isinstance(document.vector_2d, np.ndarray) else document.vector_2d
        })
    return documents

# @app.get("/get_topic_graph")
# async def get_topic_graph(query_topic: str, db: Session = Depends(get_db)):
#     return "FIX THIS"

@app.post("/process_text")
async def process_text(content: TextInput, url: TextInput, page_type: TextInput, db: Session = Depends(get_db)):
    content.text = content.text.replace("\n", " ").strip()
    content.text = content.text.replace("\\", " ").strip()

    # use bs4 to get all the text from content
    soup = BeautifulSoup(content.text, 'html.parser')
    if page_type.text == "chatgpt":
        # Find all agent turns and join their text with spaces
        agent_turns = soup.find_all("div", class_="agent-turn")
        content.text = ' '.join(turn.get_text() for turn in agent_turns) if agent_turns else soup.get_text()
    else:
        content.text = soup.get_text()

    # filter all non-alphanumeric characters
    content.text = re.sub(r'[^A-Za-z0-9(),./;:\'"\[\]{}_-]', ' ', content.text)

    nlp = initialize_nlp_pipeline()
    doc = nlp(content.text)
    sentences = list(doc.sents)
    sentences = [str(sentences) for sentences in sentences]
    chunk_size = 5
    sentence_chunks = split_into_chunks(sentences, chunk_size)

    documents = []
    for chunk in sentence_chunks:
        joined_chunk = "".join(chunk).replace("  ", " ").strip()
        joined_chunk = re.sub(r'\.([A-Z])', r'. \1', joined_chunk)
        documents.append(joined_chunk)

    topic_model, embedding_model = initialize_models()
    embeddings = embedding_model.encode(documents)
    topics, _ = topic_model.fit_transform(documents, embeddings)
    all_topic_names = set([topic.name for topic in get_all_topics(db)])
    print("Getting topic number and keywords")
    topic_keywords = get_topic_number_and_keywords(topic_model)
    print("Getting topics taxonomy")
    taxonomy = get_topics_taxonomy(all_topic_names, topic_keywords, API_KEY)
    formatted_list = format_json_string(taxonomy)
    topic_keywords, identity, keywords_layer = generate_keywords_and_topic_identity(formatted_list)
    print("Storing topics in db")
    store_topics_in_db(db, topic_keywords, all_topic_names)
    new_all_topics = get_all_topics(db)
    new_all_topic_names = set([topic.name for topic in new_all_topics])
    store_connections_in_db(db, keywords_layer, new_all_topic_names, new_all_topics)
    print("Storing sources in db")
    reduced_embeddings = UMAP(n_neighbors=3, n_components=2, min_dist=0.0, metric='cosine', random_state=42).fit_transform(embeddings)
    data = store_sources_in_db(db, documents, topics, embeddings, reduced_embeddings, identity, url.text, page_type.text)

    # Store URL in websites table if it doesn't exist
    existing_website = db.query(models.Websites).filter(models.Websites.url == url.text).first()

    if not existing_website:
        new_website = models.Websites(url=url.text, content=content.text, page_type=page_type.text)
        db.add(new_website)
        db.commit()
        db.refresh(new_website)
    print("Successfully added source to Memoir")
    return {"message": data}

def get_all_topics(db: Session = Depends(get_db)):
    db_topics = db.query(models.Topics).all()
    return db_topics

def get_all_connections(db: Session = Depends(get_db)):
    db_connections = db.query(models.Connections).all()
    return db_connections

@app.get("/get_all_topics")
async def get_all_topics_request(db: Session = Depends(get_db)):
    db_topics = db.query(models.Topics).all()
    return db_topics

@app.get("/get_all_connections")
async def get_all_connections_request(db: Session = Depends(get_db)):
    db_connections = db.query(models.Connections).all()
    return db_connections

@app.get("/get_all_sources")
async def get_all_sources(db: Session = Depends(get_db)):
    db_sources = db.query(models.Sources).all()
    # Convert SQLAlchemy objects to dictionaries and remove the 768d vector
    data = []
    for source in db_sources:
        source_dict = {
            "id": source.id,
            "topic_id": source.topic_id,
            "vector_2d": source.vector_2d.tolist() if hasattr(source.vector_2d, 'tolist') else source.vector_2d,
            "url": source.url,
            "page_type": source.page_type,
            "content": source.content
        }
        data.append(source_dict)
    return data

@app.get("/get_all_websites")
async def get_all_websites(db: Session = Depends(get_db)):
    db_websites = db.query(models.Websites).all()
    return db_websites
