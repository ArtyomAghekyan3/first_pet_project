from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):

    DB_PASSWORD :str
    DB_USERNAME:str
    DB_PORT:int
    DB_NAME:str
    DB_HOST:str
    

    @property
    def DB_WITH_asycopg(self):
        return  f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def DB_WITH_psycopg(self):
        return  f"postgresql+psycopg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config=SettingsConfigDict(env_file='.env')

settings=Settings()