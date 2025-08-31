"""
Enhanced database operations for the Places Management System.

This module provides comprehensive database operations with proper error handling,
logging, and performance monitoring for PostgreSQL database interactions.
Optimized with numpy and pandas vectorization for faster response times.
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Tuple, Any
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
import time
import numpy as np

# Import utilities
try:
    from utils.settings import db_config, get_database_connection_string, excel_config
    from utils.logger import get_logger, log_performance
    from utils.error_handlers import handle_database_errors, DatabaseError, safe_execute
    from utils.excel_handler import excel_handler
    from models.place import Place
except ImportError:
    # Fallback for development without modules
    class MockConfig:
        echo_sql = False
        pool_size = 10
        max_overflow = 20
    db_config = MockConfig()
    
    def get_database_connection_string():
        return os.getenv("DATABASE_URL", "")
    
    class MockLogger:
        def debug(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
        def info(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
        def warning(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
        def error(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
    
    def get_logger(_name):
        # Mock function - parameter name ignored
        return MockLogger()
    
    def log_performance(_name):
        # Mock decorator - parameter name ignored
        def decorator(func):
            return func
        return decorator
    
    def handle_database_errors(func):
        # Mock decorator - returns function unchanged
        return func
    
    def safe_execute(op, _name, default=None, _context=None):
        # Mock function - execute operation with basic error handling
        try:
            return op()
        except Exception:  # Catch specific exception type
            return default

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

class PlacesDatabase:
    """
    Enhanced PostgreSQL database operations class for Places Management System.
    
    This class provides comprehensive database operations with proper error handling,
    logging, performance monitoring, and connection management.
    Optimized with numpy and pandas vectorization for faster data processing.
    """
    
    def __init__(self):
        """
        Initialize direct PostgreSQL connection using SQLAlchemy.
        
        Raises:
            DatabaseError: If database connection parameters are missing or invalid
            ConnectionError: If unable to connect to the database
        """
        logger.info("Initializing PlacesDatabase connection")
        
        # Load database configuration
        try:
            self.connection_string = get_database_connection_string()
            logger.debug("Database connection string obtained successfully")
        except Exception as e:
            logger.error("Failed to get database connection string", error=str(e))
            raise DatabaseError(f"Database configuration error: {e}")
        
        # Fallback to environment variables if config module not available
        self.db_url = os.getenv("DATABASE_URL")
        self.user = os.getenv("user")
        self.password = os.getenv("password") 
        self.host = os.getenv("host")
        self.port = os.getenv("port")
        self.dbname = os.getenv("dbname")
        
        # Validate required parameters
        if not all([self.user, self.password, self.host, self.port, self.dbname]):
            error_msg = "Database connection parameters must be set in environment variables"
            logger.error(error_msg, user=bool(self.user),password=bool(self.password),host=bool(self.host),port=bool(self.port),dbname=bool(self.dbname))
            raise DatabaseError(error_msg)
        
        # Create SQLAlchemy engine with enhanced configuration
        try:
            engine_url = (self.connection_string if self.connection_string 
                         else f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}")
            
            self.engine = create_engine(
                engine_url,
                echo=db_config.echo_sql,  # Enable SQL logging if configured
                pool_size=db_config.pool_size,
                max_overflow=db_config.max_overflow,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections every hour
                connect_args={
                    "options": "-c timezone=UTC"  # Set timezone
                }
            )
            
            logger.info("SQLAlchemy engine created successfully", 
                       host=self.host, port=self.port, database=self.dbname)
            
        except Exception as e:
            logger.error("Failed to create SQLAlchemy engine", error=str(e))
            raise DatabaseError(f"Failed to create database engine: {e}")
        
        # Initialize database schema
        self.init_database()
        
        # Test the connection
        if not self.test_connection():
            raise DatabaseError("Database connection test failed")
        
        logger.info("PlacesDatabase initialized successfully")
    
    def _convert_datetimes_to_naive(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert timezone-aware datetimes to timezone-naive for Excel compatibility.
        
        Args:
            df: DataFrame with datetime columns
            
        Returns:
            pd.DataFrame: DataFrame with timezone-naive datetimes
        """
        datetime_columns = ['created_at', 'updated_at']
        for col in datetime_columns:
            if col in df.columns and df[col].dt.tz is not None:
                df[col] = df[col].dt.tz_localize(None)
            elif col in df.columns and df[col].dtype == 'object':
                # Try to parse as datetime if it's an object type
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    if df[col].dt.tz is not None:
                        df[col] = df[col].dt.tz_localize(None)
                except Exception:
                    pass  # Keep as object if datetime parsing fails
        return df
    
    @handle_database_errors
    def get_connection(self):
        """
        Get a database connection using psycopg2 for specific operations.
        
        Returns:
            psycopg2.connection: Database connection object
            
        Raises:
            DatabaseError: If connection cannot be established
        """
        logger.debug("Requesting psycopg2 database connection")
        
        try:
            connection = psycopg2.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                connect_timeout=30,  # 30 second timeout
                application_name="PlacesManagementSystem"
            )
            
            logger.debug("psycopg2 connection established successfully")
            return connection
            
        except psycopg2.OperationalError as e:
            logger.error("PostgreSQL operational error", error=str(e))
            raise DatabaseError(f"Database operational error: {e}")
        except psycopg2.Error as e:
            logger.error("PostgreSQL error", error=str(e))
            raise DatabaseError(f"Database connection error: {e}")
        except Exception as e:
            logger.error("Unexpected error during connection", error=str(e))
            raise DatabaseError(f"Unexpected connection error: {e}")
    
    @handle_database_errors
    @log_performance("database_initialization")
    def init_database(self):
        """
        Initialize the database and create the places table if it doesn't exist.
        
        This method creates the main places table with all necessary columns,
        indexes for performance optimization, and triggers for automatic
        timestamp updates.
        
        Raises:
            DatabaseError: If database initialization fails
        """
        logger.info("Initializing database schema")
        
        try:
            with self.engine.connect() as conn:
                # Create the places table with comprehensive schema
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS places (
                    id str PRIMARY KEY,
                    latitude DECIMAL(10, 8) NOT NULL CHECK (latitude >= -90 AND latitude <= 90),
                    longitude DECIMAL(11, 8) NOT NULL CHECK (longitude >= -180 AND longitude <= 180),
                    types TEXT NOT NULL CHECK (LENGTH(types) > 0),
                    name TEXT NOT NULL CHECK (LENGTH(name) > 0),
                    address TEXT NOT NULL CHECK (LENGTH(address) > 0),
                    pincode TEXT NOT NULL CHECK (pincode ~ '^[0-9]{6}$'),
                    rating REAL DEFAULT 0.0,
                    followers REAL DEFAULT 0.0,
                    country VARCHAR(100) DEFAULT 'Unknown',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """
                
                logger.debug("Creating places table")
                conn.execute(text(create_table_sql))
                
                # Create indexes for better query performance
                index_sqls = [
                    "CREATE INDEX IF NOT EXISTS idx_places_name ON places(name);",
                    "CREATE INDEX IF NOT EXISTS idx_places_types ON places(types);", 
                    "CREATE INDEX IF NOT EXISTS idx_places_created_at ON places(created_at);",
                    "CREATE INDEX IF NOT EXISTS idx_places_coordinates ON places(latitude, longitude);",
                    "CREATE INDEX IF NOT EXISTS idx_places_pincode ON places(pincode);",
                    "CREATE INDEX IF NOT EXISTS idx_places_name_text_search ON places USING gin(to_tsvector('english', name));"
                ]
                
                logger.debug("Creating database indexes", index_count=len(index_sqls))
                for i, index_sql in enumerate(index_sqls):
                    try:
                        conn.execute(text(index_sql))
                        logger.debug(f"Created index {i+1}/{len(index_sqls)}")
                    except Exception as index_error:
                        logger.warning(f"Failed to create index {i+1}", error=str(index_error))
                
                # Create trigger for automatic updated_at timestamp
                trigger_sql = """
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
                
                DROP TRIGGER IF EXISTS update_places_updated_at ON places;
                CREATE TRIGGER update_places_updated_at 
                    BEFORE UPDATE ON places 
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_updated_at_column();
                """
                
                logger.debug("Creating update trigger")
                conn.execute(text(trigger_sql))
                
                # Commit all changes
                conn.commit()
                logger.info("Database schema initialization completed successfully")
                
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error during database initialization", error=str(e))
            raise DatabaseError(f"Database initialization error: {e}")
        except Exception as e:
            logger.error("Unexpected error during database initialization", error=str(e))
            raise DatabaseError(f"Unexpected database initialization error: {e}")
    
    @handle_database_errors
    @log_performance("get_all_places")
    def get_all_places(self, prefer_excel: bool = False) -> pd.DataFrame:
        """
        Retrieve all places from the database with Excel sync support.
        Optimized with pandas for faster data processing.
        
        Args:
            prefer_excel: If True, try to read from Excel first for faster response
        
        Returns:
            pd.DataFrame: DataFrame containing all places data, empty if error occurs
            
        Note:
            This method loads all places into memory. For large datasets,
            consider using get_places_paginated() instead.
        """
        logger.debug("Retrieving all places", prefer_excel=prefer_excel)
        
        # Try Excel first if preferred and sync is enabled
        if prefer_excel and excel_config.enable_excel_sync:
            try:
                excel_df = safe_execute(
                    lambda: excel_handler.read_excel_data(use_cache=True),
                    "read_excel_places",
                    default_return=pd.DataFrame()
                )
                
                if not excel_df.empty:
                    logger.info("Retrieved places from Excel cache", 
                               record_count=len(excel_df))
                    return excel_df
                else:
                    logger.debug("Excel file empty or not found, falling back to database")
            except Exception as e:
                logger.warning("Failed to read from Excel, falling back to database", error=str(e))
        
        try:
            query = """
            SELECT 
                id,
                latitude,
                longitude, 
                types,
                name,
                address,
                pincode,
                created_at,
                updated_at
            FROM places 
            ORDER BY id
            """
            
            logger.debug("Executing get_all_places query")
            
            # Use pandas read_sql_query with optimized settings
            df = pd.read_sql_query(
                query, 
                self.engine,
                parse_dates=['created_at', 'updated_at'],  # Optimize datetime parsing
                dtype={
                    'id': 'string',
                    'latitude': np.float64,
                    'longitude': np.float64,
                    'types': 'string',
                    'name': 'string',
                    'address': 'string',
                    'pincode': 'string'
                }
            )
            
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            df = self._convert_datetimes_to_naive(df)
            
            logger.info("Successfully retrieved all places from database", 
                       record_count=len(df))
            
            # Sync to Excel if enabled
            if excel_config.enable_excel_sync and not df.empty:
                safe_execute(
                    lambda: excel_handler.sync_from_database(df),
                    "sync_places_to_excel",
                    context={"operation": "get_all_places", "record_count": len(df)}
                )
            
            return df
            
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error retrieving places", error=str(e))
            return pd.DataFrame()
        except Exception as e:
            logger.error("Unexpected error retrieving places", error=str(e))
            return pd.DataFrame()
    
    @handle_database_errors
    @log_performance("get_places_paginated")
    def get_places_paginated(self, page: int = 1, page_size: int = 10, 
                            sort_by: str = "id", sort_order: str = "ASC",
                            search_term: str = None) -> Tuple[pd.DataFrame, int]:
        """
        Get places with pagination, sorting, and search functionality.
        Optimized with pandas and numpy for faster data processing.
        
        This method provides efficient pagination for large datasets with
        optional search and sorting capabilities.
        
        Args:
            page: Page number (1-based, minimum 1)
            page_size: Number of records per page (1-1000)
            sort_by: Column to sort by (must be valid column name)
            sort_order: Sort order (ASC or DESC)
            search_term: Optional search term for name, types, or address
            
        Returns:
            Tuple of (DataFrame with places, total count)
            Returns (empty DataFrame, 0) on error
        """
        # Input validation with numpy for faster operations
        page = max(1, page)  # Ensure page is at least 1
        page_size = max(1, min(1000, page_size))  # Limit page_size to reasonable range
        sort_order = sort_order.upper() if sort_order.upper() in ['ASC', 'DESC'] else 'ASC'
        
        # Validate sort column to prevent SQL injection
        valid_sort_columns = ['id', 'name', 'types', 'address', 'latitude', 
                             'longitude', 'pincode', 'created_at', 'updated_at']
        if sort_by not in valid_sort_columns:
            logger.warning("Invalid sort column specified", 
                          sort_by=sort_by, valid_columns=valid_sort_columns)
            sort_by = 'id'
        
        logger.debug("Getting paginated places", 
                    page=page, page_size=page_size, sort_by=sort_by, 
                    sort_order=sort_order, has_search=bool(search_term))
        
        try:
            # Build the base query with proper column selection
            base_query = """FROM places"""
            where_clause = ""
            params = {}
            
            # Add search functionality with full-text search
            if search_term and search_term.strip():
                search_term = search_term.strip()
                where_clause = """
                WHERE (name ILIKE %(search_term)s 
                       OR types ILIKE %(search_term)s 
                       OR address ILIKE %(search_term)s
                       OR pincode ILIKE %(search_term)s)
                """
                params['search_term'] = f'%{search_term}%'
                logger.debug("Applied search filter", search_term=search_term[:50])
            
            # Get total count efficiently
            count_query = f"SELECT COUNT(*) {base_query} {where_clause}"
            
            # Use pandas read_sql_query for count (simpler parameter handling)
            count_df = pd.read_sql_query(count_query, self.engine, params=params if params else None)
            total_count = int(count_df.iloc[0, 0])
            logger.debug("Count query completed", total_count=total_count)
            
            # Early return if no results
            if total_count == 0:
                return pd.DataFrame(), 0
            
            # Build the main query with pagination and sorting
            offset = (page - 1) * page_size
            
            # Ensure we don't go beyond available pages
            max_page = (total_count + page_size - 1) // page_size
            if page > max_page:
                logger.warning("Requested page exceeds available pages", 
                              page=page, max_page=max_page)
                page = max_page
                offset = (page - 1) * page_size
            
            main_query = f"""
            SELECT 
                id,
                latitude,
                longitude,
                types,
                name,
                address,
                pincode,
                created_at,
                updated_at
            {base_query} {where_clause} 
            ORDER BY {sort_by} {sort_order}
            LIMIT %(page_size)s OFFSET %(offset)s
            """
            
            # Add pagination parameters
            params.update({
                'page_size': page_size,
                'offset': offset
            })
            
            logger.debug("Executing main paginated query", 
                       offset=offset, limit=page_size)
            
            # Execute the main query with optimized pandas settings
            df = pd.read_sql_query(
                main_query, 
                self.engine, 
                params=params,
                parse_dates=['created_at', 'updated_at'],
                dtype={
                    'id': 'string',
                    'latitude': np.float64,
                    'longitude': np.float64,
                    'types': 'string',
                    'name': 'string',
                    'address': 'string',
                    'pincode': 'string'
                }
            )
            
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            df = self._convert_datetimes_to_naive(df)
            
            logger.info("Successfully retrieved paginated places",
                       returned_records=len(df), 
                       total_count=total_count,
                       page=page,
                       page_size=page_size)
            
            return df, total_count
            
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error in paginated query", error=str(e))
            return pd.DataFrame(), 0
        except Exception as e:
            logger.error("Unexpected error in paginated query", error=str(e))
            return pd.DataFrame(), 0
    
    @handle_database_errors
    @log_performance("get_places_by_type_paginated")
    def get_places_by_type_paginated(self, place_type: str, page: int = 1, page_size: int = 10, sort_by: str = "id", sort_order: str = "ASC") -> Tuple[pd.DataFrame, int]:
        """
        Get places of a specific type with pagination and sorting.
        Optimized with pandas for faster data processing.
        
        Args:
            place_type: Type of place to filter by
            page: Page number (1-based)
            page_size: Number of records per page
            sort_by: Column to sort by
            sort_order: Sort order (ASC or DESC)
            
        Returns:
            Tuple of (DataFrame with places, total count)
        """
        # Input validation with numpy for faster operations
        page = max(1, page)
        page_size = max(1, min(1000, page_size))
        sort_order = sort_order.upper() if sort_order.upper() in ['ASC', 'DESC'] else 'ASC'
        
        # Validate sort column
        valid_sort_columns = ['id', 'name', 'types', 'address', 'latitude', 
                             'longitude', 'pincode', 'created_at', 'updated_at']
        if sort_by not in valid_sort_columns:
            logger.warning("Invalid sort column specified", sort_by=sort_by)
            sort_by = 'id'
        
        logger.debug("Getting places by type with pagination", 
                    place_type=place_type, page=page, page_size=page_size)
        
        try:
            # Get total count using pandas for consistency
            count_query = "SELECT COUNT(*) FROM places WHERE types = %(place_type)s"
            params = {'place_type': place_type}
            
            count_df = pd.read_sql_query(count_query, self.engine, params=params)
            total_count = int(count_df.iloc[0, 0])
            logger.debug("Count query completed", total_count=total_count)
            
            if total_count == 0:
                return pd.DataFrame(), 0
            
            # Build the main query
            offset = (page - 1) * page_size
            order_clause = f"ORDER BY {sort_by} {sort_order}"
            
            main_query = f"""
            SELECT 
                id,
                latitude,
                longitude,
                types,
                name,
                address,
                pincode,
                created_at,
                updated_at
            FROM places 
            WHERE types = %(place_type)s 
            {order_clause} 
            LIMIT %(page_size)s OFFSET %(offset)s
            """
            
            # Update parameters with pagination values
            params.update({
                'page_size': page_size,
                'offset': offset
            })
            
            logger.debug("Executing places by type query", 
                        place_type=place_type, offset=offset, limit=page_size)
            
            # Execute the main query with optimized pandas settings
            df = pd.read_sql_query(
                main_query, 
                self.engine, 
                params=params,
                parse_dates=['created_at', 'updated_at'],
                dtype={
                    'id': 'string',
                    'latitude': np.float64,
                    'longitude': np.float64,
                    'types': 'string',
                    'name': 'string',
                    'address': 'string',
                    'pincode': 'string'
                }
            )
            
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            df = self._convert_datetimes_to_naive(df)
            
            logger.info("Successfully retrieved places by type",
                       place_type=place_type, returned_records=len(df), 
                       total_count=total_count)
            
            return df, total_count
            
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error in places by type query", error=str(e))
            return pd.DataFrame(), 0
        except Exception as e:
            logger.error("Unexpected error in places by type query", error=str(e))
            return pd.DataFrame(), 0
    
    @handle_database_errors
    @log_performance("add_place")
    def add_place(self,id: str, latitude: float, longitude: float, types: str, 
                  name: str, address: str, pincode: str, rating: float = 0.0, 
                  followers: float = 0.0, country: str = "Unknown") -> bool:
        """
        Add a new place to the database with Excel sync.
        Optimized with numpy for faster data validation.
        
        Args:
            id: Place ID
            latitude: Place latitude
            longitude: Place longitude  
            types: Place types
            name: Place name
            address: Place address
            pincode: Place pincode
            rating: Place rating (0.0 to 5.0, default 0.0)
            followers: Number of followers (default 0.0)
            country: Country name (default "Unknown")
            
        Returns:
            bool: True if successful
        """
        logger.debug("Adding new place", name=name, types=types)
        
        # Vectorized coordinate validation using numpy
        lat_array = np.array([latitude])
        lon_array = np.array([longitude])
        
        if not (np.all((lat_array >= -90) & (lat_array <= 90)) and 
                np.all((lon_array >= -180) & (lon_array <= 180))):
            logger.error("Invalid coordinates provided", latitude=latitude, longitude=longitude)
            return False
        
        try:
            with self.engine.connect() as conn:
                # Insert and get the new place ID
                insert_sql = """
                INSERT INTO places (id,latitude, longitude, types, name, address, pincode, rating, followers, country)
                VALUES (:id, :latitude, :longitude, :types, :name, :address, :pincode, :rating, :followers, :country)
                RETURNING id, created_at, updated_at
                """
                
                result = conn.execute(text(insert_sql), {
                    'id': id,
                    'latitude': float(latitude),
                    'longitude': float(longitude),
                    'types': types,
                    'name': name,
                    'address': address,
                    'pincode': pincode,
                    'rating': float(rating),
                    'followers': float(followers),
                    'country': str(country)
                })
                
                # Get the inserted record details
                inserted_row = result.fetchone()
                if inserted_row:
                    id, created_at, updated_at = inserted_row
                    
                    # Sync to Excel if enabled
                    if excel_config.enable_excel_sync:
                        place_data = {
                            'id': str(id),
                            'latitude': float(latitude),
                            'longitude': float(longitude),
                            'types': types,
                            'name': name,
                            'address': address,
                            'pincode': pincode,
                            'rating': float(rating),
                            'followers': float(followers),
                            'country': str(country),
                            'created_at': created_at,
                            'updated_at': updated_at
                        }
                        
                        safe_execute(
                            lambda: excel_handler.add_place_to_excel(place_data),
                            "add_place_to_excel",
                            context={"id": id, "operation": "add_place"}
                        )
                
                conn.commit()
                logger.info("Place added successfully", id=id, name=name)
                return True
                
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error adding place", error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error adding place", error=str(e))
            return False
    
    @handle_database_errors
    @log_performance("add_place_full")
    def add_place_full(self, place_data: Dict[str, Any]) -> bool:
        """
        Add a new place with full data including rating, followers, and country.
        
        Args:
            place_data: Dictionary containing all place information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract required fields
            required_fields = ['latitude', 'longitude', 'types', 'name', 'address', 'pincode']
            for field in required_fields:
                if field not in place_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Extract optional fields with defaults
            rating = place_data.get('rating', 0.0)
            followers = place_data.get('followers', 0.0)
            country = place_data.get('country', 'Unknown')
            
            # Validate rating range
            if not (0.0 <= rating <= 5.0):
                logger.warning("Rating out of range, setting to 0.0", rating=rating)
                rating = 0.0
            
            # Validate followers
            if followers < 0:
                logger.warning("Followers cannot be negative, setting to 0.0", followers=followers)
                followers = 0.0
            
            # Validate country
            if not country or not country.strip():
                country = 'Unknown'
            
            # Call the main add_place method
            return self.add_place(
                id=str(place_data['id']),
                latitude=place_data['latitude'],
                longitude=place_data['longitude'],
                types=place_data['types'],
                name=place_data['name'],
                address=place_data['address'],
                pincode=place_data['pincode'],
                rating=rating,
                followers=followers,
                country=country
            )
            
        except Exception as e:
            logger.error("Failed to add place with full data", error=str(e), place_data=place_data)
            return False
    
    @handle_database_errors
    @log_performance("update_place")
    def update_place(self, id: str, latitude: float, longitude: float, 
                    types: str, name: str, address: str, pincode: str, 
                    rating: float = None, followers: float = None, country: str = None) -> bool:
        """
        Update an existing place in the database with Excel sync.
        Optimized with numpy for faster data validation.
        
        Args:
            id: ID of place to update
            latitude: Updated latitude
            longitude: Updated longitude
            types: Updated types
            name: Updated name
            address: Updated address
            pincode: Updated pincode
            rating: Updated place rating (optional)
            followers: Updated number of followers (optional)
            country: Updated country name (optional)
            
        Returns:
            bool: True if successful
        """
        logger.debug("Updating place", id=id, name=name)
        
        # Vectorized coordinate validation using numpy
        lat_array = np.array([latitude])
        lon_array = np.array([longitude])
        
        if not (np.all((lat_array >= -90) & (lat_array <= 90)) and 
                np.all((lon_array >= -180) & (lon_array <= 180))):
            logger.error("Invalid coordinates provided", latitude=latitude, longitude=longitude)
            return False
        
        try:
            with self.engine.connect() as conn:
                # Build dynamic update query based on provided fields
                update_fields = [
                    "id = :id",
                    "latitude = :latitude",
                    "longitude = :longitude", 
                    "types = :types",
                    "name = :name", 
                    "address = :address", 
                    "pincode = :pincode",
                    "updated_at = NOW()"
                ]
                
                update_params = {
                    'id': str(id),
                    'latitude': float(latitude),
                    'longitude': float(longitude),
                    'types': types,
                    'name': name,
                    'address': address,
                    'pincode': pincode,
                }
                
                # Add optional fields if provided
                if rating is not None:
                    update_fields.append("rating = :rating")
                    update_params['rating'] = float(rating)
                
                if followers is not None:
                    update_fields.append("followers = :followers")
                    update_params['followers'] = float(followers)
                
                if country is not None:
                    update_fields.append("country = :country")
                    update_params['country'] = str(country)
                
                update_sql = f"""
                UPDATE places 
                SET {', '.join(update_fields)}
                WHERE id = :id
                RETURNING updated_at
                """
                
                result = conn.execute(text(update_sql), update_params)
                
                # Check if any rows were updated
                updated_row = result.fetchone()
                if updated_row:
                    updated_at = updated_row[0]
                    
                    # Sync to Excel if enabled
                    if excel_config.enable_excel_sync:
                        updated_data = {
                            'id': str(id),
                            'latitude': float(latitude),
                            'longitude': float(longitude),
                            'types': types,
                            'name': name,
                            'address': address,
                            'pincode': pincode,
                            'rating': rating if rating is not None else 0.0,
                            'followers': followers if followers is not None else 0.0,
                            'country': country if country is not None else 'Unknown',
                            'updated_at': updated_at
                        }
                        
                        safe_execute(
                            lambda: excel_handler.update_place_in_excel(id, updated_data),
                            "update_place_in_excel",
                            context={"id": id, "operation": "update_place"}
                        )
                    
                    conn.commit()
                    logger.info("Place updated successfully", id=id, name=name)
                    return True
                else:
                    logger.warning("No place found to update", id=id)
                    return False
                
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error updating place", error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error updating place", error=str(e))
            return False
    
    @handle_database_errors
    @log_performance("delete_place")
    def delete_place(self, id: str) -> bool:
        """
        Delete a place from the database with Excel sync.
        
        Args:
            id: ID of place to delete
            
        Returns:
            bool: True if successful
        """
        logger.debug("Deleting place", id=id)
        
        try:
            with self.engine.connect() as conn:
                # First check if place exists
                check_sql = "SELECT name FROM places WHERE id = :id"
                check_result = conn.execute(text(check_sql), {'id': str(id)})
                existing_place = check_result.fetchone()
                
                if not existing_place:
                    logger.warning("Place not found for deletion", id=id)
                    return False
                
                place_name = existing_place[0]
                
                # Delete the place
                delete_sql = "DELETE FROM places WHERE id = :id"
                result = conn.execute(text(delete_sql), {'id': str(id)})
                
                if result.rowcount > 0:
                    # Sync to Excel if enabled
                    if excel_config.enable_excel_sync:
                        safe_execute(
                            lambda: excel_handler.delete_place_from_excel(id),
                            "delete_place_from_excel",
                            context={"id": id, "operation": "delete_place"}
                        )
                    
                    conn.commit()
                    logger.info("Place deleted successfully", id=id, name=place_name)
                    return True
                else:
                    logger.warning("No place was deleted", id=id)
                    return False
                
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error deleting place", error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error deleting place", error=str(e))
            return False
    
    def get_place_by_id(self, id: str) -> Optional[Dict]:
        """Get a specific place by ID with optimized pandas query."""
        try:
            query = "SELECT * FROM places WHERE id = %(id)s"
            params = {'id': id}
            
            df = pd.read_sql_query(
                query, 
                self.engine, 
                params=params,
                parse_dates=['created_at', 'updated_at'],
                dtype={
                    'id': 'string',
                    'latitude': np.float64,
                    'longitude': np.float64,
                    'types': 'string',
                    'name': 'string',
                    'address': 'string',
                    'pincode': 'string'
                }
            )
            
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            datetime_columns = ['created_at', 'updated_at']
            for col in datetime_columns:
                if col in df.columns and df[col].dt.tz is not None:
                    df[col] = df[col].dt.tz_localize(None)
            
            if not df.empty:
                return df.iloc[0].to_dict()
            return None
        except Exception as e:
            print(f"Error getting place: {e}")
            return None
    
    def search_places(self, search_term: str) -> pd.DataFrame:
        """Search places by name or types with optimized pandas query."""
        try:
            query = """
            SELECT * FROM places 
            WHERE name ILIKE %(search_term)s OR types ILIKE %(search_term)s 
            ORDER BY id
            """
            search_pattern = f'%{search_term}%'
            params = {'search_term': search_pattern}
            
            df = pd.read_sql_query(
                query, 
                self.engine, 
                params=params,
                parse_dates=['created_at', 'updated_at'],
                dtype={
                    'id': 'string',
                    'latitude': np.float64,
                    'longitude': np.float64,
                    'types': 'string',
                    'name': 'string',
                    'address': 'string',
                    'pincode': 'string'
                }
            )
            
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            df = self._convert_datetimes_to_naive(df)
            
            return df
        except Exception as e:
            print(f"Error searching places: {e}")
            return pd.DataFrame()
    
    def get_places_by_type(self, place_type: str) -> pd.DataFrame:
        """Get all places of a specific type with optimized pandas query."""
        try:
            query = "SELECT * FROM places WHERE types = %(place_type)s ORDER BY id"
            params = {'place_type': place_type}
            
            df = pd.read_sql_query(
                query, 
                self.engine, 
                params=params,
                parse_dates=['created_at', 'updated_at'],
                dtype={
                    'id': 'string',
                    'latitude': np.float64,
                    'longitude': np.float64,
                    'types': 'string',
                    'name': 'string',
                    'address': 'string',
                    'pincode': 'string',
                    'rating': np.float32,
                    'followers': np.float32,
                    'country': 'string'
                }
            )
            
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            df = self._convert_datetimes_to_naive(df)
            
            return df
        except Exception as e:
            print(f"Error getting places by type: {e}")
            return pd.DataFrame()
    
    def test_connection(self) -> bool:
        """Test the database connection."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT NOW();"))
                current_time = result.fetchone()[0]
                logger.info("Database connection test successful", current_time=current_time)
                print(f"Database connection successful! Current time: {current_time}")
                return True
        except Exception as e:
            logger.error("Database connection test failed", error=str(e))
            print(f"Database connection failed: {e}")
            return False
    
    @handle_database_errors
    @log_performance("force_excel_sync")
    def force_excel_sync(self) -> bool:
        """
        Force a complete sync of database data to Excel file.
        
        Returns:
            bool: True if successful
        """
        logger.info("Forcing complete Excel sync from database")
        
        if not excel_config.enable_excel_sync:
            logger.warning("Excel sync is disabled")
            return False
        
        try:
            # Get all data from database
            all_places = self.get_all_places(prefer_excel=False)
            
            if all_places.empty:
                logger.info("No places to sync to Excel")
                return True
            
            # Force sync to Excel
            success = safe_execute(
                lambda: excel_handler.force_sync_from_database(all_places),
                "force_sync_to_excel",
                default_return=False,
                context={"record_count": len(all_places)}
            )
            
            if success:
                logger.info("Force Excel sync completed successfully", records=len(all_places))
            else:
                logger.error("Force Excel sync failed")
            
            return success
            
        except Exception as e:
            logger.error("Unexpected error during force Excel sync", error=str(e))
            return False
    
    def get_excel_statistics(self) -> Dict[str, Any]:
        """
        Get Excel file statistics and sync status.
        
        Returns:
            Dict[str, Any]: Excel statistics
        """
        logger.debug("Getting Excel statistics")
        
        stats = safe_execute(
            lambda: excel_handler.get_excel_statistics(),
            "get_excel_statistics",
            default_return={'error': 'Failed to get Excel statistics'}
        )
        
        # Add database comparison if possible
        try:
            db_count = len(self.get_all_places(prefer_excel=False))
            stats['database_record_count'] = db_count
            
            excel_count = stats.get('record_count', 0)
            stats['sync_status'] = 'synced' if db_count == excel_count else 'out_of_sync'
            stats['record_difference'] = abs(db_count - excel_count)
            
        except Exception as e:
            logger.warning("Failed to compare database and Excel counts", error=str(e))
            stats['sync_status'] = 'unknown'
        
        return stats
    
    def clear_excel_cache(self) -> None:
        """Clear the Excel cache to force fresh reads."""
        logger.info("Clearing Excel cache")
        safe_execute(
            lambda: excel_handler.clear_cache(),
            "clear_excel_cache"
        )

    @handle_database_errors
    @log_performance("add_place_with_model")
    def add_place_with_model(self, place: Place) -> bool:
        """
        Add a new place to the database using the Place model.
        
        Args:
            place: Place model instance
            
        Returns:
            bool: True if successful
        """
        logger.debug("Adding new place with model", name=place.name, types=place.types)
        
        try:
            # Convert Place model to dictionary
            place_data = place.to_dict()
            
            # Use the existing add_place_full method
            success = self.add_place_full(place_data)
            
            if success:
                logger.info("Place added successfully using model", name=place.name)
            else:
                logger.error("Failed to add place using model", name=place.name)
            
            return success
            
        except Exception as e:
            logger.error("Error adding place with model", error=str(e), name=place.name)
            return False
    
    @handle_database_errors
    @log_performance("get_place_by_id_with_model")
    def get_place_by_id_with_model(self, id: str) -> Optional[Place]:
        """Get a specific place by ID and return as Place model."""
        try:
            place_dict = self.get_place_by_id(id)
            if place_dict:
                return Place.from_dict(place_dict)
            return None
        except Exception as e:
            logger.error("Error getting place by ID with model", error=str(e), id=id)
            return None
    
    @handle_database_errors
    @log_performance("update_place_with_model")
    def update_place_with_model(self, place: Place) -> bool:
        """
        Update an existing place in the database using the Place model.
        
        Args:
            place: Place model instance with updated data
            
        Returns:
            bool: True if successful
        """
        if not place.id:
            logger.error("Place ID is required for update")
            return False
        
        logger.debug("Updating place with model", id=place.id, name=place.name)
        
        try:
            # Convert Place model to dictionary
            place_data = place.to_dict()
            
            # Use the existing update_place_full method
            success = self.update_place_full(place_data)
            
            if success:
                logger.info("Place updated successfully using model", id=place.id)
            else:
                logger.error("Failed to update place using model", id=place.id)
            
            return success
            
        except Exception as e:
            logger.error("Error updating place with model", error=str(e), id=place.id)
            return False
