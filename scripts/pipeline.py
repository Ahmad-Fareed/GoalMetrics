import csv
import os
import mysql.connector
from mysql.connector import Error

# Configuration: Update these with your local MySQL credentials
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # Your MySQL username (default for XAMPP is 'root')
    'password': 'root',          # Your MySQL password (default for XAMPP is blank '')
    'database': 'goalmetric_db'
}

def setup_database():
    """Connects to MySQL server, creates the database, table, and performance indexes."""
    try:
        # Establish connection to the root MySQL server (no database specified yet)
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()

        # 1. Create Database dynamically if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")

        # 2. System Design: Define schema with composite performance indexing
        # match_date is used instead of 'date' to prevent collision with SQL reserved keywords.
        table_query = """
        CREATE TABLE IF NOT EXISTS matches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            match_date DATE NOT NULL,
            home_team VARCHAR(100) NOT NULL,
            away_team VARCHAR(100) NOT NULL,
            home_score INT NOT NULL,
            away_score INT NOT NULL,
            tournament VARCHAR(150),
            city VARCHAR(100),
            country VARCHAR(100),
            neutral_venue BOOLEAN,
            INDEX idx_home_team (home_team),
            INDEX idx_away_team (away_team),
            UNIQUE KEY unique_match (match_date, home_team, away_team)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(table_query)
        print(f" Database '{DB_CONFIG['database']}' and 'matches' table verified/created.")
        return connection, cursor

    except Error as e:
        print(f"❌ Critical Database Setup Error: {e}")
        return None, None

def ingest_csv_data(connection, cursor, csv_filename):
    """Parses the CSV line by line and executes optimal chunk-based batch inserts."""
    # Find the absolute path to ensure the file is caught regardless of where the script runs from
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_filepath = os.path.join(script_dir, csv_filename)

    if not os.path.exists(csv_filepath):
        print(f"❌ Error: Raw dataset file missing at expected path: {csv_filepath}")
        return

    try:
        # Parameterized query to safely prevent SQL Injection attacks
        insert_query = """
        INSERT IGNORE INTO matches (match_date, home_team, away_team, home_score, away_score, tournament, city, country, neutral_venue)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        batch_data = []
        batch_size = 5000  # Performance sweet spot: minimizes network trips without exploding memory
        total_rows = 0

        print("⚡ Processing CSV data stream and preparing transactions...")
        
        with open(csv_filepath, mode='r', encoding='utf-8', errors='replace') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Basic Data Validation: Skip rows with broken or missing core metrics
                if not row['home_score'] or not row['away_score']:
                    continue

                # Data Normalization: Parse strings to correct database types
                neutral_bool = 1 if row.get('neutral', 'False').strip().lower() == 'true' else 0
                
                data_tuple = (
                    row['date'],
                    row['home_team'].strip(),
                    row['away_team'].strip(),
                    int(row['home_score']),
                    int(row['away_score']),
                    row['tournament'].strip(),
                    row['city'].strip(),
                    row['country'].strip(),
                    neutral_bool
                )
                batch_data.append(data_tuple)
                
                # When batch is complete, flush it to the network layer
                if len(batch_data) == batch_size:
                    cursor.executemany(insert_query, batch_data)
                    connection.commit()  # Commits the transactional unit of work safely
                    total_rows += len(batch_data)
                    print(f" Imported {total_rows} matches...")
                    batch_data.clear()
            
            # Catch any trailing rows left over at the end of the file
            if batch_data:
                cursor.executemany(insert_query, batch_data)
                connection.commit()
                total_rows += len(batch_data)
                
        print(f" Ingestion successful! Total atomic match rows uploaded: {total_rows}")

    except Error as e:
        print(f"❌ Ingestion aborted due to SQL Error: {e}")
        connection.rollback()  # ACID Compliance: rolls back the failed chunk to keep database consistent
    except Exception as ex:
        print(f"❌ Runtime Exception: {ex}")

if __name__ == "__main__":
    # Execution sequence
    conn, curs = setup_database()
    
    if conn and curs:
        ingest_csv_data(conn, curs, 'results.csv')
        
        # System Resource Clean Up
        curs.close()
        conn.close()
        print("🔌 MySQL network channels successfully closed.")
