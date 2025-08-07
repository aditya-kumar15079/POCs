"""
NLP Metrics Package

Contains implementations of various NLP evaluation metrics:
- BLEU: N-gram overlap metric
- ROUGE: Recall-oriented understanding metric
- METEOR: Metric considering synonyms and stemming
- BERT Score: Semantic similarity using BERT embeddings
- Accuracy: Factual correctness metric
- Answer Relevance: Relevance to prompt metric
- Toxicity: Harmful content detection metric
"""

from .bleu_metric import BLEUMetric
from .rouge_metric import ROUGEMetric
from .meteor_metric import METEORMetric
from .bert_score_metric import BERTScoreMetric
from .accuracy_metric import AccuracyMetric
from .answer_relevance_metric import AnswerRelevanceMetric
from .toxicity_metric import ToxicityMetric

__all__ = [
    'BLEUMetric',
    'ROUGEMetric',
    'METEORMetric',
    'BERTScoreMetric',
    'AccuracyMetric',
    'AnswerRelevanceMetric',
    'ToxicityMetric'
]