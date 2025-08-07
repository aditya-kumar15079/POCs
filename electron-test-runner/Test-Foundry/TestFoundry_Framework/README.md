# TestFoundry Framework

**AI-Powered Testing Framework for Document Q&A Generation**

TestFoundry is a comprehensive, production-ready framework that automatically generates question-answer pairs and specialized test cases from various document types (PDF, Word, Excel, Text, Images) using OpenAI or Azure OpenAI.

## 🚀 Features

- **Multi-format Support**: PDF, Word (.docx/.doc), Excel (.xlsx/.xls), Text (.txt/.md), Images
- **Dual AI Provider Support**: OpenAI and Azure OpenAI with seamless switching
- **Advanced Document Processing**: OCR, table extraction, image analysis, smart chunking
- **Comprehensive Test Generation**:
  - Question-Answer pairs with difficulty levels and quality scoring
  - Adversarial testing scenarios
  - Bias detection test cases
  - Hallucination detection tests
- **Professional Excel Reports**: Multi-sheet reports with statistics, formatting, and analysis
- **Concurrent Processing**: Efficient batch processing with configurable concurrency
- **Production-Ready**: Full error handling, logging, and configuration management

## 📁 Framework Structure

```
C:\TestFoundry_Framework\
│
├── main.py                          # Main execution script
├── requirements.txt                 # Python dependencies
├── config.yaml                      # Configuration file
├── README.md                        # This documentation
│
├── src/                            # Source code
│   ├── core/                       # Core framework components
│   │   ├── document_processor.py   # Document processing coordination
│   │   ├── qa_generator.py         # Q&A generation engine
│   │   ├── test_case_generator.py  # Test case generation
│   │   ├── report_generator.py     # Excel report generation
│   │   └── config_manager.py       # Configuration management
│   │
│   ├── processors/                 # Document type processors
│   │   ├── pdf_processor.py        # PDF processing
│   │   ├── word_processor.py       # Word document processing
│   │   ├── excel_processor.py      # Excel spreadsheet processing
│   │   ├── text_processor.py       # Text file processing
│   │   └── image_processor.py      # Image processing with OCR
│   │
│   ├── ai_clients/                 # AI service clients
│   │   ├── openai_client.py        # OpenAI integration
│   │   └── azure_openai_client.py  # Azure OpenAI integration
│   │
│   └── utils/                      # Utility functions
│       ├── logger.py               # Logging configuration
│       ├── chunking.py             # Text chunking strategies
│       └── file_utils.py           # File handling utilities
│
├── prompts/                        # AI prompt templates
│   ├── pdf_prompts.yaml            # PDF-specific prompts
│   ├── word_prompts.yaml           # Word-specific prompts
│   ├── excel_prompts.yaml          # Excel-specific prompts
│   ├── text_prompts.yaml           # Text-specific prompts
│   ├── image_prompts.yaml          # Image-specific prompts
│   └── test_case_prompts.yaml      # Test case generation prompts
│
├── input/                          # Place documents here
├── output/                         # Generated reports
└── logs/                          # Application logs
```

## ⚡ Quick Start

### 1. Installation

```bash
# Clone or download the framework to C:\TestFoundry_Framework\

# Install Python dependencies
cd C:\TestFoundry_Framework
pip install -r requirements.txt

# Install additional system dependencies for OCR (Windows)
# Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
# Add Tesseract to your PATH
```

### 2. Configuration

Edit `config.yaml` to configure your AI provider:

**For OpenAI:**
```yaml
ai_service:
  provider: "openai"
  openai:
    api_key: "your_openai_api_key_here"
    model: "gpt-4-turbo-preview"
```

**For Azure OpenAI:**
```yaml
ai_service:
  provider: "azure_openai"
  azure_openai:
    api_key: "your_azure_openai_api_key_here"
    endpoint: "https://your-resource.openai.azure.com/"
    deployment_name: "gpt-4-turbo"
```

### 3. Add Documents

Place your documents in the `input/` folder:
- PDF files (.pdf)
- Word documents (.docx, .doc)
- Excel spreadsheets (.xlsx, .xls)
- Text files (.txt, .md)
- Images (.png, .jpg, .jpeg, .gif, .bmp)

