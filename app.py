from flask import Flask, request, jsonify, render_template
import os
import PyPDF2

from rag_engine import RAGEngine

app = Flask(__name__)
rag = RAGEngine()


# -------------------------------------------------
# HOME PAGE
# -------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
@app.route("/health")
def health():
    return "OK", 200


# -------------------------------------------------
# PDF TEXT EXTRACTION
# -------------------------------------------------
def extract_pdf_text(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


# -------------------------------------------------
# SIMPLE FACT EXTRACTION (Pipeline Core)
# -------------------------------------------------
TRIGGER_WORDS = [
    "shows", "demonstrates", "indicates",
    "reveals", "confirms", "improves",
    "developed", "introduces"
]

def extract_facts(text):
    sentences = text.split(".")
    return [
        s.strip()
        for s in sentences
        if any(w in s.lower() for w in TRIGGER_WORDS)
    ]


# -------------------------------------------------
# ANALYZE ROUTE
# -------------------------------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

  import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/analyze", methods=["POST"])
def analyze():

    question = request.form.get("question")
    text = request.form.get("text")

    prompt = f"""
    Document:
    {text}

    Question:
    {question}

    Answer clearly and concisely.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.choices[0].message.content

        return jsonify({
            "answer": answer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500  

    # Build vector index if we have text
    if text:
        rag.build_index([text])

    # Retrieve relevant context
    context_docs = rag.retrieve(question)

    # Run cognitive extraction
    facts = extract_facts(text)

    return jsonify({
        "question": question,
        "facts_found": facts,
        "context_docs": context_docs,
        "text_length": len(text),
        "file_processed": bool(file)
    })


# -------------------------------------------------
# START SERVER
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
