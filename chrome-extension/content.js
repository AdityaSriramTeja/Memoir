function showOverlayNotification(message) {
    let existingNotification = document.getElementById("extension-notification");
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification container
    let notification = document.createElement("div");
    notification.id = "extension-notification";
    notification.style.position = "fixed";
    notification.style.top = "20px";
    notification.style.right = "20px";
    notification.style.width = "300px";  // Bigger width
    notification.style.padding = "15px";
    notification.style.display = "flex";
    notification.style.alignItems = "center";
    notification.style.gap = "10px";
    notification.style.background = "rgba(0, 0, 0, 0.85)";
    notification.style.color = "#fff";
    notification.style.borderRadius = "8px";
    notification.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.3)";
    notification.style.zIndex = "9999";
    notification.style.fontSize = "16px";
    notification.style.fontWeight = "bold";
    notification.style.transition = "opacity 0.5s ease-in-out";
    
    // Create icon
    let icon = document.createElement("img");
    icon.src = chrome.runtime.getURL("icon96.png"); // Use an icon from the extension folder
    icon.style.width = "24px";
    icon.style.height = "24px";

    // Create text
    let text = document.createElement("span");
    text.innerText = message;

    // Append icon and text to notification
    notification.appendChild(icon);
    notification.appendChild(text);
    document.body.appendChild(notification);


    setTimeout(() => {
        notification.style.opacity = "0";
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "showOverlayNotification") {
        showOverlayNotification(message.text);
    }
});