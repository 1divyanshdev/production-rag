from typing import Optional

from rag_core.config import EmbeddingSettings, load_embedding_settings
from rag_core.exceptions import EmbeddingError
from rag_core.embeddings.base import EmbeddingProvider
from rag_core.embeddings.jina_provider import JinaEmbeddingProvider


def get_embedding_provider(settings: Optional[EmbeddingSettings] = None) -> EmbeddingProvider:
    """Factory that returns an :class:`EmbeddingProvider` instance for the
    configured provider name.

    Currently only ``jina`` is implemented; additional providers can be
    added by extending this function and the corresponding subclass.
    """
    if settings is None:
        settings = load_embedding_settings()

    provider_name = settings.provider.lower()
    if provider_name == "jina":
        return JinaEmbeddingProvider(
            settings,
            transport=getattr(settings, "transport", None),
            dimension=getattr(settings, "dimension", None),
        )

    raise EmbeddingError(
        f"Unsupported embedding provider '{provider_name}'. "
        "Supported: jina"
    )