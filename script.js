
"use strict";

// ==========================================
// IMBERE_RWANDA - WEBSITE CHAT CONNECTION
// ==========================================

// The website and backend use the same address.
const API_URL = "/chat";

// ==========================================
// PAGE ELEMENTS
// ==========================================

const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const messageList = document.getElementById("messageList");
const languageSelector = document.getElementById("languageSelector");
const welcomeScreen = document.getElementById("welcomeScreen");
const newChatButton = document.getElementById("newChat");
const sendButton = document.getElementById("sendButton");

const categoryButtons = document.querySelectorAll(".category");
const suggestionButtons = document.querySelectorAll(".suggestion");

// ==========================================
// CHECK REQUIRED HTML ELEMENTS
// ==========================================

const requiredElements = {
    chatForm,
    messageInput,
    messageList,
    languageSelector,
    welcomeScreen,
    newChatButton,
    sendButton
};

let pageReady = true;

for (const [name, element] of Object.entries(requiredElements)) {
    if (!element) {
        console.error("Missing homepage element:", name);
        pageReady = false;
    }
}

if (!pageReady) {
    throw new Error(
        "Imbere_Rwanda could not initialize. Check index.html."
    );
}

console.log("Imbere_Rwanda script loaded successfully.");

// ==========================================
// CHAT STATE
// ==========================================

let selectedCategory = null;

// ==========================================
// SELECT A KNOWLEDGE CATEGORY
// ==========================================

categoryButtons.forEach(button => {
    button.addEventListener("click", () => {

        categoryButtons.forEach(item => {
            item.classList.remove("active");
        });

        button.classList.add("active");

        selectedCategory = button.dataset.category;

        messageInput.focus();

        console.log("Selected category:", selectedCategory);
    });
});

// ==========================================
// LANGUAGE SELECTOR
// ==========================================

languageSelector.addEventListener("change", () => {

    const language = languageSelector.value;

    const placeholders = {
        en: "Ask anything about Rwanda...",
        rw: "Baza ikibazo cyawe ku Rwanda...",
        fr: "Posez votre question sur le Rwanda...",
        sw: "Uliza swali lako kuhusu Rwanda..."
    };

    messageInput.placeholder =
        placeholders[language] || placeholders.en;

    console.log("Selected language:", language);
});

// ==========================================
// DISPLAY A MESSAGE
// ==========================================

function addMessage(text, sender) {

    const message = document.createElement("div");

    message.classList.add("message", sender);

    const content = document.createElement("p");

    content.textContent = text;

    message.appendChild(content);

    messageList.appendChild(message);

    messageList.scrollTop = messageList.scrollHeight;

    return message;
}

// ==========================================
// DISPLAY SOURCES AND REFERENCES
// ==========================================

function addSources(documents, notice) {

    if (!documents || documents.length === 0) {
        return;
    }

    const sourceContainer = document.createElement("div");

    sourceContainer.classList.add("sources");

    const heading = document.createElement("h4");

    heading.textContent = "Sources and references";

    sourceContainer.appendChild(heading);

    documents.forEach(document => {

        const source = document.createElement("div");

        source.classList.add("source-item");

        const title = document.createElement("strong");

        title.textContent =
            document.source_title || document.title;

        source.appendChild(title);

        if (document.organization) {

            const organization = document.createElement("p");

            organization.textContent = document.organization;

            source.appendChild(organization);
        }

        const documentTitle = document.createElement("p");

        documentTitle.textContent = document.title;

        source.appendChild(documentTitle);

        if (document.source_url) {

            const link = document.createElement("a");

            link.href = document.source_url;

            link.textContent = "View source";

            link.target = "_blank";

            link.rel = "noopener noreferrer";

            source.appendChild(link);
        }

        sourceContainer.appendChild(source);
    });

    if (notice) {

        const noticeText = document.createElement("p");

        noticeText.textContent = notice;

        sourceContainer.appendChild(noticeText);
    }

    messageList.appendChild(sourceContainer);

    messageList.scrollTop = messageList.scrollHeight;
}

// ==========================================
// SEND MESSAGE TO FASTAPI
// ==========================================

async function sendMessage(messageText) {

    const message = messageText.trim();

    if (!message) {
        return;
    }

    console.log("Sending message:", message);

    // Hide welcome screen.
    welcomeScreen.style.display = "none";

    // Display user's message.
    addMessage(message, "user");

    // Clear input.
    messageInput.value = "";

    // Disable controls while waiting.
    sendButton.disabled = true;
    messageInput.disabled = true;

    const loadingMessage = addMessage(
        "Imbere_Rwanda is preparing a response...",
        "assistant"
    );

    try {

        const response = await fetch(API_URL, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: message,

                language: languageSelector.value,

                category: selectedCategory

            })
        });

        console.log("Server response status:", response.status);

        if (!response.ok) {

            throw new Error(
                "Server error: " + response.status
            );
        }

        const data = await response.json();

        console.log("Server response:", data);

        // Remove loading message.
        loadingMessage.remove();

        // Display assistant answer.
        addMessage(
            data.answer || "No response was returned.",
            "assistant"
        );

        // Display retrieved documents and sources.
        addSources(data.documents, data.notice);

    } catch (error) {

        console.error("Chat connection error:", error);

        loadingMessage.remove();

        addMessage(
            "Sorry, I couldn't connect to the Imbere_Rwanda server. " +
            "Please check that the backend is running and try again.",
            "assistant"
        );

    } finally {

        sendButton.disabled = false;

        messageInput.disabled = false;

        messageInput.focus();
    }
}

// ==========================================
// CHAT FORM SUBMISSION
// ==========================================

chatForm.addEventListener("submit", async event => {

    event.preventDefault();

    await sendMessage(messageInput.value);

});

// ==========================================
// SUGGESTED QUESTIONS
// ==========================================

suggestionButtons.forEach(button => {

    button.addEventListener("click", () => {

        messageInput.value = button.textContent.trim();

        selectedCategory = null;

        categoryButtons.forEach(item => {
            item.classList.remove("active");
        });

        sendMessage(messageInput.value);

    });

});

// ==========================================
// NEW CHAT
// ==========================================

newChatButton.addEventListener("click", () => {

    messageList.innerHTML = "";

    welcomeScreen.style.display = "";

    messageInput.value = "";

    selectedCategory = null;

    categoryButtons.forEach(button => {
        button.classList.remove("active");
    });

    messageInput.focus();

    console.log("New chat started.");

});

// ==========================================
// ENTER KEY BEHAVIOUR
// ==========================================

messageInput.addEventListener("keydown", event => {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        chatForm.requestSubmit();

    }

});

// ==========================================
// INITIALIZATION COMPLETE
// ==========================================

console.log("Imbere_Rwanda chat interface is ready.");
