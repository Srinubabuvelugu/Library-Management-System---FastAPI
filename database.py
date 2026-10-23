import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_CA_CERT = os.getenv("DB_CA_CERT","")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

connect_args = {}

if DB_CA_CERT:
    ca_cert_path = "/tmp/aiven-ca.pem"

    with open(ca_cert_path, "w") as cert_file:
        cert_file.write(DB_CA_CERT)

    connect_args["ssl"] = {"ca": ca_cert_path}

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args=connect_args
)

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()