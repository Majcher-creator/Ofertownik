"""
Database service for SQLite-based data storage.
Provides CRUD operations for clients, materials, and cost estimates.
"""

import sqlite3
import json
import os
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from contextlib import contextmanager


class Database:
    """
    SQLite database manager for the Ofertownik application.
    Handles persistence of clients, materials, and cost estimates.
    """
    
    def __init__(self, db_path: str = "ofertownik.db"):
        """
        Initialize database connection and create tables if needed.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._create_tables()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Clients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT,
                    tax_id TEXT,
                    phone TEXT,
                    email TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Materials table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    unit TEXT,
                    price_net REAL NOT NULL,
                    vat_rate INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Cost estimates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cost_estimates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estimate_number TEXT NOT NULL UNIQUE,
                    client_id INTEGER,
                    title TEXT,
                    date TEXT NOT NULL,
                    items_json TEXT NOT NULL,
                    transport_percent REAL,
                    transport_vat INTEGER,
                    total_net REAL,
                    total_vat REAL,
                    total_gross REAL,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(id)
                )
            """)
            
            # Estimate history/versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS estimate_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estimate_id INTEGER NOT NULL,
                    version_number INTEGER NOT NULL,
                    items_json TEXT NOT NULL,
                    transport_percent REAL,
                    transport_vat INTEGER,
                    total_net REAL,
                    total_vat REAL,
                    total_gross REAL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (estimate_id) REFERENCES cost_estimates(id)
                )
            """)
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
    
    # Client CRUD operations
    
    def create_client(self, name: str, address: str = "", tax_id: str = "", 
                     phone: str = "", email: str = "") -> int:
        """
        Create a new client record.
        
        Args:
            name: Client name
            address: Client address
            tax_id: Tax identification number (NIP)
            phone: Phone number
            email: Email address
            
        Returns:
            ID of the created client
        """
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clients (name, address, tax_id, phone, email, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, address, tax_id, phone, email, now, now))
            return cursor.lastrowid
    
    def get_client(self, client_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a client by ID.
        
        Args:
            client_id: Client ID
            
        Returns:
            Client dictionary or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_clients(self, search: str = "") -> List[Dict[str, Any]]:
        """
        List all clients, optionally filtered by search term.
        
        Args:
            search: Optional search term to filter by name, address, or tax_id
            
        Returns:
            List of client dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if search:
                cursor.execute("""
                    SELECT * FROM clients 
                    WHERE name LIKE ? OR address LIKE ? OR tax_id LIKE ?
                    ORDER BY name
                """, (f"%{search}%", f"%{search}%", f"%{search}%"))
            else:
                cursor.execute("SELECT * FROM clients ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_client(self, client_id: int, name: str = None, address: str = None,
                     tax_id: str = None, phone: str = None, email: str = None) -> bool:
        """
        Update a client record.
        
        Args:
            client_id: Client ID
            name: New name (if provided)
            address: New address (if provided)
            tax_id: New tax ID (if provided)
            phone: New phone (if provided)
            email: New email (if provided)
            
        Returns:
            True if updated, False if client not found
        """
        client = self.get_client(client_id)
        if not client:
            return False
        
        now = datetime.now().isoformat()
        updates = {
            'name': name if name is not None else client['name'],
            'address': address if address is not None else client['address'],
            'tax_id': tax_id if tax_id is not None else client['tax_id'],
            'phone': phone if phone is not None else client['phone'],
            'email': email if email is not None else client['email'],
            'updated_at': now
        }
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clients 
                SET name = ?, address = ?, tax_id = ?, phone = ?, email = ?, updated_at = ?
                WHERE id = ?
            """, (updates['name'], updates['address'], updates['tax_id'], 
                  updates['phone'], updates['email'], updates['updated_at'], client_id))
            return True
    
    def delete_client(self, client_id: int) -> bool:
        """
        Delete a client record.
        
        Args:
            client_id: Client ID
            
        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            return cursor.rowcount > 0
    
    # Material CRUD operations
    
    def create_material(self, name: str, unit: str = "", price_net: float = 0.0,
                       vat_rate: int = 23, category: str = "material",
                       description: str = "") -> int:
        """
        Create a new material record.
        
        Args:
            name: Material name
            unit: Unit of measurement
            price_net: Net price
            vat_rate: VAT rate (0, 8, or 23)
            category: Category ("material" or "service")
            description: Material description
            
        Returns:
            ID of the created material
        """
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO materials (name, unit, price_net, vat_rate, category, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, unit, price_net, vat_rate, category, description, now, now))
            return cursor.lastrowid
    
    def get_material(self, material_id: int) -> Optional[Dict[str, Any]]:
        """Get a material by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_materials(self, category: str = None) -> List[Dict[str, Any]]:
        """
        List all materials, optionally filtered by category.
        
        Args:
            category: Optional category filter ("material" or "service")
            
        Returns:
            List of material dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("SELECT * FROM materials WHERE category = ? ORDER BY name", (category,))
            else:
                cursor.execute("SELECT * FROM materials ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_material(self, material_id: int, **kwargs) -> bool:
        """Update a material record."""
        material = self.get_material(material_id)
        if not material:
            return False
        
        now = datetime.now().isoformat()
        updates = {k: kwargs.get(k, material[k]) for k in 
                   ['name', 'unit', 'price_net', 'vat_rate', 'category', 'description']}
        updates['updated_at'] = now
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE materials 
                SET name = ?, unit = ?, price_net = ?, vat_rate = ?, 
                    category = ?, description = ?, updated_at = ?
                WHERE id = ?
            """, (updates['name'], updates['unit'], updates['price_net'], updates['vat_rate'],
                  updates['category'], updates['description'], updates['updated_at'], material_id))
            return True
    
    def delete_material(self, material_id: int) -> bool:
        """Delete a material record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
            return cursor.rowcount > 0
    
    # Backup functionality
    
    def create_backup(self, backup_path: str = None) -> str:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path for the backup file. If None, generates timestamp-based name.
            
        Returns:
            Path to the backup file
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.db_path}.backup_{timestamp}"
        
        with self._get_connection() as conn:
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
        
        return backup_path
    
    # Settings management
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row['value'])
                except json.JSONDecodeError:
                    return row['value']
            return default
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a setting value."""
        now = datetime.now().isoformat()
        value_json = json.dumps(value) if not isinstance(value, str) else value
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value_json, now))
