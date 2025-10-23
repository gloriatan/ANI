from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# --- Constant Definitions ---
BUDGET_MAX_ENTRY_FEE = 0
INTRA_AREA_TRANSPORT_FEE = 150
MAX_SIGHTS_PER_DAY = 5

# Cost estimations based on travel style
DAILY_FOOD_ESTIMATE = {
    'budget': 2000,
    'balanced': 3500,
    'luxury': 6000
}

DAILY_ACCOMMODATION_ESTIMATE = {
    'budget': 5000,
    'balanced': 10000,
    'luxury': 20000
}

# Daily transportation pass caps by city for cost optimization
DAILY_TRANSPORT_PASS_CAPS = {
    "Tokyo": 1600,
    "Kamakura": 650,
    "Osaka": 800,
    "Kyoto": 1100,
    "Nara": 1500,
    "Uji": 1000,
    "Hokkaido": 2000
}

def filter_locations_by_style(locations: List[Dict[str, Any]], travel_style: str) -> List[Dict[str, Any]]:
    """
    Filter locations based on the user's selected travel style.
    - 'budget': Includes only locations with no entry fee.
    - 'luxury': Prioritizes locations with an entry fee, assuming they are premium spots.
    - 'balanced': Includes all locations.
    """
    logger.info(f"Filtering locations for '{travel_style}' style...")
    if not locations:
        logger.warning("No locations were provided for filtering.")
        return []
    
    if travel_style == 'budget':
        filtered = [loc for loc in locations if loc.get('entry_fee', 0) <= BUDGET_MAX_ENTRY_FEE]
        logger.info(f"Original: {len(locations)}, After budget filter: {len(filtered)}")
        return filtered
    elif travel_style == 'luxury':
        # For luxury, prioritize paid attractions
        filtered = [loc for loc in locations if loc.get('entry_fee', 0) > 0]
        # If no paid attractions are found, include all to provide some results
        if not filtered:
            filtered = locations
        logger.info(f"Original: {len(locations)}, After luxury filter: {len(filtered)}")
        return filtered
    
    # 'balanced' style includes all locations
    logger.info(f"'{travel_style}' style includes all {len(locations)} locations.")
    return locations

