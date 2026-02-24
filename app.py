from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# =====================================================
# GLOBALS (Lazy Loaded)
# =====================================================

rag_engine = None
pipeline_engine = None


# =====================================================
# LAZY INITIALIZATION
# =====================================================

def initialize_engines():
    global rag_engine, pipeline_engine

    if pipeline_engine is None:
        from cognitive_pipeline import CognitivePipeline
        pipeline_engine = CognitivePipeline()

    if rag_engine is None:
        from rag_engine import RAGEngine
        rag_engine = RAGEngine()


# =====================================================
# ROUTES
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    initialize_engines()

    data = request.json
    article = data.get("article", "")
    question = data.get("question", "")

    result = pipeline_engine.run(article, question)

    return jsonify(result)


# =====================================================
# START SERVER (Render Compatible)
# =====================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
