import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "dev"
    
    # ServiceNow PDI Configuration
    SERVICENOW_INSTANCE_URL: str = "https://dev00000.service-now.com"
    SERVICENOW_INTEGRATION_USER: str = "admin"
    SERVICENOW_INTEGRATION_PASSWORD: str = "password"
    
    # Entra ID Authentication
    ENTRA_TENANT_ID: str = ""
    ENTRA_CLIENT_ID: str = ""
    AUTH_MODE: str = "dev_bypass"
    
    # LLM Configuration
    LLM_PROVIDER: str = "mock"  # mock | groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Databases
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def validate_dev_auth_guard(self) -> None:
        """
        Enforces Section 5 Startup Safety Guard:
        AUTH_MODE=dev_bypass is strictly forbidden when ENV != dev.
        """
        if self.AUTH_MODE == "dev_bypass" and self.ENV.lower() != "dev":
            raise RuntimeError(
                f"CRITICAL SECURITY FAILURE: AUTH_MODE='{self.AUTH_MODE}' is forbidden when ENV='{self.ENV}'. "
                "Dev bypass can only run when ENV=dev."
            )


settings = Settings()
