# OLA Maps API Testing Guide

## Overview

The OLA Maps API Testing page provides a comprehensive interface for testing all OLA Maps API endpoints directly from the application. This feature allows you to:

- Test all API endpoints from the Postman collections
- Customize request parameters
- View real-time responses
- Track test results and performance metrics
- Manage API credentials

## Features

### 🗺️ Dynamic API Coverage

The testing interface dynamically loads API endpoints from Postman collection files:

- **Automatic Detection**: Scans the `OLAMAPSapi/` directory for `.postman_collection.json` files
- **Real-time Loading**: Loads endpoints on-demand from selected collection files
- **Complete Coverage**: Supports all OLA Maps API categories available in your Postman collections
- **Flexible Structure**: Adapts to any Postman collection structure and naming conventions

**Available Collections:**

- Elevation API
- Geocode API  
- Geofencing API
- OLA Map API
- Places API
- Roads API
- Routing APIs
- Tiles API

### 🎯 Three Testing Modes

#### 1. Category View (📋)

- Test all endpoints within a specific API category
- Batch testing with progress tracking
- Quick overview of endpoint configurations

#### 2. Individual Testing (🔍)

- Test specific endpoints with custom parameters
- Real-time parameter customization
- Detailed request/response inspection

#### 3. Test Results (📊)

- View all test results in a centralized dashboard
- Performance metrics and success rates
- Historical test data

## Getting Started

### Accessing the API Testing Page

1. Navigate to the application
2. In the sidebar, select "OLA Maps API Testing" from the navigation menu
3. The API testing interface will load with a collection file selector

### Loading Postman Collections

1. **Select Collection File**: Choose a Postman collection file from the dropdown menu
   - Available files: All `.postman_collection.json` files in the `OLAMAPSapi/` directory
   - Files are automatically detected and listed
2. **Load Collection**: Click "📂 Load Collection" to parse and load the endpoints
3. **View Endpoints**: Once loaded, you can see all API endpoints organized by category

### Configuring API Credentials

Before testing, configure your API credentials in the sidebar:

1. **API Key**: Enter your OLA Maps API key
2. **Bearer Token**: Enter your OLA Maps bearer token

These credentials are used for all API requests and can be updated at any time.

## Usage Guide

### Loading and Testing Collections

1. **Select Collection**: Choose a Postman collection file from the dropdown
2. **Load Collection**: Click "📂 Load Collection" to parse and load endpoints
3. **Select Category**: Choose an API category from the loaded collection
4. **View Endpoints**: See all available endpoints in the selected category
5. **Batch Test**: Click "Test All [Category] Endpoints" to test all endpoints at once
6. **Individual Test**: Click "Test [Endpoint Name]" to test a specific endpoint

### Individual Endpoint Testing

1. **Load Collection**: First load a Postman collection file
2. **Select Endpoint**: Choose a specific endpoint from the dropdown
3. **Review Configuration**: See the endpoint's method, URL, and description
4. **Customize Parameters**: Modify query parameters and body data as needed
5. **Execute Test**: Click "Test Endpoint" to send the request

### Understanding Test Results

Each test result includes:

- **Status**: Success (✅) or Failure (❌)
- **Response Time**: Time taken for the request in milliseconds
- **Status Code**: HTTP response status code
- **Request URL**: The complete URL that was called
- **Response Data**: The actual response from the API

## API Categories and Endpoints

### Tiles API

- **Get Vector Styles**: Retrieve available vector map styles
- **Get Vector Style Detail**: Get detailed information about a specific style
- **Get Static Map**: Generate static map images
- **Get 3D Tiles Tileset**: Access 3D tiles information

### Routing APIs

- **Directions**: Get routing directions between points
- **Directions Basic**: Simplified directions without extra metadata
- **Distance Matrix**: Calculate distances and ETAs between multiple points
- **Route Optimizer**: Optimize routes with multiple waypoints

### Roads API

- **SnapToRoad**: Snap coordinates to nearest road segments
- **NearestRoads**: Find nearest road segments for coordinates
- **SpeedLimits**: Get speed limit information for road segments

