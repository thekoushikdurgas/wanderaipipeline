"""
Excel file handling utilities for the Places Management System.

This module provides comprehensive Excel operations for backup, caching, and fast
data access with proper error handling and performance optimization.
Optimized with numpy and pandas vectorization for faster response times.
"""

import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import numpy as np

# Import utilities and configuration
try:
    from utils.settings import excel_config
    from utils.logger import get_logger, log_performance
    from utils.error_handlers import (
        handle_errors, safe_execute, FileSystemError, 
        ErrorContext, PlacesAppException
    )
except ImportError:
    # Fallback configuration
    class MockExcelConfig:
        excel_file_path = "utils/places.xlsx"
        sheet_name = "Places"
        enable_excel_sync = True
        excel_backup_enabled = True
        excel_backup_count = 5
        use_excel_cache = True
        excel_cache_timeout = 300
        auto_save_threshold = 10
        excel_columns = [
            'id', 'latitude', 'longitude', 'types', 
            'name', 'address', 'pincode', 'rating', 'followers', 'country',
            'created_at', 'updated_at'
        ]
    
    excel_config = MockExcelConfig()
    
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
        return MockLogger()
    
    def log_performance(_name):
        def decorator(func):
            return func
        return decorator
    
    def handle_errors(**_kwargs):
        def decorator(func):
            return func
        return decorator
    
    def safe_execute(op, _name, default=None, _context=None):
        try:
            return op()
        except Exception:
            return default

# Initialize logger
logger = get_logger(__name__)


class ExcelCacheManager:
    """Manages Excel file caching for improved performance with numpy optimization."""
    
    def __init__(self):
        """Initialize cache manager."""
        self._cache: Optional[pd.DataFrame] = None
        self._cache_timestamp: Optional[datetime] = None
        self._operation_count = 0
        self.logger = get_logger(self.__class__.__name__)
    
    def is_cache_valid(self) -> bool:
        """
        Check if the current cache is still valid.
        
        Returns:
            bool: True if cache is valid and not expired
        """
        if self._cache is None or self._cache_timestamp is None:
            return False
        
        # Check if cache has expired
        cache_age = datetime.now() - self._cache_timestamp
        max_age = timedelta(seconds=excel_config.excel_cache_timeout)
        
        is_valid = cache_age < max_age
        self.logger.debug("Cache validity check", 
                         is_valid=is_valid, 
                         cache_age_seconds=cache_age.total_seconds(),
                         max_age_seconds=max_age.total_seconds())
        
        return is_valid
    
    def get_cached_data(self) -> Optional[pd.DataFrame]:
        """
        Get cached data if valid.
        
        Returns:
            Optional[pd.DataFrame]: Cached data or None if invalid
        """
        if not excel_config.use_excel_cache:
            return None
        
        if self.is_cache_valid():
            self.logger.debug("Returning cached data", records=len(self._cache))
            return self._cache.copy()
        else:
            self.logger.debug("Cache invalid or expired, clearing cache")
            self.clear_cache()
            return None
    
    def update_cache(self, data: pd.DataFrame) -> None:
        """
        Update the cache with new data using optimized pandas operations.
        
        Args:
            data: New data to cache
        """
        if not excel_config.use_excel_cache:
            return
        
        # Optimize data types for faster operations
        optimized_data = data.copy()
        
        # Use numpy dtypes for better performance
        if 'id' in optimized_data.columns:
            optimized_data['id'] = optimized_data['id'].astype('string')
        if 'latitude' in optimized_data.columns:
            optimized_data['latitude'] = optimized_data['latitude'].astype(np.float64)
        if 'longitude' in optimized_data.columns:
            optimized_data['longitude'] = optimized_data['longitude'].astype(np.float64)
        if 'types' in optimized_data.columns:
            optimized_data['types'] = optimized_data['types'].astype('string')
        if 'name' in optimized_data.columns:
            optimized_data['name'] = optimized_data['name'].astype('string')
        if 'address' in optimized_data.columns:
            optimized_data['address'] = optimized_data['address'].astype('string')
        if 'pincode' in optimized_data.columns:
            optimized_data['pincode'] = optimized_data['pincode'].astype('string')
        
        self._cache = optimized_data
        self._cache_timestamp = datetime.now()
        self.logger.debug("Cache updated", records=len(data))
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache = None
        self._cache_timestamp = None
        self.logger.debug("Cache cleared")
    
    def increment_operation_count(self) -> bool:
        """
        Increment operation count and check if auto-save threshold reached.
        
        Returns:
            bool: True if auto-save threshold reached
        """
        self._operation_count += 1
        should_save = self._operation_count >= excel_config.auto_save_threshold
        
        if should_save:
            self._operation_count = 0
            self.logger.debug("Auto-save threshold reached")
        
        return should_save


