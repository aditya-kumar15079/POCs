from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Any
import re
import numpy as np

class AnswerRelevanceMetric:
    """
    Evaluates how well the response addresses the given prompt
    """
    
    def __init__(self):
        self.name = "Answer Relevance"
        self.description = "Evaluates how well the response addresses the given prompt"
        self.dependencies = ["Prompt", "Generated_Response", "Context"]
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            self.model = None
    
    def calculate(self, prompt: str, generated: str, context: str = "", **kwargs) -> Dict[str, Any]:
        """
        Calculate answer relevance score with detailed analysis
        
        Args:
            prompt: The original question/prompt
            generated: Generated response text
            context: Optional context information
            
        Returns:
            Dict containing score and detailed remarks
        """
        try:
            if not prompt.strip() or not generated.strip():
                return {
                    'score': 0.0,
                    'remarks': 'Empty prompt or generated text'
                }
            
            # Calculate different relevance aspects
            direct_relevance = self._calculate_direct_relevance(prompt, generated)
            topical_relevance = self._calculate_topical_relevance(prompt, generated, context)
            completeness_score = self._calculate_completeness(prompt, generated)
            focus_score = self._calculate_focus_score(prompt, generated)
            
            # Weighted combination
            relevance_score = (
                direct_relevance * 0.4 + 
                topical_relevance * 0.25 + 
                completeness_score * 0.25 +
                focus_score * 0.1
            )
            
            # Calculate detailed metrics
            detailed_metrics = self._calculate_detailed_metrics(prompt, generated, context, direct_relevance, topical_relevance, completeness_score, focus_score)
            
            # Generate detailed remarks
            remarks = self._generate_detailed_remarks(
                relevance_score, direct_relevance, topical_relevance, completeness_score, focus_score, detailed_metrics, prompt, generated, context
            )
            
            return {
                'score': relevance_score,
                'remarks': remarks,
                'detailed_scores': {
                    'direct_relevance': direct_relevance,
                    'topical_relevance': topical_relevance,
                    'completeness': completeness_score,
                    'focus': focus_score
                }
            }
            
        except Exception as e:
            return {
                'score': 0.0,
                'remarks': f'Error calculating answer relevance: {str(e)}'
            }
    
    def _calculate_direct_relevance(self, prompt: str, generated: str) -> float:
        """
        Calculate direct relevance using semantic similarity
        """
        if self.model is None:
            return self._fallback_relevance(prompt, generated)
        
        try:
            prompt_embedding = self.model.encode([prompt])
            response_embedding = self.model.encode([generated])
            similarity = cosine_similarity(prompt_embedding, response_embedding)[0][0]
            return max(0.0, min(1.0, similarity))
        except Exception:
            return self._fallback_relevance(prompt, generated)
    
    def _calculate_topical_relevance(self, prompt: str, generated: str, context: str) -> float:
        """
        Calculate topical relevance considering context
        """
        prompt_topics = self._extract_topics(prompt)
        response_topics = self._extract_topics(generated)
        
        if context:
            context_topics = self._extract_topics(context)
            prompt_topics.update(context_topics)
        
        if not prompt_topics:
            return 0.5
        
        common_topics = prompt_topics & response_topics
        topic_relevance = len(common_topics) / len(prompt_topics) if prompt_topics else 0.0
        return max(0.0, min(1.0, topic_relevance))
    
    def _calculate_completeness(self, prompt: str, generated: str) -> float:
        """
        Calculate how completely the response addresses the prompt
        """
        question_indicators = self._identify_question_type(prompt)
        response_elements = self._analyze_response_elements(generated)
        
        completeness = 0.0
        total_requirements = len(question_indicators)
        
        if total_requirements == 0:
            return 0.8  # Default for non-question prompts
        
        for requirement in question_indicators:
            if self._addresses_requirement(requirement, response_elements):
                completeness += 1.0 / total_requirements
        
        return min(1.0, completeness)
    
    def _calculate_focus_score(self, prompt: str, generated: str) -> float:
        """
        Calculate how focused the response is on the prompt
        """
        prompt_words = set(self._normalize_text(prompt).split())
        response_words = set(self._normalize_text(generated).split())
        
        if not response_words:
            return 0.0
        
        # Calculate relevance density
        relevant_words = prompt_words & response_words
        relevance_density = len(relevant_words) / len(response_words) if response_words else 0.0
        
        # Adjust for response length appropriateness
        word_ratio = len(generated.split()) / len(prompt.split()) if len(prompt.split()) > 0 else 1.0
        
        if word_ratio > 5.0:  # Very long response
            focus_penalty = 0.8
        elif word_ratio > 3.0:  # Long response
            focus_penalty = 0.9
        else:
            focus_penalty = 1.0
        
        return min(1.0, relevance_density * focus_penalty)
    
    def _calculate_detailed_metrics(self, prompt: str, generated: str, context: str, 
                                  direct_relevance: float, topical_relevance: float, 
                                  completeness_score: float, focus_score: float) -> Dict[str, Any]:
        """
        Calculate additional detailed metrics for analysis
        """
        metrics = {}
        
        # Text statistics
        prompt_words = prompt.split()
        generated_words = generated.split()
        metrics['prompt_word_count'] = len(prompt_words)
        metrics['generated_word_count'] = len(generated_words)
        metrics['response_length_ratio'] = len(generated_words) / len(prompt_words) if len(prompt_words) > 0 else 0
        
        # Question analysis
        metrics['question_type'] = self._identify_question_type(prompt)
        metrics['is_question'] = '?' in prompt
        metrics['question_words'] = self._count_question_words(prompt)
        
        # Topic analysis
        prompt_topics = self._extract_topics(prompt)
        generated_topics = self._extract_topics(generated)
        metrics['prompt_topics'] = len(prompt_topics)
        metrics['generated_topics'] = len(generated_topics)
        metrics['common_topics'] = len(prompt_topics & generated_topics)
        
        # Context usage
        metrics['has_context'] = bool(context.strip())
        if context:
            context_topics = self._extract_topics(context)
            metrics['context_topics'] = len(context_topics)
            metrics['context_usage'] = len(context_topics & generated_topics) / len(context_topics) if context_topics else 0
        else:
            metrics['context_topics'] = 0
            metrics['context_usage'] = 0
        
        # Component scores
        metrics['direct_relevance'] = direct_relevance
        metrics['topical_relevance'] = topical_relevance
        metrics['completeness'] = completeness_score
        metrics['focus'] = focus_score
        
        return metrics
    
    def _extract_topics(self, text: str) -> set:
        """
        Extract key topics from text
        """
        topics = set()
        text = text.lower()
        words = re.findall(r'\b[a-z]{3,}\b', text)
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        topics.update([word for word in words if word not in stop_words])
        return topics
    
    def _identify_question_type(self, prompt: str) -> list:
        """
        Identify the type of question and its requirements
        """
        prompt_lower = prompt.lower()
        requirements = []
        
        if any(word in prompt_lower for word in ['what', 'which']):
            requirements.append('definition_or_identification')
        if any(word in prompt_lower for word in ['how', 'explain']):
            requirements.append('explanation_or_process')
        if any(word in prompt_lower for word in ['why', 'because']):
            requirements.append('reasoning_or_cause')
        if any(word in prompt_lower for word in ['when', 'where']):
            requirements.append('specific_information')
        if any(word in prompt_lower for word in ['compare', 'versus', 'vs']):
            requirements.append('comparison')
        if any(word in prompt_lower for word in ['list', 'enumerate']):
            requirements.append('enumeration')
        
        if not requirements:
            requirements.append('general_information')
        
        return requirements
    
    def _count_question_words(self, prompt: str) -> int:
        """
        Count question words in the prompt
        """
        question_words = ['what', 'who', 'when', 'where', 'why', 'how', 'which', 'whose', 'whom']
        prompt_lower = prompt.lower()
        return sum(1 for word in question_words if word in prompt_lower)
    
    def _analyze_response_elements(self, response: str) -> dict:
        """
        Analyze elements present in the response
        """
        response_lower = response.lower()
        
        elements = {
            'has_definition': any(word in response_lower for word in ['is', 'are', 'defined', 'means']),
            'has_explanation': len(response) > 100,
            'has_reasoning': any(word in response_lower for word in ['because', 'since', 'due to', 'reason']),
            'has_specific_info': bool(re.search(r'\b\d+\b', response)) or any(word in response_lower for word in ['when', 'where', 'date']),
            'has_comparison': any(word in response_lower for word in ['than', 'versus', 'compared', 'while', 'whereas']),
            'has_enumeration': bool(re.search(r'\b\d+[\.\)]\s', response)) or any(word in response_lower for word in ['first', 'second', 'finally'])
        }
        
        return elements
    
    def _addresses_requirement(self, requirement: str, response_elements: dict) -> bool:
        """
        Check if response addresses a specific requirement
        """
        mapping = {
            'definition_or_identification': response_elements['has_definition'],
            'explanation_or_process': response_elements['has_explanation'],
            'reasoning_or_cause': response_elements['has_reasoning'],
            'specific_information': response_elements['has_specific_info'],
            'comparison': response_elements['has_comparison'],
            'enumeration': response_elements['has_enumeration'],
            'general_information': True
        }
        
        return mapping.get(requirement, False)
    
    def _fallback_relevance(self, prompt: str, generated: str) -> float:
        """
        Fallback relevance calculation when embedding model is unavailable
        """
        prompt_words = set(self._normalize_text(prompt).split())
        response_words = set(self._normalize_text(generated).split())
        
        if not prompt_words:
            return 0.5
        
        overlap = len(prompt_words & response_words) / len(prompt_words)
        return min(1.0, overlap * 1.5)
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison
        """
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _generate_detailed_remarks(self, overall_score: float, direct_relevance: float, 
                                 topical_relevance: float, completeness_score: float, focus_score: float,
                                 metrics: Dict[str, Any], prompt: str, generated: str, context: str) -> str:
        """
        Generate comprehensive explanatory remarks for answer relevance score
        """
        remarks = []
        
        # Main score with percentage
        remarks.append(f"Answer Relevance Score: {overall_score * 100:.2f}%")
        
        # Component breakdown
        remarks.append(f"Component Breakdown:")
        remarks.append(f"  • Direct Relevance: {direct_relevance * 100:.2f}%")
        remarks.append(f"  • Topical Relevance: {topical_relevance * 100:.2f}%")
        remarks.append(f"  • Completeness: {completeness_score * 100:.2f}%")
        remarks.append(f"  • Focus: {focus_score * 100:.2f}%")
        
        # Prompt analysis
        remarks.append(f"Prompt Analysis:")
        remarks.append(f"  • Prompt length: {metrics['prompt_word_count']} words")
        remarks.append(f"  • Question type: {', '.join(metrics['question_type'])}")
        remarks.append(f"  • Is question: {'Yes' if metrics['is_question'] else 'No'}")
        remarks.append(f"  • Question words: {metrics['question_words']}")
        remarks.append(f"  • Prompt topics: {metrics['prompt_topics']}")
        
        # Response analysis
        remarks.append(f"Response Analysis:")
        remarks.append(f"  • Response length: {metrics['generated_word_count']} words")
        remarks.append(f"  • Length ratio: {metrics['response_length_ratio']:.2f}")
        remarks.append(f"  • Response topics: {metrics['generated_topics']}")
        remarks.append(f"  • Common topics: {metrics['common_topics']}")
        
        # Context analysis
        if metrics['has_context']:
            remarks.append(f"Context Analysis:")
            remarks.append(f"  • Context topics: {metrics['context_topics']}")
            remarks.append(f"  • Context usage: {metrics['context_usage'] * 100:.1f}%")
        else:
            remarks.append("Context Analysis: No context provided")
        
        # Overall assessment
        if overall_score >= 0.8:
            assessment = "Highly relevant response that directly and comprehensively addresses the prompt"
        elif overall_score >= 0.6:
            assessment = "Good relevance with strong alignment to prompt requirements"
        elif overall_score >= 0.4:
            assessment = "Moderately relevant response with some alignment issues"
        else:
            assessment = "Low relevance with significant gaps in addressing the prompt"
        
        remarks.append(f"Assessment: {assessment}")
        
        # Component-specific analysis
        best_component = max(direct_relevance, topical_relevance, completeness_score, focus_score)
        worst_component = min(direct_relevance, topical_relevance, completeness_score, focus_score)
        
        if direct_relevance == best_component and direct_relevance > 0.7:
            remarks.append("Strength: Excellent direct semantic alignment with the prompt")
        elif topical_relevance == best_component and topical_relevance > 0.7:
            remarks.append("Strength: Strong topical coverage and thematic relevance")
        elif completeness_score == best_component and completeness_score > 0.7:
            remarks.append("Strength: Comprehensive response addressing all prompt requirements")
        elif focus_score == best_component and focus_score > 0.7:
            remarks.append("Strength: Well-focused response staying on topic")
        
        # Weakness identification
        if direct_relevance == worst_component and direct_relevance < 0.5:
            remarks.append("Weakness: Poor direct semantic connection to the prompt")
        elif topical_relevance == worst_component and topical_relevance < 0.5:
            remarks.append("Weakness: Limited topical alignment with prompt themes")
        elif completeness_score == worst_component and completeness_score < 0.5:
            remarks.append("Weakness: Incomplete addressing of prompt requirements")
        elif focus_score == worst_component and focus_score < 0.5:
            remarks.append("Weakness: Unfocused response with excessive tangential content")
        
        # Length and appropriateness analysis
        length_ratio = metrics['response_length_ratio']
        if length_ratio < 0.5 and completeness_score < 0.6:
            remarks.append("Length analysis: Response may be too brief to adequately address the prompt")
        elif length_ratio > 5.0 and focus_score < 0.6:
            remarks.append("Length analysis: Response may be too verbose, potentially diluting relevance")
        elif 1.0 <= length_ratio <= 3.0 and overall_score > 0.7:
            remarks.append("Length analysis: Appropriate response length for comprehensive coverage")
        
        # Question type specific analysis
        question_types = metrics['question_type']
        if 'definition_or_identification' in question_types:
            response_elements = self._analyze_response_elements(generated)
            if response_elements['has_definition']:
                remarks.append("Question handling: Successfully provides definition/identification as requested")
            else:
                remarks.append("Question handling: May lack clear definition/identification for 'what/which' question")
        
        if 'explanation_or_process' in question_types:
            if metrics['generated_word_count'] > 50:
                remarks.append("Question handling: Provides substantial explanation as appropriate for 'how/explain' question")
            else:
                remarks.append("Question handling: May be too brief for explanation-type question")
        
        # Topic coverage analysis
        if metrics['prompt_topics'] > 0:
            topic_coverage = metrics['common_topics'] / metrics['prompt_topics']
            if topic_coverage > 0.8:
                remarks.append("Topic coverage: Excellent coverage of prompt topics")
            elif topic_coverage > 0.5:
                remarks.append("Topic coverage: Good coverage of most prompt topics")
            elif topic_coverage > 0.3:
                remarks.append("Topic coverage: Partial coverage of prompt topics")
            else:
                remarks.append("Topic coverage: Limited coverage of prompt topics")
        
        # Context utilization
        if metrics['has_context'] and metrics['context_usage'] > 0:
            if metrics['context_usage'] > 0.6:
                remarks.append("Context utilization: Effectively incorporates contextual information")
            elif metrics['context_usage'] > 0.3:
                remarks.append("Context utilization: Moderate use of available context")
            else:
                remarks.append("Context utilization: Limited use of available contextual information")
        elif metrics['has_context']:
            remarks.append("Context utilization: Available context not effectively utilized")
        
        # Improvement suggestions
        if overall_score < 0.7:
            suggestions = []
            if direct_relevance < 0.6:
                suggestions.append("improve direct semantic alignment with the prompt")
            if topical_relevance < 0.6:
                suggestions.append("better address the key topics and themes")
            if completeness_score < 0.6:
                suggestions.append("ensure all aspects of the prompt are addressed")
            if focus_score < 0.6:
                suggestions.append("maintain better focus and reduce tangential content")
            if metrics['common_topics'] < metrics['prompt_topics'] * 0.5:
                suggestions.append("cover more of the specific topics mentioned in the prompt")
            if metrics['has_context'] and metrics['context_usage'] < 0.4:
                suggestions.append("better utilize the provided contextual information")
            
            if suggestions:
                remarks.append(f"Suggestions: {', '.join(suggestions)}")
        
        # Quality indicators
        quality_indicators = []
        if overall_score > 0.8:
            quality_indicators.append("high overall relevance")
        if metrics['common_topics'] == metrics['prompt_topics'] and metrics['prompt_topics'] > 0:
            quality_indicators.append("complete topic coverage")
        if completeness_score > 0.8:
            quality_indicators.append("comprehensive response")
        if focus_score > 0.8:
            quality_indicators.append("well-focused content")
        if metrics['has_context'] and metrics['context_usage'] > 0.7:
            quality_indicators.append("effective context integration")
        
        if quality_indicators:
            remarks.append(f"Quality indicators: {', '.join(quality_indicators)}")
        
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
                'direct_relevance': 'Semantic similarity to prompt (40%)',
                'topical_relevance': 'Topic overlap with context (25%)',
                'completeness': 'Addresses all prompt requirements (25%)',
                'focus': 'Stays on topic without tangents (10%)'
            }
        }