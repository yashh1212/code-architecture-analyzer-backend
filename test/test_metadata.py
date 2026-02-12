from enrichment.enrich_pipeline import enrich_chunks

sample_chunks = [
    {
        "type": "function",
        "name": "predict",
        "language": "python",
        "file": "predict.py",
        "content": "def predict(...):",
        "metadata": {
            "imports": ["pickle", "sklearn"],
            "calls": ["predict"]
        }
    }
]

enriched = enrich_chunks(sample_chunks)

print(enriched[0]["metadata"])
