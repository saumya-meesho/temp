#!/usr/bin/env python3
"""
SQL DDL Parser Script
Fetches newly added files from GitHub PR and parses SQL DDL commands
to extract CREATE/ALTER operations with detailed analysis.
"""

import requests
import os
import json
from dotenv import load_dotenv
import re
import base64

class MigrationFileValidator:
    """Validates migration and rollback file pairs from GitHub PR."""
    
    def __init__(self):
        # Pattern: V{number}__{name}.sql and U{number}__{name}-rollback.sql
        self.migration_pattern = re.compile(r'^V(\d+)__(.+)\.sql$')
        self.rollback_pattern = re.compile(r'^U(\d+)__(.+)-rollback\.sql$')
        self.migration_files = []
        self.rollback_files = []
    
    def extract_file_info(self, files_data):
        """Extract migration and rollback files from PR files data."""
        self.migration_files = []
        self.rollback_files = []
        
        for file_info in files_data:
            filename = file_info.get("filename", "")
            status = file_info.get("status", "")
            basename = filename.split('/')[-1]  # Get just the filename part
            
            if status == "added" and filename.lower().endswith('.sql'):
                # Check if it's a migration file
                migration_match = self.migration_pattern.match(basename)
                print(f"Migration match: {migration_match}")
                print(f"Basename: {basename}")
                if migration_match:
                    version = migration_match.group(1)
                    name = migration_match.group(2)
                    self.migration_files.append({
                        'file_info': file_info,
                        'version': version,
                        'name': name,
                        'basename': basename,
                        'filename': filename
                    })
                
                # Check if it's a rollback file
                rollback_match = self.rollback_pattern.match(basename)
                if rollback_match:
                    version = rollback_match.group(1)
                    name = rollback_match.group(2)
                    self.rollback_files.append({
                        'file_info': file_info,
                        'version': version,
                        'name': name,
                        'basename': basename,
                        'filename': filename
                    })
    
    def validate_file_counts(self):
        """Validate that exactly one migration and one rollback file exist."""
        # Validate exactly one migration file
        if len(self.migration_files) == 0:
            print("❌ ERROR: No valid migration files found in this PR!")
            print("   Required: Exactly one migration file with pattern:")
            print("   - V{number}__{name}.sql (e.g., V1__create_users_table.sql)")
            print("   - Status: newly added")
            return False
        elif len(self.migration_files) > 1:
            print("❌ ERROR: Multiple migration files found in this PR!")
            print("   Required: Exactly ONE migration file, but found:")
            for mf in self.migration_files:
                print(f"   - {mf['filename']}")
            print("   Please ensure only one migration file is added per PR.")
            return False
        
        # Validate exactly one rollback file
        if len(self.rollback_files) == 0:
            print("❌ ERROR: No valid rollback files found in this PR!")
            print("   Required: Exactly one rollback file with pattern:")
            print("   - U{number}__{name}-rollback.sql")
            print("   - Status: newly added")
            return False
        elif len(self.rollback_files) > 1:
            print("❌ ERROR: Multiple rollback files found in this PR!")
            print("   Required: Exactly ONE rollback file, but found:")
            for rf in self.rollback_files:
                print(f"   - {rf['filename']}")
            print("   Please ensure only one rollback file is added per PR.")
            return False
        
        return True
    
    def validate_file_matching(self):
        """Validate that migration and rollback files have matching versions and names."""
        migration = self.migration_files[0]
        rollback = self.rollback_files[0]
        
        if migration['version'] != rollback['version']:
            print("❌ ERROR: Migration and rollback version numbers don't match!")
            print(f"   Migration: V{migration['version']}__{migration['name']}.sql")
            print(f"   Rollback:  U{rollback['version']}__{rollback['name']}-rollback.sql")
            print("   Both files must have the same version number.")
            return False
        
        if migration['name'] != rollback['name']:
            print("❌ ERROR: Migration and rollback names don't match!")
            print(f"   Migration: V{migration['version']}__{migration['name']}.sql")
            print(f"   Rollback:  U{rollback['version']}__{rollback['name']}-rollback.sql")
            print("   Both files must have the same name part.")
            return False
        
        return True
    
    def validate(self, files_data):
        """Main validation method that runs all checks."""
        print(f"📁 Total Changed Files: {len(files_data)}")
        
        # Extract file information
        self.extract_file_info(files_data)
        
        print(f"📄 Migration Files Found: {len(self.migration_files)}")
        print(f"📄 Rollback Files Found: {len(self.rollback_files)}")
        
        # Validate file counts
        if not self.validate_file_counts():
            return False, None, None
        
        # Validate file matching
        if not self.validate_file_matching():
            return False, None, None
        
        # Success
        migration = self.migration_files[0]
        rollback = self.rollback_files[0]
        
        print(f"✅ Valid migration pair found:")
        print(f"   Migration: {migration['filename']}")
        print(f"   Rollback:  {rollback['filename']}")
        
        return True, migration, rollback


