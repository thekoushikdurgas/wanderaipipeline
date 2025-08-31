# Nearby Search API Section - Add Place Page

## Overview

A new API testing section has been added to the "Add New Place" page that allows users to test the OLA Maps Places API "4) Nearby Search - GET" endpoint with dynamic parameters and view real-time results.

## Features

### 🔍 API Testing Interface

The section provides a comprehensive interface for testing the Nearby Search API:

- **Dynamic Parameter Configuration**: Users can modify all API parameters in real-time
- **Real-time API Testing**: Execute API calls and view results immediately
- **Comprehensive Results Display**: View request details, response data, and performance metrics
- **User-friendly Interface**: Clean, organized layout with helpful tooltips

### 📍 Parameter Configuration

The interface allows users to configure the following parameters:

#### Location Parameters

- **Location (lat,lng)**: Latitude and longitude coordinates (default: Bangalore airport coordinates)
- **Radius**: Search radius in meters (100-50,000m, default: 10,000m)

#### Search Parameters

- **Types**: Place types to search for (e.g., restaurant, hotel, tourist_attraction)
- **Rank By**: How to rank results (popular, distance, rating)

### 📊 Results Display

When an API call is executed, the interface displays:

#### Request Information

- HTTP method and URL
- Status code and response time
- Complete request configuration

#### Response Data

- Raw JSON response
- Parsed place information in a table format
- Summary of found places with key details

#### Error Handling

- Clear error messages for failed requests
- Validation of input parameters
- Graceful handling of API errors

## Technical Implementation

### Integration

The API testing section is integrated into the `render_add_place_page` function in `app.py`:

```python
def render_add_place_page(place_ops: PlaceOperations):
    """Render the add new place page."""
    # ... existing form code ...
    
    # Add API Testing Section for Nearby Search
    st.markdown("---")
    st.header("🔍 API Testing - Nearby Search")
    # ... API testing implementation ...
```

### Dependencies

The implementation uses:

- `OLAMapsAPITester` from `api_testing.ola_maps_api_tester`
- Streamlit components for UI
- JSON parsing for response handling
- Error handling and logging

### API Configuration

The section uses the following API configuration:

- **Base URL**: `https://api.olamaps.io`
- **Endpoint**: `/places/v1/nearbysearch`
- **Method**: GET
- **Authentication**: Bearer token and API key

## Usage Guide

### Accessing the Feature

1. Navigate to the application
2. Select "Add New Place" from the sidebar
3. Scroll down to the "🔍 API Testing - Nearby Search" section

### Testing the API

1. **Configure Parameters**:
   - Enter location coordinates (latitude,longitude)
   - Set search radius
   - Choose place types
   - Select ranking method

2. **Execute Test**:
   - Click "🚀 Test Nearby Search API" button
   - Wait for the API call to complete

3. **View Results**:
   - Check request details and status
   - Review response data
   - Examine found places in the table

### Example Use Cases

#### Finding Restaurants

- **Location**: `12.931544865377818,77.61638622280486` (Bangalore airport)
- **Types**: `restaurant`
- **Radius**: `5000`
- **Rank By**: `popular`

#### Finding Tourist Attractions

- **Location**: `12.9716,77.5946` (Bangalore city center)
- **Types**: `tourist_attraction`
- **Radius**: `10000`
- **Rank By**: `rating`

## Benefits

### For Users

- **Real-time Testing**: Test API endpoints without leaving the application
- **Parameter Experimentation**: Try different parameters to understand API behavior
- **Learning Tool**: Understand how the Nearby Search API works
- **Validation**: Verify API responses before implementing in code

### For Developers

- **Debugging**: Quickly test API calls during development
- **Documentation**: See actual API responses and behavior
- **Integration Testing**: Verify API integration works correctly
- **Performance Monitoring**: Track response times and success rates

## Error Handling 1

The section includes comprehensive error handling:

- **Collection Loading Errors**: Graceful handling if Postman collection can't be loaded
- **API Call Errors**: Clear error messages for failed requests
- **Parameter Validation**: Validation of input parameters
- **Response Parsing**: Safe handling of malformed responses

## Future Enhancements

Potential improvements for the feature:

1. **Save Test Results**: Allow users to save and compare test results
2. **Batch Testing**: Test multiple parameter combinations at once
3. **Export Results**: Export API responses to various formats
4. **Historical Data**: Track API performance over time
5. **Custom Endpoints**: Support for testing other API endpoints

## Technical Notes

- The section uses the existing `OLAMapsAPITester` infrastructure
- API credentials are loaded from the tester configuration
- Response data is parsed and displayed in a user-friendly format
- The interface is responsive and works on different screen sizes
- All API calls include proper timeout and error handling
