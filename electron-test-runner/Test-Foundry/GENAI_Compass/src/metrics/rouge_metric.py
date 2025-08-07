from rouge_score import rouge_scorer
from typing import Dict, Any

class ROUGEMetric:
    """
    Calculates ROUGE scores between reference and generated responses
    """
    
    def __init__(self):
        self.name = "ROUGE"
        self.description = "Evaluates recall-oriented understanding for gisting evaluation"
        self.dependencies = ["Reference_Response", "Generated_Response"]
        self.scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    def calculate(self, reference: str, generated: str, **kwargs) -> Dict[str, Any]:
        """
        Calculate ROUGE scores with detailed breakdown
        
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
            
            # Calculate ROUGE scores
            scores = self.scorer.score(reference, generated)
            
            # Extract all scores
            rouge1_precision = scores['rouge1'].precision
            rouge1_recall = scores['rouge1'].recall
            rouge1_f1 = scores['rouge1'].fmeasure
            
            rouge2_precision = scores['rouge2'].precision
            rouge2_recall = scores['rouge2'].recall
            rouge2_f1 = scores['rouge2'].fmeasure
            
            rougeL_precision = scores['rougeL'].precision
            rougeL_recall = scores['rougeL'].recall
            rougeL_f1 = scores['rougeL'].fmeasure
            
            # Calculate average F1 score
            avg_rouge = (rouge1_f1 + rouge2_f1 + rougeL_f1) / 3
            
            # Generate detailed remarks
            remarks = self._generate_detailed_remarks(
                avg_rouge, scores, reference, generated
            )
            
            return {
                'score': avg_rouge,
                'remarks': remarks,
                'detailed_scores': {
                    'rouge1_f1': rouge1_f1,
                    'rouge2_f1': rouge2_f1,
                    'rougeL_f1': rougeL_f1
                }
            }
            
        except Exception as e:
            return {
                'score': 0.0,
                'remarks': f'Error calculating ROUGE: {str(e)}'
            }
    
    def _generate_detailed_remarks(self, avg_score: float, scores: Dict, 
                                 reference: str, generated: str) -> str:
        """
        Generate comprehensive explanatory remarks for ROUGE scores
        
        Args:
            avg_score: Average ROUGE score
            scores: Individual ROUGE scores
            reference: Reference text
            generated: Generated text
            
        Returns:
            Detailed explanatory remarks
        """
        remarks = []
        
        # Main score with percentage
        remarks.append(f"ROUGE Score: {avg_score * 100:.2f}%")
        
        # Individual ROUGE scores with all metrics
        rouge1 = scores['rouge1']
        rouge2 = scores['rouge2']
        rougeL = scores['rougeL']
        
        remarks.append(f"ROUGE-1 (Unigram overlap):")
        remarks.append(f"  • Precision: {rouge1.precision * 100:.2f}%")
        remarks.append(f"  • Recall: {rouge1.recall * 100:.2f}%")
        remarks.append(f"  • F1-Score: {rouge1.fmeasure * 100:.2f}%")
        
        remarks.append(f"ROUGE-2 (Bigram overlap):")
        remarks.append(f"  • Precision: {rouge2.precision * 100:.2f}%")
        remarks.append(f"  • Recall: {rouge2.recall * 100:.2f}%")
        remarks.append(f"  • F1-Score: {rouge2.fmeasure * 100:.2f}%")
        
        remarks.append(f"ROUGE-L (Longest Common Subsequence):")
        remarks.append(f"  • Precision: {rougeL.precision * 100:.2f}%")
        remarks.append(f"  • Recall: {rougeL.recall * 100:.2f}%")
        remarks.append(f"  • F1-Score: {rougeL.fmeasure * 100:.2f}%")
        
        # Length analysis
        ref_words = len(reference.split())
        gen_words = len(generated.split())
        remarks.append(f"Reference length: {ref_words} words")
        remarks.append(f"Generated length: {gen_words} words")
        
        length_ratio = gen_words / ref_words if ref_words > 0 else 0
        remarks.append(f"Length ratio: {length_ratio:.2f}")
        
        # Performance analysis
        if avg_score >= 0.6:
            assessment = "Excellent recall and content overlap"
        elif avg_score >= 0.4:
            assessment = "Good recall with substantial overlap"
        elif avg_score >= 0.2:
            assessment = "Moderate recall with some overlap"
        else:
            assessment = "Poor recall with minimal overlap"
        
        remarks.append(f"Assessment: {assessment}")
        
        # Detailed analysis of each component
        best_rouge = max(rouge1.fmeasure, rouge2.fmeasure, rougeL.fmeasure)
        if rouge1.fmeasure == best_rouge and rouge1.fmeasure > rouge2.fmeasure and rouge1.fmeasure > rougeL.fmeasure:
            remarks.append("Strongest performance: Word-level matching (ROUGE-1)")
        elif rouge2.fmeasure == best_rouge and rouge2.fmeasure > rouge1.fmeasure and rouge2.fmeasure > rougeL.fmeasure:
            remarks.append("Strongest performance: Phrase-level matching (ROUGE-2)")
        elif rougeL.fmeasure == best_rouge and rougeL.fmeasure > rouge1.fmeasure and rougeL.fmeasure > rouge2.fmeasure:
            remarks.append("Strongest performance: Structural similarity (ROUGE-L)")
        
        # Precision vs Recall analysis
        avg_precision = (rouge1.precision + rouge2.precision + rougeL.precision) / 3
        avg_recall = (rouge1.recall + rouge2.recall + rougeL.recall) / 3
        
        if avg_precision > avg_recall + 0.1:
            remarks.append(f"Higher precision ({avg_precision*100:.1f}%) than recall ({avg_recall*100:.1f}%): Generated text is focused but may miss content")
        elif avg_recall > avg_precision + 0.1:
            remarks.append(f"Higher recall ({avg_recall*100:.1f}%) than precision ({avg_precision*100:.1f}%): Generated text covers content well but may include extra information")
        else:
            remarks.append(f"Balanced precision ({avg_precision*100:.1f}%) and recall ({avg_recall*100:.1f}%)")
        
        # Improvement suggestions
        if avg_score < 0.5:
            suggestions = []
            if rouge1.fmeasure < 0.4:
                suggestions.append("improve word-level similarity")
            if rouge2.fmeasure < 0.3:
                suggestions.append("enhance phrase-level matching")
            if rougeL.fmeasure < 0.4:
                suggestions.append("better preserve sentence structure")
            if avg_recall < 0.4:
                suggestions.append("include more relevant content")
            if avg_precision < 0.4:
                suggestions.append("reduce irrelevant information")
            
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
                'excellent': '60%-100%',
                'good': '40%-60%',
                'acceptable': '20%-40%',
                'poor': '0%-20%'
            },
            'components': {
                'ROUGE-1': 'Unigram overlap',
                'ROUGE-2': 'Bigram overlap',
                'ROUGE-L': 'Longest common subsequence'
            }
        }