### 4. Run the Framework

```bash
python main.py
```

### 5. View Results

Check the `output/` folder for:
- Comprehensive Excel report with multiple sheets
- Detailed Q&A pairs with metadata
- Test cases for adversarial, bias, and hallucination testing
- Statistics and analysis

## 🔧 Configuration Options

### Q&A Generation Settings

```yaml
qa_generation:
  enabled: true
  questions_per_document: 25      # Number of Q&A pairs per document
  concurrent_requests: 3          # Parallel AI requests
  chunk_size: 2000               # Text chunk size for processing
  chunk_overlap: 200             # Overlap between chunks
  include_context: true          # Include page/section references
```

### Test Case Generation

```yaml
test_case_generation:
  types:
    adversarial:
      enabled: true
      questions_per_type: 8      # Adversarial test cases per document
    
    bias:
      enabled: false             # Enable/disable bias testing
      questions_per_type: 0
    
    hallucination:
      enabled: true
      questions_per_type: 5      # Hallucination test cases per document
```

### Document Processing

```yaml
document_processing:
  supported_formats:
    - ".txt"
    - ".pdf"
    - ".docx"
    - ".xlsx"
    - ".png"
    - ".jpg"
  
  pdf:
    extract_images: true         # Extract images from PDFs
    extract_tables: true         # Extract table data
    ocr_enabled: true           # OCR for scanned PDFs
  
  excel:
    read_all_sheets: true       # Process all Excel sheets
    include_formulas: false     # Include Excel formulas
  
  image:
    ocr_enabled: true           # OCR for image documents
    confidence_threshold: 0.8   # OCR confidence threshold
```

## 📊 Output Format

The framework generates a comprehensive Excel report with multiple sheets:

### Summary Sheet
- Execution overview and statistics
- Document processing summary
- Error reporting

### Statistics Sheet
- Q&A generation metrics
- Test case statistics
- Quality analysis

### Document Sheets (Individual)
- Q&A pairs for each document
- Quality scores and difficulty levels
- Page/section references
- Keywords and categorization

### Test Case Sheets
- **Adversarial Tests**: Edge cases, prompt injection, misleading questions
- **Bias Tests**: Demographic, cultural, and representation bias detection
- **Hallucination Tests**: Information fabrication and source boundary testing

## 🎯 Use Cases

### 1. Training Data Generation
Generate high-quality Q&A pairs for training AI models and chatbots from your documentation.

### 2. Testing Team Support
Reduce manual testing effort by automatically generating comprehensive test scenarios.

### 3. Document Quality Assessment
Evaluate how well AI systems understand and process your documents.

### 4. Compliance Testing
Generate bias and fairness test cases to ensure AI system compliance.

### 5. Educational Content Creation
Create assessment materials and study guides from educational documents.

## 🏗️ Architecture

### Core Components

1. **Document Processor**: Coordinates processing across different document types
2. **AI Clients**: Abstracts OpenAI and Azure OpenAI interactions
3. **Q&A Generator**: Creates question-answer pairs with quality scoring
4. **Test Case Generator**: Generates specialized test scenarios
5. **Report Generator**: Creates formatted Excel reports with analysis

### Processing Pipeline

1. **Document Loading**: Detect format and route to appropriate processor
2. **Content Extraction**: Extract text, images, tables, and metadata
3. **Intelligent Chunking**: Break content into manageable pieces with context preservation
4. **AI Generation**: Generate Q&A pairs and test cases using configured AI provider
5. **Quality Assessment**: Score and categorize generated content
6. **Report Creation**: Compile results into comprehensive Excel reports

## 🔍 Advanced Features

### Smart Chunking
- Context-aware text segmentation
- Page and section reference preservation
- Overlap management for continuity

### Quality Scoring
- Automatic quality assessment for Q&A pairs
- Difficulty level classification
- Question type categorization

### Concurrent Processing
- Parallel document processing
- Configurable concurrency limits
- Progress tracking and error handling

### Comprehensive Logging
- Detailed execution logs
- Error tracking and reporting
- Performance metrics