def area_based_clustering(
    locations: List[Dict[str, Any]], 
    max_sights_per_day: int = MAX_SIGHTS_PER_DAY
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Groups locations by their 'area' to minimize travel time.
    If a single area has more locations than 'max_sights_per_day', it splits them into multiple days.
    """
    logger.info("Performing area-based clustering...")
    if not locations:
        logger.warning("No locations available for clustering.")
        return {}
    
    clusters = {}
    for loc in locations:
        area = loc.get('area', 'Unknown Area')
        if area not in clusters:
            clusters[area] = []
        clusters[area].append(loc)
    
    # Split large clusters if they exceed the daily limit
    final_clusters = {}
    for area, area_locations in clusters.items():
        if len(area_locations) <= max_sights_per_day:
            final_clusters[area] = area_locations
        else:
            for i in range(0, len(area_locations), max_sights_per_day):
                sub_area_name = f"{area} (Part {i//max_sights_per_day + 1})"
                final_clusters[sub_area_name] = area_locations[i:i+max_sights_per_day]
    
    logger.info(f"Created {len(final_clusters)} daily clusters.")
    return final_clusters

def contextualized_budget_simulation(
    clustered_locations: Dict[str, List[Dict[str, Any]]], 
    travel_style: str, 
    city: str,
    include_accommodation: bool = True
) -> Dict[str, Any]:
    """
    Simulates the budget for the entire trip based on the clustered daily plans.
    Calculates costs for transport, entry fees, food, and accommodation.
    Optimizes transport costs using daily passes where applicable.
    """
    logger.info("Performing contextual budget simulation...")
    
    if not clustered_locations:
        return {
            'hasContent': False,
            'message': f"Based on your '{travel_style}' travel style, no suitable locations were found.",
            'days': [], 'totalCost': 0, 'totalEntryFee': 0, 'totalTransportFee': 0,
            'totalFoodCost': 0, 'totalAccommodationCost': 0, 'locationTypes': {}
        }
    
    days, total_cost, total_entry_fee, total_transport_fee, total_food_cost, total_accommodation_cost = [], 0, 0, 0, 0, 0
    location_types = {}
    fare_cap = DAILY_TRANSPORT_PASS_CAPS.get(city)
    
    for day_index, (area, locations) in enumerate(clustered_locations.items(), 1):
        day_entry_fees = sum(loc.get('entry_fee', 0) for loc in locations)
        
        for loc in locations:
            loc_type = loc.get('location_type', 'Other')
            location_types[loc_type] = location_types.get(loc_type, 0) + 1
        
        # Calculate transport costs for the day
        calculated_transport_cost = 0
        if locations:
            anchor_transport_cost = max(loc.get('transport_cost', 0) for loc in locations)
            calculated_transport_cost = anchor_transport_cost + (len(locations) - 1) * INTRA_AREA_TRANSPORT_FEE
        
        # Apply daily pass optimization
        day_transport_cost = calculated_transport_cost
        optimization_note = ""
        if fare_cap and calculated_transport_cost > fare_cap:
            savings = calculated_transport_cost - fare_cap
            day_transport_cost = fare_cap
            optimization_note = f"Optimized with Day Pass (saved ¥{savings})"
        
        # Calculate food and accommodation for the day
        day_food_cost = DAILY_FOOD_ESTIMATE.get(travel_style, DAILY_FOOD_ESTIMATE['balanced'])
        day_accommodation_cost = 0
        # MODIFIED LOGIC: Add accommodation cost if it's a single-day trip OR it's not the last day of a multi-day trip.
        if include_accommodation and (len(clustered_locations) == 1 or day_index < len(clustered_locations)):
            day_accommodation_cost = DAILY_ACCOMMODATION_ESTIMATE.get(travel_style, DAILY_ACCOMMODATION_ESTIMATE['balanced'])
        
        day_total_cost = day_transport_cost + day_entry_fees + day_food_cost + day_accommodation_cost
        
        # Update trip totals
        total_cost += day_total_cost
        total_entry_fee += day_entry_fees
        total_transport_fee += day_transport_cost
        total_food_cost += day_food_cost
        total_accommodation_cost += day_accommodation_cost
        
        days.append({
            'day': day_index, 'area': area, 'locations': locations,
            'totalCost': day_total_cost, 'entryFee': day_entry_fees,
            'transportFee': day_transport_cost, 'foodCost': day_food_cost,
            'accommodationCost': day_accommodation_cost, 'optimizationNote': optimization_note
        })
    
    return {
        'hasContent': True, 'days': days, 'totalCost': total_cost,
        'totalEntryFee': total_entry_fee, 'totalTransportFee': total_transport_fee,
        'totalFoodCost': total_food_cost, 'totalAccommodationCost': total_accommodation_cost,
        'locationTypes': location_types, 'style': travel_style, 'city': city
    }

def generate_itinerary(
    locations: List[Dict[str, Any]], 
    travel_style: str, 
    city: str,
    max_sights_per_day: Optional[int] = None,
    include_accommodation: bool = True
) -> Dict[str, Any]:
    """
    Main function that integrates all planning algorithms to generate a complete itinerary.
    """
    try:
        logger.info("Starting itinerary generation...")
        
        filtered_locations = filter_locations_by_style(locations, travel_style)
        
        clustered_data = area_based_clustering(
            filtered_locations, 
            max_sights_per_day or MAX_SIGHTS_PER_DAY
        )
        
        result = contextualized_budget_simulation(
            clustered_data, travel_style, city, include_accommodation
        )
        
        logger.info("Itinerary generation completed successfully.")
        return result
        
    except Exception as e:
        logger.error(f"Error during itinerary generation: {str(e)}", exc_info=True)
        return {
            'hasContent': False,
            'error': str(e),
            'message': f'An error occurred while generating your itinerary: {str(e)}',
            'days': [], 'totalCost': 0, 'totalEntryFee': 0, 'totalTransportFee': 0, 'locationTypes': {}
        }
