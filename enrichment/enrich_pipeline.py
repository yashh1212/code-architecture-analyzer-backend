from typing import List, Dict
from enrichment.metadata_enricher import enrich_chunk


def enrich_chunks(chunks: List[Dict]) -> List[Dict]:
    """
    Apply metadata enrichment to all semantic chunks.
    """
    enriched = []

    for chunk in chunks:
        enriched_chunk = enrich_chunk(chunk)
        enriched.append(enriched_chunk)

    return enriched
