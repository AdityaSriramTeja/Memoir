import requests
import json
import models
from database import engine

BASE_URL = "http://localhost:8000"

def erase_all_tables():
    models.Base.metadata.drop_all(bind=engine)

def test_process_text(filename):
    print(f"\nTesting /process_text endpoint with {filename}...")
    url = f"{BASE_URL}/process_text"

    # Read the content from the specified text file
    try:
        with open(filename, 'r', encoding="utf8") as file:
            text_content = file.read()
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return

    payload = {
        "content": {
            "text": text_content
        },
        "url": {
            "text": "www.example.com/networking"
        },
        "page_type": {
            "text": "article"
        }
    }

    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_get_articles():
    print("\nTesting /get_articles endpoint...")
    query = "What tunneling protocols does ngrok use?"
    url = f"{BASE_URL}/get_articles?text={query}"

    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_get_topic_graph():
    print("\nTesting /get_topic_graph endpoint...")
    # test_topics = [
    #     "Artificial Intelligence",
    #     "Computer Science",
    #     "Networking",
    #     "Philosophy"
    # ]

    # for topic in test_topics:
    #     print(f"\nTesting with topic: {topic}")
    #     url = f"{BASE_URL}/get_topic_graph?topic={topic}"

    #     try:
    #         response = requests.get(url)
    #         print(f"Status Code: {response.status_code}")
    #         print("Response:")
    #         print(json.dumps(response.json(), indent=2))
    #     except Exception as e:
    #         print(f"Error: {e}")

    topic = "Artificial Intelligence"
    print(f"\nTesting with topic: {topic}")
    url = f"{BASE_URL}/get_topic_graph?topic={topic}"

    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # delete all tables
    erase_all_tables()
    # Test process_text for each of the four longtext files
    # for i in range(5, 8):
    #     filename = f"longtext{i}.txt"
    #     test_process_text(filename)
    # # Run the get_articles test once after processing all texts
    # test_get_articles()
    # test_get_topic_graph()
