from pydantic_settings import BaseSettings


class Settings(BaseSettings):
  openai_api_key: str
  openai_model: str
  openai_model: str