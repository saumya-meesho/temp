#!/usr/bin/env python3
"""
MySQL Query Script
Connects to MySQL server and runs SHOW CREATE TABLE ab.audiences
"""

import mysql.connector
from mysql.connector import Error
import sys


class MySQLQueryTool:
    def __init__(self, host: str, user: str, password: str, port: int = 3306):
        """Initialize MySQL connection parameters."""
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Establish connection to MySQL server."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print(f"✅ Successfully connected to MySQL server at {self.host}:{self.port}")
            return True
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return False

    def show_create_table(self, table_name: str) -> None:
        """Execute SHOW CREATE TABLE query and display results."""
        try:
            query = f"SHOW CREATE TABLE {table_name}"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if not results:
                print("📋 Query returned no results.")
                return
            
            print(f"\nQuery: {query}")
            print("-" * 80)
            for row in results:
                table_name = row[0]
                create_statement = row[1]
                print(f"Table: {table_name}")
                print(f"Create Table: {create_statement}")
            print()
            
            # Consume any remaining results
            while self.cursor.nextset():
                pass
                
        except Error as e:
            print(f"❌ Error executing query: {e}")

    def close(self) -> None:
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔒 Database connection closed.")


def main():
    # Hardcoded connection parameters
    host = 'localhost'
    user = 'root'
    password = 'saumya'
    port = 3306
    
    print(f"🔄 Attempting to connect to MySQL server at {host}:{port}")
    print(f"   User: {user}")
    print(f"   Password: ***")
    
    # Create MySQL tool and connect
    mysql_tool = MySQLQueryTool(
        host=host,
        user=user,
        password=password,
        port=port
    )
    
    if not mysql_tool.connect():
        print(f"\nCould not connect to MySQL server")
        sys.exit(1)
    
    try:
        # Execute the specific query
        print("\nConnected successfully! Running query...")
        mysql_tool.show_create_table("ab.audiences")
    
    finally:
        mysql_tool.close()


if __name__ == "__main__":
    main() 