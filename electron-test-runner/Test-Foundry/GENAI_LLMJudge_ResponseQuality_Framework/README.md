# LLM Judge Framework

A comprehensive framework for evaluating GenAI responses using LLM as a judge for quality parameters such as accuracy, coherence, relevance, faithfulness, bias, and toxicity.

## Features

- **LLM Judge**: Uses OpenAI or Azure OpenAI models to evaluate GenAI responses
- **Flexible Configuration**: Configure evaluation parameters via YAML or Excel
- **Multiple Quality Metrics**: Evaluate responses on accuracy, coherence, relevance, faithfulness, bias, and toxicity
- **Color-coded Reports**: Generate detailed Excel reports with color-coded scores and remarks
- **Customizable Scoring**: Define your own scoring categories and thresholds

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/llm-judge-framework.git
   cd llm-judge-framework
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure your API keys in `config/config.yaml`

## Usage

### Basic Usage

1. Place your test cases in an Excel file in the `input` folder (see template format below)

2. Run the framework:
   ```
   python -m src.main
   ```

3. Find the evaluation report in the `output` folder

### Configuration

#### YAML Configuration

Edit `config/config.yaml` to configure:
- LLM provider (OpenAI or Azure OpenAI)
- API keys and model parameters
- Input/output paths
- Enabled metrics
- Scoring categories

#### Excel Configuration

In your input Excel file, you can include a "Metrics" sheet to enable/disable specific metrics:

| Metric       | Enabled |
|--------------|---------|
| accuracy     | TRUE    |
| coherence    | TRUE    |
| relevance    | FALSE   |
| faithfulness | TRUE    |
| bias         | TRUE    |
| toxicity     | FALSE   |

### Input Format

Create an Excel file with a "TestCases" sheet containing:

| TestID | Prompt | ReferenceAnswer | GeneratedAnswer |
|--------|--------|-----------------|-----------------|
| 1      | What is the capital of France? | The capital of France is Paris. | Paris is the capital city of France. |

## Output

The framework generates a color-coded Excel report with:
- Original test cases
- Scores for each metric (0-100)
- Detailed remarks explaining each score
- Color-coding based on score ranges:
  - 90-100: Green (Excellent)
  - 75-89: Light Green (Good)
  - 50-74: Amber (Moderate)
  - 0-49: Red (Poor)

## Development

### Running Tests

```
python -m unittest discover tests
```

### Project Structure

```
llm-judge-framework/
├── config/
│   └── config.yaml
├── input/
│   └── test_cases.xlsx
├── output/
│   └── (generated reports)
├── src/
│   ├── evaluators/
│   ├── llm/
│   ├── utils/
│   └── main.py
├── tests/
│   ├── test_evaluators.py
│   ├── test_llm.py
│   └── test_utils.py
├── requirements.txt
└── README.md
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.