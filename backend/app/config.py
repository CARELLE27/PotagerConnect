from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration lue depuis les variables d'environnement.

    Aucun secret en dur : tout vient de l'environnement (.env).
    """

    database_url: str = "postgresql+psycopg2://potager:potager@db:5432/potagerconnect"

    secret_key: str = "changeme-en-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    jardin_latitude: float = 47.9029
    jardin_longitude: float = 1.9093
    jardin_nom: str = "Jardin des Groues"

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
