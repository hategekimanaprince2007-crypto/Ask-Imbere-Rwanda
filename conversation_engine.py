
def classify_message(message, selected_category=None):
    text = message.lower().strip()

    if not text:
        return {"intent": "unknown", "category": None}

    if any(word in text for word in ["hello", "hi", "hey", "muraho", "bonjour", "habari"]):
        return {"intent": "greeting", "category": None}

    if any(word in text for word in ["goodbye", "bye", "murabeho", "kwaheri", "au revoir"]):
        return {"intent": "farewell", "category": None}

    if any(word in text for word in ["thank you", "thanks", "murakoze", "merci", "asante"]):
        return {"intent": "thanks", "category": None}

    if any(word in text for word in ["how are you", "amakuru yawe", "umeze ute"]):
        return {"intent": "casual_chat", "category": None}

    categories = [
        "agriculture",
        "healthcare",
        "culture",
        "genocide_1994",
        "education",
        "tourism"
    ]

    category = selected_category if selected_category in categories else None

    if category is None:
        for item in categories:
            if item == "genocide_1994":
                keywords = ["genocide against the tutsi", "1994 genocide"]
            else:
                keywords = [item]

            if any(word in text for word in keywords):
                category = item
                break

    if category:
        return {"intent": "knowledge", "category": category}

    if "?" in message:
        return {"intent": "general_question", "category": None}

    return {"intent": "unknown", "category": None}


def main():
    examples = [
        "Hello",
        "How are you?",
        "Tell me about education in Rwanda",
        "What is Python?",
        "Goodbye"
    ]

    for message in examples:
        result = classify_message(message)
        print("Message:", message)
        print("Result:", result)
        print("-" * 40)


if __name__ == "__main__":
    main()
