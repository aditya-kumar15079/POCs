# NLP Evaluation Framework

A comprehensive framework for evaluating generated text responses using multiple NLP metrics including BLEU, ROUGE, METEOR, BERT Score, Accuracy, Answer Relevance, and Toxicity scoring.

## Features

- **7 NLP Metrics**: BLEU, ROUGE, METEOR, BERT Score, Accuracy, Answer Relevance, Toxicity
- **Configurable Weights**: Set custom weights for each metric in the overall score
- **Excel Input/Output**: Easy-to-use Excel interface for data input and comprehensive reporting
- **Color-Coded Reports**: Visual indicators for performance levels
- **Detailed Analysis**: Individual metric scores with explanatory remarks
- **Dependency Tracking**: Clear documentation of required inputs for each metric
- **Flexible Configuration**: YAML-based configuration for easy customization

## Quick Start

### Installation

1. Clone or download the framework
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

1. **Prepare your data** in Excel format with columns:
   - `Prompt`: The original question/instruction
   - `Reference_Response`: Expected/correct answer
   - `Generated_Response`: AI-generated response to evaluate
   - `Context`: Additional context (optional)
   - `Enable_Flag`: Y/N to run the test (optional, defaults to Y)

2. **Run evaluation**:
```bash
python src/main.py --input data/input/your_responses.xlsx
```

3. **View results** in the generated Excel report at `data/output/evaluation_report.xlsx`

### Create Sample Data

Generate sample input file for testing:
```bash
python src/main.py create-sample
```

## Configuration

Edit `config/metrics_config.yaml` to customize:

- **Enable/disable metrics**: Set `enabled: true/false`
- **Adjust weights**: Modify weight values (must sum to 1.0)
- **Set thresholds**: Define good/acceptable/poor score ranges
- **Customize colors**: Change color scheme for reports

### Example Configuration

```yaml
metrics:
  bleu:
    enabled: true
    weight: 0.15
    thresholds:
      good: 0.7
      acceptable: 0.5
      poor: 0.0
```

## Metrics Overview

| Metric | Description | Range | Dependencies |
|--------|-------------|-------|--------------|
| **BLEU** | N-gram overlap between generated and reference text | 0-1 | Reference, Generated |
| **ROUGE** | Recall-oriented understanding evaluation | 0-1 | Reference, Generated |
| **METEOR** | Considers stemming, synonymy, and word order | 0-1 | Reference, Generated |
| **BERT Score** | Semantic similarity using BERT embeddings | 0-1 | Reference, Generated |
| **Accuracy** | Factual correctness assessment | 0-1 | Reference, Generated |
| **Answer Relevance** | How well response addresses the prompt | 0-1 | Prompt, Generated, Context |
| **Toxicity** | Harmful content detection (lower is better) | 0-1 | Generated |

## Output Reports

The framework generates a comprehensive Excel report with multiple sheets:

### 1. Detailed Results
- Individual test case scores
- Color-coded performance indicators
- Detailed remarks for each metric

### 2. Summary Statistics
- Overall performance metrics
- Grade distribution
- Individual metric averages
- Performance ratings

### 3. Metrics Information
- Metric descriptions and configurations
- Weight assignments
- Threshold definitions

### 4. Dependencies
- Required input columns for each metric
- Column mapping guide

### 5. Score Interpretation
- Performance level definitions
- Color coding explanations
- Improvement guidelines

## Advanced Usage

### Command Line Options

```bash
python src/main.py \
  --input path/to/input.xlsx \
  --config path/to/config.yaml \
  --output path/to/output.xlsx \
  --verbose
```

### Programmatic Usage

```python
from src.data_loader import DataLoader
from src.evaluator import MetricsEvaluator
from src.report_generator import ReportGenerator

# Load data
loader = DataLoader("input.xlsx")
df = loader.load_data()

# Evaluate
evaluator = MetricsEvaluator("config.yaml")
results = evaluator.evaluate_dataset(df)

# Generate report
generator = ReportGenerator(evaluator.config)
generator.generate_report(results, summary, metadata, "output.xlsx")
```

## Understanding Scores

### Color Coding
- 🟢 **Green**: Good performance (meets thresholds)
- 🟡 **Yellow**: Acceptable performance (moderate scores)
- 🔴 **Red**: Poor performance (below thresholds)

### Overall Score Calculation
Overall score = Σ(metric_score × metric_weight) for all enabled metrics

### Toxicity Scoring
⚠️ **Note**: Toxicity uses reverse scoring - lower values indicate better (safer) content.

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Install all requirements from `requirements.txt`
2. **NLTK Data**: Framework automatically downloads required NLTK data
3. **Memory Issues**: Use CPU-only mode for BERT Score if GPU memory is limited
4. **Empty Context**: Context column is optional for Answer Relevance

### Performance Tips

