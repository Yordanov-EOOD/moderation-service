import re
import logging
import json
from datetime import datetime
from typing import Dict, List, Tuple
import os
import numpy as np
from scipy.special import expit

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. Falling back to rule-based detection.")

logger = logging.getLogger(__name__)

class ToxicityDetector:
    def __init__(self, use_ml_model=True):
        """
        Initialize the toxicity detector
        
        Args:
            use_ml_model (bool): Whether to use ML model or fall back to rule-based
        """
        self.use_ml_model = use_ml_model and TRANSFORMERS_AVAILABLE
        
        if self.use_ml_model:
            self._initialize_ml_model()
        else:
            self._initialize_rule_based()
    
    def _initialize_ml_model(self):
        """Initialize the ML-based toxicity detection model"""
        try:
            # Get model name from environment variable or use custom model as default
            model_name = os.getenv("MODEL_NAME", "toxicity-model-fast")
            model_cache_dir = os.getenv("MODEL_CACHE_DIR", "./models")
            use_gpu = os.getenv("USE_GPU", "false").lower() == "true"
            
            # Construct the full path to the local model
            model_path = os.path.join(model_cache_dir, model_name)
            
            logger.info(f"Loading toxicity detection model from: {model_path}")
            logger.info(f"Model cache directory: {model_cache_dir}")
            logger.info(f"GPU usage: {use_gpu}")
            
            # Check if local model exists
            if os.path.exists(model_path) and os.path.isdir(model_path):
                logger.info(f"Found local model at {model_path}")
                # Load tokenizer and model from local directory
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
                
                # Load model configuration for threshold and max_length
                config_path = os.path.join(model_path, "model_config.json")
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        config = json.load(f)
                    # Support both flat and nested config formats
                    if "model_info" in config and isinstance(config["model_info"], dict):
                        mi = config["model_info"]
                        self.optimal_threshold = mi.get("optimal_threshold", float(os.getenv("TOXICITY_THRESHOLD", 0.5)))
                        self.max_length = mi.get("max_length", 512)
                    else:
                        self.optimal_threshold = config.get("optimal_threshold", float(os.getenv("TOXICITY_THRESHOLD", 0.5)))
                        self.max_length = config.get("max_length", 512)
                else:
                    self.optimal_threshold = float(os.getenv("TOXICITY_THRESHOLD", 0.5))
                    self.max_length = 512
                self.model_name_loaded = model_name

                # NOTE: Direct inference will be used instead of pipeline
                self.classifier = None
            else:
                logger.warning(f"Local model not found at {model_path}")
                logger.info("Attempting to load from Hugging Face Hub")
                # Fallback to loading from Hugging Face Hub
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=model_cache_dir
                )
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    cache_dir=model_cache_dir
                )
                
                # Create a pipeline for easier inference
                device = 0 if use_gpu and torch.cuda.is_available() else -1
                self.classifier = pipeline(
                    "text-classification",
                    model=self.model,
                    tokenizer=self.tokenizer,
                framework="pt",  # Use PyTorch
                device=device  # Use GPU if available and requested, otherwise CPU
            )
            
            # Define toxicity categories based on model outputs
            self.toxicity_categories = {
                'general_toxicity': 0.5,
                'severe_toxicity': 0.7,
                'obscene': 0.6,
                'threat': 0.8,
                'insult': 0.6,
                'identity_attack': 0.7
            }
            
            logger.info("ML-based toxicity detector initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML model: {str(e)}")
            logger.info("Falling back to rule-based detection")
            self.use_ml_model = False
            self._initialize_rule_based()
    
    def _initialize_rule_based(self):
        """Initialize rule-based toxicity detection as fallback"""
        self.toxic_patterns = [
            # Profanity patterns
            r'\b(fuck|shit|damn|bitch|asshole|bastard)\b',
            r'\b(nigger|faggot|retard|cunt)\b',
            # Hate speech patterns
            r'\b(kill yourself|kys|die)\b',
            r'\b(hate|despise).*(you|him|her|them)\b',
            # Harassment patterns
            r'\b(stupid|idiot|moron|dumb).*(person|people|you)\b',
            # Toxic behavior patterns
            r'\b(spam|troll|harassment)\b',
        ]
        
        # Compile patterns for better performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.toxic_patterns]
        
        # Toxicity categories for rule-based
        self.toxicity_categories = {
            'profanity': [0, 1],
            'hate_speech': [2, 3],
            'harassment': [4, 5],
            'toxic_behavior': [6]
        }
        
        # Severity weights
        self.severity_weights = {
            'profanity': 0.3,
            'hate_speech': 0.9,
            'harassment': 0.7,
            'toxic_behavior': 0.5
        }
        
        logger.info("Rule-based toxicity detector initialized")
    
    def check_toxicity(self, content: str) -> Dict:
        """
        Check if content is toxic using ML model or rule-based approach
        
        Args:
            content (str): The text content to analyze
            
        Returns:
            Dict: Analysis result containing toxicity information
        """
        if not content or not isinstance(content, str):
            raise ValueError("Content must be a non-empty string")
        
        if self.use_ml_model:
            return self._check_toxicity_ml(content)
        else:
            return self._check_toxicity_rule_based(content)
    
    def _check_toxicity_ml(self, content: str) -> Dict:
        """Check toxicity using ML model"""
        try:
            # Clean content for better model performance
            clean_content = self._clean_content_for_ml(content)

            # Direct model inference
            inputs = self.tokenizer(
                clean_content,
                return_tensors='pt',
                truncation=True,
                padding='max_length',
                max_length=getattr(self, 'max_length', 512)
            )
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.model(**inputs).logits
            # Single logit; apply sigmoid
            toxicity_score = float(expit(logits.squeeze().cpu().item()))

            # Ensure score is within valid range [0, 1]
            toxicity_score = max(0.0, min(1.0, toxicity_score))

            # Use threshold from config or default
            toxicity_threshold = getattr(self, 'optimal_threshold', 0.5)
            logger.debug(f"Using toxicity threshold: {toxicity_threshold}")

            # Final toxicity decision based on threshold
            is_toxic = toxicity_score >= toxicity_threshold

            # Calculate confidence based on distance from threshold
            threshold_distance = abs(toxicity_score - toxicity_threshold)
            confidence = min(1.0, max(threshold_distance * 2, 0.0))

            # Combine extremes confidence
            confidence = max(confidence, 1.0 - abs(0.5 - toxicity_score) * 2)

            # Ensure minimum confidence
            if toxicity_score <= 0.1 or toxicity_score >= 0.9:
                confidence = max(confidence, 0.85)
            confidence = min(1.0, confidence)

            # Determine categories heuristically
            categories = self._analyze_toxicity_categories_ml(clean_content, toxicity_score)

            return {
                'is_toxic': is_toxic,
                'toxicity_score': round(toxicity_score, 3),
                'confidence': round(confidence, 3),
                'categories': categories,
                'content_length': len(content),
                'timestamp': datetime.utcnow().isoformat(),
                'detector_version': '2.0.5-ml-fast',
                'model_used': getattr(self, 'model_name_loaded', 'toxicity-model-fast'),
                'threshold_used': toxicity_threshold,
                'raw_score': round(toxicity_score, 4)
            }
        except Exception as e:
            logger.error(f"ML toxicity detection failed: {str(e)}")
            logger.info("Falling back to rule-based detection for this request")
            return self._check_toxicity_rule_based(content)
    
    def _check_toxicity_rule_based(self, content: str) -> Dict:
        """Check toxicity using rule-based approach (fallback)"""
        # Clean and prepare content
        clean_content = self._clean_content(content)
        
        # Check for toxic patterns
        matches = self._find_toxic_patterns(clean_content)
        
        # Calculate toxicity score and determine if toxic
        toxicity_score, categories = self._calculate_toxicity_score(matches)
        is_toxic = toxicity_score > 0.5  # Threshold for toxicity
        
        # Determine confidence based on number and severity of matches
        confidence = min(0.9, 0.3 + (len(matches) * 0.2))
        
        return {
            'is_toxic': is_toxic,
            'toxicity_score': round(toxicity_score, 3),
            'confidence': round(confidence, 3),
            'categories': categories,
            'content_length': len(content),
            'timestamp': datetime.utcnow().isoformat(),
            'detector_version': '1.0.0-rule-based',
            'model_used': 'rule-based-patterns'
        }
    
    def _clean_content_for_ml(self, content: str) -> str:
        """Clean content for ML model processing"""
        # Remove excessive whitespace
        clean = re.sub(r'\s+', ' ', content).strip()
        
        # Remove or replace some special characters that might confuse the model
        clean = re.sub(r'[^\w\s\.\!\?\,\;\:\-\'\"]', ' ', clean)
        
        # Truncate if too long (BERT models have token limits)
        if len(clean) > 512:
            clean = clean[:512]
        
        return clean
    
    def _analyze_toxicity_categories_ml(self, content: str, toxicity_score: float) -> List[str]:
        """Analyze which categories of toxicity are present using additional heuristics"""
        categories = []
        content_lower = content.lower()
        
        # Use keyword-based categorization as supplement to ML model
        if toxicity_score > 0.3:
            # Check for profanity
            profanity_keywords = ['fuck', 'shit', 'damn', 'bitch', 'asshole']
            if any(word in content_lower for word in profanity_keywords):
                categories.append('profanity')
            
            # Check for hate speech
            hate_keywords = ['hate', 'kill', 'die', 'murder']
            if any(word in content_lower for word in hate_keywords):
                categories.append('hate_speech')
            
            # Check for harassment
            harassment_keywords = ['stupid', 'idiot', 'moron', 'loser', 'pathetic']
            if any(word in content_lower for word in harassment_keywords):
                categories.append('harassment')
            
            # Check for threats
            threat_keywords = ['kill you', 'hurt you', 'destroy you', 'eliminate']
            if any(phrase in content_lower for phrase in threat_keywords):
                categories.append('threat')
            
            # If no specific category found but score is high, mark as general toxicity
            if not categories and toxicity_score > 0.6:
                categories.append('general_toxicity')
        
        
        return categories
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content for rule-based analysis"""
        # Convert to lowercase
        clean = content.lower()
        
        # Remove extra whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Handle common obfuscation techniques
        clean = re.sub(r'[4@]', 'a', clean)
        clean = re.sub(r'[3]', 'e', clean)
        clean = re.sub(r'[1!]', 'i', clean)
        clean = re.sub(r'[0]', 'o', clean)
        clean = re.sub(r'[5$]', 's', clean)
        
        # Remove non-alphanumeric except spaces
        clean = re.sub(r'[^a-z0-9\s]', '', clean)
        
        return clean
    
    def _find_toxic_patterns(self, content: str) -> List[Tuple[str, int]]:
        """Find all toxic patterns in content"""
        matches = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            pattern_matches = pattern.findall(content)
            for match in pattern_matches:
                matches.append((match, i))
        
        return matches
    
    def _calculate_toxicity_score(self, matches: List[Tuple[str, int]]) -> Tuple[float, List[str]]:
        """Calculate overall toxicity score and identify categories"""
        if not matches:
            return 0.0, []
        
        category_scores = {}
        identified_categories = set()
        
        # Calculate scores for each category
        for match, pattern_index in matches:
            for category, pattern_indices in self.toxicity_categories.items():
                if pattern_index in pattern_indices:
                    if category not in category_scores:
                        category_scores[category] = 0
                    category_scores[category] += self.severity_weights[category]
                    identified_categories.add(category)
        
        # Calculate overall score (average of category scores, capped at 1.0)
        if category_scores:
            total_score = sum(category_scores.values()) / len(category_scores)
            final_score = min(1.0, total_score)
        else:
            final_score = 0.0
        
        return final_score, sorted(list(identified_categories))
    
    def get_detector_info(self) -> Dict:
        """Get information about the detector"""
        if self.use_ml_model:
            return {
                'detector_type': 'ml_model',
                'version': '2.0.5',
                'model_name': 'toxicity-model-fast',
                'framework': 'transformers',
                'description': 'ML-based toxicity detector using custom-trained DistilBERT regression model'
            }
        else:
            return {
                'detector_type': 'rule_based',
                'version': '1.0.0',
                'total_patterns': len(self.compiled_patterns),
                'categories': list(self.toxicity_categories.keys()),
                'description': 'Rule-based toxicity detector for social media content'
            }