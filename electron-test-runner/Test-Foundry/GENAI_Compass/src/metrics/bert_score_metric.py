from bert_score import score
from typing import Dict, Any, List
import torch

class BERTScoreMetric:
    """
    Calculates BERT score between reference and generated responses
    """
    
    def __init__(self):
        self.name = "BERT Score"
        self.description = "Uses BERT embeddings to measure semantic similarity"
        self.dependencies = ["Reference_Response", "Generated_Response"]
        self.model_type = "microsoft/deberta-xlarge-mnli"  # High-quality model
    
    def calculate(self, reference: str, generated: str, **kwargs) -> Dict[str, Any]:
        """
        Calculate BERT score with detailed semantic analysis
        
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
            
            # Calculate BERT score
            P, R, F1 = score(
                [generated], 
                [reference], 
                model_type=self.model_type,
                verbose=False,
                device='cpu'  # Use CPU to avoid GPU memory issues
            )
            
            # Use F1 score as the main metric
            bert_score = F1.item()
            precision = P.item()
            recall = R.item()
            
            # Calculate additional semantic metrics
            semantic_metrics = self._calculate_semantic_metrics(reference, generated, precision, recall, bert_score)
            
            # Generate detailed remarks
            remarks = self._generate_detailed_remarks(bert_score, precision, recall, semantic_metrics, reference, generated)
            
            return {
                'score': bert_score,
                'remarks': remarks,
                'detailed_scores': {
                    'precision': precision,
                    'recall': recall,
                    'f1': bert_score
                }
            }
            
        except Exception as e:
            return {
                'score': 0.0,
                'remarks': f'Error calculating BERT Score: {str(e)}'
            }
    
    def _calculate_semantic_metrics(self, reference: str, generated: str, precision: float, recall: float, f1: float) -> Dict[str, Any]:
        """
        Calculate additional semantic analysis metrics
        
        Args:
            reference: Reference text
            generated: Generated text
            precision: BERT precision score
            recall: BERT recall score
            f1: BERT F1 score
            
        Returns:
            Dictionary with semantic metrics
        """
        metrics = {}
        
        # Basic text metrics
        ref_sentences = reference.split('.')
        gen_sentences = generated.split('.')
        ref_words = reference.split()
        gen_words = generated.split()
        
        metrics['ref_sentences'] = len([s for s in ref_sentences if s.strip()])
        metrics['gen_sentences'] = len([s for s in gen_sentences if s.strip()])
        metrics['ref_words'] = len(ref_words)
        metrics['gen_words'] = len(gen_words)
        metrics['sentence_ratio'] = metrics['gen_sentences'] / metrics['ref_sentences'] if metrics['ref_sentences'] > 0 else 0
        metrics['word_ratio'] = metrics['gen_words'] / metrics['ref_words'] if metrics['ref_words'] > 0 else 0
        
        # Semantic quality indicators
        metrics['precision_recall_balance'] = abs(precision - recall)
        metrics['semantic_compression'] = f1 / metrics['word_ratio'] if metrics['word_ratio'] > 0 else 0
        
        # Contextual similarity categories
        if f1 >= 0.9:
            metrics['similarity_category'] = 'Near-identical semantic meaning'
        elif f1 >= 0.8:
            metrics['similarity_category'] = 'High semantic similarity'
        elif f1 >= 0.7:
            metrics['similarity_category'] = 'Good semantic similarity'
        elif f1 >= 0.6:
            metrics['similarity_category'] = 'Moderate semantic similarity'
        elif f1 >= 0.4:
            metrics['similarity_category'] = 'Low semantic similarity'
        else:
            metrics['similarity_category'] = 'Poor semantic similarity'
        
        return metrics
    
    def _generate_detailed_remarks(self, f1_score: float, precision: float, recall: float, 
                                 metrics: Dict[str, Any], reference: str, generated: str) -> str:
        """
        Generate comprehensive explanatory remarks for BERT score
        
        Args:
            f1_score: F1 BERT score
            precision: Precision BERT score
            recall: Recall BERT score
            metrics: Additional semantic metrics
            reference: Reference text
            generated: Generated text
            
        Returns:
            Detailed explanatory remarks
        """
        remarks = []
        
        # Main score with percentage
        remarks.append(f"BERT Score (F1): {f1_score * 100:.2f}%")
        
        # Individual BERT components
        remarks.append(f"BERT Precision: {precision * 100:.2f}%")
        remarks.append(f"BERT Recall: {recall * 100:.2f}%")
        
        # Semantic similarity category
        remarks.append(f"Semantic Category: {metrics['similarity_category']}")
        
        # Text structure analysis
        remarks.append(f"Reference structure: {metrics['ref_sentences']} sentences, {metrics['ref_words']} words")
        remarks.append(f"Generated structure: {metrics['gen_sentences']} sentences, {metrics['gen_words']} words")
        remarks.append(f"Sentence ratio: {metrics['sentence_ratio']:.2f}")
        remarks.append(f"Word ratio: {metrics['word_ratio']:.2f}")
        
        # Precision vs Recall analysis
        balance = metrics['precision_recall_balance']
        if precision > recall + 0.1:
            remarks.append(f"Precision-focused ({precision*100:.1f}% vs {recall*100:.1f}%): Generated text is semantically focused but may miss some content")
        elif recall > precision + 0.1:
            remarks.append(f"Recall-focused ({recall*100:.1f}% vs {precision*100:.1f}%): Generated text covers content well but may include semantically distant information")
        else:
            remarks.append(f"Balanced precision and recall ({precision*100:.1f}% vs {recall*100:.1f}%): Well-aligned semantic content")
        
        # Model-specific insights
        remarks.append(f"Model used: {self.model_type}")
        remarks.append("BERT advantage: Captures contextual and semantic meaning beyond surface-level text similarity")
        
        # Semantic quality assessment
        if f1_score >= 0.9:
            assessment = "Exceptional semantic alignment with near-perfect contextual understanding"
        elif f1_score >= 0.8:
            assessment = "Excellent semantic similarity with strong contextual matching"
        elif f1_score >= 0.7:
            assessment = "Good semantic similarity with solid contextual understanding"
        elif f1_score >= 0.6:
            assessment = "Moderate semantic similarity with reasonable contextual overlap"
        elif f1_score >= 0.4:
            assessment = "Limited semantic similarity with weak contextual alignment"
        else:
            assessment = "Poor semantic similarity with minimal contextual relationship"
        
        remarks.append(f"Assessment: {assessment}")
        
        # Contextual understanding analysis
        if f1_score > 0.8:
            remarks.append("Contextual understanding: Generated text demonstrates strong comprehension of the reference meaning")
        elif f1_score > 0.6:
            remarks.append("Contextual understanding: Generated text shows good grasp of the main concepts")
        elif f1_score > 0.4:
            remarks.append("Contextual understanding: Generated text captures some key concepts but misses important nuances")
        else:
            remarks.append("Contextual understanding: Generated text shows limited comprehension of the reference content")
        
        # Length and efficiency analysis
        word_ratio = metrics['word_ratio']
        if word_ratio < 0.7 and f1_score > 0.7:
            remarks.append("Efficiency: High semantic similarity achieved with concise expression")
        elif word_ratio > 1.5 and f1_score < 0.7:
            remarks.append("Efficiency: Verbose expression without proportional semantic improvement")
        elif word_ratio > 1.3 and f1_score > 0.8:
            remarks.append("Efficiency: Detailed expression maintains high semantic fidelity")
        else:
            remarks.append("Efficiency: Reasonable balance between length and semantic content")
        
        # Semantic compression metric
        if metrics['semantic_compression'] > 1.2:
            remarks.append("Semantic density: High information density relative to text length")
        elif metrics['semantic_compression'] < 0.8:
            remarks.append("Semantic density: Lower information density, may benefit from more concise expression")
        
        # Performance indicators
        quality_indicators = []
        if f1_score > 0.8:
            quality_indicators.append("strong semantic understanding")
        if balance < 0.1:
            quality_indicators.append("well-balanced precision and recall")
        if 0.8 <= word_ratio <= 1.2:
            quality_indicators.append("appropriate length matching")
        if precision > 0.8:
            quality_indicators.append("high semantic precision")
        if recall > 0.8:
            quality_indicators.append("comprehensive content coverage")
        
        if quality_indicators:
            remarks.append(f"Quality indicators: {', '.join(quality_indicators)}")
        
        # Improvement suggestions
        if f1_score < 0.7:
            suggestions = []
            if precision < 0.6:
                suggestions.append("improve semantic accuracy and relevance")
            if recall < 0.6:
                suggestions.append("ensure comprehensive coverage of key concepts")
            if balance > 0.2:
                suggestions.append("balance precision and recall for better overall performance")
            if f1_score < 0.5:
                suggestions.append("focus on better understanding the core meaning and context")
            
            if suggestions:
                remarks.append(f"Suggestions: {', '.join(suggestions)}")
        
        # Comparative insight
        if f1_score > 0.8:
            remarks.append("BERT insight: Text demonstrates sophisticated semantic understanding that goes beyond word-level matching")
        elif f1_score > 0.6:
            remarks.append("BERT insight: Semantic relationship detected despite potential differences in surface-level expression")
        else:
            remarks.append("BERT insight: Limited semantic relationship suggests fundamental differences in meaning or context")
        
        return '\n'.join(remarks)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metric metadata
        
        Returns:
            Dict containing metadata
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
            'model_used': self.model_type,
            'advantages': [
                'Captures semantic similarity beyond word overlap',
                'Uses contextual embeddings',
                'Robust to paraphrasing and synonyms'
            ]
        }