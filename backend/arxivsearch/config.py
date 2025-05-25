import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://arxivsearch:arxivsearch@localhost:5432/arxivsearch")
ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")
DEBUG = int(os.getenv("DEBUG", "1"))
LOGGER_LEVEL = int(os.getenv("LOGGER_LEVEL", "10"))
CORS = os.getenv("CORS", "http://localhost:5173").split(",")
