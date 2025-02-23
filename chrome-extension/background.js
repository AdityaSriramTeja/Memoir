chrome.commands.onCommand.addListener((command) => {
    if (command === "trigger_fetch") {
        trigger_fetch();
    }
});

function parseURL(url) {
    let index = url.indexOf("www.youtube.com/watch?v=");
    if (index != -1) {
        console.log("YouTube video detected. Video ID:", url.substring(index + 24));
        return {type: "youtube", videoId: url.substring(index + 24)};
    }
    index = url.indexOf("chatgpt.com/c/");
    if (index != -1) {
        console.log("ChatGPT page detected. Chat ID:", url.substring(index + 14));
        return {type: "chatgpt", chatID: url.substring(index + 14)};
    }
    console.log("Unknown page type");
    return {type:"unknown"};
}

async function trigger_fetch() {
    // Get the URL
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const url = tabs[0].url;
        console.log("Current URL:", url);
        const urlData = parseURL(url);
        // Parse the URL to determine what type of content it is
        if (urlData.type === "youtube") {
            // Fetch video captions
            console.log("Video ID:", urlData.videoId);
            try {

                const res = fetch("https://www.youtube-transcript.io/api/transcripts", {
                    method: "POST",
                    headers: {
                        "Authorization": "Basic 67b96b7f40491247acc6286e",
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ ids: [urlData.videoId] })
                })
                .then(res => res.json())
                .then(data => {
                    // Process the data
                    // console.log("Captions:", data[0]["tracks"][0]["language"]);
                    let track = data[0]["tracks"].find((item) => item["language"].includes("English"));
                    let fullText = "";
                    console.log("Transcript:", track.transcript);
                    track.transcript.map((item) => {
                        fullText += item.text + " ";
                    });
                    
                    // Send the data to the backend
                    const payload = {
                        content: {
                            text: fullText
                        },
                        url: {
                            text: url
                        },
                        page_type: {
                            text: urlData.type
                        }
                    }
                    
                    sendData(payload);
                    // Send notification to the user
                    sendOverlayNotification("Added video captions to Mindmap");
                });
            } catch (error) {   
                console.error("Error fetching captions:", error);
                sendOverlayNotification("Error fetching captions. Could not add to Mindmap");
            }
        } else {
            // Retrieve the source HTML
            chrome.scripting.executeScript(
                {
                    target: { tabId: tabs[0].id },
                    function: () => {
                        return document.documentElement.outerHTML;
                    }
                },
                (results) => {
                    if (results && results[0]) {
                        // console.log("Page Source:", results[0].result);
                        console.log("Retrieved page source");
                        // Send the data to the backend
                        const payload = {
                            content: {
                                text: results[0].result
                            },
                            url: {
                                text: url
                            },
                            page_type: {
                                text: urlData.type
                            }
                        }
                        sendData(payload);
                        // Send notification to the user
                        sendOverlayNotification("Added page source to Mindmap");

                    }
                }
            );
        }
    });
    
}

function sendData(data) {
    console.log("Sending data to backend:", data);
    fetch("https://dce2-2607-fea8-e362-a500-40f6-a651-7636-8608.ngrok-free.app/process_text",{
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    } 
    )
    // Send data to the backend
}

function sendOverlayNotification(text) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs.length > 0) {
            chrome.tabs.sendMessage(tabs[0].id, { action: "showOverlayNotification", text: text });
        }
        
    });
}

// Context menu functions
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "addToMindmap",
        title: "Add to Mindmap",
        contexts: ["selection"]
    });
});
  
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "addToMindmap") {
        const query = info.selectionText;
        console.log("Selected text:", query);
        console.log("URL: " + tab.url);
        console.log("Parsed URL:", parseURL(tab.url));
        // Send the data to the backend
        const payload = {
            content: {
                text: query
            },
            url: {
                text: tab.url
            },
            page_type: {
                text: parseURL(tab.url).type
            }
        }
        sendData(payload);
        // Send notification
        sendOverlayNotification("Added selected text to Mindmap")
    }
});