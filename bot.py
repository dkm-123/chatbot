from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import traceback

app = Flask(__name__)

# OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",   # put your key here
    default_headers={
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Handicraft Chatbot"
    }
)

def translate_message(user_message, lang):
    """
    Translate user input into the chosen language before sending to main chat.
    """
    if lang == "en":
        return user_message

    try:
        translation = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "system", "content": f"Translate the following text into {lang}. Only give translated text."},
                {"role": "user", "content": user_message}
            ]
        )

        if translation.choices:
            return translation.choices[0].message.content.strip()

        return user_message

    except Exception as e:
        print("Translation failed:")
        traceback.print_exc()
        return user_message


@app.route("/icon")
def icon():
    return render_template("icon.html")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    print("Incoming data:", data)

    user_message = data.get("message", "")
    lang = data.get("lang", "en")

    if not user_message.strip():
        return jsonify({"reply": "Please type something to ask!"})

    translated_input = translate_message(user_message, lang)

    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a handicraft expert. Reply ONLY in {lang} language.\n"
                        "Your response must be formatted in HTML with the following sections:\n\n"
                        "<b>📜 History:</b> ...<br><br>"
                        "<b>👷 Labour Needed:</b> ...<br><br>"
                        "<b>⏳ Time to Make:</b> ...<br><br>"
                        "<b>🌟 Unique Facts:</b> ...<br><br>"
                        "<b>🤔 Follow-up:</b> End with a question to keep the conversation going.<br>\n"
                        "Avoid unnecessary explanations and always return cleanly formatted HTML."
                    )
                },
                {"role": "user", "content": translated_input}
            ]
        )

        if completion.choices:
            bot_reply = completion.choices[0].message.content.strip()
        else:
            bot_reply = "Sorry, no response from AI."

    except Exception as e:
        print("Error generating response:")
        traceback.print_exc()
        bot_reply = "Sorry, there was an error processing your request."

    return jsonify({"reply": bot_reply})


if __name__ == "__main__":
    app.run(debug=True)