def extract_file_content_from_patch(patch):
    """Extract complete file content from git patch for newly added files."""
    if not patch:
        return None
    
    lines = patch.split('\n')
    content_lines = []
    
    for line in lines:
        # Skip patch headers and metadata
        if line.startswith('@@') or line.startswith('+++') or line.startswith('---'):
            continue
        
        # For newly added files, all content lines start with '+'
        if line.startswith('+'):
            content_lines.append(line[1:])  # Remove the '+' prefix
        elif line.startswith(' '):
            content_lines.append(line[1:])  # Remove the ' ' prefix (context lines)
    
    return '\n'.join(content_lines)


class SQLDDLParser:
    def __init__(self):
        self.ddl_operations = []
    
    def extract_database_name(self, file_path):
        """Extract database name from file path (directory just before filename)."""
        path_parts = file_path.strip('/').split('/')
        if len(path_parts) >= 2:
            return path_parts[-2]  # Directory just before the filename
        return "unknown_database"
    
    def parse_create_table(self, sql_content, database_name):
        """Parse CREATE TABLE statements."""
        # Regex to match CREATE TABLE statements (non-greedy up to the next semicolon)
        create_table_pattern = r'CREATE\s+TABLE\s+.*?;'
        matches = re.finditer(create_table_pattern, sql_content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            full_statement = match.group(0)
            # Try to extract the table name using regex
            table_name_match = re.search(r'CREATE\s+TABLE\s+[`"]?(\w+)[`"]?', full_statement, re.IGNORECASE)
            table_name = table_name_match.group(1) if table_name_match else "unknown_table"
            operation = {
                'type': 'CREATE',
                'command': 'CREATE_TABLE',
                'database': database_name,
                'table': table_name,
                'full_statement': full_statement.strip().replace(';', '')
            }
            self.ddl_operations.append(operation)
    
    
    def parse_alter_table(self, sql_content, database_name):
        """Parse ALTER TABLE statements."""
        # Regex to match ALTER TABLE statements
        alter_pattern = r'ALTER\s+TABLE\s+[`"]?(\w+)[`"]?\s+(.*?);'
        
        matches = re.finditer(alter_pattern, sql_content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            table_name = match.group(1)
            alter_clause = match.group(2).strip()
            
            # Parse the specific ALTER operation
            alter_operations = self.parse_alter_operations(alter_clause)
            
            for alter_op in alter_operations:
                operation = {
                    'type': 'ALTER',
                    'command': 'ALTER_TABLE',
                    'database': database_name,
                    'table': table_name,
                    'operation': alter_op['operation'],
                    'target': alter_op['target'],
                    'target_type': alter_op['target_type'],
                    'details': alter_op['details'],
                    'full_statement': match.group(0).strip()
                }
                
                self.ddl_operations.append(operation)
    
    def parse_table_definition(self, definition):
        """Parse table definition to extract columns, indexes, and constraints."""
        columns = []
        indexes = []
        constraints = []
        
        # Split by commas, but be careful of commas inside parentheses
        parts = self.split_table_definition(definition)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Check if it's a column definition
            if self.is_column_definition(part):
                column_info = self.parse_column_definition(part)
                columns.append(column_info)
            
            # Check if it's an index
            elif re.match(r'(?:KEY|INDEX)\s+', part, re.IGNORECASE):
                index_info = self.parse_index_definition(part)
                indexes.append(index_info)
            
            # Check if it's a primary key
            elif re.match(r'PRIMARY\s+KEY', part, re.IGNORECASE):
                constraint_info = self.parse_primary_key_definition(part)
                constraints.append(constraint_info)
            
            # Check if it's a foreign key
            elif re.match(r'(?:CONSTRAINT\s+\w+\s+)?FOREIGN\s+KEY', part, re.IGNORECASE):
                constraint_info = self.parse_foreign_key_definition(part)
                constraints.append(constraint_info)
            
            # Check if it's a unique constraint
            elif re.match(r'UNIQUE\s+(?:KEY\s+)?', part, re.IGNORECASE):
                constraint_info = self.parse_unique_constraint_definition(part)
                constraints.append(constraint_info)
        
        return columns, indexes, constraints
    
    def split_table_definition(self, definition):
        """Split table definition by commas, respecting parentheses."""
        parts = []
        current_part = ""
        paren_count = 0
        
        for char in definition:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                parts.append(current_part.strip())
                current_part = ""
                continue
            
            current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        return parts
    
    def is_column_definition(self, part):
        """Check if a part is a column definition."""
        # Column definitions start with a column name followed by a data type
        column_pattern = r'^[`"]?\w+[`"]?\s+\w+'
        return re.match(column_pattern, part, re.IGNORECASE) is not None
    
    def parse_column_definition(self, part):
        """Parse a column definition."""
        attrs = {}
        # Extract column name and data type
        match = re.match(r'[`"]?(\w+)[`"]?\s+(\w+(?:\([^)]*\))?)(.*)', part, re.IGNORECASE)
        if match:
            attrs['COLUMN_NAME'] = match.group(1)
            attrs['COLUMN_TYPE'] = match.group(2)
            attributes = match.group(3).strip()

            # Check for NOT NULL
            if re.search(r'NOT\s+NULL', attributes, re.IGNORECASE):
                attrs['IS_NULLABLE'] = "NO"
            
            # Check for NULL
            elif re.search(r'\bNULL\b', attributes, re.IGNORECASE):
                attrs['IS_NULLABLE'] = "YES"
            
            # Check for AUTO_INCREMENT
            if re.search(r'AUTO_INCREMENT', attributes, re.IGNORECASE):
                attrs['EXTRA'] = "auto_increment"
            
            # Check for DEFAULT
            default_match = re.search(r'DEFAULT\s+([^,\s]+)', attributes, re.IGNORECASE)
            if default_match:
                attrs['COLUMN_DEFAULT'] = default_match.group(1).strip()
                # If the column data type is TIMESTAMP or DATETIME, set EXTRA to DEFAULT_GENERATED
                if re.search(r'\bCURRENT_TIMESTAMP\b', attributes, re.IGNORECASE):
                    attrs['EXTRA'] = "DEFAULT_GENERATED"
                
            # Check if there's ON UPDATE 
            on_update_match = re.search(r'ON\s+UPDATE\s+([^,\s]+(?:\s+[^,]*)?)', attributes, re.IGNORECASE)
            if on_update_match:
                on_update_value = on_update_match.group(1).strip()
                # Combine DEFAULT and ON UPDATE for EXTRA field
                if attrs.get('EXTRA'):
                    attrs['EXTRA'] += f" on update {on_update_value}"
                else:
                    attrs['EXTRA'] = f"on update {on_update_value}"
            
            # Check for COMMENT
            comment_match = re.search(r'COMMENT\s+[\'"]([^\'"]*)[\'"]', attributes, re.IGNORECASE)
            if comment_match:
                attrs['COLUMN_COMMENT'] = comment_match.group(1)

            
            return attrs
        
        return {'COLUMN_NAME': 'unknown', 'COLUMN_TYPE': 'unknown', 'full_definition': part}
    
    
    def parse_index_definition(self, part):
        """Parse index definition."""
        # KEY index_name (columns)
        match = re.match(r'(?:KEY|INDEX)\s+(?:[`"]?(\w+)[`"]?\s+)?\(([^)]+)\)', part, re.IGNORECASE)
        
        if match:
            index_name = match.group(1) or 'unnamed_index'
            columns = [col.strip().strip('`"') for col in match.group(2).split(',')]
            
            return {
                'name': index_name,
                'columns': columns,
                'type': 'INDEX',
                'full_definition': part
            }
        
        return {'name': 'unknown', 'columns': [], 'type': 'INDEX', 'full_definition': part}
    
    def parse_primary_key_definition(self, part):
        """Parse primary key definition."""
        match = re.match(r'PRIMARY\s+KEY\s+\(([^)]+)\)', part, re.IGNORECASE)
        
        if match:
            columns = [col.strip().strip('`"') for col in match.group(1).split(',')]
            
            return {
                'type': 'PRIMARY_KEY',
                'columns': columns,
                'full_definition': part
            }
        
        return {'type': 'PRIMARY_KEY', 'columns': [], 'full_definition': part}
    
    def parse_foreign_key_definition(self, part):
        """Parse foreign key definition."""
        # CONSTRAINT name FOREIGN KEY (columns) REFERENCES table(columns)
        match = re.match(r'(?:CONSTRAINT\s+[`"]?(\w+)[`"]?\s+)?FOREIGN\s+KEY\s+\(([^)]+)\)\s+REFERENCES\s+[`"]?(\w+)[`"]?\s*\(([^)]+)\)', part, re.IGNORECASE)
        
        if match:
            constraint_name = match.group(1) or 'unnamed_fk'
            local_columns = [col.strip().strip('`"') for col in match.group(2).split(',')]
            referenced_table = match.group(3)
            referenced_columns = [col.strip().strip('`"') for col in match.group(4).split(',')]
            
            return {
                'type': 'FOREIGN_KEY',
                'name': constraint_name,
                'columns': local_columns,
                'referenced_table': referenced_table,
                'referenced_columns': referenced_columns,
                'full_definition': part
            }
        
        return {'type': 'FOREIGN_KEY', 'name': 'unknown', 'columns': [], 'full_definition': part}
    
    def parse_unique_constraint_definition(self, part):
        """Parse unique constraint definition."""
        match = re.match(r'UNIQUE\s+(?:KEY\s+[`"]?(\w+)[`"]?\s+)?\(([^)]+)\)', part, re.IGNORECASE)
        
        if match:
            constraint_name = match.group(1) or 'unnamed_unique'
            columns = [col.strip().strip('`"') for col in match.group(2).split(',')]
            
            return {
                'type': 'UNIQUE',
                'name': constraint_name,
                'columns': columns,
                'full_definition': part
            }
        
        return {'type': 'UNIQUE', 'name': 'unknown', 'columns': [], 'full_definition': part}
    
    def parse_alter_operations(self, alter_clause):
        """Parse ALTER TABLE operations."""
        operations = []
        
        # Split multiple operations separated by commas
        parts = self.split_table_definition(alter_clause)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # ADD COLUMN
            if re.match(r'ADD\s+(?:COLUMN\s+)?', part, re.IGNORECASE):
                op = self.parse_add_column(part)
                operations.append(op)
            
            # DROP COLUMN
            elif re.match(r'DROP\s+(?:COLUMN\s+)?', part, re.IGNORECASE):
                op = self.parse_drop_column(part)
                operations.append(op)
            
            # MODIFY COLUMN
            elif re.match(r'MODIFY\s+(?:COLUMN\s+)?', part, re.IGNORECASE):
                op = self.parse_modify_column(part)
                operations.append(op)
            
            # CHANGE COLUMN
            elif re.match(r'CHANGE\s+(?:COLUMN\s+)?', part, re.IGNORECASE):
                op = self.parse_change_column(part)
                operations.append(op)
            
            # ADD INDEX
            elif re.match(r'ADD\s+(?:INDEX|KEY)', part, re.IGNORECASE):
                op = self.parse_add_index(part)
                operations.append(op)
            
            # DROP INDEX
            elif re.match(r'DROP\s+(?:INDEX|KEY)', part, re.IGNORECASE):
                op = self.parse_drop_index(part)
                operations.append(op)
            
            # ADD PRIMARY KEY
            elif re.match(r'ADD\s+PRIMARY\s+KEY', part, re.IGNORECASE):
                op = self.parse_add_primary_key(part)
                operations.append(op)
            
            # DROP PRIMARY KEY
            elif re.match(r'DROP\s+PRIMARY\s+KEY', part, re.IGNORECASE):
                op = self.parse_drop_primary_key(part)
                operations.append(op)
            
            # ADD FOREIGN KEY
            elif re.match(r'ADD\s+(?:CONSTRAINT\s+\w+\s+)?FOREIGN\s+KEY', part, re.IGNORECASE):
                op = self.parse_add_foreign_key(part)
                operations.append(op)
            
            # DROP FOREIGN KEY
            elif re.match(r'DROP\s+FOREIGN\s+KEY', part, re.IGNORECASE):
                op = self.parse_drop_foreign_key(part)
                operations.append(op)
            
            else:
                # Unknown operation
                operations.append({
                    'operation': 'UNKNOWN',
                    'target': 'unknown',
                    'target_type': 'unknown',
                    'details': {'raw': part}
                })
        
        return operations
    
    def parse_add_column(self, part):
        """Parse ADD COLUMN operation."""
        match = re.match(r'ADD\s+(?:COLUMN\s+)?(.+)', part, re.IGNORECASE)
        if match:
            column_def = match.group(1)
            column_info = self.parse_column_definition(column_def)
            
            return {
                'operation': 'ADD',
                'target': column_info['COLUMN_NAME'],
                'target_type': 'COLUMN',
                'details': column_info
            }
        
        return {'operation': 'ADD', 'target': 'unknown', 'target_type': 'COLUMN', 'details': {}}
    
    def parse_drop_column(self, part):
        """Parse DROP COLUMN operation."""
        match = re.match(r'DROP\s+(?:COLUMN\s+)?[`"]?(\w+)[`"]?', part, re.IGNORECASE)
        if match:
            column_name = match.group(1)
            
            return {
                'operation': 'DROP',
                'target': column_name,
                'target_type': 'COLUMN',
                'details': {'name': column_name}
            }
        
        return {'operation': 'DROP', 'target': 'unknown', 'target_type': 'COLUMN', 'details': {}}
    
    def parse_modify_column(self, part):
        """Parse MODIFY COLUMN operation."""
        match = re.match(r'MODIFY\s+(?:COLUMN\s+)?(.+)', part, re.IGNORECASE)
        if match:
            column_def = match.group(1)
            column_info = self.parse_column_definition(column_def)
            
            return {
                'operation': 'MODIFY',
                'target': column_info['COLUMN_NAME'],
                'target_type': 'COLUMN',
                'details': column_info
            }
        
        return {'operation': 'MODIFY', 'target': 'unknown', 'target_type': 'COLUMN', 'details': {}}
    
    def parse_change_column(self, part):
        """Parse CHANGE COLUMN operation."""
        match = re.match(r'CHANGE\s+(?:COLUMN\s+)?[`"]?(\w+)[`"]?\s+(.+)', part, re.IGNORECASE)
        if match:
            old_name = match.group(1)
            new_column_def = match.group(2)
            new_column_info = self.parse_column_definition(new_column_def)
            
            return {
                'operation': 'CHANGE',
                'target': new_column_info['COLUMN_NAME'],
                'target_type': 'COLUMN',
                'details': new_column_info
            }
        
        return {'operation': 'CHANGE', 'target': 'unknown', 'target_type': 'COLUMN', 'details': {}}
    
    def parse_add_index(self, part):
        """Parse ADD INDEX operation."""
        match = re.match(r'ADD\s+(?:INDEX|KEY)\s+(?:[`"]?(\w+)[`"]?\s+)?\(([^)]+)\)', part, re.IGNORECASE)
        if match:
            index_name = match.group(1) or 'unnamed_index'
            columns = [col.strip().strip('`"') for col in match.group(2).split(',')]
            
            return {
                'operation': 'ADD',
                'target': index_name,
                'target_type': 'INDEX',
                'details': {
                    'name': index_name,
                    'columns': columns
                }
            }
        
        return {'operation': 'ADD', 'target': 'unknown', 'target_type': 'INDEX', 'details': {}}
    
    def parse_drop_index(self, part):
        """Parse DROP INDEX operation."""
        match = re.match(r'DROP\s+(?:INDEX|KEY)\s+[`"]?(\w+)[`"]?', part, re.IGNORECASE)
        if match:
            index_name = match.group(1)
            
            return {
                'operation': 'DROP',
                'target': index_name,
                'target_type': 'INDEX',
                'details': {'name': index_name}
            }
        
        return {'operation': 'DROP', 'target': 'unknown', 'target_type': 'INDEX', 'details': {}}
    
    def parse_add_primary_key(self, part):
        """Parse ADD PRIMARY KEY operation."""
        match = re.match(r'ADD\s+PRIMARY\s+KEY\s+\(([^)]+)\)', part, re.IGNORECASE)
        if match:
            columns = [col.strip().strip('`"') for col in match.group(1).split(',')]
            
            return {
                'operation': 'ADD',
                'target': 'PRIMARY_KEY',
                'target_type': 'PRIMARY_KEY',
                'details': {'columns': columns}
            }
        
        return {'operation': 'ADD', 'target': 'PRIMARY_KEY', 'target_type': 'PRIMARY_KEY', 'details': {}}
    
    def parse_drop_primary_key(self, part):
        """Parse DROP PRIMARY KEY operation."""
        return {
            'operation': 'DROP',
            'target': 'PRIMARY_KEY',
            'target_type': 'PRIMARY_KEY',
            'details': {}
        }
    
    def parse_add_foreign_key(self, part):
        """Parse ADD FOREIGN KEY operation."""
        match = re.match(r'ADD\s+(?:CONSTRAINT\s+[`"]?(\w+)[`"]?\s+)?FOREIGN\s+KEY\s+\(([^)]+)\)\s+REFERENCES\s+[`"]?(\w+)[`"]?\s*\(([^)]+)\)', part, re.IGNORECASE)
        if match:
            constraint_name = match.group(1) or 'unnamed_fk'
            local_columns = [col.strip().strip('`"') for col in match.group(2).split(',')]
            referenced_table = match.group(3)
            referenced_columns = [col.strip().strip('`"') for col in match.group(4).split(',')]
            
            return {
                'operation': 'ADD',
                'target': constraint_name,
                'target_type': 'FOREIGN_KEY',
                'details': {
                    'name': constraint_name,
                    'columns': local_columns,
                    'referenced_table': referenced_table,
                    'referenced_columns': referenced_columns
                }
            }
        
        return {'operation': 'ADD', 'target': 'unknown', 'target_type': 'FOREIGN_KEY', 'details': {}}
    
    def parse_drop_foreign_key(self, part):
        """Parse DROP FOREIGN KEY operation."""
        match = re.match(r'DROP\s+FOREIGN\s+KEY\s+[`"]?(\w+)[`"]?', part, re.IGNORECASE)
        if match:
            constraint_name = match.group(1)
            
            return {
                'operation': 'DROP',
                'target': constraint_name,
                'target_type': 'FOREIGN_KEY',
                'details': {'name': constraint_name}
            }
        
        return {'operation': 'DROP', 'target': 'unknown', 'target_type': 'FOREIGN_KEY', 'details': {}}
    
    def parse_sql_file(self, file_content, file_path):
        """Parse SQL file content and extract DDL operations."""
        database_name = self.extract_database_name(file_path)
        
        # Clean up the SQL content
        # sql_content = self.clean_sql_content(file_content)
        sql_content = file_content
        
        # Parse CREATE TABLE statements
        self.parse_create_table(sql_content, database_name)
        
        # Parse ALTER TABLE statements
        self.parse_alter_table(sql_content, database_name)
        
        # Parse other DDL statements if needed (CREATE INDEX, DROP TABLE, etc.)
        self.parse_other_ddl(sql_content, database_name)
    
    def clean_sql_content(self, content):
        """Clean SQL content by removing comments and normalizing whitespace."""
        # Remove single-line comments
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def parse_other_ddl(self, sql_content, database_name):
        """Parse other DDL statements like CREATE INDEX, DROP TABLE, etc."""
        # DROP TABLE
        drop_table_pattern = r'DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?[`"]?(\w+)[`"]?'
        matches = re.finditer(drop_table_pattern, sql_content, re.IGNORECASE)
        
        for match in matches:
            table_name = match.group(1)
            
            operation = {
                'type': 'DROP',
                'command': 'DROP_TABLE',
                'database': database_name,
                'table': table_name,
                'full_statement': match.group(0).strip()
            }
            
            self.ddl_operations.append(operation)
        
        # CREATE INDEX
        create_index_pattern = r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+[`"]?(\w+)[`"]?\s+ON\s+[`"]?(\w+)[`"]?\s*\(([^)]+)\)'
        matches = re.finditer(create_index_pattern, sql_content, re.IGNORECASE)
        
        for match in matches:
            index_name = match.group(1)
            table_name = match.group(2)
            columns = [col.strip().strip('`"') for col in match.group(3).split(',')]
            
            operation = {
                'type': 'CREATE',
                'command': 'CREATE_INDEX',
                'database': database_name,
                'table': table_name,
                'index_name': index_name,
                'columns': columns,
                'full_statement': match.group(0).strip()
            }
            
            self.ddl_operations.append(operation)
    
    def get_operations(self):
        """Get all parsed DDL operations."""
        return self.ddl_operations
    
    def print_operations_summary(self):
        """Print a summary of all parsed operations."""
        if not self.ddl_operations:
            print("No DDL operations found.")
            return
        
        print(f"\n🔍 Found {len(self.ddl_operations)} DDL Operations:")
        print("=" * 80)
        
        for i, op in enumerate(self.ddl_operations, 1):
            print(f"\n{i}. {op['type']} Operation:")
            print(f"   Command: {op['command']}")
            print(f"   Database: {op['database']}")
            print(f"   Table: {op['table']}")
            
            if op['type'] == 'CREATE' and op['command'] == 'CREATE_TABLE':
                print(f"   Full statement: {op['full_statement']}")
                
            
            elif op['type'] == 'ALTER':
                print(f"   Operation: {op['operation']}")
                print(f"   Target: {op['target']} ({op['target_type']})")
                print(f"   Details: {op['details']}")
            
            elif op['command'] == 'CREATE_INDEX':
                print(f"   Index: {op['index_name']}")
                print(f"   Columns: {', '.join(op['columns'])}")


def main():
    """Main function to fetch and parse SQL files from GitHub PR."""
    
    # Load environment variables
    try:
        github_actions = os.getenv("GITHUB_ACTIONS")
        if github_actions == "true":
            print("🔄 Running in GitHub Actions environment")
            event_path = os.getenv("GITHUB_EVENT_PATH")
            if not event_path or not os.path.exists(event_path):
                print("❌ GITHUB_EVENT_PATH not found!")
                exit(1)
            
            with open(event_path) as f:
                event = json.load(f)
                pr_number = event["pull_request"]["number"]
        else:
            print("🔄 Running in local environment")
            load_dotenv('config.env')
            pr_number = os.getenv("GITHUB_PR_NUMBER")
        
        repo_full = os.getenv("GITHUB_REPOSITORY")
        token = os.getenv("GITHUB_TOKEN")
        
        print(f"Repository: {repo_full}")
        print(f"PR Number: {pr_number}")
        
    except Exception as e:
        print(f"❌ Error reading environment: {e}")
        exit(1)
    
    if not all([repo_full, token, pr_number]):
        print("❌ Missing required environment variables!")
        exit(1)
    
    # GitHub API headers
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    # Fetch files changed in the PR
    files_url = f"https://api.github.com/repos/{repo_full}/pulls/{pr_number}/files"
    print(f"\n🔍 Fetching changed files from PR #{pr_number}...")
    
    files_response = requests.get(files_url, headers=headers)
    
    if files_response.status_code != 200:
        print(f"❌ Error fetching files: {files_response.status_code}")
        print(f"Response: {files_response.text}")
        exit(1)
    
    files_data = files_response.json()
    
    # Validate migration file pairs using the validator class
    validator = MigrationFileValidator()
    is_valid, migration, rollback = validator.validate(files_data)
    
    if not is_valid:
        exit(1)
    
    # Initialize SQL parser
    parser = SQLDDLParser()
    
    # Process the migration file (main DDL operations)
    file_info = migration['file_info']
    filename = migration['filename']
    print(f"\n📄 Processing migration file: {filename}")
    print("-" * 50)
    
    # Get file content from PR patch (for newly added files)
    patch = file_info.get('patch', '')
    if patch:
        # For newly added files, extract content from patch
        file_content = extract_file_content_from_patch(patch)
        
        if file_content:
            # Parse the migration file
            parser.parse_sql_file(file_content, filename)
        else:
            print("❌ Could not extract file content from patch")
            exit(1)
    else:
        print("❌ No patch data available for newly added file")
        exit(1)
    
    
    
    # Print summary of all operations
    print(f"\n" + "=" * 80)
    print(f"📊 MIGRATION FILE ANALYSIS")
    parser.print_operations_summary()


if __name__ == "__main__":
    main() 