# Anime Pilgrimage Planner - Complete Deployment Guide

## Project Structure

```
anime-pilgrimage-planner/
├── flask_backend.py           # Flask backend main application
├── data_manager_class.py      # Data querying module
├── planning_algorithms_structured.py # Itinerary planning algorithms
├── anime_pilgrimages.json     # Anime pilgrimage database (sole data source)
├── Anime.html                 # Frontend interface
├── requirements.txt           # Python dependencies
└── README.md                  # This document
```

## Quick Start

### Step 1: Environment Setup

Ensure your system has the following installed:

  * Python 3.8+
  * A modern web browser (Chrome, Firefox, Edge, etc.)

### Step 2: Install Dependencies

In the project's root directory, execute the following:

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Start the Backend Service

```bash
python flask_backend.py
```

Once started successfully, you will see output similar to the following, on **port 8000**:

```
* Running on http://0.0.0.0:8000
```

### Step 4: Access the Frontend Interface

Open the `Anime.html` file directly in your browser to access the application.

> Note: Due to security policies, some browsers may restrict local files from making network requests (Fetch API). The recommended way is to serve `Anime.html` via a simple HTTP server or access it through the backend.

## System Architecture

### Data Flow

1.  **User Action (Frontend `Anime.html`)**: The user selects a city, travel style, and anime in the browser.
2.  **Fetch API Request**: The browser sends an asynchronous HTTP request to the backend (e.g., to get an anime list, or submit a generation request).
3.  **Flask Backend Receives (`flask_backend.py`)**: The backend API endpoint receives the request.
4.  **Query Data (`data_manager_class.py`)**: The `DataManager` class retrieves the required location data from the `anime_pilgrimages.json` file.
5.  **Generate Itinerary (`planning_algorithms_structured.py`)**: The queried data is passed to the planning algorithm module for filtering, clustering, and budget simulation based on the user's selected style.
6.  **Return JSON Result**: The backend packages the generated itinerary data into JSON format and returns it to the frontend.
7.  **Frontend Rendering (`Anime.html`)**: JavaScript parses the returned JSON data, dynamically generates daily itinerary cards, and renders cost analysis charts using Chart.js.

### API Endpoints

#### 1\. Get All Cities

  * **Endpoint**: `GET /api/cities`
  * **Description**: Retrieves a list of all available cities for display on the frontend.
  * **Example Response**:
    ```json
    {
      "success": true,
      "cities": [
        {"name": "Tokyo", "icon": "🗼"},
        {"name": "Kyoto", "icon": "⛩️"},
        {"name": "Osaka", "icon": "🏯"}
      ]
    }
    ```

#### 2\. Get Anime List by City

  * **Endpoint**: `GET /api/anime/<city>`
  * **Description**: Retrieves a list of anime that have pilgrimage locations in the specified city.
  * **Example Request**: `GET /api/anime/Tokyo`
  * **Example Response**:
    ```json
    {
        "success": true,
        "city": "Tokyo",
        "anime": [
            {
                "anime_name": "君の名は。",
                "anime_name_en": "Your Name."
            },
            {
                "anime_name": "呪術廻戦",
                "anime_name_en": "Jujutsu Kaisen"
            }
        ]
    }
    ```

#### 3\. Generate Personalized Itinerary

  * **Endpoint**: `POST /api/generate-itinerary`
  * **Description**: Receives the user's selected city, anime, and travel style to generate a detailed, personalized itinerary plan.
  * **Request Body**:
    ```json
    {
        "city": "Tokyo",
        "anime": ["君の名は。", "呪術廻戦"],
        "style": "balanced"
    }
    ```
  * **Example Response**:
    ```json
    {
        "success": true,
        "itinerary": {
            "hasContent": true,
            "days": [...],
            "totalCost": 28600,
            "totalEntryFee": 0,
            "totalTransportFee": 350,
            "totalFoodCost": 7000,
            "totalAccommodationCost": 20000,
            "locationTypes": {
                "Outdoor Attraction": 1,
                "Commercial Area": 1
            },
            "style": "balanced",
            "city": "Tokyo"
        }
    }
    ```

## User Flow

1.  **Select City**: Click on the Japanese city you plan to visit (e.g., Tokyo, Kyoto).
2.  **Select Travel Style**:
      * `「節約」 Budget`: Includes only free pilgrimage locations.
      * `「標準」 Balanced`: Includes all locations, providing the most comprehensive options.
      * `「豪華」 Luxury`: Prioritizes paid attractions that require an entry fee.
3.  **Select Anime**: In the list that appears below the city, select one or more anime series you wish to make a pilgrimage for.
4.  **Generate Itinerary**: Click the “🌸 Generate My Itinerary” button.
5.  **View Results**: The page will scroll to the results section, displaying:
      * Detailed daily itineraries, including locations, costs, and route optimization notes.
      * A cost composition analysis chart (doughnut chart).
      * A location type distribution chart (bar chart).

