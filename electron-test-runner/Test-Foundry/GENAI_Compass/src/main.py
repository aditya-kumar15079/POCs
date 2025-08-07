#!/usr/bin/env python3
"""
NLP Evaluation Framework - Main Application
Evaluates generated responses using multiple NLP metrics
"""

import sys
import os
import argparse
from pathlib import Path
import traceback

# Fix import paths - add parent directory to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

# Import modules directly (avoiding relative imports issue)
from data_loader import DataLoader
from evaluator import MetricsEvaluator
from report_generator import ReportGenerator

def main():
    """
    Main application entry point
    """
    parser = argparse.ArgumentParser(
        description="NLP Evaluation Framework - Evaluate generated responses using multiple metrics"
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help="Path to input Excel file with test cases"
    )
    
    parser.add_argument(
        '--config', '-c',
        default="../config/metrics_config.yaml",
        help="Path to configuration file (default: ../config/metrics_config.yaml)"
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    try:
        print("=" * 60)
        print("NLP EVALUATION FRAMEWORK")
        print("=" * 60)
        print(f"Input file: {args.input}")
        print(f"Config file: {args.config}")
        print(f"Output directory: C:/GENAI_Compass/Reports")
        print("=" * 60)
        
        # Step 1: Load and validate data
        print("\n📁 STEP 1: Loading and validating data...")
        data_loader = DataLoader(args.input)
        df = data_loader.load_data()
        
        # Get data summary
        summary = data_loader.get_data_summary(df)
        print(f"📊 Data Summary:")
        print(f"   • Total rows: {summary['total_rows']}")
        print(f"   • Enabled tests: {summary['enabled_tests']}")
        print(f"   • Tests with context: {summary['has_context']}")
        print(f"   • Avg prompt length: {summary['average_prompt_length']:.0f} chars")
        print(f"   • Avg reference length: {summary['average_reference_length']:.0f} chars")
        print(f"   • Avg generated length: {summary['average_generated_length']:.0f} chars")
        
        # Check data quality
        warnings = data_loader.validate_data_quality(df)
        if warnings:
            print("⚠ Data Quality Warnings:")
            for warning in warnings:
                print(f"   • {warning}")
        
        # Step 2: Initialize evaluator
        print("\n🔧 STEP 2: Initializing metrics evaluator...")
        evaluator = MetricsEvaluator(args.config)
        
        # Validate dependencies
        dep_warnings = evaluator.validate_dependencies(df)
        if dep_warnings:
            print("⚠ Dependency Warnings:")
            for warning in dep_warnings:
                print(f"   • {warning}")
        
        # Step 3: Run evaluation
        print("\n📊 STEP 3: Running metrics evaluation...")
        results_df = evaluator.evaluate_dataset(df)
        
        # Step 4: Generate summary statistics
        print("\n📈 STEP 4: Calculating summary statistics...")
        summary_stats = evaluator.get_summary_statistics(results_df)
        metadata = evaluator.get_metric_metadata()
        
        print(f"📋 Evaluation Summary:")
        print(f"   • Cases evaluated: {summary_stats['total_cases']}")
        print(f"   • Average overall score: {summary_stats['overall_stats']['mean_score'] * 100:.2f}%")
        print(f"   • Score range: {summary_stats['overall_stats']['min_score'] * 100:.2f}% - {summary_stats['overall_stats']['max_score'] * 100:.2f}%")
        
        # Grade distribution
        grade_dist = summary_stats['grade_distribution']
        print(f"   • Grade distribution: {dict(grade_dist)}")
        
        # Top performing metrics
        metric_avgs = summary_stats['metric_averages']
        if metric_avgs:
            best_metric = max(metric_avgs.items(), key=lambda x: x[1]['mean'])
            worst_metric = min(metric_avgs.items(), key=lambda x: x[1]['mean'])
            print(f"   • Best performing metric: {best_metric[0]} ({best_metric[1]['mean'] * 100:.2f}%)")
            print(f"   • Lowest performing metric: {worst_metric[0]} ({worst_metric[1]['mean'] * 100:.2f}%)")
        
        # Step 5: Generate comprehensive report with new naming
        print("\n📄 STEP 5: Generating comprehensive report...")
        report_generator = ReportGenerator(evaluator.config)
        
        # Extract input filename for report naming
        input_filename = Path(args.input).name
        report_generator.generate_report(
            results_df=results_df,
            summary_stats=summary_stats,
            metadata=metadata,
            input_filename=input_filename
        )
        
        print("\n✅ EVALUATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 Enhanced report generated in: C:/GENAI_Compass/Reports")
        print(f"📈 {summary_stats['total_cases']} test cases evaluated")
        print(f"🎯 Average score: {summary_stats['overall_stats']['mean_score'] * 100:.2f}%")
        print("=" * 60)
        
        # Show quick insights
        print("\n💡 QUICK INSIGHTS:")
        
        # Performance insights
        avg_score = summary_stats['overall_stats']['mean_score']
        if avg_score >= 0.8:
            print("🟢 Overall performance is EXCELLENT")
        elif avg_score >= 0.6:
            print("🟡 Overall performance is GOOD")
        else:
            print("🔴 Overall performance NEEDS IMPROVEMENT")
        
        # Metric-specific insights
        if metric_avgs:
            for metric_name, avg_data in metric_avgs.items():
                score = avg_data['mean']
                metric_meta = metadata.get(metric_name, {})
                weight = metric_meta.get('weight', 0)
                
                if weight > 0.15:  # High weight metrics
                    if score < 0.6:
                        print(f"⚠ Focus on improving {metric_name.replace('_', ' ')} (high weight: {weight*100:.1f}%, low score: {score*100:.1f}%)")
        
        print("\n📋 REPORT FEATURES:")
        print("   • All scores displayed as percentages for easier interpretation")
        print("   • Detailed remarks with breakdown analysis for each metric")
        print("   • Toxicity shown as 'Safety Score' (higher = safer)")
        print("   • Color-coded performance indicators")
        print("   • 5 comprehensive analysis sheets")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠ Evaluation interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        if args.verbose:
            print("\nFull traceback:")
            traceback.print_exc()
        return 1

def create_sample_input():
    """
    Create a sample input Excel file for testing
    """
    import pandas as pd
    
    sample_data = {
        'Prompt': [
            'What is the capital of France?',
            'Explain how photosynthesis works.',
            'What are the benefits of renewable energy?',
            'How does machine learning work?',
            'What is the largest planet in our solar system?'
        ],
        'Reference_Response': [
            'The capital of France is Paris.',
            'Photosynthesis is the process by which plants convert sunlight, carbon dioxide, and water into glucose and oxygen.',
            'Renewable energy benefits include reduced greenhouse gas emissions, energy independence, and sustainable development.',
            'Machine learning uses algorithms to find patterns in data and make predictions or decisions without explicit programming.',
            'Jupiter is the largest planet in our solar system.'
        ],
        'Generated_Response': [
            'Paris is the capital city of France.',
            'Plants use sunlight to make food through photosynthesis, combining CO2 and water to create sugar.',
            'Renewable energy sources like solar and wind help reduce pollution and provide clean electricity.',
            'Machine learning algorithms learn from data to make predictions and automate decision-making processes.',
            'The largest planet in our solar system is Jupiter, which is a gas giant.'
        ],
        'Context': [
            'Geography question about European capitals',
            'Biology topic about plant processes',
            'Environmental science and energy policy',
            'Computer science and artificial intelligence',
            'Astronomy and planetary science'
        ],
        'Enable_Flag': ['Y', 'Y', 'Y', 'Y', 'Y']
    }
    
    df = pd.DataFrame(sample_data)
    sample_path = "../data/input/sample_responses.xlsx"
    
    os.makedirs(os.path.dirname(sample_path), exist_ok=True)
    df.to_excel(sample_path, index=False)
    
    print(f"✓ Sample input file created: {sample_path}")
    return sample_path

if __name__ == "__main__":
    # Check if user wants to create sample data
    if len(sys.argv) > 1 and sys.argv[1] == 'create-sample':
        create_sample_input()
        sys.exit(0)
    
    sys.exit(main())