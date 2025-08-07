from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Any
import numpy as np
import re

class AccuracyMetric:
    """
    Measures factual accuracy of generated responses against reference
    """
    
    def __init__(self):
        self.name = "Accuracy"
        self.description = "Measures factual correctness of the generated response"
        self.dependencies = ["Reference_Response", "Generated_Response"]
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            self.model = None
    
    def calculate(self, reference: str, generated: str, **kwargs) -> Dict[str, Any]:
        """
        Calculate accuracy score with detailed factual analysis
        
        Args:
            reference: Reference response text
            generated: Generated response text
            
        Returns:
            Dict containing score and detailed remarks
        """
        try:
            if not reference.strip() or not generated.strip():
                return {
                    'score': 0.0,
                    'remarks': 'Empty reference or generated text'
                }
            
            # Calculate multiple accuracy indicators
            semantic_score = self._calculate_semantic_accuracy(reference, generated)
            content_score = self._calculate_content_accuracy(reference, generated)
            factual_score = self._calculate_factual_consistency(reference, generated)
            entity_score = self._calculate_entity_accuracy(reference, generated)
            
            # Weighted combination
            accuracy_score = (semantic_score * 0.3 + content_score * 0.3 + factual_score * 0.2 + entity_score * 0.2)
            
            # Calculate detailed metrics
            detailed_metrics = self._calculate_detailed_metrics(reference, generated, semantic_score, content_score, factual_score, entity_score)
            
            # Generate detailed remarks
            remarks = self._generate_detailed_remarks(
                accuracy_score, semantic_score, content_score, factual_score, entity_score, detailed_metrics, reference, generated
            )
            
            return {
                'score': accuracy_score,
                'remarks': remarks,
                'detailed_scores': {
                    'semantic_accuracy': semantic_score,
                    'content_accuracy': content_score,
                    'factual_consistency': factual_score,
                    'entity_accuracy': entity_score
                }
            }
            
        except Exception as e:
            return {
                'score': 0.0,
                'remarks': f'Error calculating accuracy: {str(e)}'
            }
    
    def _calculate_semantic_accuracy(self, reference: str, generated: str) -> float:
        """
        Calculate semantic accuracy using sentence embeddings
        """
        if self.model is None:
            return 0.5  # Fallback score
        
        try:
            ref_embedding = self.model.encode([reference])
            gen_embedding = self.model.encode([generated])
            similarity = cosine_similarity(ref_embedding, gen_embedding)[0][0]
            return max(0.0, min(1.0, similarity))
        except Exception:
            return 0.5
    
    def _calculate_content_accuracy(self, reference: str, generated: str) -> float:
        """
        Calculate content accuracy based on key information overlap
        """
        ref_entities = self._extract_key_entities(reference)
        gen_entities = self._extract_key_entities(generated)
        
        if not ref_entities:
            return 1.0 if not gen_entities else 0.8
        
        common_entities = ref_entities & gen_entities
        accuracy = len(common_entities) / len(ref_entities) if ref_entities else 0.0
        
        # Penalize for incorrect entities
        incorrect_entities = gen_entities - ref_entities
        penalty = len(incorrect_entities) * 0.1
        
        return max(0.0, min(1.0, accuracy - penalty))
    
    def _calculate_factual_consistency(self, reference: str, generated: str) -> float:
        """
        Calculate factual consistency score
        """
        ref_words = set(self._normalize_text(reference).split())
        gen_words = set(self._normalize_text(generated).split())
        
        if not ref_words:
            return 1.0
        
        overlap = len(ref_words & gen_words) / len(ref_words)
        
        # Bonus for maintaining key factual indicators
        factual_indicators = {'is', 'are', 'was', 'were', 'has', 'have', 'will', 'would', 'can', 'cannot'}
        ref_indicators = ref_words & factual_indicators
        gen_indicators = gen_words & factual_indicators
        
        if ref_indicators:
            indicator_overlap = len(ref_indicators & gen_indicators) / len(ref_indicators)
            overlap = (overlap + indicator_overlap) / 2
        
        return max(0.0, min(1.0, overlap))
    
    def _calculate_entity_accuracy(self, reference: str, generated: str) -> float:
        """
        Calculate accuracy of specific entities (numbers, dates, names)
        """
        ref_entities = self._extract_key_entities(reference)
        gen_entities = self._extract_key_entities(generated)
        
        if not ref_entities:
            return 1.0
        
        # Calculate precision and recall for entities
        correct_entities = ref_entities & gen_entities
        precision = len(correct_entities) / len(gen_entities) if gen_entities else 0.0
        recall = len(correct_entities) / len(ref_entities) if ref_entities else 0.0
        
        # F1 score for entity accuracy
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0
        
        return f1
    
    def _calculate_detailed_metrics(self, reference: str, generated: str, semantic_score: float, 
                                  content_score: float, factual_score: float, entity_score: float) -> Dict[str, Any]:
        """
        Calculate additional detailed metrics for analysis
        """
        metrics = {}
        
        # Text statistics
        ref_words = reference.split()
        gen_words = generated.split()
        metrics['ref_word_count'] = len(ref_words)
        metrics['gen_word_count'] = len(gen_words)
        metrics['word_ratio'] = len(gen_words) / len(ref_words) if len(ref_words) > 0 else 0
        
        # Entity analysis
        ref_entities = self._extract_key_entities(reference)
        gen_entities = self._extract_key_entities(generated)
        metrics['ref_entity_count'] = len(ref_entities)
        metrics['gen_entity_count'] = len(gen_entities)
        metrics['common_entities'] = len(ref_entities & gen_entities)
        metrics['missing_entities'] = len(ref_entities - gen_entities)
        metrics['extra_entities'] = len(gen_entities - ref_entities)
        
        # Accuracy components
        metrics['semantic_accuracy'] = semantic_score
        metrics['content_accuracy'] = content_score
        metrics['factual_consistency'] = factual_score
        metrics['entity_accuracy'] = entity_score
        
        return metrics
    
    def _extract_key_entities(self, text: str) -> set:
        """
        Extract key entities from text (numbers, dates, proper nouns)
        """
        entities = set()
        
        # Numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        entities.update(numbers)
        
        # Dates
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
        entities.update(dates)
        
        # Years
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        entities.update(years)
        
        # Capitalized words (potential proper nouns)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
        entities.update(proper_nouns)
        
        return entities
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison
        """
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _generate_detailed_remarks(self, overall_score: float, semantic_score: float, 
                                 content_score: float, factual_score: float, entity_score: float,
                                 metrics: Dict[str, Any], reference: str, generated: str) -> str:
        """
        Generate comprehensive explanatory remarks for accuracy score
        """
        remarks = []
        
        # Main score with percentage
        remarks.append(f"Accuracy Score: {overall_score * 100:.2f}%")
        
        # Component breakdown
        remarks.append(f"Component Breakdown:")
        remarks.append(f"  • Semantic Accuracy: {semantic_score * 100:.2f}%")
        remarks.append(f"  • Content Accuracy: {content_score * 100:.2f}%")
        remarks.append(f"  • Factual Consistency: {factual_score * 100:.2f}%")
        remarks.append(f"  • Entity Accuracy: {entity_score * 100:.2f}%")
        
        # Text statistics
        remarks.append(f"Text Analysis:")
        remarks.append(f"  • Reference: {metrics['ref_word_count']} words, {metrics['ref_entity_count']} entities")
        remarks.append(f"  • Generated: {metrics['gen_word_count']} words, {metrics['gen_entity_count']} entities")
        remarks.append(f"  • Word ratio: {metrics['word_ratio']:.2f}")
        
        # Entity analysis
        remarks.append(f"Entity Analysis:")
        remarks.append(f"  • Correct entities: {metrics['common_entities']}/{metrics['ref_entity_count']}")
        remarks.append(f"  • Missing entities: {metrics['missing_entities']}")
        remarks.append(f"  • Extra entities: {metrics['extra_entities']}")
        
        if metrics['ref_entity_count'] > 0:
            entity_precision = metrics['common_entities'] / metrics['gen_entity_count'] if metrics['gen_entity_count'] > 0 else 0
            entity_recall = metrics['common_entities'] / metrics['ref_entity_count']
            remarks.append(f"  • Entity precision: {entity_precision * 100:.1f}%")
            remarks.append(f"  • Entity recall: {entity_recall * 100:.1f}%")
        
        # Overall assessment
        if overall_score >= 0.8:
            assessment = "High factual accuracy with strong alignment across all components"
        elif overall_score >= 0.6:
            assessment = "Good factual accuracy with solid performance in most areas"
        elif overall_score >= 0.4:
            assessment = "Moderate factual accuracy with some areas needing improvement"
        else:
            assessment = "Low factual accuracy with significant issues across multiple components"
        
        remarks.append(f"Assessment: {assessment}")
        
        # Component-specific analysis
        best_component = max(semantic_score, content_score, factual_score, entity_score)
        worst_component = min(semantic_score, content_score, factual_score, entity_score)
        
        if semantic_score == best_component and semantic_score > 0.7:
            remarks.append("Strength: Excellent semantic understanding and meaning preservation")
        elif content_score == best_component and content_score > 0.7:
            remarks.append("Strength: Strong content accuracy with good key information retention")
        elif factual_score == best_component and factual_score > 0.7:
            remarks.append("Strength: High factual consistency in language and expression")
        elif entity_score == best_component and entity_score > 0.7:
            remarks.append("Strength: Accurate handling of specific entities and factual details")
        
        # Weakness identification
        if semantic_score == worst_component and semantic_score < 0.5:
            remarks.append("Weakness: Poor semantic alignment affecting overall meaning accuracy")
        elif content_score == worst_component and content_score < 0.5:
            remarks.append("Weakness: Missing or incorrect key information content")
        elif factual_score == worst_component and factual_score < 0.5:
            remarks.append("Weakness: Inconsistent factual language and terminology")
        elif entity_score == worst_component and entity_score < 0.5:
            remarks.append("Weakness: Inaccurate or missing specific factual entities")
        
        # Length and completeness analysis
        word_ratio = metrics['word_ratio']
        if word_ratio < 0.7 and overall_score < 0.6:
            remarks.append("Completeness: Generated text may be too brief, potentially missing important factual details")
        elif word_ratio > 1.5 and content_score < 0.6:
            remarks.append("Completeness: Generated text is verbose but doesn't improve factual accuracy proportionally")
        elif 0.8 <= word_ratio <= 1.2 and overall_score > 0.7:
            remarks.append("Completeness: Well-balanced length with good factual coverage")
        
        # Specific improvement suggestions
        if overall_score < 0.7:
            suggestions = []
            if semantic_score < 0.6:
                suggestions.append("improve semantic understanding and meaning alignment")
            if content_score < 0.6:
                suggestions.append("ensure accurate inclusion of key factual information")
            if factual_score < 0.6:
                suggestions.append("maintain consistent factual terminology and language")
            if entity_score < 0.6:
                suggestions.append("verify accuracy of specific entities (numbers, dates, names)")
            if metrics['missing_entities'] > metrics['common_entities']:
                suggestions.append("include more essential factual entities from the reference")
            if metrics['extra_entities'] > metrics['missing_entities']:
                suggestions.append("reduce inclusion of potentially inaccurate additional entities")
            
            if suggestions:
                remarks.append(f"Suggestions: {', '.join(suggestions)}")
        
        # Reliability indicator
        component_variance = np.var([semantic_score, content_score, factual_score, entity_score])
        if component_variance < 0.05:
            remarks.append("Reliability: Consistent performance across all accuracy components")
        elif component_variance > 0.15:
            remarks.append("Reliability: Variable performance across components suggests mixed factual quality")
        
        return '\n'.join(remarks)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metric metadata
        """
        return {
            'name': self.name,
            'description': self.description,
            'dependencies': self.dependencies,
            'range': '[0%, 100%]',
            'higher_is_better': True,
            'interpretation': {
                'excellent': '80%-100%',
                'good': '60%-80%',
                'acceptable': '40%-60%',
                'poor': '0%-40%'
            },
            'components': {
                'semantic_accuracy': 'Semantic similarity (30%)',
                'content_accuracy': 'Key information overlap (30%)',
                'factual_consistency': 'Language consistency (20%)',
                'entity_accuracy': 'Specific entity correctness (20%)'
            }
        }