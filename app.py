from flask import Flask, request, jsonify, render_template import os

app = Flask(name)

=====================================================

GLOBALS (Lazy Loaded Engines)

=====================================================

rag_engine = None pipeline_engine = None

=====================================================

ENGINE INITIALIZATION

=====================================================

def initialize_engines(): global rag_engine, pipeline_engine

if pipeline_engine is None:
    print("Initializing Cognitive Pipeline...")
    from cognitive_pipeline import CognitivePipeline
    pipeline_engine = CognitivePipeline()

if rag_engine is None:
    print("Initializing RAG Engine...")
    from rag_engine import RAGEngine
    rag_engine = RAGEngine()

=====================================================

ROUTES

=====================================================

@app.route("/") def home(): return render_template("index.html")

@app.route("/health") def health(): return "OK", 200

@app.route("/analyze", methods=["POST"]) def analyze(): initialize_engines()

try:
    # Handle text pasted in textarea
    question = request.form.get("question", "")
    article = request.form.get("text", "")

    # Handle optional uploaded file
    file = request.files.get("file")
    if file and file.filename:
        try:
            article += "\n" + file.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print("File read error:", e)

    print("Analyze hit")
    print("Question:", question)
    print("Article length:", len(article))

    result = pipeline_engine.run(article, question)

    return jsonify(result)

except Exception as e:
    print("ANALYZE ERROR:", e)
    return jsonify({"error": str(e)}), 500

=====================================================

RENDER COMPATIBLE START

=====================================================

if name == "main": port = int(os.environ.get("PORT", 10000)) app.run(host="0.0.0.0", port=port)