### Places API

- **Autocomplete**: Get place suggestions as you type
- **Place Details**: Get detailed information about a specific place
- **Nearby Search**: Find places of a specific type near a location
- **Address Validation**: Validate and parse address components

### Geocode API

- **Forward Geocode**: Convert addresses to coordinates
- **Reverse Geocode**: Convert coordinates to addresses

### Elevation API

- **Single Elevation**: Get elevation for one location
- **Multi Elevation**: Get elevation for multiple locations

### Geofencing API

- **Create Geofence**: Create a new geofence
- **Get Geofence**: Retrieve geofence details
- **Geofence Status**: Check if coordinates are inside a geofence

## Best Practices

### Testing Strategy

1. **Start with Simple Endpoints**: Begin with GET requests that don't require complex parameters
2. **Test Categories**: Use category testing to quickly validate all endpoints in a group
3. **Customize Parameters**: Use individual testing for detailed parameter customization
4. **Monitor Results**: Check the test results tab for performance insights

### Parameter Customization

- **Query Parameters**: Modify URL parameters for different test scenarios
- **Body Parameters**: For POST requests, customize the request body
- **Required Parameters**: Some endpoints require specific parameters (marked in the interface)

### Error Handling

- **Network Errors**: Check your internet connection and API credentials
- **Parameter Errors**: Ensure all required parameters are provided
- **Rate Limiting**: Be aware of API rate limits and test accordingly

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your API key and bearer token are correct
   - Ensure tokens haven't expired
   - Check that credentials have the necessary permissions

2. **Network Errors**
   - Check your internet connection
   - Verify the API endpoint is accessible
   - Try again after a few minutes

3. **Parameter Errors**
   - Review the endpoint documentation
   - Ensure all required parameters are provided
   - Check parameter format and data types

### Getting Help

If you encounter issues:

1. Check the test results for specific error messages
2. Review the API documentation for endpoint requirements
3. Verify your credentials and permissions
4. Contact support if problems persist

## Technical Details

### Architecture

- **Modular Design**: API testing functionality is separated into its own module
- **Dynamic Loading**: Postman collections are loaded and parsed on-demand
- **Session State**: Test results are stored in Streamlit session state
- **Error Handling**: Comprehensive error handling for network and API errors
- **Performance Tracking**: Response times and success rates are tracked

### Postman Collection Parsing

- **Automatic Detection**: Scans for `.postman_collection.json` files in the `OLAMAPSapi/` directory
- **Variable Substitution**: Automatically substitutes Postman variables with actual values
- **URL Parsing**: Extracts API paths from full URLs in Postman collections
- **Parameter Extraction**: Parses query parameters, headers, and body data from Postman format
- **Category Mapping**: Automatically maps collection names to API categories

### Security

- **Credential Management**: API keys and tokens are handled securely
- **Request Validation**: Parameters are validated before sending requests
- **Error Sanitization**: Sensitive information is not exposed in error messages

### Performance

- **Async Testing**: Multiple endpoints can be tested simultaneously
- **Progress Tracking**: Real-time progress indicators for batch tests
- **Result Caching**: Test results are cached in session state for quick access

## Integration with Main Application

The API testing feature is fully integrated with the main Places Management System:

- **Navigation**: Accessible through the main sidebar navigation
- **Consistent UI**: Follows the same design patterns as other pages
- **Error Handling**: Uses the same error handling framework
- **Logging**: Integrated with the application's logging system

## Future Enhancements

Planned improvements for the API testing feature:

1. **Test Suites**: Save and run predefined test configurations
2. **Export Results**: Export test results to various formats
3. **Performance Monitoring**: Track API performance over time
4. **Automated Testing**: Schedule regular API health checks
5. **Advanced Filtering**: Filter and search through test results
6. **Collaboration**: Share test configurations with team members

---

For more information about the OLA Maps API, visit the [official documentation](https://maps.olakrutrim.com/docs).
