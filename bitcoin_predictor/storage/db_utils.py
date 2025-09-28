from .db_connection import get_db_connection

def execute_schema():
    """
    Connects to the database and executes the SQL commands in schema.sql
    to create the required tables.
    """
    conn = get_db_connection()
    if not conn:
        print("Could not connect to the database. Aborting schema setup.")
        return

    try:
        with conn.cursor() as cur:
            # Note: Assumes schema.sql is in the project root directory
            with open("schema.sql", "r") as f:
                cur.execute(f.read())
        conn.commit()
        print("Database schema created successfully.")
    except Exception as e:
        print(f"An error occurred during schema creation: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    print("Setting up the database...")
    execute_schema()