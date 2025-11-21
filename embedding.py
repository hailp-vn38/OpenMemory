"""Simple embedding client backed by an HTTP API."""

from __future__ import annotations

from typing import Any, Dict, List

import requests


class Embedding:
    """Tiny helper for requesting embeddings from a remote service."""

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def get_embedding(self, text: str) -> List[float]:
        """Request an embedding vector for `text` from the configured service."""
        payload: Dict[str, Any] = {
            "inputs": [text],
            "input_type": "document",
            "embedding_model": self.model,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(
            f"{self.base_url}/embeddings",
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        items = data.get("embeddings")
        if not items:
            raise ValueError("Invalid response payload: missing 'embeddings'")
        embedding_vector = items[0].get("embedding")
        if embedding_vector is None:
            raise ValueError("Invalid response payload: missing 'embedding'")
        return embedding_vector

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Request embedding vectors for multiple texts in one API call.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors, one per input text

        Raises:
            ValueError: If response is invalid or doesn't match input length
        """
        if not texts:
            return []

        payload: Dict[str, Any] = {
            "inputs": texts,  # Send all texts at once
            "input_type": "document",
            "embedding_model": self.model,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(
            f"{self.base_url}/embeddings",
            json=payload,
            headers=headers,
            timeout=60,  # Longer timeout for batch
        )
        response.raise_for_status()
        data = response.json()
        items = data.get("embeddings")

        if not items:
            raise ValueError("Invalid response payload: missing 'embeddings'")

        if len(items) != len(texts):
            raise ValueError(
                f"Response length mismatch: expected {len(texts)}, got {len(items)}"
            )

        # Extract all embedding vectors
        embeddings = []
        for i, item in enumerate(items):
            embedding_vector = item.get("embedding")
            if embedding_vector is None:
                raise ValueError(f"Missing 'embedding' in response item {i}")
            embeddings.append(embedding_vector)

        return embeddings
