import requests
from flask import current_app

class KlevuService:
    def __init__(self):
        # Initialize configuration attributes to None
        self.store_url = None
        self.api_key = None
        self.rest_auth_key = None
        self.cloud_search_url = None

    def init_app(self, app):
        # Load configuration from the Flask app
        self.store_url = app.config['KLEVU_STORE_URL']
        self.api_key = app.config['KLEVU_API_KEY']
        self.rest_auth_key = app.config['KLEVU_REST_AUTH_KEY']
        self.cloud_search_url = app.config['KLEVU_CLOUD_SEARCH_URL']

    def search_products(self, query, limit=10):
        """
        Search products using Klevu API
        """
        headers = {
            'Authorization': f'Bearer {self.rest_auth_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "query": query,
            "limit": limit,
            "type": "search"
        }

        try:
            response = requests.post(
                f"{self.cloud_search_url}/search",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Klevu API error: {str(e)}")
            return None

    def get_product_details(self, product_id):
        """
        Get detailed information about a specific product
        """
        headers = {
            'Authorization': f'Bearer {self.rest_auth_key}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(
                f"{self.cloud_search_url}/product/{product_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Klevu API error: {str(e)}")
            return None 
