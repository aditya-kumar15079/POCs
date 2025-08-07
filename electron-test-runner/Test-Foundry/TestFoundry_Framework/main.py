#!/usr/bin/env python3
"""
TestFoundry Framework - Main Execution Script
A comprehensive testing framework for generating Q&A pairs from documents
"""

import os
import sys
import asyncio
import time
import platform
import warnings
from pathlib import Path
from typing import List, Dict, Any

# Suppress specific asyncio warnings on Windows
if platform.system() == 'Windows':
    # Filter out the specific RuntimeError about closed event loops
    warnings.filterwarnings("ignore", message=".*Event loop is closed.*")
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="asyncio")
    
    # Set the event loop policy for Windows
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config_manager import ConfigManager
from src.core.document_processor import DocumentProcessor
from src.core.qa_generator import QAGenerator
from src.core.test_case_generator import TestCaseGenerator
from src.core.report_generator import ReportGenerator
from src.utils.logger import setup_logger
from src.utils.file_utils import get_input_files, ensure_output_directory

def print_banner():
    """Print the TestFoundry banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                        TestFoundry                           ║
    ║                  AI-Powered Testing Framework                ║
    ║                                                              ║
    ║  Generate Q&A pairs and test cases from your documents       ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

async def process_documents(
    input_files: List[Path],
    config: Dict[str, Any],
    logger
) -> Dict[str, Any]:
    """Process all input documents and generate Q&A pairs"""
    
    results = {
        'documents': {},
        'summary': {
            'total_documents': len(input_files),
            'processed_documents': 0,
            'total_questions': 0,
            'total_test_cases': 0,
            'processing_time': 0,
            'errors': []
        }
    }
    
    start_time = time.time()
    
    # Initialize processors
    doc_processor = DocumentProcessor(config, logger)
    qa_generator = QAGenerator(config, logger)
    test_case_generator = TestCaseGenerator(config, logger)
    
    logger.info(f"Starting processing of {len(input_files)} documents")
    
    try:
        for file_path in input_files:
            try:
                logger.info(f"Processing document: {file_path.name}")
                
                # Log document size for large files
                file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                if file_size > 10:
                    logger.info(f"Large document detected: {file_size:.1f} MB - using advanced chunking")
                
                # Process document and extract content
                doc_content = await doc_processor.process_document(file_path)
                
                if not doc_content:
                    logger.warning(f"No content extracted from {file_path.name}")
                    continue
                
                # Log document statistics
                stats = doc_content.get('statistics', {})
                logger.info(f"Document stats: {stats.get('total_pages', 0)} pages, "
                           f"{stats.get('total_characters', 0)} characters")
                
                # Generate Q&A pairs
                qa_pairs = await qa_generator.generate_qa_pairs(doc_content, file_path.name)
                
                # Generate test cases if enabled
                test_cases = {}
                if config['test_case_generation']['types']['adversarial']['enabled']:
                    test_cases['adversarial'] = await test_case_generator.generate_adversarial_tests(
                        doc_content, file_path.name
                    )
                
                if config['test_case_generation']['types']['bias']['enabled']:
                    test_cases['bias'] = await test_case_generator.generate_bias_tests(
                        doc_content, file_path.name
                    )
                
                if config['test_case_generation']['types']['hallucination']['enabled']:
                    test_cases['hallucination'] = await test_case_generator.generate_hallucination_tests(
                        doc_content, file_path.name
                    )
                
                # Store results
                results['documents'][file_path.name] = {
                    'file_path': str(file_path),
                    'content': doc_content,
                    'qa_pairs': qa_pairs,
                    'test_cases': test_cases,
                    'processed_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Update summary
                results['summary']['processed_documents'] += 1
                results['summary']['total_questions'] += len(qa_pairs)
                results['summary']['total_test_cases'] += sum(len(tc) for tc in test_cases.values())
                
                logger.info(f"Successfully processed {file_path.name}: "
                           f"{len(qa_pairs)} Q&A pairs, "
                           f"{sum(len(tc) for tc in test_cases.values())} test cases")
                
            except Exception as e:
                error_msg = f"Error processing {file_path.name}: {str(e)}"
                logger.error(error_msg)
                results['summary']['errors'].append(error_msg)
    
    finally:
        # Properly cleanup async resources
        try:
            await qa_generator.close()
            await test_case_generator.close()
        except Exception:
            pass  # Ignore cleanup errors
    
    results['summary']['processing_time'] = time.time() - start_time
    return results

async def main_async():
    """Main async execution function"""
    print_banner()
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Setup logging
        logger = setup_logger(config['logging'])
        logger.info("TestFoundry Framework started")
        
        # Get input files
        input_dir = Path("input")
        input_files = get_input_files(input_dir, config['document_processing']['supported_formats'])
        
        if not input_files:
            logger.warning("No supported documents found in input directory")
            print("No supported documents found in 'input' directory.")
            print("Supported formats:", ", ".join(config['document_processing']['supported_formats']))
            return
        
        print(f"Found {len(input_files)} documents to process:")
        for file_path in input_files:
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"  - {file_path.name} ({file_size:.1f} MB)")
        
        # Ensure output directory exists
        output_dir = ensure_output_directory(Path("output"))
        
        # Process documents
        print("\nProcessing documents...")
        results = await process_documents(input_files, config, logger)
        
        # Generate report
        print("Generating Excel report...")
        report_generator = ReportGenerator(config, logger)
        report_path = await report_generator.generate_report(results, output_dir)
        
        # Print summary
        summary = results['summary']
        print(f"\n{'='*60}")
        print("PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"Documents processed: {summary['processed_documents']}/{summary['total_documents']}")
        print(f"Total Q&A pairs generated: {summary['total_questions']}")
        print(f"Total test cases generated: {summary['total_test_cases']}")
        print(f"Processing time: {summary['processing_time']:.2f} seconds")
        print(f"Report saved to: {report_path}")
        
        if summary['errors']:
            print(f"\nErrors encountered: {len(summary['errors'])}")
            for error in summary['errors']:
                print(f"  - {error}")
        
        logger.info("TestFoundry Framework completed successfully")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        if 'logger' in locals():
            logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

def main():
    """Main function with proper Windows asyncio handling"""
    if platform.system() == 'Windows':
        # Windows-specific asyncio setup
        try:
            # Create new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the main async function
            loop.run_until_complete(main_async())
            
        except KeyboardInterrupt:
            print("\nProcess interrupted by user")
        except Exception as e:
            print(f"Fatal error: {str(e)}")
        finally:
            # Properly cleanup the event loop
            try:
                # Cancel all remaining tasks
                pending = asyncio.all_tasks(loop)
                if pending:
                    for task in pending:
                        task.cancel()
                    # Wait for tasks to complete cancellation
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
                # Close the loop
                loop.close()
            except Exception:
                pass  # Ignore cleanup errors
    else:
        # Standard run for non-Windows systems
        try:
            asyncio.run(main_async())
        except KeyboardInterrupt:
            print("\nProcess interrupted by user")
        except Exception as e:
            print(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    # Run the main function
    main()