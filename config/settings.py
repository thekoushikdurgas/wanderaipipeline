"""
Configuration settings for the Places Management System.

This module contains all configuration constants and settings used throughout
the application, providing a centralized location for managing application
behavior and default values.
Optimized for performance with numpy and pandas vectorization.
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    # Database connection parameters
    user: str = os.getenv("user", "")
    password: str = os.getenv("password", "")
    host: str = os.getenv("host", "")
    port: str = os.getenv("port", "5432")
    dbname: str = os.getenv("dbname", "postgres")
    database_url: str = os.getenv("DATABASE_URL", "")

    # Connection settings
    echo_sql: bool = False  # Set to True for SQL query debugging
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class UIConfig:
    """User interface configuration settings."""

    # Page configuration
    page_title: str = "Places CRUD Application - PostgreSQL"
    page_icon: str = "🗺️"
    layout: str = "wide"

    # Table pagination settings
    default_page_size: int = 10
    page_size_options: Optional[List[int]] = None
    max_page_size: int = 100

    # Search and filtering
    search_placeholder: str = "Search places..."
    search_debounce_ms: int = 300

    # Colors and styling
    primary_color: str = "#667eea"
    secondary_color: str = "#764ba2"
    success_color: str = "#28a745"
    error_color: str = "#dc3545"
    warning_color: str = "#ffc107"

    def __post_init__(self):
        """Set default values after initialization."""
        if self.page_size_options is None:
            self.page_size_options = [10, 25, 50, 100]


@dataclass
class ValidationConfig:
    """Validation rules and constraints."""

    # Coordinate validation
    min_latitude: float = -90.0
    max_latitude: float = 90.0
    min_longitude: float = -180.0
    max_longitude: float = 180.0

    # Pincode validation
    pincode_pattern: str = r"^\d{6}$"
    pincode_length: int = 6

    # Text field constraints
    max_name_length: int = 255
    max_address_length: int = 1000
    max_types_length: int = 255

    # Required field validation
    required_fields: Optional[List[str]] = None

    def __post_init__(self):
        """Set default values after initialization."""
        if self.required_fields is None:
            self.required_fields = ["name", "address", "types", "pincode"]


@dataclass
class AnalyticsConfig:
    """Analytics and reporting configuration with performance optimization."""

    # Chart settings
    chart_height: int = 400
    chart_width: int = 600

    # Map settings
    default_zoom: int = 1
    map_style: str = "open-street-map"

    # Metrics
    recent_activity_limit: int = 10

    # Place types for filtering
    place_types: Optional[List[str]] = None

    # Performance optimization settings
    use_vectorized_operations: bool = True
    batch_size_for_charts: int = 1000
    enable_chart_caching: bool = True

    def __post_init__(self):
        """Set default values after initialization."""
        if self.place_types is None:
            self.place_types = [
                "restaurant",
                "hotel",
                "tourist_attraction",
                "museum",
                "park",
                "shopping_mall",
                "hospital",
                "school",
                "bank",
                "gas_station",
            ]


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""

    # Data processing optimization
    use_numpy_operations: bool = True
    use_pandas_vectorization: bool = True
    optimize_data_types: bool = True

    # Caching settings
    enable_dataframe_cache: bool = True
    cache_timeout_seconds: int = 300
    max_cache_size_mb: int = 100

    # Database optimization
    use_connection_pooling: bool = True
    optimize_sql_queries: bool = True
    batch_database_operations: bool = True

    # UI optimization
    lazy_loading_enabled: bool = True
    virtual_scrolling_threshold: int = 1000
    debounce_search_ms: int = 300

    # Memory optimization
    garbage_collection_frequency: int = 100
    memory_monitoring_enabled: bool = True
    optimize_dataframe_memory: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration settings."""

    # Log levels
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    debug_mode: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Log formatting
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"

    # File logging
    log_to_file: bool = False
    log_file_path: str = "logs/app.log"
    log_max_bytes: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5

    # Database logging
    log_sql_queries: bool = debug_mode
    log_performance: bool = debug_mode


