# app.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import logging
# Corrected import filenames to match your project files
from data_manager_class import DataManager
from planning_algorithms_structured import generate_itinerary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Initialize DataManager with the correct data filename
data_manager = DataManager('anime_pilgrimages.json')

@app.route('/')
def index():
    """Serve the frontend HTML page"""
    # This must point to the correct HTML file name.
    return send_from_directory('.', 'Anime.html')

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """
    Get all available cities from the database.
    Returns a list of unique city names with emoji icons.
    """
    try:
        cities = data_manager.get_cities()
        
        # Define city icons (to match frontend design)
        city_icons = {
            'Tokyo': '🗼',
            'Kyoto': '⛩️',
            'Osaka': '🏯',
            'Nara': '🦌',
            'Kamakura': '🌊',
            'Hokkaido': '❄️',
            'Uji': '🍵'
        }
        
        city_data = [
            {'name': city, 'icon': city_icons.get(city, '📍')}
            for city in cities
        ]
        
        return jsonify({
            'success': True,
            'cities': city_data
        })
    except Exception as e:
        logger.error(f"Error fetching cities: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/anime/<city>', methods=['GET'])
def get_anime_by_city(city):
    """
    Get all anime available for a specific city.
    Returns a list of anime with Japanese and English names.
    """
    try:
        anime_list = data_manager.get_anime_by_city(city)
        
        return jsonify({
            'success': True,
            'city': city,
            'anime': anime_list
        })
    except Exception as e:
        logger.error(f"Error fetching anime for {city}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-itinerary', methods=['POST'])
def generate_itinerary_api():
    """
    Generate a personalized itinerary based on user selections.
    
    Expected JSON payload:
    {
        "city": "Tokyo",
        "anime": ["Your Name.", "Jujutsu Kaisen"],
        "style": "balanced"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'city' not in data or 'anime' not in data or 'style' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: city, anime, style'
            }), 400
        
        city = data['city']
        selected_anime = data['anime']
        travel_style = data['style']
        
        # Get locations from data manager
        locations = data_manager.get_locations_for_selection(city, selected_anime)
        
        if not locations:
            return jsonify({
                'success': False,
                'error': f'No locations found for the selected anime in {city}'
            }), 404
        
        # Generate itinerary using planning algorithms
        itinerary = generate_itinerary(
            locations=locations,
            travel_style=travel_style,
            city=city
        )
        
        return jsonify({
            'success': True,
            'itinerary': itinerary
        })
        
    except Exception as e:
        logger.error(f"Error generating itinerary: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify if the server is running."""
    return jsonify({
        'status': 'healthy',
        'message': 'Anime Pilgrimage Planner API is running'
    })

if __name__ == '__main__':
    logger.info("Starting Anime Pilgrimage Planner Backend...")
    app.run(debug=True, host='0.0.0.0', port=8001)