## 🛠️ Customization

### Custom Prompts
Modify prompt templates in the `prompts/` directory:
- `pdf_prompts.yaml` - PDF-specific question generation
- `word_prompts.yaml` - Word document prompts
- `excel_prompts.yaml` - Spreadsheet analysis prompts
- `text_prompts.yaml` - Plain text processing
- `image_prompts.yaml` - OCR content prompts
- `test_case_prompts.yaml` - Test case generation templates

### Adding New Document Types
1. Create a new processor in `src/processors/`
2. Implement the processor interface
3. Add file extension mapping in `document_processor.py`
4. Create corresponding prompt templates

### Custom AI Providers
1. Create a new client in `src/ai_clients/`
2. Implement the client interface
3. Add provider configuration support
4. Update the AI client factory

## 📈 Performance Optimization

### Processing Speed
- Adjust `concurrent_requests` based on your API limits
- Optimize `chunk_size` for your content type
- Enable/disable features as needed

### Cost Management
- Monitor API usage through configuration
- Adjust questions per document based on needs
- Use selective test case generation

### Memory Usage
- Configure `memory_limit` in performance settings
- Adjust chunk sizes for large documents
- Enable cleanup of temporary files

## 🔒 Security & Privacy

### API Key Management
- Store API keys securely in configuration
- Use environment variables for production
- Rotate keys regularly

### Data Privacy
- Documents are processed locally before AI submission
- No data persistence in AI provider systems
- Configurable data retention policies

## 🐛 Troubleshooting

### Common Issues

**OCR Not Working**
- Install Tesseract OCR system dependency
- Verify Tesseract is in system PATH
- Check image quality and format

**API Errors**
- Verify API keys are correct
- Check rate limits and quotas
- Ensure model deployment is active (Azure)

**Memory Issues**
- Reduce chunk_size in configuration
- Lower concurrent_requests
- Process smaller document batches

**Poor Quality Results**
- Adjust prompt templates for your domain
- Increase chunk_overlap for better context
- Fine-tune quality thresholds

### Logs and Debugging
- Check `logs/testfoundry.log` for detailed execution logs
- Enable DEBUG logging level for verbose output
- Review error messages in Summary sheet

## 📝 Example Usage Scenarios

### Scenario 1: Technical Documentation Testing
```yaml
qa_generation:
  questions_per_document: 30
  
test_case_generation:
  types:
    adversarial:
      enabled: true
      questions_per_type: 10
    hallucination:
      enabled: true
      questions_per_type: 8
```

### Scenario 2: Educational Content Assessment
```yaml
qa_generation:
  questions_per_document: 50
  
test_case_generation:
  types:
    bias:
      enabled: true
      questions_per_type: 12
```

### Scenario 3: Compliance and Fairness Testing
```yaml
test_case_generation:
  types:
    bias:
      enabled: true
      questions_per_type: 15
    adversarial:
      enabled: true
      questions_per_type: 12
```

## 🚀 Production Deployment

### Environment Setup
1. Set up dedicated Python environment
2. Configure logging directory permissions
3. Set up API key environment variables
4. Configure file system access

### Monitoring
- Set up log monitoring
- Track API usage and costs
- Monitor processing times and success rates
- Set up alerting for failures

### Scaling
- Run multiple instances for high volume
- Use queue systems for batch processing
- Implement load balancing for API calls
- Consider distributed processing for large datasets

## 📞 Support and Maintenance

### Regular Maintenance
- Update prompt templates based on results
- Monitor and optimize processing performance
- Update AI model versions when available
- Review and update quality thresholds

### Framework Updates
- Keep dependencies updated
- Monitor for security updates
- Test new AI model capabilities
- Backup and version control configurations

---

## 🎉 Getting Started

1. **Install**: Set up Python environment and dependencies
2. **Configure**: Add your AI provider credentials
3. **Test**: Run with a small sample document
4. **Scale**: Process your full document collection
5. **Analyze**: Review reports and optimize settings

The TestFoundry Framework is designed to be both powerful and easy to use. Start with default settings and customize as you learn what works best for your specific use case.

**Happy Testing! 🚀**