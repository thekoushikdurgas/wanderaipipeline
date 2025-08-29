"""
Comprehensive validation utilities for the Places Management System.

This module provides validation functions for all data types used in the application,
with detailed error reporting and logging capabilities for better debugging.
"""

import re
import string
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass

# Import configuration and logging
try:
    from config.settings import validation_config
    from utils.logger import get_logger
except ImportError:
    # Fallback configuration if modules are not available
    class FallbackValidationConfig:
        min_latitude = -90.0
        max_latitude = 90.0
        min_longitude = -180.0
        max_longitude = 180.0
        pincode_pattern = r'^\d{6}$'
        pincode_length = 6
        max_name_length = 255
        max_address_length = 1000
        max_types_length = 255
        required_fields = ['name', 'address', 'types', 'pincode']
    
    validation_config = FallbackValidationConfig()
    
    # Fallback logger
    class FallbackLogger:
        def debug(self, msg, **kwargs): 
            # Fallback logger - no operation implementation
            pass
        def warning(self, msg, **kwargs): 
            # Fallback logger - no operation implementation
            pass
        def error(self, msg, **kwargs): 
            # Fallback logger - no operation implementation
            pass
    
    def get_logger(_name):
        # Fallback function - parameter name ignored
        return FallbackLogger()

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    field_errors: Dict[str, List[str]]
    
    def __post_init__(self):
        """Ensure all fields are properly initialized."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.field_errors is None:
            self.field_errors = {}
    
    def add_error(self, message: str, field: Optional[str] = None) -> None:
        """
        Add an error to the validation result.
        
        Args:
            message: Error message
            field: Optional field name for field-specific errors
        """
        self.errors.append(message)
        self.is_valid = False
        
        if field:
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].append(message)
    
    def add_warning(self, message: str, field: Optional[str] = None) -> None:
        """
        Add a warning to the validation result.
        
        Args:
            message: Warning message
            field: Optional field name for field-specific warnings
        """
        self.warnings.append(message)
        
        if field:
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].append(f"Warning: {message}")
    
    def get_error_summary(self) -> str:
        """Get a formatted summary of all errors."""
        if not self.errors:
            return "No errors"
        
        summary = "Validation Errors:\n"
        for i, error in enumerate(self.errors, 1):
            summary += f"  {i}. {error}\n"
        
        return summary.strip()
    
    def get_field_errors(self, field: str) -> List[str]:
        """Get errors for a specific field."""
        return self.field_errors.get(field, [])


class CoordinateValidator:
    """Validator for geographic coordinates."""
    
    @staticmethod
    def validate_latitude(latitude: Union[str, int, float]) -> ValidationResult:
        """
        Validate latitude coordinate.
        
        Args:
            latitude: Latitude value to validate
            
        Returns:
            ValidationResult: Validation result with errors if any
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[], field_errors={})
        
        logger.debug("Validating latitude", value=latitude, type=type(latitude).__name__)
        
        # Check if value is provided
        if latitude is None or latitude == "":
            result.add_error("Latitude is required", "latitude")
            return result
        
        # Try to convert to float
        try:
            lat_float = float(latitude)
        except (ValueError, TypeError) as e:
            logger.warning("Invalid latitude format", value=latitude, error=str(e))
            result.add_error(f"Latitude must be a valid number, got: {latitude}", "latitude")
            return result
        
        # Check range
        if not (validation_config.min_latitude <= lat_float <= validation_config.max_latitude):
            logger.warning("Latitude out of range", 
                         value=lat_float, 
                         min_val=validation_config.min_latitude,
                         max_val=validation_config.max_latitude)
            result.add_error(
                f"Latitude must be between {validation_config.min_latitude} and {validation_config.max_latitude}, got: {lat_float}",
                "latitude"
            )
        
        # Check precision warning
        if len(str(lat_float).split('.')[-1]) > 8:
            result.add_warning(
                "Latitude has very high precision, consider rounding to 8 decimal places",
                "latitude"
            )
        
        logger.debug("Latitude validation completed", is_valid=result.is_valid, errors=len(result.errors))
        return result
    
    @staticmethod
    def validate_longitude(longitude: Union[str, int, float]) -> ValidationResult:
        """
        Validate longitude coordinate.
        
        Args:
            longitude: Longitude value to validate
            
        Returns:
            ValidationResult: Validation result with errors if any
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[], field_errors={})
        
        logger.debug("Validating longitude", value=longitude, type=type(longitude).__name__)
        
        # Check if value is provided
        if longitude is None or longitude == "":
            result.add_error("Longitude is required", "longitude")
            return result
        
        # Try to convert to float
        try:
            lon_float = float(longitude)
        except (ValueError, TypeError) as e:
            logger.warning("Invalid longitude format", value=longitude, error=str(e))
            result.add_error(f"Longitude must be a valid number, got: {longitude}", "longitude")
            return result
        
        # Check range
        if not (validation_config.min_longitude <= lon_float <= validation_config.max_longitude):
            logger.warning("Longitude out of range", 
                         value=lon_float, 
                         min_val=validation_config.min_longitude,
                         max_val=validation_config.max_longitude)
            result.add_error(
                f"Longitude must be between {validation_config.min_longitude} and {validation_config.max_longitude}, got: {lon_float}",
                "longitude"
            )
        
        # Check precision warning
        if len(str(lon_float).split('.')[-1]) > 8:
            result.add_warning(
                "Longitude has very high precision, consider rounding to 8 decimal places",
                "longitude"
            )
        
        logger.debug("Longitude validation completed", is_valid=result.is_valid, errors=len(result.errors))
        return result
    
    @staticmethod
    def validate_coordinates(latitude: Union[str, int, float], longitude: Union[str, int, float]) -> ValidationResult:
        """
        Validate both latitude and longitude coordinates.
        
        Args:
            latitude: Latitude value to validate
            longitude: Longitude value to validate
            
        Returns:
            ValidationResult: Combined validation result
        """
        logger.debug("Validating coordinate pair", latitude=latitude, longitude=longitude)
        
        lat_result = CoordinateValidator.validate_latitude(latitude)
        lon_result = CoordinateValidator.validate_longitude(longitude)
        
        # Combine results
        combined_result = ValidationResult(
            is_valid=lat_result.is_valid and lon_result.is_valid,
            errors=lat_result.errors + lon_result.errors,
            warnings=lat_result.warnings + lon_result.warnings,
            field_errors={**lat_result.field_errors, **lon_result.field_errors}
        )
        
        # Additional coordinate pair validations
        if lat_result.is_valid and lon_result.is_valid:
            try:
                lat_float = float(latitude)
                lon_float = float(longitude)
                
                # Check for common invalid coordinates (using small epsilon for float comparison)
                if abs(lat_float) < 1e-10 and abs(lon_float) < 1e-10:
                    combined_result.add_warning(
                        "Coordinates (0, 0) point to the Gulf of Guinea. Please verify this is correct.",
                        "coordinates"
                    )
                
                # Check for obviously invalid coordinates
                if abs(abs(lat_float) - abs(lon_float)) < 1e-10 and abs(lat_float) > 1e-10:
                    combined_result.add_warning(
                        "Identical absolute values for latitude and longitude are unusual. Please verify.",
                        "coordinates"
                    )
                
            except (ValueError, TypeError):
                pass  # Already handled in individual validations
        
        logger.debug("Coordinate pair validation completed", 
                    is_valid=combined_result.is_valid, 
                    errors=len(combined_result.errors),
                    warnings=len(combined_result.warnings))
        
        return combined_result


class TextValidator:
    """Validator for text fields."""
    
    @staticmethod
    def validate_name(name: str) -> ValidationResult:
        """
        Validate place name.
        
        Args:
            name: Name to validate
            
        Returns:
            ValidationResult: Validation result with errors if any
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[], field_errors={})
        
        logger.debug("Validating place name", name=name, length=len(name) if name else 0)
        
        # Check if name is provided
        if not name or not name.strip():
            result.add_error("Place name is required", "name")
            return result
        
        name = name.strip()
        
        # Check length
        if len(name) > validation_config.max_name_length:
            result.add_error(
                f"Name must be no more than {validation_config.max_name_length} characters, got: {len(name)}",
                "name"
            )
        
        # Check minimum length
        if len(name) < 2:
            result.add_error("Name must be at least 2 characters long", "name")
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9\s\-\'\"\.&,()]+$', name):
            result.add_warning(
                "Name contains special characters that might cause issues",
                "name"
            )
        
        # Check for potentially unsafe content
        dangerous_patterns = ['<script', 'javascript:', 'vbscript:', '<iframe', '<object']
        for pattern in dangerous_patterns:
            if pattern.lower() in name.lower():
                result.add_error("Name contains potentially unsafe content", "name")
                break
        
        logger.debug("Name validation completed", is_valid=result.is_valid, errors=len(result.errors))
        return result
    
    @staticmethod
    def validate_address(address: str) -> ValidationResult:
        """
        Validate place address.
        
        Args:
            address: Address to validate
            
        Returns:
            ValidationResult: Validation result with errors if any
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[], field_errors={})
        
        logger.debug("Validating address", address=address[:50] if address else None, 
                    length=len(address) if address else 0)
        
        # Check if address is provided
        if not address or not address.strip():
            result.add_error("Address is required", "address")
            return result
        
        address = address.strip()
        
        # Check length
        if len(address) > validation_config.max_address_length:
            result.add_error(
                f"Address must be no more than {validation_config.max_address_length} characters, got: {len(address)}",
                "address"
            )
        
        # Check minimum length
        if len(address) < 5:
            result.add_error("Address must be at least 5 characters long", "address")
        
        # Check for potentially unsafe content
        dangerous_patterns = ['<script', 'javascript:', 'vbscript:', '<iframe', '<object']
        for pattern in dangerous_patterns:
            if pattern.lower() in address.lower():
                result.add_error("Address contains potentially unsafe content", "address")
                break
        
        # Address format suggestions
        if not any(char.isdigit() for char in address):
            result.add_warning(
                "Address doesn't contain any numbers. Consider adding house/building number.",
                "address"
            )
        
        logger.debug("Address validation completed", is_valid=result.is_valid, errors=len(result.errors))
        return result
    
    @staticmethod
    def validate_types(types: str) -> ValidationResult:
        """
        Validate place types.
        
        Args:
            types: Types string to validate
            
        Returns:
            ValidationResult: Validation result with errors if any
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[], field_errors={})
        
        logger.debug("Validating types", types=types, length=len(types) if types else 0)
        
        # Check if types is provided
        if not types or not types.strip():
            result.add_error("Place types are required", "types")
            return result
        
        types = types.strip()
        
        # Check length
        if len(types) > validation_config.max_types_length:
            result.add_error(
                f"Types must be no more than {validation_config.max_types_length} characters, got: {len(types)}",
                "types"
            )
        
        # Check format (should be lowercase, underscore-separated)
        if not re.match(r'^[a-z0-9_,\s]+$', types):
            result.add_warning(
                "Types should contain only lowercase letters, numbers, underscores, commas, and spaces",
                "types"
            )
        
        # Parse individual types
        type_list = [t.strip() for t in types.replace(',', ' ').split() if t.strip()]
        
        if not type_list:
            result.add_error("At least one place type must be specified", "types")
        
        # Validate individual types
        valid_types = {
            'restaurant', 'hotel', 'tourist_attraction', 'museum', 'park', 
            'shopping_mall', 'hospital', 'school', 'bank', 'gas_station',
            'cafe', 'bar', 'gym', 'pharmacy', 'supermarket', 'library',
            'police', 'fire_station', 'post_office', 'church', 'mosque',
            'temple', 'cemetery', 'airport', 'train_station', 'bus_station'
        }
        
        unknown_types = []
        for place_type in type_list:
            if place_type not in valid_types:
                unknown_types.append(place_type)
        
        if unknown_types:
            result.add_warning(
                f"Unknown place types: {', '.join(unknown_types)}. Consider using standard types.",
                "types"
            )
        
        logger.debug("Types validation completed", 
                    is_valid=result.is_valid, 
                    errors=len(result.errors),
                    type_count=len(type_list))
        return result


