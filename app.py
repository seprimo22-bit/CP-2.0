from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

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
# ANALYZE ROUTE (WORKING BASELINE)
# -------------------------------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    question = request.form.get("question")
    text = request.form.get("text")
    file = request.files.get("file")

    return jsonify({
        "status": "pipeline online",
        "question": question,
        "text_length": len(text) if text else 0,
        "file_uploaded": bool(file)
    })


# -------------------------------------------------
# START SERVER
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
