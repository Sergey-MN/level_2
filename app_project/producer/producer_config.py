from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitSettings(BaseSettings):
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_QUEUE: str
    RABBITMQ_EXCHANGE: str

    PRODUCER_INTERVAL:int

    @property
    def RABBIT_URL(self) -> str:
        return f"pyamqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"

    model_config = SettingsConfigDict(env_file=r".env",
                                      extra='ignore')


mq_settings = RabbitSettings()
