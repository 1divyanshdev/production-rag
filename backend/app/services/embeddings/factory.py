from typing import Optional

from backend.app.core.config import EmbeddingSettings
from backend.app.core.exceptions import EmbeddingError
from backend.app.services.embeddings.base import EmbeddingProvider
from backend.app.services.embeddings.jina_provider import JinaEmbeddingProvider


def get_embedding_provider(settings: Optional[EmbeddingSettings] = None) -> EmbeddingProvider:
    """Factory that returns an :class:`EmbeddingProvider` instance for the
    configured provider name.

    Currently only ``jina`` is implemented; additional providers can be
    added by extending this function and the corresponding subclass.
    """
    if settings is None:
        from backend.app.core.config import load_embedding_settings
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