@dataclass
class ExcelConfig:
    """Excel file handling configuration settings with performance optimization."""

    # Excel file settings
    excel_file_path: str = "utils/places.xlsx"
    sheet_name: str = "Places"
    enable_excel_sync: bool = True
    excel_backup_enabled: bool = True
    excel_backup_count: int = 5

    # Performance settings
    use_excel_cache: bool = True
    excel_cache_timeout: int = 300  # 5 minutes in seconds
    auto_save_threshold: int = 10  # Auto-save after N operations

    # Column mappings for Excel
    excel_columns: Optional[List[str]] = None

    # Performance optimization
    optimize_excel_reading: bool = True
    use_compression: bool = False
    batch_excel_operations: bool = True

    def __post_init__(self):
        """Set default values after initialization."""
        if self.excel_columns is None:
            self.excel_columns = [
                "place_id",
                "latitude",
                "longitude",
                "types",
                "name",
                "address",
                "pincode",
                "created_at",
                "updated_at",
            ]


# Global configuration instances
db_config = DatabaseConfig()
ui_config = UIConfig()
validation_config = ValidationConfig()
analytics_config = AnalyticsConfig()
performance_config = PerformanceConfig()
logging_config = LoggingConfig()
excel_config = ExcelConfig()


# Application constants
class AppConstants:
    """Application-wide constants."""

    # Navigation pages
    PAGES = {
        "VIEW_ALL": "View All Places",
        "ADD_NEW": "Add New Place",
        "SEARCH": "Search Places",
        "ANALYTICS": "Analytics Dashboard",
        "API_TESTING": "OLA Maps API Testing",
    }

    # Sort orders
    SORT_ORDERS = {"ASC": "ASC", "DESC": "DESC"}

    # Default sort columns
    DEFAULT_SORT_COLUMN = "place_id"

    # Session state keys
    SESSION_KEYS = {
        "CURRENT_PAGE": "current_page",
        "PAGE_SIZE": "page_size",
        "SORT_BY": "sort_by",
        "SORT_ORDER": "sort_order",
        "SEARCH_TERM": "search_term",
        "EDIT_PLACE_ID": "edit_place_id",
        "EDIT_MODE": "edit_mode",
        "SELECTED_COLLECTION_KEY": "selected_collection_key",
    }

    # CSS classes
    CSS_CLASSES = {
        "SUCCESS_MESSAGE": "success-message",
        "ERROR_MESSAGE": "error-message",
        "WARNING_MESSAGE": "warning-message",
        "MODERN_TABLE": "modern-table",
        "TABLE_HEADER": "table-header",
    }

    # Performance constants
    PERFORMANCE = {
        "MAX_BATCH_SIZE": 1000,
        "CACHE_TIMEOUT": 300,
        "DEBOUNCE_DELAY": 300,
        "LAZY_LOADING_THRESHOLD": 100,
    }


def get_database_connection_string() -> str:
    """
    Generate database connection string from configuration.

    Returns:
        str: PostgreSQL connection string

    Raises:
        ValueError: If required database parameters are missing
    """
    if db_config.database_url:
        return db_config.database_url

    if not all(
        [
            db_config.user,
            db_config.password,
            db_config.host,
            db_config.port,
            db_config.dbname,
        ]
    ):
        raise ValueError(
            "Database connection parameters must be set in environment variables. "
            "Required: user, password, host, port, dbname"
        )

    return f"postgresql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.dbname}"


def validate_configuration() -> List[str]:
    """
    Validate the current configuration settings.

    Returns:
        List[str]: List of validation errors, empty if configuration is valid
    """
    errors = []

    # Validate database configuration
    if not db_config.user:
        errors.append("Database user is not configured")
    if not db_config.password:
        errors.append("Database password is not configured")
    if not db_config.host:
        errors.append("Database host is not configured")

    # Validate UI configuration
    if ui_config.default_page_size not in ui_config.page_size_options:
        errors.append("Default page size must be in page size options")

    # Validate validation configuration
    if validation_config.min_latitude >= validation_config.max_latitude:
        errors.append("Minimum latitude must be less than maximum latitude")
    if validation_config.min_longitude >= validation_config.max_longitude:
        errors.append("Minimum longitude must be less than maximum longitude")

    # Validate performance configuration
    if performance_config.cache_timeout_seconds <= 0:
        errors.append("Cache timeout must be positive")
    if performance_config.max_cache_size_mb <= 0:
        errors.append("Max cache size must be positive")

    return errors


