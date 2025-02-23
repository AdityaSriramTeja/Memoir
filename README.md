## Introduction.

In today’s fast paced digital world, we consume vast amounts of information from various sources — videos, articles, podcasts, research papers, course content, and more. However, efficiently organizing, retaining and recalling this information remains a challenge. Memoir is designed to address this problem by dynamically structuring and retrieving knowledge based on user interactions.

## Problem Statement

Traditional bookmarking bookmarking methods fail to provide an intuitive way to organize and recall information effectively. Users often struggle to find relevant content when needed, leading to a cognitive overload and wasted time. Existing tools lack a seamless way to connect ideas across different sources dynamically.

## Solution Overview

Memoir allows users to add any content they have consumed to a dynamic, evolving mindmap. The system automatically:

-   **Generates related topics** based on the user’s input, dynamically structuring knowledge.
-   **Adapts the mindmap** as users add more sources, revealing hidden connections between concepts/ topics.
-   **Provides intelligent recall mechanisms,** enabling users to retrieve stored knowledge efficiently.
-   **Supports multiple retrieval methods,** allowing users to search by topic or use natural language queries to retrieve relevant sources.

## Key Features

### Dynamic Knowledge graph and auto expansion

-   Users can add articles, YouTube videos, LLM responses and other content to their mindmap using Memoir chrome extension
-   Memoir automatically generates related topics and connects them dynamically
-   The mindmap expands based on new information, ensuring a non-linear and adaptive organization of knowledge.

### Intelligent memory recall and search

-   Users can search by topic to retrieve all of the related content they’ve stored
-   A semantic search engine enables natural language queries to retrieve relevant sources based on meaning, not just keywords.
-   Memoir understands and ranks the most relevant documents for efficient recall.

### Context-Aware Retrieval through targeted queries

-   Users can ask specific types of questions to recall information based on their needs.
-   Example queries:
    -   What are the key takeaways from the videos I watch on AI ethics?
    -   Show me all articles related to quantum computing that I’ve read.
-   The system retrieves and ranks sources based on contextual relevance

### Seamless User Experience

-   A visually appealing and intuitive UI for mindmap navigation
-   A Chrome extension that lets users easily select text and add it to Memoir via the context menu
-   A quick-save option to capture entire pages instantly using a keyboard shortcut

### Technologies Used

-   **AI & NLP:** BERTopic for topic modeling and Gemini for organizing topics into a hierarchical structure
- **Frontend:**  Chrome extension, Chatbot with ReactJs.
- **Graph:** GIS -> GeoPandas, Leaflet.js, EPSG Projection, Shapely
-   **Backend:** Python (FastAPI) for efficient processing
-   **Database:** pgvector for semantic search and contextual recall using vector embeddings

## Use Cases

### **Students & Researchers**

-   Organize study materials, research papers, and notes into an evolving knowledge graph.
-   Quickly retrieve references for academic writing.

### **Content Creators & Journalists**

-   Structure research for articles, videos, and documentaries.
-   Efficiently recall insights from past research materials.

### **Professionals & Lifelong Learners**

-   Retain industry trends, reports, and key insights for better decision-making.
-   Retrieve knowledge on demand for professional growth.

### **Potential Impact**

Memoir changes the way people interact with knowledge, making learning easier and helping information stick. Using BERTopic and Gemini, we organize scattered content into clear, useful insights that improve productivity, creativity, and decision-making.

### **Future Enhancements**

-   **AI-powered summarization** of stored content.
-   **Integration with external platforms outside of chrome based browsers**.
-   **Personalized recommendations** for new content based on user interests.
-   **Multi-user collaboration** for shared knowledge graphs.
-   Multi-lingual system
