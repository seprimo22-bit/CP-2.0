from flask import Flask, request, jsonify, render_template
import os
import logging

from rag_engine import RAGEngine
from cognitive_engine import CognitivePipeline
from storage_engine import load_documents_from_directory
from weighting_engine import combine_outputs

# ======================================================
# BASIC APP SETUP
# ======================================================

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = "uploads"
DOCUMENT_FOLDER = "documents"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOCUMENT_FOLDER, exist_ok=True)

rag = None
pipeline = None


# ======================================================
# ENGINE INITIALIZATION
# ======================================================

def initialize_engines():
    global rag, pipeline

    if pipeline is None:
        pipeline = CognitivePipeline()
        logging.info("Cognitive pipeline initialized.")

    if rag is None:
        rag = RAGEngine()

        documents = load_documents_from_directory(DOCUMENT_FOLDER)

        if documents:
            rag.build_index(documents)
            logging.info(f"{len(documents)} documents indexed.")
        else:
            logging.info("No documents found to index.")


# ======================================================
# ROUTES
# ======================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/healthz")
def health():
    return {"status": "ok"}, 200


@app.route("/analyze", methods=["POST"])
def analyze():

    initialize_engines()

    data = request.json or {}

    article = data.get("article", "")
    context = data.get("context", [])

    # Cognitive pipeline analysis
    cognitive_result = pipeline.run(article, context)

    # Document retrieval
    rag_result = rag.retrieve(article)

    # Combine hybrid output
    final_output = combine_outputs(rag_result, cognitive_result)

    return jsonify(final_output)


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("file")

    if not file:
        return {"error": "No file uploaded"}, 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    logging.info(f"Uploaded file: {file.filename}")

    return {"message": "Upload successful"}


# ======================================================
# RENDER START
# ======================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