## Core Features

  * **Intelligent Budget Optimization**
    Based on the selected city, the system automatically compares the cumulative cost of single-trip transit fares for the day with the price cap of that city's "One-Day Pass." If the total for single tickets exceeds the pass price, the system will automatically calculate the cost using the pass price and highlight the amount saved in the itinerary.

  * **Area-based Grouping**
    The algorithm automatically schedules pilgrimage spots that are geographically in the same "area" for the same day. This effectively reduces cross-district travel, saving time and transportation costs. If an area has too many locations, it will be automatically split into a multi-day plan.

  * **Multi-dimensional Cost Analysis**
    The generated itinerary cost is a comprehensive estimate that includes:

      * **Entry Fees**: The actual ticket price for each attraction.
      * **Transportation Fees**: The daily transit cost after intelligent optimization.
      * **Food Budget**: A daily estimate that varies based on the "Budget," "Balanced," and "Luxury" travel styles.
      * **Accommodation Budget**: Also estimated based on travel style; accommodation is not calculated for the last day of the trip.

## Data Management

### Data Source

All pilgrimage location data in this project is sourced from a single JSON file: `anime_pilgrimages.json`.

### Data Structure Example

```json
{
  "pilgrimages": [
    {
      "anime_name": "君の名は。",
      "anime_name_en": "Your Name.",
      "locations": [
        {
          "name": "須賀神社 階段 | Suga Shrine Stairs",
          "city": "Tokyo",
          "area": "Shinjuku Ward",
          "transport_cost": 200,
          "entry_fee": 0,
          "location_type": "Outdoor Attraction",
          "description": "The place where Mitsuha and Taki meet across time and space..."
        }
      ]
    }
  ]
}
```

### Adding New Data

To add new anime or pilgrimage locations:

1.  Directly edit the `anime_pilgrimages.json` file.
2.  Follow the existing data structure to add a new anime object or add new `locations` to an existing anime.
3.  Restart the `flask_backend.py` service; the system will automatically reload the latest data.
4.  Refresh the `Anime.html` page in your browser to see the updates.

> **Note**: Please ensure your additions follow strict JSON format, otherwise the application will fail to start.

## FAQ

  * **Q1: The frontend shows "Failed to load anime" or "Failed to generate itinerary."**

      * **Cause**: The frontend cannot connect to the backend service.
      * **Solution**:
        1.  **Check if the backend is running**: Make sure the `flask_backend.py` script is running and has not thrown any errors.
        2.  **Check the port**: This project's backend runs on port **8000**. Ensure this port is not in use by another application.
        3.  **Modify code**: If you need to change the port, you must update it in two places:
              * In `flask_backend.py`: `app.run(..., port=new_port)`
              * In the JavaScript section of `Anime.html`: `apiBaseUrl: 'http://localhost:new_port'`

  * **Q2: A CORS error appears in the browser console.**

      * **Cause**: The browser's Cross-Origin Resource Sharing policy is blocking the request.
      * **Solution**: The `flask_backend.py` in this project is already configured with `CORS(app)` via the `flask-cors` plugin, which should prevent this issue. Please ensure `flask-cors` has been installed successfully.

  * **Q3: The charts in the itinerary results do not display.**

      * **Cause**: The Chart.js library failed to load correctly.
      * **Solution**:
        1.  **Check your internet connection**: The chart library is loaded from a CDN, which requires a working internet connection.
        2.  **Check the CDN link**: Ensure the `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>` link in `Anime.html` is accessible.

  * **Q4: The itinerary generation result shows "No Results Found."**

      * **Cause**:
        1.  Your selected travel style has filtered out all available locations (e.g., selecting "Budget" style when the chosen anime has no free pilgrimage spots in that city).
        2.  The `anime_pilgrimages.json` database genuinely contains no location data for your selected anime in the specified city.
      * **Solution**:
        1.  Try changing the travel style to `「標準」 Balanced`, which includes all locations.
        2.  Try selecting a different combination of anime or cities.

### Testing Suggestions

#### Unit Tests

  * **Test the Data Manager**:
    You can run the `data_manager_class.py` script directly to verify that data loading and querying functions work correctly.
    ```bash
    python data_manager_class.py
    ```
      * **Expected Output**:
        ```
        === Test 1: Get All Cities ===
        Available cities: ['Tokyo', 'Kyoto', ...]
        === Test 2: Get Anime for Tokyo ===
        Found 14 anime in Tokyo:
        - 君の名は。(Your Name.)
        ...
        ```

#### API Endpoint Tests

  * You can use `curl` or a similar tool to test if the backend API endpoints are working as expected. Ensure the backend service is running first.
    ```bash
    # Test health check
    curl http://localhost:8000/api/health

    # Test get cities
    curl http://localhost:8000/api/cities

    # Test get anime for Tokyo
    curl http://localhost:8000/api/anime/Tokyo
    ```

#### Integration Tests

  * **Full User Flow Test**:
    1.  Open `Anime.html` in a browser and open the developer tools (F12).
    2.  Switch to the "Network" tab.
    3.  Perform the sequence of actions: Select City → Select Anime → Generate Itinerary.
    4.  Observe the API requests in the "Network" tab to ensure they succeed (Status code 200).

### Performance Optimization Suggestions

