import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from collections import Counter
from typing import Dict, Any
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class BLEUMetric:
    """
    Calculates BLEU score between reference and generated responses
    """
    
    def __init__(self):
        self.name = "BLEU"
        self.description = "Measures n-gram overlap between generated and reference text"
        self.dependencies = ["Reference_Response", "Generated_Response"]
        self.smoothing = SmoothingFunction()
    
    def calculate(self, reference: str, generated: str, **kwargs) -> Dict[str, Any]:
        """
        Calculate BLEU score with detailed breakdown
        
        Args:
            reference: Reference response text
            generated: Generated response text
            
        Returns:
            Dict containing score and detailed remarks
        """
        try:
            # Tokenize texts
            reference_tokens = self._tokenize(reference)
            generated_tokens = self._tokenize(generated)
            
            if not reference_tokens or not generated_tokens:
                return {
                    'score': 0.0,
                    'remarks': 'Empty reference or generated text'
                }
            
            # Calculate BLEU score with smoothing
            bleu_score = sentence_bleu(
                [reference_tokens], 
                generated_tokens,
                smoothing_function=self.smoothing.method1
            )
            
            # Calculate individual n-gram precisions
            precisions = self._calculate_ngram_precisions(reference_tokens, generated_tokens)
            
            # Generate detailed remarks
            remarks = self._generate_detailed_remarks(
                bleu_score, precisions, reference_tokens, generated_tokens, reference, generated
            )
            
            return {
                'score': bleu_score,
                'remarks': remarks
            }
            
        except Exception as e:
            return {
                'score': 0.0,
                'remarks': f'Error calculating BLEU: {str(e)}'
            }
    
    def _calculate_ngram_precisions(self, ref_tokens: list, gen_tokens: list) -> Dict[str, float]:
        """
        Calculate individual n-gram precisions for detailed analysis
        
        Args:
            ref_tokens: Reference tokens
            gen_tokens: Generated tokens
            
        Returns:
            Dictionary with n-gram precisions
        """
        precisions = {}
        
        for n in range(1, 5):  # 1-gram to 4-gram
            if len(gen_tokens) >= n:
                # Get n-grams
                ref_ngrams = [tuple(ref_tokens[i:i+n]) for i in range(len(ref_tokens)-n+1)]
                gen_ngrams = [tuple(gen_tokens[i:i+n]) for i in range(len(gen_tokens)-n+1)]
                
                if gen_ngrams:
                    # Count overlapping n-grams
                    ref_counter = Counter(ref_ngrams)
                    gen_counter = Counter(gen_ngrams)
                    
                    overlap = 0
                    for ngram in gen_counter:
                        overlap += min(gen_counter[ngram], ref_counter.get(ngram, 0))
                    
                    precision = overlap / len(gen_ngrams) if len(gen_ngrams) > 0 else 0.0
                    precisions[f'{n}_gram'] = precision
                else:
                    precisions[f'{n}_gram'] = 0.0
            else:
                precisions[f'{n}_gram'] = 0.0
        
        return precisions
    
    def _tokenize(self, text: str) -> list:
        """
        Tokenize text for BLEU calculation
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Clean text
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize
        tokens = nltk.word_tokenize(text)
        return [token for token in tokens if token.strip()]
    
    def _generate_detailed_remarks(self, score: float, precisions: Dict[str, float], 
                                 ref_tokens: list, gen_tokens: list, 
                                 original_ref: str, original_gen: str) -> str:
        """
        Generate comprehensive explanatory remarks for the BLEU score
        
        Args:
            score: BLEU score
            precisions: N-gram precisions
            ref_tokens: Reference tokens
            gen_tokens: Generated tokens
            original_ref: Original reference text
            original_gen: Original generated text
            
        Returns:
            Detailed explanatory remarks
        """
        remarks = []
        
        # Main score interpretation with percentage
        remarks.append(f"BLEU Score: {score * 100:.2f}%")
        
        # Individual n-gram precisions
        remarks.append(f"1-gram precision: {precisions.get('1_gram', 0) * 100:.2f}%")
        remarks.append(f"2-gram precision: {precisions.get('2_gram', 0) * 100:.2f}%")
        remarks.append(f"3-gram precision: {precisions.get('3_gram', 0) * 100:.2f}%")
        remarks.append(f"4-gram precision: {precisions.get('4_gram', 0) * 100:.2f}%")
        
        # Length information
        ref_length = len(ref_tokens)
        gen_length = len(gen_tokens)
        remarks.append(f"Reference length: {ref_length} tokens")
        remarks.append(f"Generated length: {gen_length} tokens")
        
        # Length ratio analysis
        length_ratio = gen_length / ref_length if ref_length > 0 else 0
        if length_ratio < 0.5:
            remarks.append(f"Length ratio: {length_ratio:.2f} (Generated text is much shorter)")
        elif length_ratio > 2.0:
            remarks.append(f"Length ratio: {length_ratio:.2f} (Generated text is much longer)")
        elif abs(length_ratio - 1.0) < 0.2:
            remarks.append(f"Length ratio: {length_ratio:.2f} (Similar length to reference)")
        else:
            remarks.append(f"Length ratio: {length_ratio:.2f}")
        
        # Vocabulary overlap analysis
        ref_vocab = set(ref_tokens)
        gen_vocab = set(gen_tokens)
        common_words = ref_vocab & gen_vocab
        vocab_overlap = len(common_words) / len(ref_vocab) if ref_vocab else 0
        remarks.append(f"Vocabulary overlap: {vocab_overlap * 100:.1f}% ({len(common_words)}/{len(ref_vocab)} words)")
        
        # Performance assessment
        if score >= 0.7:
            assessment = "Excellent n-gram overlap indicating high similarity"
        elif score >= 0.5:
            assessment = "Good n-gram overlap with moderate similarity"
        elif score >= 0.3:
            assessment = "Fair n-gram overlap with some similarity"
        elif score >= 0.1:
            assessment = "Poor n-gram overlap with limited similarity"
        else:
            assessment = "Very poor n-gram overlap with minimal similarity"
        
        remarks.append(f"Assessment: {assessment}")
        
        # Specific insights based on n-gram performance
        best_ngram = max(precisions.keys(), key=lambda k: precisions[k]) if precisions else None
        if best_ngram and precisions[best_ngram] > 0.1:
            remarks.append(f"Strongest performance: {best_ngram.replace('_', '-')} matching")
        
        # Brevity penalty insight
        if length_ratio < 1.0:
            brevity_penalty = min(1.0, length_ratio)
            remarks.append(f"Brevity penalty applied: {brevity_penalty:.3f} (due to shorter generated text)")
        
        # Improvement suggestions
        if score < 0.5:
            suggestions = []
            if precisions.get('1_gram', 0) < 0.4:
                suggestions.append("improve word choice")
            if precisions.get('2_gram', 0) < 0.3:
                suggestions.append("enhance phrase-level similarity")
            if length_ratio < 0.7:
                suggestions.append("increase response completeness")
            elif length_ratio > 1.5:
                suggestions.append("reduce verbosity")
            
            if suggestions:
                remarks.append(f"Suggestions: {', '.join(suggestions)}")
        
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
                'excellent': '70%-100%',
                'good': '50%-70%',
                'acceptable': '30%-50%',
                'poor': '0%-30%'
            }
        }