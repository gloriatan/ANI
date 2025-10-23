# data_manager_class.py
import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DataManager:
    """
    DataManager class handles all data operations for the anime pilgrimage database.
    It provides methods to query cities, anime, and locations from the JSON database.
    """
    
    def __init__(self, database_file: str = 'anime_pilgrimages.json'):
        """
        Initializes the DataManager with the path to the database file.
        
        :param database_file: Path to the JSON database file.
        """
        # Use the database_file argument passed to the constructor
        self.database_file = database_file
        self.database = self._load_database()
    
    def _load_database(self) -> List[Dict[str, Any]]:
        """
        Loads and returns the 'pilgrimages' list from the JSON file.
        This method handles potential file reading and JSON parsing errors.
        
        :return: A list of all anime pilgrimage data, or an empty list if an error occurs.
        """
        try:
            with open(self.database_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pilgrimages = data.get("pilgrimages", [])
                logger.info(f"Successfully loaded {len(pilgrimages)} anime entries from the database.")
                return pilgrimages
        except FileNotFoundError:
            logger.error(f"Error: The database file '{self.database_file}' was not found.")
            return []
        except json.JSONDecodeError:
            logger.error(f"Error: Could not parse '{self.database_file}'. Please check the JSON format.")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading the database: {str(e)}")
            return []
    
    def get_cities(self) -> List[str]:
        """
        Gets all unique cities from the database.
        
        :return: A list of unique city names, sorted in a predefined order for a better user experience.
        """
        cities = set()
        for anime in self.database:
            for location in anime.get('locations', []):
                city = location.get('city')
                if city:
                    cities.add(city)
        
        # Sort cities in a predefined order for better UX
        city_order = ['Tokyo', 'Kyoto', 'Osaka', 'Nara', 'Kamakura', 'Hokkaido', 'Uji']
        sorted_cities = [city for city in city_order if city in cities]
        # Add any remaining cities not in the predefined order
        sorted_cities.extend(sorted(list(cities - set(city_order))))
        
        logger.info(f"Found {len(sorted_cities)} unique cities.")
        return sorted_cities
    
    def get_anime_by_city(self, city: str) -> List[Dict[str, str]]:
        """
        Finds all anime that have at least one pilgrimage site in the given city.
        
        :param city: The name of the city to query.
        :return: A list of dictionaries, each containing anime_name, anime_name_en, image_url, and song_url, sorted alphabetically.
        """
        anime_in_city = {}
        
        for anime in self.database:
            anime_name = anime.get("anime_name")
            anime_name_en = anime.get("anime_name_en", "")
            image_url = anime.get("image_url") 
            # --- 修改开始: 获取 song_url ---
            song_url = anime.get("song_url")
            # --- 修改结束 ---
            
            if not anime_name:
                continue
            
            for location in anime.get('locations', []):
                if location.get('city', '').lower() == city.lower():
                    if anime_name not in anime_in_city:
                        anime_in_city[anime_name] = {
                            'anime_name': anime_name,
                            'anime_name_en': anime_name_en,
                            'image_url': image_url,
                            'song_url': song_url
                        }
                    break
        
        result = sorted(list(anime_in_city.values()), key=lambda x: x['anime_name'])
        
        logger.info(f"Found {len(result)} anime for city '{city}'.")
        return result
    
    def get_locations_for_selection(
        self, 
        city: str, 
        selected_anime_titles: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extracts all relevant location details based on the user's selected city and anime titles.
        
        :param city: The city selected by the user.
        :param selected_anime_titles: A list of anime titles selected by the user.
        :return: A list of location dictionaries, each enhanced with source anime information.
        """
        final_locations = []
        selected_anime_set = set(selected_anime_titles)
        
        for anime in self.database:
            anime_name = anime.get("anime_name")
            anime_name_en = anime.get("anime_name_en", "")
            
            if anime_name in selected_anime_set:
                for location in anime.get('locations', []):
                    if location.get('city', '').lower() == city.lower():
                        location_with_source = location.copy()
                        location_with_source['source_anime'] = anime_name
                        location_with_source['source_anime_en'] = anime_name_en
                        final_locations.append(location_with_source)
        
        logger.info(f"Found {len(final_locations)} locations for {len(selected_anime_titles)} anime in {city}.")
        return final_locations