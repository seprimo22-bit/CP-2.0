from flask import Flask, request, jsonify, render_template
from rag_engine import RAGEngine
from cognitive_engine import CognitiveEngine
from weighting_engine import WeightingEngine
from storage_engine import save_document

import os

app = Flask(__name__)

rag = RAGEngine()
cognitive = CognitiveEngine()
weights = WeightingEngine()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    path = save_document(file)

    with open(path, "r", errors="ignore") as f:
        content = f.read()

    rag.build_index([content])

    return jsonify({"status": "uploaded"})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    question = data.get("question", "")

    docs = rag.retrieve(question)

    combined_text = " ".join(docs)

    facts = cognitive.extract_facts(combined_text)
    ambiguity = cognitive.ambiguity_score(combined_text)
    fact_conf = cognitive.confidence(facts, ambiguity)

    final_score = weights.combine(
        ai_conf=0.5,
        doc_conf=0.6,
        fact_conf=fact_conf
    )

    return jsonify({
        "facts": facts,
        "confidence": final_score,
        "documents_used": docs
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
