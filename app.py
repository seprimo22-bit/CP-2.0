import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# -----------------------------
# LAZY IMPORT HELPERS
# -----------------------------
def get_rag():
    from rag_engine import RAGEngine
    return RAGEngine()

def get_weighting():
    from rag_engine import WeightingEngine
    return WeightingEngine()

def get_openai_client():
    from openai import OpenAI
    return OpenAI()


# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------
# UPLOAD DOCUMENT
# -----------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    return jsonify({"message": "Uploaded", "content": text})


# -----------------------------
# BUILD INDEX
# -----------------------------
@app.route("/build-index", methods=["POST"])
def build_index():
    data = request.json
    docs = data.get("documents", [])

    if not docs:
        return jsonify({"error": "No documents provided"}), 400

    rag = get_rag()
    rag.build_index(docs)

    return jsonify({"message": "Index built", "count": len(docs)})


# -----------------------------
# QUERY RAG + OPENAI + WEIGHTING
# -----------------------------
@app.route("/query", methods=["POST"])
def query():
    data = request.json
    user_query = data.get("query", "")

    if not user_query:
        return jsonify({"error": "Query missing"}), 400

    rag = get_rag()
    weighting = get_weighting()
    client = get_openai_client()

    # Retrieve docs
    retrieved_docs = rag.retrieve(user_query, k=5)
    context = "\n".join(retrieved_docs)

    # Call OpenAI
    ai_response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that uses retrieved context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuery: {user_query}"}
        ]
    )

    answer = ai_response.choices[0].message["content"]

    # Confidence placeholders
    ai_conf = 0.9
    doc_conf = 0.7 if retrieved_docs else 0.2
    fact_conf = 0.6

    final_score = weighting.combine(ai_conf, doc_conf, fact_conf)

    return jsonify({
        "answer": answer,
        "retrieved_docs": retrieved_docs,
        "confidence": final_score
    })


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
