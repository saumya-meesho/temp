#!/usr/bin/env python3
"""
DDL Validator Script
Validates that migration DDL operations have already been applied to staging database 
before allowing production deployment. This ensures staging-production synchronization.
"""

import mysql.connector
from mysql.connector import Error
import os
import sys
import re
from dotenv import load_dotenv
from sql_ddl_parser import SQLDDLParser, MigrationFileValidator, extract_file_content_from_patch, fetch_github_files_data


class DatabaseConnection:
    """Handles MySQL database connections and queries."""
    
    def __init__(self, host, user, password, database, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self.cursor = None

    

    
    def connect(self):
        """Connect to the database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print(f"✅ Connected to staging database: {self.database} at {self.host}")
            return True
        except Error as e:
            print(f"❌ Error connecting to staging database: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def get_show_create_table(self, table_name):
        """Get SHOW CREATE TABLE output for detailed structure comparison."""
        try:
            query = f"SHOW CREATE TABLE `{table_name}`"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            if result:
                return result['Create Table']
            return None
        except Error as e:
            print(f"Error getting SHOW CREATE TABLE: {e}")
            return None


    
    def table_exists(self, table_name):
        """Check if a table exists in the database."""
        try:
            query = """
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            """
            self.cursor.execute(query, (self.database, table_name))
            result = self.cursor.fetchone()
            return result['count'] > 0
        except Error as e:
            print(f"Error checking table existence: {e}")
            return False
    
    def column_exists(self, table_name, column_name):
        """Check if a column exists in a table."""
        try:
            query = """
                SELECT COUNT(*) as count 
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s AND column_name = %s
            """
            self.cursor.execute(query, (self.database, table_name, column_name))
            result = self.cursor.fetchone()
            return result['count'] > 0
        except Error as e:
            print(f"Error checking column existence: {e}")
            return False
    
    def get_column_definition(self, table_name, column_name):
        """Get column definition from database."""
        try:
            query = """
                SELECT column_type, is_nullable, column_default, extra, column_comment
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s AND column_name = %s
            """
            self.cursor.execute(query, (self.database, table_name, column_name))
            result = self.cursor.fetchone()
            return result
        except Error as e:
            print(f"Error getting column definition: {e}")
            return None
    
    def index_exists(self, table_name, index_name):
        """Check if an index exists on a table."""
        try:
            query = """
                SELECT COUNT(*) as count 
                FROM information_schema.statistics 
                WHERE table_schema = %s AND table_name = %s AND index_name = %s
            """
            self.cursor.execute(query, (self.database, table_name, index_name))
            result = self.cursor.fetchone()
            return result['count'] > 0
        except Error as e:
            print(f"Error checking index existence: {e}")
            return False
        
    def get_primary_key_columns(self, table_name):
        """Get primary key columns from a table."""
        try:
            query = """
                SELECT column_name 
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE table_schema = %s AND table_name = %s AND constraint_name = 'PRIMARY'
            """
            self.cursor.execute(query, (self.database, table_name))
            result = self.cursor.fetchall()
            return [row['column_name'] for row in result]
        except Error as e:
            print(f"Error getting primary key columns: {e}")
    

class DDLValidator:
    """Validates DDL operations against staging database to ensure changes are already applied."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.validation_results = []

    def parse_create_table_sql(self, create_table_sql):
        """
        Parse a CREATE TABLE SQL statement and return a dictionary with:
        - table_name
        - columns: list of dicts {name, data_type}
        - primary_keys: list of column names
        """
        import re

        result = {
            "table_name": None,
            "columns": [],
            "primary_keys": []
        }

        # 1. Extract table name
        table_name_match = re.search(r'CREATE\s+TABLE\s+[`"]?(\w+)[`"]?', create_table_sql, re.IGNORECASE)
        if table_name_match:
            result["table_name"] = table_name_match.group(1)

        # 2. Extract table definition (inside parentheses)
        table_def_match = re.search(r'\((.*)\)\s*(ENGINE|TYPE|$)', create_table_sql, re.DOTALL)
        if not table_def_match:
            return result
        table_def = table_def_match.group(1)

        # 3. Split table definition into parts (columns, keys, constraints)
        def split_parts(definition):
            parts = []
            current = ""
            paren = 0
            for char in definition:
                if char == '(':
                    paren += 1
                elif char == ')':
                    paren -= 1
                if char == ',' and paren == 0:
                    if current.strip():
                        parts.append(current.strip())
                    current = ""
                else:
                    current += char
            if current.strip():
                parts.append(current.strip())
            return parts

        parts = split_parts(table_def)

        # 4. Parse each part
        for part in parts:
            # Column definition
            col_match = re.match(r'[`"]?(\w+)[`"]?\s+([^\s,]+)(.*)', part)
            if col_match and not part.upper().startswith(('PRIMARY KEY', 'KEY', 'UNIQUE', 'CONSTRAINT', 'FOREIGN KEY')):
                col_name = col_match.group(1)
                # Truncate length/precision from data_type (e.g., varchar(3) -> varchar, int(2) -> int)
                data_type_raw = col_match.group(2)
                data_type = re.sub(r'\s*\(.*\)', '', data_type_raw)
                result["columns"].append({
                    "name": col_name,
                    "data_type": data_type
                })
                
                continue

            # PRIMARY KEY
            pk_match = re.match(r'PRIMARY\s+KEY\s*\(([^)]+)\)', part, re.IGNORECASE)
            if pk_match:
                pk_cols = [c.strip().strip('`"') for c in pk_match.group(1).split(',')]
                result["primary_keys"].extend(pk_cols)
                continue


        return result
    
    def compare_parsed_create_table(self, parsed_expected, parsed_actual):
        """
        Compare two parsed CREATE TABLE SQL dictionaries.
        Returns a dict with 'equal': bool, and 'differences': list of strings describing differences.
        """
        differences = []

        # Compare table name
        if parsed_expected.get("table_name") != parsed_actual.get("table_name"):
            differences.append(f"Table name differs: {parsed_expected.get('table_name')} vs {parsed_actual.get('table_name')}")

        # Compare columns
        cols1 = parsed_expected.get("columns", {})
        cols2 = parsed_actual.get("columns", {})
        all_col_names = set(cols1.keys()) | set(cols2.keys())
        for col in all_col_names:
            if col not in cols1:
                differences.append(f"Column '{col}' missing in expected table")
            elif col not in cols2:
                differences.append(f"Column '{col}' missing in actual table")
            else:
                # Compare column attributes
                attrs1 = cols1[col]
                attrs2 = cols2[col]
                for attr in set(attrs1.keys()) | set(attrs2.keys()):
                    v1 = attrs1.get(attr)
                    v2 = attrs2.get(attr)
                    if v1 != v2:
                        differences.append(f"Column '{col}' attribute '{attr}' differs: {v1} vs {v2}")

        # Compare primary keys
        pk1 = set(parsed_expected.get("primary_keys", []))
        pk2 = set(parsed_actual.get("primary_keys", []))
        if pk1 != pk2:
            differences.append(f"Primary keys differ: {sorted(pk1)} vs {sorted(pk2)}")

        return {
            "equal": len(differences) == 0,
            "differences": differences
        }
    

    def compare_table_structures(self, expected_create_sql, actual_create_sql):
        """Compare two CREATE TABLE statements and return detailed differences."""
        parsed_expected = self.parse_create_table_sql(expected_create_sql)
        parsed_actual = self.parse_create_table_sql(actual_create_sql)
        return self.compare_parsed_create_table(parsed_expected, parsed_actual)


    def compare_column_definitions(self, expected_column, actual_column_def):
        """Compare expected column definition with actual column definition from staging."""
        differences = []

        for key in actual_column_def.keys():
            if key not in expected_column.keys() and actual_column_def[key] != '' and actual_column_def[key] != 'NULL':
                differences.append(f"Column property '{key}' mismatch - Expected: {actual_column_def[key]}, Actual: {expected_column[key]}")

            elif key in expected_column.keys() and expected_column[key].upper() != actual_column_def[key].upper():
                differences.append(f"Column property '{key}' mismatch - Expected: {expected_column[key]}, Actual: {actual_column_def[key]}")

        return len(differences) == 0, differences


    def validate_create_table(self, operation):
        """Validate that CREATE TABLE has already been applied to staging with exact structure match."""
        table_name = operation['table']
        expected_create_sql = operation.get('full_statement', '')
        
        print(f"\n🔍 Validating CREATE TABLE {table_name} (detailed structure comparison)")
        print("-" * 70)
        
        # Check if table already exists in staging (it should!)
        if not self.db.table_exists(table_name):
            print(f"❌ Table '{table_name}' does not exist in staging database")
            return False
        else:
            print(f"✅ Table '{table_name}' exists in staging database")
        
        # Get the actual table structure from staging using SHOW CREATE TABLE
        actual_create_sql = self.db.get_show_create_table(table_name)
        
        # Compare expected vs actual table structures
        if expected_create_sql and actual_create_sql:
            print(f"🔍 Comparing expected vs actual table structure...")
            structures_match, differences = self.compare_table_structures(expected_create_sql, actual_create_sql)
            if structures_match:
                print(f"🎯 Staging table structure matches migration exactly")
            else:
                print(f"📝 Structure differences found:")
                for i, diff in enumerate(differences, 1): 
                    print(f"{i}. {diff}")
                return False
            
        else:
            print(f"❌ No CREATE TABLE statement available for detailed comparison or table not found in staging database")
            return False
        
        return True


    def validate_alter_table(self, operation):
        """Validate ALTER TABLE operation has already been applied to staging."""
        table_name = operation['table']
        alter_operation = operation['operation']
        target = operation['target']
        target_type = operation['target_type']
        
        print(f"\n🔍 Validating ALTER TABLE {table_name} {alter_operation} {target_type} {target}")
        print(f"    (checking if change already applied to staging)")
        print("-" * 70)
        
        # Check if table exists in staging
        if not self.db.table_exists(table_name):
            print(f"❌ Table '{table_name}' does not exist in staging database")
            return False
        
        # Validate based on operation type
        if target_type == 'COLUMN':
            return self.validate_column_operation(operation)
        elif target_type == 'INDEX':
            return self.validate_index_operation(operation)
        elif target_type == 'PRIMARY_KEY':
            return self.validate_primary_key_operation(operation)
        elif target_type == 'FOREIGN_KEY':
            return self.validate_foreign_key_operation(operation)
        else:
            print(f"❌ Unknown target type: {target_type}")
            return False


    def validate_column_operation(self, operation):
        """Validate column operations have already been applied to staging with detailed comparison."""
        table_name = operation['table']
        alter_op = operation['operation']
        column_name = operation['target']
        expected_column_def = operation['details']
        
        if alter_op in ['ADD','MODIFY', 'CHANGE']:            
            # Get detailed column definition from staging
            actual_column_def = self.db.get_column_definition(table_name, column_name)
            
            if actual_column_def and expected_column_def:
                print(f"🔍 Comparing expected vs actual column definition...")
                print(f"✅ Column '{column_name}' exists in staging")
                
                # Perform detailed comparison
                match, differences = self.compare_column_definitions(expected_column_def, actual_column_def)              
                if match:
                    print(f"✅ Column '{column_name}' details matches staging")
                else:
                    print(f"❌ Column '{column_name}' details does not match staging")
                    for i, diff in enumerate(differences, 1): 
                        print(f"     {i}. {diff}")
                    return False
                    
            else:
                # Fallback to basic validation
                print(f"❌ Column '{column_name}' does not exist in staging")
                return False
        
        elif alter_op == 'DROP':
            # Check if column does NOT exist in staging (should already be dropped!)
            if not self.db.column_exists(table_name, column_name):
                print(f"✅ Column '{column_name}' already dropped from staging")
            else:
                print(f"❌ Column '{column_name}' does not exist in staging")
                return False
        
        else:
            print(f"❌ Unknown operation: {alter_op}")
            return False
        
        return True
    

    def validate_index_operation(self, operation):
        """Validate index operations have already been applied to staging."""
        table_name = operation['table']
        alter_op = operation['operation']
        column_name = operation['target']
        
        if alter_op == 'ADD':
            # Check if index already exists in staging (it should!)
            if self.db.index_exists(table_name, column_name):
                print(f"✅ Index '{column_name}' already exists in staging")
            else:
                print(f"❌ Index '{column_name}' does not exist in staging")
                return False
        
        elif alter_op == 'DROP':
            # Check if index does NOT exist in staging (should already be dropped!)
            if not self.db.index_exists(table_name, column_name):
                print(f"✅ Index '{column_name}' already dropped from staging")
            else:
                print(f"❌ Index '{column_name}' does not exist in staging")
                return False
        else:
            print(f"❌ Unknown operation: {alter_op}")
            return False
        
        return True
    

    def validate_primary_key_operation(self, operation):
        """Validate primary key operations have already been applied to staging."""
        table_name = operation['table']
        alter_op = operation['operation']
        expected_columns = operation['details']['columns']
        
        # Get actual primary key columns from staging
        actual_columns = self.db.get_primary_key_columns(table_name)        
        
        if alter_op == 'DROP':
            # logic need to add here
            print(f"   ⚠️  WARNING: Verify new primary key operation must be applied after!")
        elif alter_op == 'ADD':
            # Compare expected vs actual primary key columns
            if expected_columns == actual_columns:
                print(f"✅ Primary key can be added (columns match staging)")
            else:
                print(f"❌ Primary key columns mismatch - Expected: {expected_columns}, Actual: {actual_columns}")
                return False
        else:
            print(f"❌ Unknown operation: {alter_op}")
            return False
        
        return True
    

    def validate_foreign_key_operation(self, operation):
        """Validate foreign key operations have already been applied to staging."""
        table_name = operation['table']
        alter_op = operation['operation']
        target = operation['target']
        details = operation['details']
        
        # logic need to update here
        if alter_op == 'ADD' and 'referenced_table' in details:
            referenced_table = details['referenced_table']
            # Check if referenced table exists in staging
            if not self.db.table_exists(referenced_table):
                print(f"❌ Referenced table '{referenced_table}' does not exist in staging")
            else:
                print(f"✅ Foreign key can be added (referenced table exists in staging)")
                print(f"   📋 References: {referenced_table}")
        else:
            # logic need to add here
            print(f"✅ Foreign key {alter_op.lower()} operation detected")
        
        return True
    

    def validate_drop_table(self, operation):
        """Validate that DROP TABLE has already been applied to staging."""
        table_name = operation['table']
        database = operation['database']
        
        print(f"\n🔍 Validating DROP TABLE {table_name} (checking if already dropped from staging)")
        print("-" * 70)
        
        # Check if table does NOT exist in staging (should already be dropped!)
        if not self.db.table_exists(table_name):
            print(f"✅ Table '{table_name}' does not exist in staging")
        else:
            print(f"❌ Table '{table_name}' exists in staging")
            return False
        
        return True
    
def get_staging_config(database_name):
    """Get staging database configuration from environment variables or github secrets."""

    # Check environment and load appropriate configuration
    github_actions = os.getenv("GITHUB_ACTIONS")
    
    # Initialize staging_config variable
    staging_config = {}
    
    # if running in github actions, use github secrets
    if github_actions == "true":
        print("🔄 Running in GitHub Actions environment")
        print("🔐 Using GitHub Secrets for database credentials")
        
        # Use GitHub secrets (set as environment variables in workflow)
        staging_config = {
            'host': os.getenv('STAGING_DB_HOST'),
            'user': os.getenv('STAGING_DB_USER'),
            'password': os.getenv('STAGING_DB_PASSWORD'),
            'port': int(os.getenv('STAGING_DB_PORT', '3306'))
        }
        
        # Validate required secrets are present
        required_secrets = ['STAGING_DB_HOST', 'STAGING_DB_USER', 'STAGING_DB_PASSWORD']
        missing_secrets = [secret for secret in required_secrets if not os.getenv(secret)]
        if missing_secrets:
            print(f"❌ Missing GitHub secrets: {', '.join(missing_secrets)}")
            print("Please configure these secrets in your GitHub repository:")
            for secret in missing_secrets:
                print(f"  - {secret}")
            exit(1)

    # if running locally, use config.env file
    else:
        print("🔄 Running in local environment")
        print("🔐 Using config.env for database credentials")
        
        # Load from config.env file for local development
        load_dotenv('config.env')
        
        # get staging config from config.env file
        staging_config = {
            'host': os.getenv('STAGING_DB_HOST'),
            'user': os.getenv('STAGING_DB_USER'),
            'password': os.getenv('STAGING_DB_PASSWORD'),
            'port': int(os.getenv('STAGING_DB_PORT', '3306'))
        }

        # validate required secrets are present
        required_secrets = ['STAGING_DB_HOST', 'STAGING_DB_USER', 'STAGING_DB_PASSWORD']
        missing_secrets = [secret for secret in required_secrets if not os.getenv(secret)]
        if missing_secrets:
            print(f"❌ Missing secrets: {', '.join(missing_secrets)}")
            print("Please configure these secrets in your config.env file:")
            for secret in missing_secrets:
                print(f"  - {secret}")
            exit(1)
    
    # add database name to staging config
    staging_config['database'] = database_name
    print(f"Staging Database: {staging_config['database']} at {staging_config['host']}")
    print(f"Database User: {staging_config['user']}")    
    
    return staging_config


def main():
    """Main function to validate that DDL operations have already been applied to staging database."""
    
    print("🔍 DDL Validator - Staging-Production Synchronization Check")
    print("=" * 60)
    print("Verifying that all migration changes have been pre-applied to staging...")

    
    #fetch github files data from new PR on github
    files_data = fetch_github_files_data()
    
    # Validate migration file pairs
    validator = MigrationFileValidator()
    is_valid, migration, rollback = validator.validate(files_data)  
    if not is_valid:
        exit(1)
    
    # Parse migration file
    file_info = migration['file_info']
    patch = file_info.get('patch', '')
    if not patch:
        print("❌ No patch data available for migration file")
        exit(1)

    # extract file content from patch
    file_content = extract_file_content_from_patch(patch)
    if not file_content:
        print("❌ Could not extract file content from patch")
        exit(1)
    
    # Parse DDL operations
    parser = SQLDDLParser()
    parser.parse_sql_file(file_content, migration['filename'])
    operations = parser.get_operations()
    print(f"\n🔍 Found {len(operations)} DDL operations to verify against staging")

    # Extract database name from migration file path
    database_name = parser.extract_database_name(migration['filename'])
    print(f"📁 Extracted database name from file path: {database_name}")
    
    # get staging config from environment variables
    staging_config = get_staging_config(database_name)
    
    # connect to staging database
    db = DatabaseConnection(**staging_config)
    if not db.connect():
        exit(1)
    
    try:
        print("Checking if each operation has already been applied to staging database...")
        
        # Validate each operation
        ddl_validator = DDLValidator(db)
        validation_summary = []
        for operation in operations:
            op_type = operation['command']
            if op_type == 'CREATE_TABLE':
                result = ddl_validator.validate_create_table(operation)
            elif op_type == 'ALTER_TABLE':
                result = ddl_validator.validate_alter_table(operation)
            elif op_type == 'DROP_TABLE':
                result = ddl_validator.validate_drop_table(operation)
            else:
                print(f"⚠️  Unknown operation: {op_type}")
                result = False

            summary_entry = {
                "operation": op_type,
                "table": operation.get('table'),
                "target": operation.get('target', None),
                "status": "PASSED" if result else "FAILED"
            }
            validation_summary.append(summary_entry)

        # print validation summary
        print("\n===== DDL Validation Summary =====")
        for entry in validation_summary:
            op = entry["operation"]
            table = entry.get("table")
            target = entry.get("target")
            status = entry["status"]
            if target:
                print(f"{op} on {table} ({target}): {status}")
            else:
                print(f"{op} on {table}: {status}")
        
        if any(entry["status"] == "FAILED" for entry in validation_summary):
            exit(1)
        
    
    finally:
        db.close()


if __name__ == "__main__":
    main() 