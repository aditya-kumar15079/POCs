import nltk
from nltk.translate.meteor_score import meteor_score
from typing import Dict, Any
import re

# Download required NLTK data
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class METEORMetric:
    """
    Calculates METEOR score between reference and generated responses
    """
    
    def __init__(self):
        self.name = "METEOR"
        self.description = "Considers stemming, synonymy, and word order for text comparison"
        self.dependencies = ["Reference_Response", "Generated_Response"]
    
    def calculate(self, reference: str, generated: str, **kwargs) -> Dict[str, Any]:
        """
        Calculate METEOR score with detailed analysis
        
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
            
            # Tokenize texts
            reference_tokens = self._tokenize(reference)
            generated_tokens = self._tokenize(generated)
            
            if not reference_tokens or not generated_tokens:
                return {
                    'score': 0.0,
                    'remarks': 'No valid tokens found'
                }
            
            # Calculate METEOR score
            score = meteor_score([reference_tokens], generated_tokens)
            
            # Calculate detailed metrics
            detailed_metrics = self._calculate_detailed_metrics(reference, generated, reference_tokens, generated_tokens)
            
            # Generate detailed remarks
            remarks = self._generate_detailed_remarks(score, detailed_metrics, reference_tokens, generated_tokens)
            
            return {
                'score': score,
                'remarks': remarks
            }
            
        except Exception as e:
            return {
                'score': 0.0,
                'remarks': f'Error calculating METEOR: {str(e)}'
            }
    
    def _calculate_detailed_metrics(self, reference: str, generated: str, ref_tokens: list, gen_tokens: list) -> Dict[str, Any]:
        """
        Calculate detailed metrics for METEOR analysis
        
        Args:
            reference: Original reference text
            generated: Original generated text
            ref_tokens: Reference tokens
            gen_tokens: Generated tokens
            
        Returns:
            Dictionary with detailed metrics
        """
        metrics = {}
        
        # Basic metrics
        metrics['ref_length'] = len(ref_tokens)
        metrics['gen_length'] = len(gen_tokens)
        metrics['length_ratio'] = len(gen_tokens) / len(ref_tokens) if len(ref_tokens) > 0 else 0
        
        # Vocabulary analysis
        ref_vocab = set(ref_tokens)
        gen_vocab = set(gen_tokens)
        common_vocab = ref_vocab & gen_vocab
        
        metrics['ref_vocab_size'] = len(ref_vocab)
        metrics['gen_vocab_size'] = len(gen_vocab)
        metrics['common_vocab_size'] = len(common_vocab)
        metrics['vocab_overlap_ratio'] = len(common_vocab) / len(ref_vocab) if len(ref_vocab) > 0 else 0
        
        # Exact match analysis
        exact_matches = sum(1 for token in gen_tokens if token in ref_tokens)
        metrics['exact_matches'] = exact_matches
        metrics['exact_match_ratio'] = exact_matches / len(gen_tokens) if len(gen_tokens) > 0 else 0
        
        # Character-level analysis
        metrics['ref_chars'] = len(reference)
        metrics['gen_chars'] = len(generated)
        metrics['char_ratio'] = len(generated) / len(reference) if len(reference) > 0 else 0
        
        return metrics
    
    def _tokenize(self, text: str) -> list:
        """
        Tokenize text for METEOR calculation
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Clean and normalize text
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize
        tokens = nltk.word_tokenize(text)
        return [token for token in tokens if token.strip()]
    
    def _generate_detailed_remarks(self, score: float, metrics: Dict[str, Any], ref_tokens: list, gen_tokens: list) -> str:
        """
        Generate comprehensive explanatory remarks for METEOR score
        
        Args:
            score: METEOR score
            metrics: Detailed metrics
            ref_tokens: Reference tokens
            gen_tokens: Generated tokens
            
        Returns:
            Detailed explanatory remarks
        """
        remarks = []
        
        # Main score with percentage
        remarks.append(f"METEOR Score: {score * 100:.2f}%")
        
        # Length analysis
        remarks.append(f"Reference length: {metrics['ref_length']} tokens ({metrics['ref_chars']} characters)")
        remarks.append(f"Generated length: {metrics['gen_length']} tokens ({metrics['gen_chars']} characters)")
        remarks.append(f"Length ratio: {metrics['length_ratio']:.2f}")
        
        # Vocabulary analysis
        remarks.append(f"Reference vocabulary: {metrics['ref_vocab_size']} unique words")
        remarks.append(f"Generated vocabulary: {metrics['gen_vocab_size']} unique words")
        remarks.append(f"Common vocabulary: {metrics['common_vocab_size']} words ({metrics['vocab_overlap_ratio']*100:.1f}% overlap)")
        
        # Exact matches
        remarks.append(f"Exact word matches: {metrics['exact_matches']}/{metrics['gen_length']} ({metrics['exact_match_ratio']*100:.1f}%)")
        
        # METEOR-specific advantages
        if score > 0.3:
            meteor_advantages = []
            if metrics['vocab_overlap_ratio'] < metrics['exact_match_ratio'] * 1.2:
                meteor_advantages.append("synonym matching")
            if score > metrics['exact_match_ratio']:
                meteor_advantages.append("stemming and word order consideration")
            
            if meteor_advantages:
                remarks.append(f"METEOR advantages: Benefits from {', '.join(meteor_advantages)}")
        
        # Performance assessment
        if score >= 0.6:
            assessment = "Excellent semantic and structural similarity with advanced matching"
        elif score >= 0.4:
            assessment = "Good semantic similarity with effective synonym and stem matching"
        elif score >= 0.2:
            assessment = "Moderate semantic similarity with some advanced matching benefits"
        else:
            assessment = "Poor semantic similarity despite advanced matching capabilities"
        
        remarks.append(f"Assessment: {assessment}")
        
        # Length analysis insights
        length_ratio = metrics['length_ratio']
        if length_ratio < 0.7:
            remarks.append("Length analysis: Generated text is notably shorter, may lack completeness")
        elif length_ratio > 1.5:
            remarks.append("Length analysis: Generated text is notably longer, may contain redundancy")
        elif 0.8 <= length_ratio <= 1.2:
            remarks.append("Length analysis: Well-matched length suggesting appropriate coverage")
        else:
            remarks.append(f"Length analysis: Moderate length difference (ratio: {length_ratio:.2f})")
        
        # Vocabulary richness analysis
        ref_vocab_density = metrics['ref_vocab_size'] / metrics['ref_length'] if metrics['ref_length'] > 0 else 0
        gen_vocab_density = metrics['gen_vocab_size'] / metrics['gen_length'] if metrics['gen_length'] > 0 else 0
        
        remarks.append(f"Vocabulary density: Reference {ref_vocab_density:.2f}, Generated {gen_vocab_density:.2f}")
        
        if gen_vocab_density > ref_vocab_density * 1.1:
            remarks.append("Vocabulary analysis: Generated text shows higher lexical diversity")
        elif gen_vocab_density < ref_vocab_density * 0.9:
            remarks.append("Vocabulary analysis: Generated text shows lower lexical diversity")
        else:
            remarks.append("Vocabulary analysis: Similar lexical diversity to reference")
        
        # Quality indicators
        quality_indicators = []
        if score > 0.5:
            quality_indicators.append("strong semantic alignment")
        if metrics['vocab_overlap_ratio'] > 0.6:
            quality_indicators.append("high vocabulary similarity")
        if 0.8 <= length_ratio <= 1.2:
            quality_indicators.append("appropriate length matching")
        if metrics['exact_match_ratio'] > 0.4:
            quality_indicators.append("good word-level precision")
        
        if quality_indicators:
            remarks.append(f"Quality indicators: {', '.join(quality_indicators)}")
        
        # Improvement suggestions
        if score < 0.5:
            suggestions = []
            if metrics['vocab_overlap_ratio'] < 0.4:
                suggestions.append("improve vocabulary similarity")
            if metrics['exact_match_ratio'] < 0.3:
                suggestions.append("increase word-level accuracy")
            if length_ratio < 0.7:
                suggestions.append("provide more comprehensive coverage")
            elif length_ratio > 1.5:
                suggestions.append("reduce verbosity and focus on key points")
            if gen_vocab_density < ref_vocab_density * 0.8:
                suggestions.append("enhance lexical diversity")
            
            if suggestions:
                remarks.append(f"Suggestions: {', '.join(suggestions)}")
        
        # METEOR vs other metrics insight
        if score > metrics.get('exact_match_ratio', 0) * 1.2:
            remarks.append("METEOR advantage: Score benefits significantly from synonym and stem matching beyond exact matches")
        
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
                'excellent': '60%-100%',
                'good': '40%-60%',
                'acceptable': '20%-40%',
                'poor': '0%-20%'
            },
            'advantages': [
                'Considers synonyms and word stems',
                'Accounts for word order',
                'More robust than simple n-gram overlap'
            ]
        }