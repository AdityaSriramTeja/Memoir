import { useState, useRef, useEffect } from "react";
import "./App.css";

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const [expandedMessages, setExpandedMessages] = useState(new Set());

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async (e) => {
        e?.preventDefault();
        if (input.trim() === "" || isLoading) return;

        const userMessage = { sender: "user", text: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const response = await fetch(
                `http://localhost:8000/get_relevant_articles?text=${encodeURIComponent(
                    input
                )}`,
                {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                }
            );

            const data = await response.json();
            console.log(data);
            const formattedText = data.map((item) => ({
                preview: item.content.substring(0, 150),
                fullContent: item.content,
                url: item.url,
                pageType: item.page_type,
            }));

            const botMessage = {
                sender: "Memoir",
                content: formattedText,
                isArticle: true,
            };
            setMessages((prev) => [...prev, botMessage]);
        } catch (error) {
            console.error("Error:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const toggleMessageExpand = (index) => {
        setExpandedMessages((prev) => {
            const newSet = new Set(prev);
            if (newSet.has(index)) {
                newSet.delete(index);
            } else {
                newSet.add(index);
            }
            return newSet;
        });
    };

    return (
        <div className="app-container">
            <div className="chat-container">
                <header className="chat-header">
                    <h2>Memoir</h2>
                </header>

                <div className="messages-container">
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`message-wrapper ${msg.sender}`}
                        >
                            <div
                                className={`message-content ${
                                    msg.isArticle ? "article-content" : ""
                                }`}
                            >
                                <span className="sender-name">
                                    {msg.sender}
                                </span>
                                <div className="message-text">
                                    {msg.isArticle
                                        ? msg.content.map((item, i) => (
                                              <div
                                                  key={i}
                                                  className="article-line"
                                              >
                                                  <div
                                                      className="article-header"
                                                      onClick={() =>
                                                          toggleMessageExpand(
                                                              `${index}-${i}`
                                                          )
                                                      }
                                                  >
                                                      <span className="article-icon">
                                                          {expandedMessages.has(
                                                              `${index}-${i}`
                                                          )
                                                              ? "📖"
                                                              : "📄"}
                                                      </span>
                                                      <div className="article-preview">
                                                          {expandedMessages.has(
                                                              `${index}-${i}`
                                                          )
                                                              ? item.fullContent
                                                              : `${item.preview}...`}
                                                      </div>
                                                  </div>
                                                  <div className="article-meta">
                                                      <a
                                                          href={item.url}
                                                          target="_blank"
                                                          rel="noopener noreferrer"
                                                          className="article-url"
                                                      >
                                                          🔗 {item.url}
                                                      </a>
                                                      <span className="article-type">
                                                          📱 {item.pageType}
                                                      </span>
                                                  </div>
                                              </div>
                                          ))
                                        : msg.text}
                                </div>
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="message-wrapper Memoir">
                            <div className="message-content">
                                <div className="typing-indicator">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <form className="input-container" onSubmit={sendMessage}>
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        disabled={isLoading}
                    />
                    <button type="submit" disabled={isLoading || !input.trim()}>
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                        </svg>
                    </button>
                </form>
            </div>
        </div>
    );
}

export default App;