- Use smaller batch sizes for large datasets
- Enable only necessary metrics to improve speed
- Ensure adequate memory for BERT-based metrics

## Framework Architecture

```
nlp_evaluation_framework/
├── config/                 # Configuration files
├── src/                   # Source code
│   ├── metrics/          # Individual metric implementations
## Framework Architecture

```
nlp_evaluation_framework/
├── config/                 # Configuration files
├── src/                   # Source code
│   ├── metrics/          # Individual metric implementations
│   ├── data_loader.py    # Excel data loading and validation
│   ├── evaluator.py      # Main evaluation orchestrator
│   ├── report_generator.py # Excel report generation
│   └── main.py          # Command-line interface
├── data/
│   ├── input/           # Input Excel files
│   └── output/          # Generated reports
└── requirements.txt     # Python dependencies
```

## Extending the Framework

### Adding New Metrics

1. Create new metric class in `src/metrics/`:
```python
class CustomMetric:
    def __init__(self):
        self.name = "Custom"
        self.description = "Custom metric description"
        self.dependencies = ["Required_Column"]
    
    def calculate(self, **kwargs):
        # Implement calculation logic
        return {
            'score': calculated_score,
            'remarks': 'Explanation of score'
        }
    
    def get_metadata(self):
        return {
            'name': self.name,
            'description': self.description,
            'dependencies': self.dependencies,
            'range': '[0, 1]',
            'higher_is_better': True
        }
```

2. Add to configuration file:
```yaml
metrics:
  custom:
    enabled: true
    weight: 0.1
    thresholds:
      good: 0.8
      acceptable: 0.6
      poor: 0.0
```

3. Register in evaluator's metric classes dictionary

### Customizing Reports

Modify `ReportGenerator` class to add new sheets or change formatting:
- Add new sheet methods following existing patterns
- Customize color schemes in configuration
- Modify column layouts and content

## Best Practices

### Data Preparation
- Ensure reference responses are high-quality and representative
- Include diverse test cases covering different scenarios
- Use consistent formatting and language
- Provide context when available for better relevance scoring

### Configuration
- Balance metric weights based on your use case priorities
- Set appropriate thresholds based on your quality standards
- Enable only metrics relevant to your evaluation goals
- Regularly review and adjust weights based on results

### Interpretation
- Focus on metrics with higher weights for overall improvement
- Look at individual metric scores to identify specific weaknesses
- Use remarks to understand the reasoning behind scores
- Consider the nature of your content when interpreting toxicity scores

## FAQ

### Q: Which metrics should I prioritize?
**A**: Depends on your use case:
- **Content Generation**: BERT Score, Answer Relevance, Toxicity
- **Translation**: BLEU, METEOR, ROUGE
- **Summarization**: ROUGE, BERT Score, Accuracy
- **Question Answering**: Answer Relevance, Accuracy, BERT Score

### Q: How do I handle missing reference responses?
**A**: Some metrics (Answer Relevance, Toxicity) don't require reference responses. For others, you can:
- Create reference responses manually
- Use human evaluation as reference
- Disable reference-dependent metrics

### Q: Can I run evaluation on non-English text?
**A**: Most metrics support multiple languages, but performance may vary:
- **BERT Score**: Supports multilingual models
- **Toxicity**: Primarily trained on English
- **BLEU/ROUGE/METEOR**: Language-agnostic but may need language-specific tokenizers

### Q: How do I interpret conflicting metric scores?
**A**: Different metrics measure different aspects:
- High BLEU, Low BERT Score: Good word overlap, poor semantic similarity
- High Relevance, Low Accuracy: Addresses question but factually incorrect
- Low Toxicity, Low other metrics: Safe but low-quality content

### Q: What if evaluation is too slow?
**A**: Optimization strategies:
- Disable computationally expensive metrics (BERT Score)
- Use smaller/faster models
- Process smaller batches
- Run on GPU if available

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Write descriptive variable names

### Testing
- Test new metrics with various input types
- Validate edge cases (empty strings, very long text)
- Ensure backward compatibility
- Test configuration changes

### Documentation
- Update README for new features
- Add inline comments for complex logic
- Document configuration options
- Provide usage examples

## License

This framework is provided as-is for educational and research purposes. Please ensure compliance with individual metric library licenses:

- NLTK: Apache License 2.0
- Transformers: Apache License 2.0
- BERT Score: MIT License
- Detoxify: Apache License 2.0

## Support

For issues and questions:
1. Check this README and documentation
2. Review error messages and verbose output
3. Ensure all dependencies are properly installed
4. Verify input data format and structure

## Changelog

### Version 1.0.0
- Initial release with 7 core metrics
- Excel input/output support
- Comprehensive reporting with multiple sheets
- Configurable weights and thresholds
- Color-coded performance indicators
- Detailed score interpretation and remarks
- Modular architecture for easy extension
python main.py --input ../data/input/KRAIOS.xlsx --config ../config/metrics_config.yaml