class ExcelBackupManager:
    """Manages Excel file backups with optimized file operations."""
    
    def __init__(self, excel_file_path: str):
        """
        Initialize backup manager.
        
        Args:
            excel_file_path: Path to the main Excel file
        """
        self.excel_file_path = Path(excel_file_path)
        self.backup_dir = self.excel_file_path.parent / "backups"
        self.logger = get_logger(self.__class__.__name__)
    
    @handle_errors(show_user_message=False)
    def create_backup(self) -> Optional[str]:
        """
        Create a backup of the Excel file.
        
        Returns:
            Optional[str]: Path to backup file or None if failed
        """
        if not excel_config.excel_backup_enabled:
            return None
        
        if not self.excel_file_path.exists():
            self.logger.warning("Excel file doesn't exist, skipping backup")
            return None
        
        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{self.excel_file_path.stem}_{timestamp}.xlsx"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Copy the file
            shutil.copy2(self.excel_file_path, backup_path)
            self.logger.info("Backup created", backup_path=str(backup_path))
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return str(backup_path)
            
        except Exception as e:
            self.logger.error("Failed to create backup", error=str(e))
            return None
    
    def _cleanup_old_backups(self) -> None:
        """Remove old backup files based on configuration."""
        try:
            # Get all backup files
            backup_files = list(self.backup_dir.glob(f"{self.excel_file_path.stem}_*.xlsx"))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove excess backups
            if len(backup_files) > excel_config.excel_backup_count:
                files_to_remove = backup_files[excel_config.excel_backup_count:]
                for file_path in files_to_remove:
                    file_path.unlink()
                    self.logger.debug("Removed old backup", file=str(file_path))
                
                self.logger.info("Backup cleanup completed", 
                               removed_count=len(files_to_remove),
                               remaining_count=excel_config.excel_backup_count)
        
        except Exception as e:
            self.logger.warning("Backup cleanup failed", error=str(e))


