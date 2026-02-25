from flask import Flask, request, jsonify, render_template
import os
import openai
import PyPDF2

app = Flask(__name__)

# -------------------------------------------------
# OPENAI SETUP
# -------------------------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")


# -------------------------------------------------
# HOME PAGE
# -------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------------------------------
# HEALTH CHECK (Render needs this sometimes)
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
        t = page.extract_text()
        if t:
            text += t
    return text


# -------------------------------------------------
# ANALYZE ROUTE (THE MAIN ONE)
# -------------------------------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    question = request.form.get("question", "")
    text = request.form.get("text", "")
    file = request.files.get("file")

    # If a PDF uploaded, extract text
    if file and file.filename.endswith(".pdf"):
        text += extract_pdf_text(file)

    if not question:
        return jsonify({"error": "No question provided"}), 400

    prompt = f"""
You are a research assistant.

Document:
{text}

Question:
{question}

Give a clear, direct answer based on the document.
If the document has no info, answer generally.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        answer = response.choices[0].message.content

        return jsonify({
            "answer": answer,
            "text_length": len(text),
            "file_uploaded": bool(file)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# START SERVER (Render compatible)
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
