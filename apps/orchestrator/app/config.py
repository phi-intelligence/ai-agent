from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/phi_agents"
    core_api_url: str = "http://localhost:8000"
    openai_api_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