class ExcelHandler:
    """Comprehensive Excel file handler for Places Management System with numpy/pandas optimization."""
    
    def __init__(self):
        """Initialize Excel handler with configuration."""
        self.excel_file_path = Path(excel_config.excel_file_path)
        self.sheet_name = excel_config.sheet_name
        self.cache_manager = ExcelCacheManager()
        self.backup_manager = ExcelBackupManager(excel_config.excel_file_path)
        self.logger = get_logger(self.__class__.__name__)
        
        # Ensure directory exists
        self.excel_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Excel handler initialized", 
                        file_path=str(self.excel_file_path),
                        sync_enabled=excel_config.enable_excel_sync)
    
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
    
    @handle_errors(show_user_message=False)
    @log_performance("excel_read_operation")
    def read_excel_data(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Read data from Excel file with caching support and optimized pandas operations.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            pd.DataFrame: Data from Excel file, empty if error or file doesn't exist
        """
        self.logger.debug("Reading Excel data", 
                         file_path=str(self.excel_file_path),
                         use_cache=use_cache)
        
        # Try to get cached data first
        if use_cache:
            cached_data = self.cache_manager.get_cached_data()
            if cached_data is not None:
                return cached_data
        
        # Read from file if cache miss or disabled
        try:
            if not self.excel_file_path.exists():
                self.logger.info("Excel file doesn't exist, returning empty DataFrame")
                return pd.DataFrame(columns=excel_config.excel_columns)
            
            # Read Excel file with optimized settings
            df = pd.read_excel(
                self.excel_file_path, 
                sheet_name=self.sheet_name,
                engine='openpyxl',
                dtype={
                    'id': 'string',
                    'latitude': np.float64,
                    'longitude': np.float64,
                    'types': 'string',
                    'name': 'string',
                    'address': 'string',
                    'pincode': 'string'
                },
                parse_dates=['created_at', 'updated_at']
            )
            
            # Ensure datetime columns are timezone-naive for Excel compatibility
            df = self._convert_datetimes_to_naive(df)
            
            # Ensure all required columns exist
            for col in excel_config.excel_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Reorder columns to match configuration
            df = df[excel_config.excel_columns]
            
            # Update cache with optimized data
            self.cache_manager.update_cache(df)
            
            self.logger.info("Excel data loaded successfully", 
                           records=len(df), 
                           file_size_mb=self.excel_file_path.stat().st_size / (1024*1024))
            
            return df
            
        except Exception as e:
            self.logger.error("Failed to read Excel file", 
                            file_path=str(self.excel_file_path),
                            error=str(e))
            
            # Return empty DataFrame with correct structure
            return pd.DataFrame(columns=excel_config.excel_columns)
    
    @handle_errors(show_user_message=False)
    @log_performance("excel_write_operation")
    def write_excel_data(self, df: pd.DataFrame, create_backup: bool = True) -> bool:
        """
        Write data to Excel file with backup and error handling.
        Optimized with pandas for faster data processing.
        
        Args:
            df: DataFrame to write
            create_backup: Whether to create a backup before writing
            
        Returns:
            bool: True if successful
        """
        if not excel_config.enable_excel_sync:
            self.logger.debug("Excel sync disabled, skipping write")
            return True
        
        self.logger.debug("Writing Excel data", 
                         records=len(df),
                         file_path=str(self.excel_file_path))
        
        try:
            # Create backup if requested and file exists
            if create_backup:
                self.backup_manager.create_backup()
            
            # Ensure all required columns are present
            for col in excel_config.excel_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Reorder columns
            df_ordered = df[excel_config.excel_columns].copy()
            
            # Handle datetime columns with vectorized operations
            datetime_columns = ['created_at', 'updated_at']
            for col in datetime_columns:
                if col in df_ordered.columns:
                    df_ordered[col] = pd.to_datetime(df_ordered[col], errors='coerce')
            
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            df_ordered = self._convert_datetimes_to_naive(df_ordered)
            
            # Optimize data types for better performance
            if 'id' in df_ordered.columns:
                df_ordered['id'] = df_ordered['id'].astype('string')
            if 'latitude' in df_ordered.columns:
                df_ordered['latitude'] = df_ordered['latitude'].astype(np.float64)
            if 'longitude' in df_ordered.columns:
                df_ordered['longitude'] = df_ordered['longitude'].astype(np.float64)
            
            # Write to Excel with formatting
            with pd.ExcelWriter(
                self.excel_file_path, 
                engine='openpyxl',
                mode='w'
            ) as writer:
                df_ordered.to_excel(
                    writer, 
                    sheet_name=self.sheet_name, 
                    index=False,
                    freeze_panes=(1, 0)  # Freeze header row
                )
                
                # Get the worksheet for formatting
                worksheet = writer.sheets[self.sheet_name]
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except (AttributeError, TypeError):
                            # Handle cases where cell.value is None or not convertible to string
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # Max width of 50
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Update cache
            self.cache_manager.update_cache(df_ordered)
            
            self.logger.info("Excel data written successfully", 
                           records=len(df_ordered),
                           file_path=str(self.excel_file_path))
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to write Excel file", 
                            file_path=str(self.excel_file_path),
                            error=str(e))
            return False
    
    @handle_errors(show_user_message=False)
    def sync_from_database(self, database_df: pd.DataFrame) -> bool:
        """
        Sync Excel file with database data using optimized pandas operations.
        
        Args:
            database_df: DataFrame from database
            
        Returns:
            bool: True if successful
        """
        if not excel_config.enable_excel_sync:
            return True
        
        self.logger.debug("Syncing Excel from database", records=len(database_df))
        
        # Check if we need to update based on operation count
        should_auto_save = self.cache_manager.increment_operation_count()
        
        return self.write_excel_data(database_df, create_backup=should_auto_save)
    
    @handle_errors(show_user_message=False)
    def add_place_to_excel(self, place_data: Dict[str, Any]) -> bool:
        """
        Add a single place to Excel file using optimized pandas operations.
        
        Args:
            place_data: Place data dictionary
            
        Returns:
            bool: True if successful
        """
        if not excel_config.enable_excel_sync:
            return True
        
        self.logger.debug("Adding place to Excel", id=place_data.get('id'))
        
        try:
            # Read current data
            df = self.read_excel_data()
            
            # Create new row with optimized data types
            new_row = pd.DataFrame([place_data])
            
            # Handle datetime fields properly to avoid dtype warnings
            for datetime_field in ['created_at', 'updated_at']:
                if datetime_field in new_row.columns:
                    value = new_row[datetime_field].iloc[0]
                    if value is not None:
                        # Convert timezone-aware datetime to timezone-naive
                        if hasattr(value, 'tzinfo') and value.tzinfo is not None:
                            value = value.replace(tzinfo=None)
                        # Ensure it's a pandas-compatible datetime
                        try:
                            new_row[datetime_field] = pd.to_datetime(value)
                        except:
                            # If conversion fails, use current time
                            new_row[datetime_field] = pd.Timestamp.now()
            
            # Optimize data types for the new row
            if 'id' in new_row.columns:
                new_row['id'] = new_row['id'].astype('string')
            if 'latitude' in new_row.columns:
                new_row['latitude'] = new_row['latitude'].astype(np.float64)
            if 'longitude' in new_row.columns:
                new_row['longitude'] = new_row['longitude'].astype(np.float64)
            
            # Append to existing data using pandas concat
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # Write back to Excel
            return self.write_excel_data(updated_df)
            
        except Exception as e:
            self.logger.error("Failed to add place to Excel", error=str(e))
            return False
    
    @handle_errors(show_user_message=False)
    def update_place_in_excel(self, id: str, updated_data: Dict[str, Any]) -> bool:
        """
        Update a specific place in Excel file using vectorized operations.
        
        Args:
            id: ID of place to update
            updated_data: Updated place data
            
        Returns:
            bool: True if successful
        """
        if not excel_config.enable_excel_sync:
            return True
        
        self.logger.debug("Updating place in Excel", id=id)
        
        try:
            # Read current data
            df = self.read_excel_data()
            
            # Use vectorized operations for finding and updating
            mask = df['id'] == id
            if mask.any():
                # Update the row using vectorized operations
                for key, value in updated_data.items():
                    if key in df.columns:
                        # Handle datetime fields properly to avoid dtype warnings
                        if key in ['created_at', 'updated_at'] and value is not None:
                            # Convert timezone-aware datetime to timezone-naive
                            if hasattr(value, 'tzinfo') and value.tzinfo is not None:
                                value = value.replace(tzinfo=None)
                            # Ensure it's a pandas-compatible datetime
                            try:
                                value = pd.to_datetime(value)
                            except:
                                # If conversion fails, use current time
                                value = pd.Timestamp.now()
                        df.loc[mask, key] = value
                
                # Write back to Excel
                return self.write_excel_data(df)
            else:
                self.logger.warning("Place not found in Excel", id=id)
                return False
            
        except Exception as e:
            self.logger.error("Failed to update place in Excel", error=str(e))
            return False
    
    @handle_errors(show_user_message=False)
    def delete_place_from_excel(self, id: str) -> bool:
        """
        Delete a specific place from Excel file using vectorized operations.
        
        Args:
            id: ID of place to delete
            
        Returns:
            bool: True if successful
        """
        if not excel_config.enable_excel_sync:
            return True
        
        self.logger.debug("Deleting place from Excel", id=id)
        
        try:
            # Read current data
            df = self.read_excel_data()
            
            # Use vectorized operations for deletion
            mask = df['id'] != id
            updated_df = df[mask]
            
            if len(updated_df) < len(df):
                # Write back to Excel
                result = self.write_excel_data(updated_df)
                self.logger.info("Place deleted from Excel", id=id)
                return result
            else:
                self.logger.warning("Place not found in Excel for deletion", id=id)
                return False
            
        except Exception as e:
            self.logger.error("Failed to delete place from Excel", error=str(e))
            return False
    
    @handle_errors(show_user_message=False)
    def get_excel_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the Excel file using optimized operations.
        
        Returns:
            Dict[str, Any]: Statistics about Excel file
        """
        try:
            stats = {
                'file_exists': self.excel_file_path.exists(),
                'file_path': str(self.excel_file_path),
                'sync_enabled': excel_config.enable_excel_sync,
                'cache_enabled': excel_config.use_excel_cache,
                'backup_enabled': excel_config.excel_backup_enabled,
            }
            
            if self.excel_file_path.exists():
                file_stat = self.excel_file_path.stat()
                stats.update({
                    'file_size_bytes': file_stat.st_size,
                    'file_size_mb': file_stat.st_size / (1024 * 1024),
                    'last_modified': datetime.fromtimestamp(file_stat.st_mtime),
                })
                
                # Get record count using optimized read
                df = self.read_excel_data()
                stats['record_count'] = len(df)
            else:
                stats.update({
                    'file_size_bytes': 0,
                    'file_size_mb': 0,
                    'last_modified': None,
                    'record_count': 0,
                })
            
            # Cache statistics
            cache_valid = self.cache_manager.is_cache_valid()
            stats['cache_valid'] = cache_valid
            if cache_valid and self.cache_manager._cache is not None:
                stats['cache_record_count'] = len(self.cache_manager._cache)
            else:
                stats['cache_record_count'] = 0
            
            return stats
            
        except Exception as e:
            self.logger.error("Failed to get Excel statistics", error=str(e))
            return {'error': str(e)}
    
    def clear_cache(self) -> None:
        """Clear the Excel cache."""
        self.cache_manager.clear_cache()
        self.logger.info("Excel cache cleared")
    
    def force_sync_from_database(self, database_df: pd.DataFrame) -> bool:
        """
        Force a complete sync from database, ignoring cache and thresholds.
        
        Args:
            database_df: Complete database data
            
        Returns:
            bool: True if successful
        """
        self.logger.info("Force syncing Excel from database", records=len(database_df))
        
        # Clear cache first
        self.clear_cache()
        
        # Write data with backup
        return self.write_excel_data(database_df, create_backup=True)


# Global Excel handler instance
excel_handler = ExcelHandler()


# Convenience functions
def read_places_from_excel(use_cache: bool = True) -> pd.DataFrame:
    """
    Read places data from Excel file with optimized operations.
    
    Args:
        use_cache: Whether to use cached data
        
    Returns:
        pd.DataFrame: Places data
    """
    return excel_handler.read_excel_data(use_cache=use_cache)


def sync_excel_with_database(database_df: pd.DataFrame) -> bool:
    """
    Sync Excel file with database data.
    
    Args:
        database_df: Database data to sync
        
    Returns:
        bool: True if successful
    """
    return excel_handler.sync_from_database(database_df)


def get_excel_stats() -> Dict[str, Any]:
    """Get Excel file statistics."""
    return excel_handler.get_excel_statistics()


# Export all Excel utilities
__all__ = [
    'ExcelHandler',
    'ExcelCacheManager',
    'ExcelBackupManager',
    'excel_handler',
    'read_places_from_excel',
    'sync_excel_with_database',
    'get_excel_stats'
]
