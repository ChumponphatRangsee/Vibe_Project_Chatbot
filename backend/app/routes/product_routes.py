from flask import Blueprint, jsonify, request
from app.services.klevu_service import KlevuService

product_bp = Blueprint('products', __name__)
klevu_service = KlevuService() # Create instance, but don't initialize config yet

@product_bp.route('/search', methods=['POST'])
def search_products():
    data = request.get_json()
    query = data.get('query')
    limit = data.get('limit', 10)

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    results = klevu_service.search_products(query, limit)
    if results is None:
        return jsonify({'error': 'Failed to fetch search results'}), 500

    return jsonify(results)

@product_bp.route('/product/<product_id>', methods=['GET'])
def get_product(product_id):
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    product = klevu_service.get_product_details(product_id)
    if product is None:
        return jsonify({'error': 'Failed to fetch product details'}), 500

    return jsonify(product) 