def get_optimized_dtypes() -> Dict[str, str]:
    """
    Get optimized data types for pandas DataFrames.

    Returns:
        Dict[str, str]: Dictionary mapping column names to optimized data types
    """
    return {
        "place_id": "int32",
        "latitude": "float64",
        "longitude": "float64",
        "types": "string",
        "name": "string",
        "address": "string",
        "pincode": "string",
        "created_at": "datetime64[ns]",
        "updated_at": "datetime64[ns]",
    }


def get_performance_settings() -> Dict[str, Any]:
    """
    Get performance optimization settings.

    Returns:
        Dict[str, Any]: Performance settings dictionary
    """
    return {
        "use_numpy": performance_config.use_numpy_operations,
        "use_vectorization": performance_config.use_pandas_vectorization,
        "optimize_dtypes": performance_config.optimize_data_types,
        "enable_caching": performance_config.enable_dataframe_cache,
        "cache_timeout": performance_config.cache_timeout_seconds,
        "batch_operations": performance_config.batch_database_operations,
        "lazy_loading": performance_config.lazy_loading_enabled,
        "virtual_scrolling": performance_config.virtual_scrolling_threshold,
        "debounce_search": performance_config.debounce_search_ms,
    }


def get_default_types() -> List[str]:
    """
    Get default types for the Places Management System.

    Returns:
        List[str]: Default types list
    """
    return [
        # "OLA_railway=monorail_station",
        # "OLA_railway=station",
        "accounting",
        # "advertising_agency",
        "airport",
        # "amusement_park",
        # "aquarium",
        # "archipelago",
        "art_gallery",
        "atm",
        "bakery",
        "bank",
        "bar",
        "beauty_salon",
        "bicycle_store",
        "book_store",
        "bowling_alley",
        "bowling_alley",
        "bus_station",
        "bus_station",
        # "business_and_service",
        "cafe",
        "cafe",
        "campground",
        "car_dealer",
        "car_rental",
        "car_repair",
        "car_wash",
        "casino",
        "cemetery",
        "church",
        "city_hall",
        "clothing_store",
        # "commercial_and_industrial",
        "convenience_store",
        "courthouse",
        "dentist",
        "department_store",
        "doctor",
        "drugstore",
        # "education",
        "electrician",
        "electronics_store",
        "embassy",
        # "establishment",
        "finance",
        # "financial_service",
        "fire_station",
        "florist",
        "food",
        "funeral_home",
        "furniture_store",
        "gas_station",
        "general_contractor",
        "grocery_or_supermarket",
        "gym",
        "hair_care",
        "hardware_store",
        "health",
        # "healthcare",
        # "healthcare_service",
        "hindu_temple",
        "home_goods_store",
        "hospital",
        # "hospitality",
        "insurance_agency",
        "intersection",
        # "jewelry",
        "jewelry_store",
        "landmark",
        "laundry",
        "lawyer",
        "library",
        "light_rail_station",
        "liquor_store",
        "local_government_office",
        "locksmith",
        "lodging",
        # "meal_delivery",
        # "meal_takeaway",
        "mosque",
        "movie_rental",
        "movie_theater",
        "moving_company",
        "museum",
        "natural_feature",
        "night_club",
        "painter",
        "park",
        "parking",
        "pet_store",
        "pharmacy",
        "physiotherapist",
        "pickup_drop=yes",
        "place_of_worship",
        "plumber",
        "point_of_interest",
        "police",
        "post_office",
        "postal_code",
        "postal_code_prefix",
        "premise",
        "primary_school",
        "real_estate_agency",
        "recreation_and_entertainment",
        "residential_accommodation",
        "restaurant",
        "roofing_contractor",
        "route",
        "rv_park",
        "salon",
        "school",
        "secondary_school",
        "shoe_store",
        "shop",
        "shopping_mall",
        "spa",
        "stadium",
        "storage",
        "store",
        "subway_station",
        "supermarket",
        "synagogue",
        "taxi_stand",
        "tourist_attraction",
        "town_square",
        "train_station",
        "transit_station",
        "travel_agency",
        "university",
        "veterinary_care",
        "zoo",
    ]


# Export all configurations for easy import
__all__ = [
    "db_config",
    "ui_config",
    "validation_config",
    "analytics_config",
    "performance_config",
    "logging_config",
    "excel_config",
    "AppConstants",
    "get_database_connection_string",
    "validate_configuration",
    "get_optimized_dtypes",
    "get_performance_settings",
    "get_default_types",
]
