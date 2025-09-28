import os
import psycopg2
from dotenv import load_dotenv

def connect_to_db():
    """
    Establishes a connection to the Neon PostgreSQL database.
    Loads credentials from a .env file in the project root.
    """
    # Load .env file from the root directory
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)

    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode=os.getenv("DB_SSLMODE", "require")
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}")
        return None

def setup_database():
    """
    Executes the schema.sql file to create the database tables.
    """
    conn = connect_to_db()
    if not conn:
        print("Aborting database setup.")
        return

    # Path to the schema.sql file, assuming it's in the project root
    schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'schema.sql')

    try:
        with conn.cursor() as cur:
            with open(schema_path, "r") as f:
                cur.execute(f.read())
        conn.commit()
        print("Database tables created successfully from schema.sql.")
    except Exception as e:
        print(f"An error occurred during database setup: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    # This allows running the script directly to set up the database
    print("Initializing database setup...")
    setup_database()