class PincodeValidator:
    """Validator for postal codes."""
    
    @staticmethod
    def validate_pincode(pincode: str) -> ValidationResult:
        """
        Validate pincode format.
        
        Args:
            pincode: Pincode to validate
            
        Returns:
            ValidationResult: Validation result with errors if any
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[], field_errors={})
        
        logger.debug("Validating pincode", pincode=pincode, length=len(pincode) if pincode else 0)
        
        # Check if pincode is provided
        if not pincode or not pincode.strip():
            result.add_error("Pincode is required", "pincode")
            return result
        
        pincode = pincode.strip()
        
        # Check length
        if len(pincode) != validation_config.pincode_length:
            result.add_error(
                f"Pincode must be exactly {validation_config.pincode_length} digits, got: {len(pincode)}",
                "pincode"
            )
        
        # Check format using regex
        if not re.match(validation_config.pincode_pattern, pincode):
            result.add_error(
                f"Pincode must contain only digits, got: {pincode}",
                "pincode"
            )
        
        # Additional validations for Indian postal codes
        if len(pincode) == 6 and pincode.isdigit():
            # Check for obviously invalid pincodes
            if pincode == "000000":
                result.add_error("Invalid pincode: 000000", "pincode")
            elif pincode == "999999":
                result.add_warning("Pincode 999999 is reserved and might be invalid", "pincode")
            elif pincode[0] == '0':
                result.add_warning("Pincodes starting with 0 are rare in India", "pincode")
        
        logger.debug("Pincode validation completed", is_valid=result.is_valid, errors=len(result.errors))
        return result


class PlaceValidator:
    """Comprehensive validator for place data."""
    
    @staticmethod
    def validate_place_data(place_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate complete place data.
        
        Args:
            place_data: Dictionary containing place information
            
        Returns:
            ValidationResult: Comprehensive validation result
        """
        logger.debug("Starting comprehensive place data validation", 
                    fields=list(place_data.keys()) if place_data else [])
        
        if not place_data:
            result = ValidationResult(is_valid=False, errors=["No place data provided"], 
                                   warnings=[], field_errors={})
            return result
        
        # Initialize combined result
        combined_result = ValidationResult(is_valid=True, errors=[], warnings=[], field_errors={})
        
        # Check required fields
        missing_fields = []
        for field in validation_config.required_fields:
            if field not in place_data or not place_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            for field in missing_fields:
                combined_result.add_error(f"Required field '{field}' is missing", field)
        
        # Validate individual fields if present
        validators = {
            'name': TextValidator.validate_name,
            'address': TextValidator.validate_address,
            'types': TextValidator.validate_types,
            'pincode': PincodeValidator.validate_pincode,
        }
        
        for field, validator in validators.items():
            if field in place_data and place_data[field]:
                field_result = validator(place_data[field])
                combined_result.errors.extend(field_result.errors)
                combined_result.warnings.extend(field_result.warnings)
                combined_result.field_errors.update(field_result.field_errors)
                if not field_result.is_valid:
                    combined_result.is_valid = False
        
        # Validate coordinates if both are present
        if 'latitude' in place_data and 'longitude' in place_data:
            coord_result = CoordinateValidator.validate_coordinates(
                place_data['latitude'], 
                place_data['longitude']
            )
            combined_result.errors.extend(coord_result.errors)
            combined_result.warnings.extend(coord_result.warnings)
            combined_result.field_errors.update(coord_result.field_errors)
            if not coord_result.is_valid:
                combined_result.is_valid = False
        
        logger.debug("Place data validation completed", 
                    is_valid=combined_result.is_valid,
                    total_errors=len(combined_result.errors),
                    total_warnings=len(combined_result.warnings))
        
        return combined_result


# Convenience functions for backward compatibility
def validate_coordinates(lat: Union[str, int, float], lon: Union[str, int, float]) -> bool:
    """
    Simple coordinate validation function for backward compatibility.
    
    Args:
        lat: Latitude value
        lon: Longitude value
        
    Returns:
        bool: True if coordinates are valid
    """
    logger.debug("Using legacy coordinate validation", latitude=lat, longitude=lon)
    result = CoordinateValidator.validate_coordinates(lat, lon)
    return result.is_valid


def validate_pincode(pincode: str) -> bool:
    """
    Simple pincode validation function for backward compatibility.
    
    Args:
        pincode: Pincode to validate
        
    Returns:
        bool: True if pincode is valid
    """
    logger.debug("Using legacy pincode validation", pincode=pincode)
    result = PincodeValidator.validate_pincode(pincode)
    return result.is_valid


# Export all validation classes and functions
__all__ = [
    'ValidationResult',
    'CoordinateValidator',
    'TextValidator', 
    'PincodeValidator',
    'PlaceValidator',
    'validate_coordinates',
    'validate_pincode'
]
