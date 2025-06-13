from flask import Blueprint, request, jsonify, current_app
from utils.validators import validate_content, validate_yeet_id, validate_user_id, sanitize_input
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

yeet_check_bp = Blueprint('yeet_check', __name__)

@yeet_check_bp.route('/check', methods=['POST'])
def check_yeet_toxicity():
    """
    Check if a yeet (post) content is toxic
    
    Request body:
    {
        "content": "The text content to check",
        "yeet_id": "optional_yeet_id",
        "user_id": "optional_user_id"
    }
    
    Response:
    {
        "is_toxic": boolean,
        "confidence": float,
        "toxicity_score": float,
        "categories": ["category1", "category2"],
        "yeet_id": "yeet_id",
        "timestamp": "ISO timestamp"
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Check required fields
        if 'content' not in data:
            return jsonify({
                'error': 'Missing required field: content'
            }), 400
        
        content = sanitize_input(data['content'])
        yeet_id = data.get('yeet_id', None)
        user_id = data.get('user_id', None)
        
        # Validate content
        content_validation = validate_content(content)
        if not content_validation['valid']:
            return jsonify({
                'error': content_validation['error']
            }), 400
        
        # Validate IDs
        if not validate_yeet_id(yeet_id):
            return jsonify({
                'error': 'Invalid yeet_id format'
            }), 400
        
        if not validate_user_id(user_id):
            return jsonify({
                'error': 'Invalid user_id format'
            }), 400
        
        # Get toxicity detector from app config
        toxicity_detector = current_app.config['TOXICITY_DETECTOR']
        
        # Check toxicity
        logger.info(f"Checking toxicity for content: {content[:50]}...")
        result = toxicity_detector.check_toxicity(content)
        
        # Add metadata
        result['yeet_id'] = yeet_id
        result['user_id'] = user_id
        
        # Log result
        logger.info(f"Toxicity check result - Toxic: {result['is_toxic']}, Score: {result['toxicity_score']:.3f}")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error checking toxicity: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to check content toxicity'
        }), 500

@yeet_check_bp.route('/batch', methods=['POST'])
def check_batch_toxicity():
    """
    Check toxicity for multiple yeets at once
    
    Request body:
    {
        "yeets": [
            {
                "content": "text1",
                "yeet_id": "id1",
                "user_id": "user1"
            },
            {
                "content": "text2", 
                "yeet_id": "id2",
                "user_id": "user2"
            }
        ]
    }
    """
    try:
        # Get toxicity detector from app config
        toxicity_detector = current_app.config['TOXICITY_DETECTOR']
        
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        if 'yeets' not in data or not isinstance(data['yeets'], list):
            return jsonify({
                'error': 'Missing or invalid field: yeets (must be an array)'
            }), 400
        
        yeets = data['yeets']
        
        if len(yeets) == 0:
            return jsonify({
                'error': 'Yeets array cannot be empty'
            }), 400
        
        if len(yeets) > 100:  # Limit batch size
            return jsonify({
                'error': 'Batch size cannot exceed 100 yeets'
            }), 400
        
        results = []
        
        # Get the shared toxicity detector instance
        detector = current_app.config['TOXICITY_DETECTOR']
        
        for i, yeet in enumerate(yeets):
            if 'content' not in yeet:
                results.append({
                    'error': f'Missing content for yeet at index {i}',
                    'yeet_id': yeet.get('yeet_id'),
                    'user_id': yeet.get('user_id')
                })
                continue
            
            try:
                result = detector.check_toxicity(yeet['content'])
                result['yeet_id'] = yeet.get('yeet_id')
                result['user_id'] = yeet.get('user_id')
                results.append(result)
            except Exception as e:
                logger.error(f"Error checking toxicity for yeet {i}: {str(e)}")
                results.append({
                    'error': f'Failed to check toxicity: {str(e)}',
                    'yeet_id': yeet.get('yeet_id'),
                    'user_id': yeet.get('user_id')
                })
        
        return jsonify({
            'results': results,
            'total_processed': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in batch toxicity check: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to process batch toxicity check'
        }), 500