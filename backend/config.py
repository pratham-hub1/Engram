import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application settings
    port: int = 8000
    environment: str = "development"
    log_level: str = "INFO"

    # Cognee Dataset
    cognee_dataset_name: str = "engram_core"
    
    # Cognee Proxy Configuration
    cognee_llm_provider: str = "openai"
    cognee_llm_model: str = "gpt-4o"
    cognee_llm_endpoint: str = "http://localhost:4000"
    cognee_llm_api_key: str = "sk-proxy-key" # Dummy key for proxy

    cognee_embedding_provider: str = "openai_compatible"
    cognee_embedding_model: str = "text-embedding-3-large"
    cognee_embedding_endpoint: str = "http://localhost:4000"
    cognee_embedding_api_key: str = "sk-proxy-key"

    # App LLM settings (Used strictly for local extract_reasoning, NOT for Cognee Graph)
    app_llm_provider: str = "openai"
    app_llm_model: str = "nvidia/nemotron-3-super-120b-a12b"
    app_llm_endpoint: str = "https://integrate.api.nvidia.com/v1"
    app_llm_api_key: str = ""

    # Pydantic configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def set_environment(self):
        """Inject required settings directly into the OS environment."""
        pass

# Singleton instance
settings = Settings()