#### Backend Optimization

  * **Server-side Caching**: For data that does not change often, like the city and anime lists, consider using a library like Flask-Caching to add a server-side cache. This will reduce redundant file reads and computations.
  * **Asynchronous Processing**: If the itinerary generation algorithm becomes very complex, consider converting it to an asynchronous task using Celery. This will prevent long-running operations from blocking API requests.

#### Frontend Optimization

  * **Lazy Loading**: When the anime list for a city is very long, implement virtual scrolling or lazy loading to improve rendering performance.
  * **Debouncing**: When a user rapidly changes selections (like checking anime boxes), debounce the "Generate" button's click event or related API calls to prevent sending redundant requests.

#### Database Optimization

  * **Indexing**: If the data volume grows and is migrated to a database like PostgreSQL or MongoDB in the future, you should add indexes to frequently queried fields like `city` and `anime_name`.
  * **Data Compression**: If the `anime_pilgrimages.json` file becomes very large, consider using gzip compression for server responses to reduce network payload size.

### Production Deployment

#### Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Start the service (e.g., with 4 worker processes), making sure to use the correct port and entry point
gunicorn -w 4 -b 0.0.0.0:8000 flask_backend:app
```

#### Using Nginx as a Reverse Proxy

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        # Make sure to use the correct port
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Docker Deployment

  * **Dockerfile**:
    ```dockerfile
    FROM python:3.10-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    # Make sure to use the correct port and entry point
    EXPOSE 8000
    CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "flask_backend:app"]
    ```
  * **Build and Run**:
    ```bash
    docker build -t anime-planner .
    # Make sure to use the correct port mapping
    docker run -p 8000:8000 anime-planner
    ```

### License & Contribution

#### Data Sources

  * Anime data is compiled from publicly available information.
  * Transportation fees and ticket prices are reference values for 2025.

#### Contribution Guide

Pull requests to add new anime pilgrimage data are welcome\!

  * **Requirements**:
    1.  Ensure correct JSON format.
    2.  Provide accurate location names and descriptions.
    3.  Cite data sources (Optional).

### Technical Support

Encounter a problem? You can:

1.  Check the "FAQ" section of this document.

2.  **Check the browser developer console and backend service console logs (Simulated Example)**.

      * **Scenario**: The itinerary generation fails. First, press `F12` to open the browser's developer tools.
      * **Browser-side (Network Tab)**: You might see a request record in red with a status of `500 Internal Server Error`. This indicates a server-side error occurred.
        ```
        Request URL: http://localhost:8000/api/generate-itinerary
        Request Method: POST
        Status Code: 500 Internal Server Error
        ```
      * **Backend Service Console**: Now, check the terminal window where `flask_backend.py` is running. You will likely see a detailed Python traceback, which can pinpoint the problem.
        ```
        ERROR: Exception on /api/generate-itinerary [POST]
        Traceback (most recent call last):
          File "/path/to/venv/lib/python3.10/site-packages/flask/app.py", line 1478, in wsgi_app
            response = self.full_dispatch_request()
        ...
          File "/path/to/anime-pilgrimage-planner/planning_algorithms_structured.py", line 89, in area_based_clustering
            area = loc.get('areaa', 'Unknown Area') # <- Hypothetical typo 'areaa'
        KeyError: 'areaa'
        ```
      * **Conclusion**: By comparing the frontend and backend logs, you can quickly determine that the problem is a `KeyError` in the backend code, caused by a typo where `area` was misspelled as `areaa`.

3.  ## **Submit a GitHub Issue (with repository) (Simulated Example)**. If you cannot solve the problem yourself, feel free to submit a clear issue.

      * **Repository URL**: `https://github.com/your-username/anime-pilgrimage-planner`

      * **Issue Title**: `Bug: Application crashes when generating itinerary for Kyoto with "Luxury" style`

      * **Issue Body**:

        **Bug Description**
        When selecting "Kyoto" as the city and "Luxury" as the travel style, and choosing any anime (e.g., "Detective Conan"), clicking the generate button causes a frontend error and the backend service logs an exception.

        **Steps to Reproduce**

        1.  Start the backend service with `python flask_backend.py`.
        2.  Open `Anime.html` in a browser.
        3.  Click the "Kyoto" city button.
        4.  Click the "「豪華」 Luxury" travel style button.
        5.  Check the "名探偵コナン" (Detective Conan) anime.
        6.  Click the "🌸 Generate My Itinerary" button.
        7.  Observe the error.

        **Expected Behavior**
        A valid itinerary for "Detective Conan" featuring paid attractions in Kyoto should be successfully generated and displayed.

        **Actual Behavior**
        The frontend shows an error message: “Failed to generate itinerary: ...”. The browser's developer console shows that the request to `/api/generate-itinerary` returned a 500 error. The backend log shows a `TypeError: '>' not supported between instances of 'NoneType' and 'int'`.

        **My Environment**

          * OS: macOS Sonoma
          * Browser: Chrome 125.0
          * Python Version: 3.11.2

### Get Started

You are now ready to use this tool to plan your anime pilgrimage journey\!

```bash
# Start with one command
python flask_backend.py
```

Then, open the `Anime.html` file or visit the configured URL (e.g., `http://localhost:8000`) to begin your journey\!
