import pandas as pd
import numpy as np
import yaml
from typing import Dict, List, Any, Tuple
import importlib
import sys
import os
from pathlib import Path
import logging

class MetricsEvaluator:
    """
    FINAL WORKING: Keep original numeric values, let report generator handle conversion
    """
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.metrics = self._initialize_metrics()
        self.logger = self._setup_logging()
        
        # Validate weights on initialization
        self._validate_weights()
        
    def _validate_weights(self):
        """Validate that weights are properly configured"""
        total_weight = 0.0
        enabled_metrics = []
        
        for metric_name, metric_config in self.config['metrics'].items():
            if metric_config.get('enabled', False):
                weight = metric_config.get('weight', 0.0)
                total_weight += weight
                enabled_metrics.append(f"{metric_name}={weight}")
        
        self.logger.info(f"Weight validation - Total: {total_weight}, Enabled: {enabled_metrics}")
        
        if total_weight == 0:
            raise Exception("CRITICAL ERROR: Total metric weights sum to zero! Cannot calculate overall score.")
        
        if total_weight < 0.95 or total_weight > 1.05:
            self.logger.warning(f"Warning: Total weights ({total_weight}) should sum to approximately 1.0")
    
    def _setup_logging(self):
        """Setup logging for execution history"""
        logs_dir = Path("C:/GENAI_Compass/Reports/logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = logs_dir / f"evaluation_log_{timestamp}.txt"
        
        logger = logging.getLogger('NLPEvaluator')
        logger.setLevel(logging.DEBUG)
        
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        file_handler = logging.FileHandler(log_file, mode='w')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        logger.info("="*60)
        logger.info("NLP EVALUATION FRAMEWORK - FINAL WORKING VERSION")
        logger.info("="*60)
        logger.info(f"Log file: {log_file}")
        logger.info(f"Config file: {self.config_path}")
        
        return logger
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            print(f"✓ Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            raise Exception(f"Error loading config: {str(e)}")
    
    def _initialize_metrics(self) -> Dict[str, Any]:
        """Initialize metric instances based on configuration"""
        metrics = {}
        
        metric_classes = {
            'bleu': 'BLEUMetric',
            'rouge': 'ROUGEMetric',
            'meteor': 'METEORMetric',
            'bert_score': 'BERTScoreMetric',
            'accuracy': 'AccuracyMetric',
            'answer_relevance': 'AnswerRelevanceMetric',
            'toxicity': 'ToxicityMetric'
        }
        
        for metric_name, class_name in metric_classes.items():
            if self.config['metrics'].get(metric_name, {}).get('enabled', False):
                try:
                    module_name = f"metrics.{metric_name}_metric"
                    module = importlib.import_module(module_name)
                    metric_class = getattr(module, class_name)
                    metrics[metric_name] = metric_class()
                    print(f"✓ {class_name} initialized")
                    if hasattr(self, 'logger'):
                        self.logger.info(f"Successfully initialized {class_name}")
                except Exception as e:
                    print(f"⚠ Failed to initialize {class_name}: {str(e)}")
                    if hasattr(self, 'logger'):
                        self.logger.warning(f"Failed to initialize {class_name}: {str(e)}")
                    continue
        
        if not metrics:
            error_msg = "No metrics were successfully initialized"
            if hasattr(self, 'logger'):
                self.logger.error(error_msg)
            raise Exception(error_msg)
        
        if hasattr(self, 'logger'):
            self.logger.info(f"Total metrics initialized: {len(metrics)}")
            
        return metrics
    
    def evaluate_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        FINAL WORKING: Keep all scores as NUMERIC values (0.0 to 1.0)
        Let the report generator handle percentage conversion
        """
        self.logger.info(f"FINAL WORKING: Starting evaluation of {len(df)} test cases...")
        
        # Get enabled test cases
        enabled_df = df[df['Enable_Flag'] == 'Y'].copy()
        enabled_df = enabled_df.reset_index(drop=True)
        
        self.logger.info(f"Processing {len(enabled_df)} enabled test cases")
        print(f"Evaluating {len(enabled_df)} enabled test cases")
        
        # Initialize results with explicit dtypes
        results_data = []
        
        # Process each test case
        for i in range(len(enabled_df)):
            row = enabled_df.iloc[i]
            case_num = i + 1
            
            print(f"Evaluating test case {case_num}/{len(enabled_df)}")
            self.logger.info(f"=== CASE {case_num} ===")
            
            # Prepare input data
            input_data = {
                'prompt': str(row['Prompt']),
                'reference': str(row['Reference_Response']),
                'generated': str(row['Generated_Response']),
                'context': str(row.get('Context', ''))
            }
            
            # Initialize result row with original data
            result_row = row.to_dict()
            
            # Calculate metrics
            metric_results = self._calculate_metrics_for_case(input_data)
            
            # Store individual metric results as NUMERIC values
            for metric_name, result in metric_results.items():
                score = self._ensure_valid_numeric_score(result.get('score', 0.0))
                remarks = str(result.get('remarks', ''))
                
                result_row[f'{metric_name}_score'] = score  # Keep as numeric (0.0 to 1.0)
                result_row[f'{metric_name}_remarks'] = remarks
                
                self.logger.info(f"  {metric_name}: {score:.4f}")
            
            # Calculate overall score
            overall_score = self._calculate_overall_score_working(metric_results, case_num)
            
            # Ensure overall score is valid NUMERIC
            if overall_score is None or pd.isna(overall_score) or overall_score <= 0:
                # Fallback: Calculate simple average
                valid_scores = [self._ensure_valid_numeric_score(result.get('score', 0.0)) 
                              for result in metric_results.values()]
                overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.5
                self.logger.warning(f"  Used fallback average: {overall_score:.4f}")
            
            # Store as NUMERIC value (not percentage!)
            overall_score = self._ensure_valid_numeric_score(overall_score)
            result_row['overall_score'] = overall_score  # Keep as 0.0 to 1.0
            result_row['overall_grade'] = self._get_grade(overall_score)
            
            self.logger.info(f"  ✓ FINAL Overall Score: {overall_score:.4f} (Grade: {result_row['overall_grade']})")
            
            results_data.append(result_row)
        
        # Create results DataFrame
        results_df = pd.DataFrame(results_data)
        
        # Ensure all score columns are numeric
        score_columns = [col for col in results_df.columns if '_score' in col or col == 'overall_score']
        for col in score_columns:
            results_df[col] = pd.to_numeric(results_df[col], errors='coerce').fillna(0.0)
        
        # Final verification - all scores should be numeric between 0 and 1
        self.logger.info("=== FINAL VERIFICATION ===")
        self.logger.info(f"Overall score dtype: {results_df['overall_score'].dtype}")
        self.logger.info(f"Overall score range: {results_df['overall_score'].min():.4f} - {results_df['overall_score'].max():.4f}")
        self.logger.info(f"All overall scores are numeric: {results_df['overall_score'].dtype.kind in 'biufc'}")
        
        for i, score in enumerate(results_df['overall_score']):
            self.logger.info(f"  Row {i}: {score:.4f} (type: {type(score)})")
        
        self.logger.info("✓ FINAL WORKING: Evaluation completed with numeric scores")
        print("✓ Evaluation completed")
        return results_df
    
    def _ensure_valid_numeric_score(self, score) -> float:
        """Ensure score is a valid float between 0 and 1"""
        try:
            if pd.isna(score) or score is None:
                return 0.0
            
            # If it's already a string percentage, extract the number
            if isinstance(score, str) and '%' in score:
                # Extract number from percentage string
                num_str = score.replace('%', '').strip()
                return max(0.0, min(1.0, float(num_str) / 100.0))
            
            score = float(score)
            return max(0.0, min(1.0, score))
        except (ValueError, TypeError):
            return 0.0
    
    def _calculate_metrics_for_case(self, input_data: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Calculate all enabled metrics for a single test case"""
        results = {}
        
        for metric_name, metric_instance in self.metrics.items():
            try:
                if not self.config['metrics'].get(metric_name, {}).get('enabled', False):
                    continue
                
                dependencies = metric_instance.dependencies
                kwargs = {}
                
                for dep in dependencies:
                    if dep == 'Prompt':
                        kwargs['prompt'] = input_data['prompt']
                    elif dep == 'Reference_Response':
                        kwargs['reference'] = input_data['reference']
                    elif dep == 'Generated_Response':
                        kwargs['generated'] = input_data['generated']
                    elif dep == 'Context':
                        kwargs['context'] = input_data['context']
                
                result = metric_instance.calculate(**kwargs)
                
                # Validate result
                if not isinstance(result, dict) or 'score' not in result:
                    result = {'score': 0.0, 'remarks': 'Invalid result structure'}
                
                results[metric_name] = result
                
            except Exception as e:
                self.logger.error(f"Error calculating {metric_name}: {str(e)}")
                results[metric_name] = {
                    'score': 0.0,
                    'remarks': f'Calculation error: {str(e)}'
                }
        
        return results
    
    def _calculate_overall_score_working(self, metric_results: Dict[str, Dict[str, Any]], case_num: int) -> float:
        """Calculate overall score and return NUMERIC value (not percentage)"""
        try:
            self.logger.debug(f"=== OVERALL SCORE CALCULATION (Case {case_num}) ===")
            
            total_weighted_score = 0.0
            total_weight = 0.0
            processed_metrics = []
            
            # Process each metric
            for metric_name, result in metric_results.items():
                try:
                    # Get configuration
                    metric_config = self.config['metrics'].get(metric_name, {})
                    if not metric_config.get('enabled', False):
                        continue
                    
                    weight = float(metric_config.get('weight', 0.0))
                    if weight <= 0:
                        continue
                    
                    # Get and validate score
                    raw_score = result.get('score', 0.0)
                    score = self._ensure_valid_numeric_score(raw_score)
                    
                    # Apply reverse scoring if needed
                    if metric_config.get('reverse_scoring', False):
                        score = 1.0 - score
                    
                    # Calculate contribution
                    contribution = score * weight
                    total_weighted_score += contribution
                    total_weight += weight
                    processed_metrics.append(metric_name)
                    
                    self.logger.debug(f"    {metric_name}: score={score:.4f}, weight={weight:.4f}, contrib={contribution:.4f}")
                    
                except Exception as e:
                    self.logger.error(f"    Error processing {metric_name}: {e}")
                    continue
            
            self.logger.debug(f"    Total weighted score: {total_weighted_score:.6f}")
            self.logger.debug(f"    Total weight: {total_weight:.6f}")
            
            # Calculate final score
            if total_weight > 0 and len(processed_metrics) > 0:
                overall_score = total_weighted_score / total_weight
                self.logger.debug(f"    Calculated overall: {overall_score:.6f}")
                return self._ensure_valid_numeric_score(overall_score)
            else:
                # Fallback: simple average
                valid_scores = [self._ensure_valid_numeric_score(result.get('score', 0.0)) 
                              for result in metric_results.values()]
                if valid_scores:
                    fallback_score = sum(valid_scores) / len(valid_scores)
                    self.logger.debug(f"    Fallback average: {fallback_score:.6f}")
                    return fallback_score
                else:
                    return 0.5
                    
        except Exception as e:
            self.logger.error(f"Critical error in overall score calculation: {e}")
            return 0.5
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        try:
            score = float(score)
            if score >= 0.9:
                return 'A+'
            elif score >= 0.8:
                return 'A'
            elif score >= 0.7:
                return 'B'
            elif score >= 0.6:
                return 'C'
            elif score >= 0.5:
                return 'D'
            else:
                return 'F'
        except:
            return 'F'
    
    def get_summary_statistics(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary statistics with guaranteed numeric values"""
        self.logger.info("Calculating summary statistics...")
        
        # Ensure overall_score is numeric
        overall_scores = pd.to_numeric(results_df['overall_score'], errors='coerce')
        overall_scores = overall_scores.fillna(0.5)
        
        summary = {
            'total_cases': int(len(results_df)),
            'overall_stats': {
                'mean_score': float(overall_scores.mean()),
                'median_score': float(overall_scores.median()),
                'std_score': float(overall_scores.std()),
                'min_score': float(overall_scores.min()),
                'max_score': float(overall_scores.max())
            },
            'grade_distribution': results_df['overall_grade'].value_counts().to_dict(),
            'metric_averages': {}
        }
        
        # Calculate metric averages
        for metric_name in self.metrics.keys():
            score_col = f'{metric_name}_score'
            if score_col in results_df.columns:
                metric_scores = pd.to_numeric(results_df[score_col], errors='coerce').fillna(0.0)
                summary['metric_averages'][metric_name] = {
                    'mean': float(metric_scores.mean()),
                    'median': float(metric_scores.median()),
                    'std': float(metric_scores.std())
                }
        
        self.logger.info(f"Summary calculated - Mean: {summary['overall_stats']['mean_score']:.4f}")
        return summary
    
    def get_metric_metadata(self) -> Dict[str, Any]:
        """Get metadata for all initialized metrics"""
        metadata = {}
        
        for metric_name, metric_instance in self.metrics.items():
            try:
                metric_meta = metric_instance.get_metadata()
                config_meta = self.config['metrics'].get(metric_name, {})
                
                metadata[metric_name] = {
                    **metric_meta,
                    'weight': config_meta.get('weight', 0.0),
                    'thresholds': config_meta.get('thresholds', {}),
                    'enabled': config_meta.get('enabled', False)
                }
                
            except Exception as e:
                self.logger.error(f"Error getting metadata for {metric_name}: {str(e)}")
                
        return metadata
    
    def validate_dependencies(self, df: pd.DataFrame) -> List[str]:
        """Validate dependencies"""
        warnings = []
        available_columns = set(df.columns)
        
        for metric_name, metric_instance in self.metrics.items():
            if not self.config['metrics'].get(metric_name, {}).get('enabled', False):
                continue
                
            dependencies = metric_instance.dependencies
            missing_deps = [dep for dep in dependencies if dep not in available_columns]
            
            if missing_deps:
                warning = f"{metric_name}: missing dependencies {missing_deps}"
                warnings.append(warning)
                self.logger.warning(warning)
        
        return warnings