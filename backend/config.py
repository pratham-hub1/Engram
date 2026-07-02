import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application settings
    port: int = 8000
    environment: str = "development"
    log_level: str = "INFO"

    # Litellm settings
    litellm_tokenizer: str = "cl100k_base"

    # Cognee Dataset
    cognee_dataset_name: str = "memory_ai_core"

    # LLM settings
    cognee_llm_provider: str = "openai"
    cognee_llm_model: str = "nvidia/nemotron-3-super-120b-a12b"
    cognee_llm_endpoint: str = "https://integrate.api.nvidia.com/v1"
    cognee_llm_api_key: str = ""

    # Embedding settings
    cognee_embedding_provider: str = "openai"
    cognee_embedding_model: str = "nvidia/nv-embedqa-e5-v5"
    cognee_embedding_endpoint: str = "https://integrate.api.nvidia.com/v1"
    cognee_embedding_api_key: str = ""

    # Pydantic configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def set_environment(self):
        """Inject required settings directly into the OS environment."""
        os.environ["LITELLM_TOKENIZER"] = self.litellm_tokenizer

# Singleton instance
settings = Settings()
