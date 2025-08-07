"""
Excel Report Generator for TestFoundry Framework
Creates comprehensive Excel reports with multiple sheets and formatting
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

class ReportGenerator:
    """Generates comprehensive Excel reports with Q&A pairs and test cases"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize report generator
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.output_config = config.get('output', {})
        
        # Settings
        self.include_summary = self.output_config.get('include_summary', True)
        self.include_statistics = self.output_config.get('include_statistics', True)
        self.separate_sheets = self.output_config.get('separate_sheets_per_document', True)
        self.timestamp_reports = self.output_config.get('timestamp_reports', True)
    
    async def generate_report(self, 
                            results: Dict[str, Any], 
                            output_dir: Path) -> Path:
        """Generate comprehensive Excel report
        
        Args:
            results: Processing results dictionary
            output_dir: Output directory path
            
        Returns:
            Path to generated report file
        """
        try:
            self.logger.info("Generating Excel report")
            
            # Create report filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') if self.timestamp_reports else ''
            filename = f"TestFoundry_Report_{timestamp}.xlsx" if timestamp else "TestFoundry_Report.xlsx"
            report_path = output_dir / filename
            
            # Create Excel writer
            with pd.ExcelWriter(str(report_path), engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Define styles
                styles = self._create_styles(workbook)
                
                # Generate summary sheet
                if self.include_summary:
                    await self._create_summary_sheet(writer, workbook, styles, results)
                
                # Generate statistics sheet
                if self.include_statistics:
                    await self._create_statistics_sheet(writer, workbook, styles, results)
                
                # Generate document sheets
                if self.separate_sheets:
                    await self._create_document_sheets(writer, workbook, styles, results)
                else:
                    await self._create_combined_sheet(writer, workbook, styles, results)
                
                # Generate test case sheets
                await self._create_test_case_sheets(writer, workbook, styles, results)
            
            self.logger.info(f"Excel report generated: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"Error generating Excel report: {e}")
            raise
    
    def _create_styles(self, workbook) -> Dict[str, Any]:
        """Create Excel formatting styles
        
        Args:
            workbook: XlsxWriter workbook object
            
        Returns:
            Dictionary of styles
        """
        styles = {
            'title': workbook.add_format({
                'bold': True,
                'font_size': 16,
                'font_color': '#FFFFFF',        # White text
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#2E74B5',          # Professional Blue
                'border': 1
            }),
            'header': workbook.add_format({
                'bold': True,
                'font_size': 12,
                'font_color': '#FFFFFF',        # White text
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#5B9BD5',          # Lighter Blue (change this color)
                'border': 1,
                'text_wrap': True
            }),
            'subheader': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'font_color': '#2E74B5',        # Dark Blue text
                'align': 'left',
                'valign': 'vcenter',
                'bg_color': '#DEEBF7',          # Very Light Blue
                'border': 1
            }),
            'data': workbook.add_format({
                'font_size': 10,
                'align': 'left',
                'valign': 'top',
                'border': 1,
                'text_wrap': True
            }),
            'number': workbook.add_format({
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '#,##0'
            }),
            'percentage': workbook.add_format({
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '0.0%'
            }),
            'date': workbook.add_format({
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'num_format': 'yyyy-mm-dd hh:mm:ss'
            }),
            'quality_high': workbook.add_format({
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'bg_color': '#C6EFCE',          # Light Green
                'font_color': '#006100'         # Dark Green
            }),
            'quality_medium': workbook.add_format({
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'bg_color': '#FFEB9C',          # Light Yellow
                'font_color': '#9C5700'         # Dark Orange
            }),
            'quality_low': workbook.add_format({
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'bg_color': '#FFC7CE',          # Light Red
                'font_color': '#9C0006'         # Dark Red
            })
        }
        
        return styles
    
    async def _create_summary_sheet(self, 
                                  writer, 
                                  workbook, 
                                  styles: Dict[str, Any], 
                                  results: Dict[str, Any]):
        """Create summary sheet
        
        Args:
            writer: Excel writer object
            workbook: Workbook object
            styles: Formatting styles
            results: Processing results
        """
        worksheet = workbook.add_worksheet('Summary')
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 40)
        worksheet.set_column('C:D', 15)
        
        row = 0
        
        # Title
        worksheet.merge_range('A1:D1', 'TestFoundry Framework - Execution Summary', styles['title'])
        row += 2
        
        # Basic information
        summary = results.get('summary', {})
        basic_info = [
            ['Generated On', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Documents Processed', summary.get('processed_documents', 0)],
            ['Total Q&A Pairs Generated', summary.get('total_questions', 0)],
            ['Total Test Cases Generated', summary.get('total_test_cases', 0)],
            ['Processing Time (seconds)', f"{summary.get('processing_time', 0):.2f}"],
            ['Success Rate', f"{(summary.get('processed_documents', 0) / max(summary.get('total_documents', 1), 1) * 100):.1f}%"]
        ]
        
        worksheet.write(row, 0, 'Execution Overview', styles['subheader'])
        row += 1
        
        for label, value in basic_info:
            worksheet.write(row, 0, label, styles['data'])
            worksheet.write(row, 1, value, styles['data'])
            row += 1
        
        row += 1
        
        # Document breakdown
        documents = results.get('documents', {})
        if documents:
            worksheet.write(row, 0, 'Document Breakdown', styles['subheader'])
            row += 1
            
            # Headers
            headers = ['Document Name', 'Type', 'Q&A Pairs', 'Test Cases', 'Status']
            for col, header in enumerate(headers):
                worksheet.write(row, col, header, styles['header'])
            row += 1
            
            # Document data
            for doc_name, doc_data in documents.items():
                qa_count = len(doc_data.get('qa_pairs', []))
                test_count = sum(len(tc) for tc in doc_data.get('test_cases', {}).values())
                doc_type = doc_data.get('content', {}).get('file_type', 'unknown')
                status = 'Success' if 'error' not in doc_data else 'Failed'
                
                doc_row_data = [doc_name, doc_type, qa_count, test_count, status]
                for col, data in enumerate(doc_row_data):
                    if col in [2, 3]:  # Numeric columns
                        worksheet.write(row, col, data, styles['number'])
                    else:
                        worksheet.write(row, col, data, styles['data'])
                row += 1
        
        # Errors section
        errors = summary.get('errors', [])
        if errors:
            row += 1
            worksheet.write(row, 0, 'Errors and Warnings', styles['subheader'])
            row += 1
            
            for error in errors:
                worksheet.write(row, 0, error, styles['data'])
                row += 1
    
    async def _create_statistics_sheet(self, 
                                     writer, 
                                     workbook, 
                                     styles: Dict[str, Any], 
                                     results: Dict[str, Any]):
        """Create statistics sheet
        
        Args:
            writer: Excel writer object
            workbook: Workbook object
            styles: Formatting styles
            results: Processing results
        """
        worksheet = workbook.add_worksheet('Statistics')
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:E', 15)
        
        row = 0
        
        # Title
        worksheet.merge_range('A1:E1', 'TestFoundry Framework - Detailed Statistics', styles['title'])
        row += 2
        
        documents = results.get('documents', {})
        
        # Q&A Statistics
        worksheet.write(row, 0, 'Q&A Generation Statistics', styles['subheader'])
        row += 1
        
        qa_stats_headers = ['Document', 'Total Q&A', 'Avg Quality', 'Question Types', 'Difficulty Levels']
        for col, header in enumerate(qa_stats_headers):
            worksheet.write(row, col, header, styles['header'])
        row += 1
        
        for doc_name, doc_data in documents.items():
            qa_pairs = doc_data.get('qa_pairs', [])
            
            # Calculate statistics
            total_qa = len(qa_pairs)
            avg_quality = sum(qa.get('quality_score', 0) for qa in qa_pairs) / max(total_qa, 1)
            
            # Count question types
            question_types = {}
            difficulty_levels = {}
            
            for qa in qa_pairs:
                q_type = qa.get('question_type', 'unknown')
                difficulty = qa.get('difficulty_level', 'unknown')
                question_types[q_type] = question_types.get(q_type, 0) + 1
                difficulty_levels[difficulty] = difficulty_levels.get(difficulty, 0) + 1
            
            # Format type and difficulty strings
            types_str = ', '.join([f"{k}({v})" for k, v in question_types.items()])
            diff_str = ', '.join([f"{k}({v})" for k, v in difficulty_levels.items()])
            
            row_data = [doc_name, total_qa, avg_quality, types_str, diff_str]
            
            worksheet.write(row, 0, row_data[0], styles['data'])
            worksheet.write(row, 1, row_data[1], styles['number'])
            worksheet.write(row, 2, row_data[2], styles['percentage'])
            worksheet.write(row, 3, row_data[3], styles['data'])
            worksheet.write(row, 4, row_data[4], styles['data'])
            row += 1
        
        row += 2
        
        # Test Case Statistics
        worksheet.write(row, 0, 'Test Case Statistics', styles['subheader'])
        row += 1
        
        test_stats_headers = ['Document', 'Adversarial', 'Bias', 'Hallucination', 'Total Tests']
        for col, header in enumerate(test_stats_headers):
            worksheet.write(row, col, header, styles['header'])
        row += 1
        
        for doc_name, doc_data in documents.items():
            test_cases = doc_data.get('test_cases', {})
            
            adversarial_count = len(test_cases.get('adversarial', []))
            bias_count = len(test_cases.get('bias', []))
            hallucination_count = len(test_cases.get('hallucination', []))
            total_tests = adversarial_count + bias_count + hallucination_count
            
            row_data = [doc_name, adversarial_count, bias_count, hallucination_count, total_tests]
            
            for col, data in enumerate(row_data):
                if col == 0:
                    worksheet.write(row, col, data, styles['data'])
                else:
                    worksheet.write(row, col, data, styles['number'])
            row += 1
    
    async def _create_document_sheets(self, 
                                    writer, 
                                    workbook, 
                                    styles: Dict[str, Any], 
                                    results: Dict[str, Any]):
        """Create separate sheets for each document
        
        Args:
            writer: Excel writer object
            workbook: Workbook object
            styles: Formatting styles
            results: Processing results
        """
        documents = results.get('documents', {})
        
        for doc_name, doc_data in documents.items():
            # Create safe sheet name
            safe_name = self._create_safe_sheet_name(doc_name)
            worksheet = workbook.add_worksheet(safe_name)
            
            await self._populate_document_sheet(worksheet, styles, doc_name, doc_data)
    
    async def _populate_document_sheet(self, 
                                     worksheet, 
                                     styles: Dict[str, Any], 
                                     doc_name: str, 
                                     doc_data: Dict[str, Any]):
        """Populate individual document sheet
        
        Args:
            worksheet: Excel worksheet object
            styles: Formatting styles
            doc_name: Document name
            doc_data: Document data
        """
        # Set column widths
        worksheet.set_column('A:A', 8)   # ID
        worksheet.set_column('B:B', 50)  # Question
        worksheet.set_column('C:C', 50)  # Answer
        worksheet.set_column('D:D', 12)  # Type
        worksheet.set_column('E:E', 12)  # Difficulty
        worksheet.set_column('F:F', 10)  # Page/Section
        worksheet.set_column('G:G', 12)  # Quality Score
        worksheet.set_column('H:H', 30)  # Keywords
        
        row = 0
        
        # Title
        worksheet.merge_range('A1:H1', f'Q&A Pairs for: {doc_name}', styles['title'])
        row += 2
        
        # Document info
        content = doc_data.get('content', {})
        info_data = [
            ['Document Type', content.get('file_type', 'unknown')],
            ['File Path', content.get('file_path', 'unknown')],
            ['Processed At', doc_data.get('processed_at', 'unknown')],
            ['Total Pages/Sheets', len(content.get('pages', content.get('sheets', [])))],
            ['Total Characters', content.get('statistics', {}).get('total_characters', 0)]
        ]
        
        for label, value in info_data:
            worksheet.write(row, 0, label, styles['subheader'])
            worksheet.write(row, 1, value, styles['data'])
            row += 1
        
        row += 1
        
        # Q&A Headers
        headers = ['ID', 'Question', 'Answer', 'Type', 'Difficulty', 'Reference', 'Quality', 'Keywords']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles['header'])
        row += 1
        
        # Q&A Data
        qa_pairs = doc_data.get('qa_pairs', [])
        for i, qa in enumerate(qa_pairs):
            # Use sequential numbering for display
            display_id = f"Q{qa.get('sequential_id', i+1)}"  # Q1, Q2, Q3, etc.
            technical_id = qa.get('id', f'Q{i+1}')  # Keep technical ID for reference
            question = qa.get('question', '')
            answer = qa.get('answer', '')
            q_type = qa.get('question_type', 'factual')
            difficulty = qa.get('difficulty_level', 'medium')
            
            # Reference info with better formatting
            reference = ""
            page_ref = qa.get('page_number')
            section_ref = qa.get('section')
            chunk_ref = qa.get('chunk_index', 0) + 1  # 1-based chunk number
            
            if page_ref:
                reference += f"Page {page_ref}"
            if section_ref:
                reference += f" | {section_ref}"
            reference += f" | Chunk {chunk_ref}"  # Add chunk info for clarity
            
            quality_score = qa.get('quality_score', 0)
            keywords = ', '.join(qa.get('keywords', [])[:5])  # Limit keywords
            
            # Write data with improved ID display
            worksheet.write(row, 0, display_id, styles['data'])  # Q1, Q2, Q3 format
            worksheet.write(row, 1, question, styles['data'])
            worksheet.write(row, 2, answer, styles['data'])
            worksheet.write(row, 3, q_type, styles['data'])
            worksheet.write(row, 4, difficulty, styles['data'])
            worksheet.write(row, 5, reference, styles['data'])
            
            # Quality score with conditional formatting
            if quality_score >= 0.8:
                worksheet.write(row, 6, quality_score, styles['quality_high'])
            elif quality_score >= 0.6:
                worksheet.write(row, 6, quality_score, styles['quality_medium'])
            else:
                worksheet.write(row, 6, quality_score, styles['quality_low'])
            
            worksheet.write(row, 7, keywords, styles['data'])
            
            # Add a comment with technical ID for reference
            worksheet.write_comment(row, 0, f"Technical ID: {technical_id}")
            
            row += 1
        
        # Set row heights for better readability
        for r in range(row):
            worksheet.set_row(r, 30 if r > 6 else 20)  # Taller rows for Q&A content
    
    async def _create_combined_sheet(self, 
                                   writer, 
                                   workbook, 
                                   styles: Dict[str, Any], 
                                   results: Dict[str, Any]):
        """Create combined sheet with all Q&A pairs
        
        Args:
            writer: Excel writer object
            workbook: Workbook object
            styles: Formatting styles
            results: Processing results
        """
        worksheet = workbook.add_worksheet('All Q&A Pairs')
        
        # Set column widths
        worksheet.set_column('A:A', 20)  # Document
        worksheet.set_column('B:B', 8)   # ID
        worksheet.set_column('C:C', 45)  # Question
        worksheet.set_column('D:D', 45)  # Answer
        worksheet.set_column('E:E', 12)  # Type
        worksheet.set_column('F:F', 12)  # Difficulty
        worksheet.set_column('G:G', 15)  # Reference
        worksheet.set_column('H:H', 10)  # Quality
        
        row = 0
        
        # Title
        worksheet.merge_range('A1:H1', 'All Generated Q&A Pairs', styles['title'])
        row += 2
        
        # Headers
        headers = ['Document', 'ID', 'Question', 'Answer', 'Type', 'Difficulty', 'Reference', 'Quality']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles['header'])
        row += 1
        
        # Data from all documents
        documents = results.get('documents', {})
        for doc_name, doc_data in documents.items():
            qa_pairs = doc_data.get('qa_pairs', [])
            
            for qa in qa_pairs:
                qa_id = qa.get('id', '')
                question = qa.get('question', '')
                answer = qa.get('answer', '')
                q_type = qa.get('question_type', 'factual')
                difficulty = qa.get('difficulty_level', 'medium')
                
                # Reference info
                reference = ""
                if qa.get('page_number'):
                    reference += f"Page {qa['page_number']}"
                if qa.get('section'):
                    reference += f" | {qa['section']}"
                
                quality_score = qa.get('quality_score', 0)
                
                # Write data
                row_data = [doc_name, qa_id, question, answer, q_type, difficulty, reference]
                
                for col, data in enumerate(row_data):
                    worksheet.write(row, col, data, styles['data'])
                
                # Quality score with conditional formatting
                if quality_score >= 0.8:
                    worksheet.write(row, 7, quality_score, styles['quality_high'])
                elif quality_score >= 0.6:
                    worksheet.write(row, 7, quality_score, styles['quality_medium'])
                else:
                    worksheet.write(row, 7, quality_score, styles['quality_low'])
                
                row += 1
    
    async def _create_test_case_sheets(self, 
                                     writer, 
                                     workbook, 
                                     styles: Dict[str, Any], 
                                     results: Dict[str, Any]):
        """Create test case sheets
        
        Args:
            writer: Excel writer object
            workbook: Workbook object
            styles: Formatting styles
            results: Processing results
        """
        # Collect all test cases by type
        test_types = ['adversarial', 'bias', 'hallucination']
        
        for test_type in test_types:
            all_tests = []
            documents = results.get('documents', {})
            
            # Collect test cases of this type from all documents
            for doc_name, doc_data in documents.items():
                test_cases = doc_data.get('test_cases', {}).get(test_type, [])
                for test_case in test_cases:
                    test_case_copy = test_case.copy()
                    test_case_copy['document_name'] = doc_name
                    all_tests.append(test_case_copy)
            
            if all_tests:
                await self._create_test_type_sheet(workbook, styles, test_type, all_tests)
    
    async def _create_test_type_sheet(self, 
                                    workbook, 
                                    styles: Dict[str, Any], 
                                    test_type: str, 
                                    test_cases: List[Dict[str, Any]]):
        """Create sheet for specific test type
        
        Args:
            workbook: Workbook object
            styles: Formatting styles
            test_type: Type of test cases
            test_cases: List of test cases
        """
        sheet_name = f"{test_type.title()} Tests"
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Set column widths
        worksheet.set_column('A:A', 20)  # Document
        worksheet.set_column('B:B', 12)  # ID
        worksheet.set_column('C:C', 45)  # Input
        worksheet.set_column('D:D', 45)  # Expected
        worksheet.set_column('E:E', 12)  # Category
        worksheet.set_column('F:F', 10)  # Severity
        worksheet.set_column('G:G', 15)  # Reference
        worksheet.set_column('H:H', 30)  # Rationale
        
        row = 0
        
        # Title
        worksheet.merge_range('A1:H1', f'{test_type.title()} Test Cases', styles['title'])
        row += 2
        
        # Headers
        headers = ['Document', 'Test ID', 'Input', 'Expected Response', 'Category', 'Severity', 'Reference', 'Rationale']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles['header'])
        row += 1
        
        # Test case data
        for test_case in test_cases:
            doc_name = test_case.get('document_name', '')
            test_id = test_case.get('id', '')
            input_text = test_case.get('input', '')
            expected = test_case.get('expected', '')
            category = test_case.get('category', 'general')
            severity = test_case.get('severity', 'medium')
            rationale = test_case.get('rationale', '')
            
            # Reference info
            reference = ""
            if test_case.get('page_number'):
                reference += f"Page {test_case['page_number']}"
            if test_case.get('section'):
                reference += f" | {test_case['section']}"
            
            # Write data
            row_data = [doc_name, test_id, input_text, expected, category, reference, rationale]
            
            for col, data in enumerate(row_data):
                if col == 5:  # Severity column will be handled separately
                    continue
                worksheet.write(row, col, data, styles['data'])
            
            # Severity with conditional formatting
            if severity == 'critical':
                worksheet.write(row, 5, severity, styles['quality_low'])
            elif severity == 'high':
                worksheet.write(row, 5, severity, styles['quality_medium'])
            else:
                worksheet.write(row, 5, severity, styles['quality_high'])
            
            row += 1
        
        # Set row heights for better readability
        for r in range(row):
            worksheet.set_row(r, 35 if r > 2 else 20)  # Taller rows for test content
    
    def _create_safe_sheet_name(self, name: str) -> str:
        """Create a safe Excel sheet name
        
        Args:
            name: Original name
            
        Returns:
            Safe sheet name
        """
        # Remove invalid characters
        invalid_chars = ['\\', '/', '?', '*', '[', ']', ':']
        safe_name = name
        
        for char in invalid_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Limit length to Excel's 31 character limit
        if len(safe_name) > 31:
            safe_name = safe_name[:28] + "..."
        
        return safe_name
    
    async def create_csv_export(self, 
                              results: Dict[str, Any], 
                              output_dir: Path) -> List[Path]:
        """Create CSV exports as alternative to Excel
        
        Args:
            results: Processing results
            output_dir: Output directory
            
        Returns:
            List of created CSV file paths
        """
        try:
            csv_files = []
            documents = results.get('documents', {})
            
            # Export Q&A pairs
            qa_data = []
            for doc_name, doc_data in documents.items():
                qa_pairs = doc_data.get('qa_pairs', [])
                for qa in qa_pairs:
                    qa_row = {
                        'document_name': doc_name,
                        'qa_id': qa.get('id', ''),
                        'question': qa.get('question', ''),
                        'answer': qa.get('answer', ''),
                        'question_type': qa.get('question_type', ''),
                        'difficulty_level': qa.get('difficulty_level', ''),
                        'page_number': qa.get('page_number', ''),
                        'section': qa.get('section', ''),
                        'quality_score': qa.get('quality_score', 0),
                        'keywords': ', '.join(qa.get('keywords', []))
                    }
                    qa_data.append(qa_row)
            
            if qa_data:
                qa_df = pd.DataFrame(qa_data)
                qa_csv_path = output_dir / 'qa_pairs.csv'
                qa_df.to_csv(qa_csv_path, index=False, encoding='utf-8')
                csv_files.append(qa_csv_path)
            
            # Export test cases by type
            test_types = ['adversarial', 'bias', 'hallucination']
            for test_type in test_types:
                test_data = []
                
                for doc_name, doc_data in documents.items():
                    test_cases = doc_data.get('test_cases', {}).get(test_type, [])
                    for test_case in test_cases:
                        test_row = {
                            'document_name': doc_name,
                            'test_id': test_case.get('id', ''),
                            'test_type': test_type,
                            'input': test_case.get('input', ''),
                            'expected': test_case.get('expected', ''),
                            'category': test_case.get('category', ''),
                            'severity': test_case.get('severity', ''),
                            'page_number': test_case.get('page_number', ''),
                            'section': test_case.get('section', ''),
                            'rationale': test_case.get('rationale', '')
                        }
                        test_data.append(test_row)
                
                if test_data:
                    test_df = pd.DataFrame(test_data)
                    test_csv_path = output_dir / f'{test_type}_tests.csv'
                    test_df.to_csv(test_csv_path, index=False, encoding='utf-8')
                    csv_files.append(test_csv_path)
            
            self.logger.info(f"Created {len(csv_files)} CSV export files")
            return csv_files
            
        except Exception as e:
            self.logger.error(f"Error creating CSV exports: {e}")
            return []
    
    async def generate_summary_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive summary statistics
        
        Args:
            results: Processing results
            
        Returns:
            Summary statistics dictionary
        """
        try:
            documents = results.get('documents', {})
            summary_stats = {
                'document_stats': {},
                'qa_stats': {},
                'test_case_stats': {},
                'quality_metrics': {}
            }
            
            # Document statistics
            total_docs = len(documents)
            successful_docs = len([d for d in documents.values() if 'error' not in d])
            
            summary_stats['document_stats'] = {
                'total_documents': total_docs,
                'successful_documents': successful_docs,
                'success_rate': successful_docs / max(total_docs, 1),
                'document_types': {}
            }
            
            # Count document types
            for doc_data in documents.values():
                doc_type = doc_data.get('content', {}).get('file_type', 'unknown')
                summary_stats['document_stats']['document_types'][doc_type] = \
                    summary_stats['document_stats']['document_types'].get(doc_type, 0) + 1
            
            # Q&A statistics
            all_qa_pairs = []
            for doc_data in documents.values():
                all_qa_pairs.extend(doc_data.get('qa_pairs', []))
            
            if all_qa_pairs:
                quality_scores = [qa.get('quality_score', 0) for qa in all_qa_pairs]
                question_types = [qa.get('question_type', 'unknown') for qa in all_qa_pairs]
                difficulty_levels = [qa.get('difficulty_level', 'unknown') for qa in all_qa_pairs]
                
                summary_stats['qa_stats'] = {
                    'total_qa_pairs': len(all_qa_pairs),
                    'average_quality': sum(quality_scores) / len(quality_scores),
                    'quality_distribution': {
                        'high': len([s for s in quality_scores if s >= 0.8]),
                        'medium': len([s for s in quality_scores if 0.6 <= s < 0.8]),
                        'low': len([s for s in quality_scores if s < 0.6])
                    },
                    'question_type_distribution': {},
                    'difficulty_distribution': {}
                }
                
                # Count distributions
                for q_type in set(question_types):
                    summary_stats['qa_stats']['question_type_distribution'][q_type] = question_types.count(q_type)
                
                for difficulty in set(difficulty_levels):
                    summary_stats['qa_stats']['difficulty_distribution'][difficulty] = difficulty_levels.count(difficulty)
            
            # Test case statistics
            all_test_cases = {'adversarial': [], 'bias': [], 'hallucination': []}
            for doc_data in documents.values():
                test_cases = doc_data.get('test_cases', {})
                for test_type in all_test_cases.keys():
                    all_test_cases[test_type].extend(test_cases.get(test_type, []))
            
            summary_stats['test_case_stats'] = {
                'total_test_cases': sum(len(tests) for tests in all_test_cases.values()),
                'test_type_counts': {k: len(v) for k, v in all_test_cases.items()},
                'severity_distribution': {}
            }
            
            # Count severity distribution across all test types
            all_severities = []
            for test_list in all_test_cases.values():
                all_severities.extend([tc.get('severity', 'unknown') for tc in test_list])
            
            for severity in set(all_severities):
                summary_stats['test_case_stats']['severity_distribution'][severity] = all_severities.count(severity)
            
            return summary_stats
            
        except Exception as e:
            self.logger.error(f"Error generating summary statistics: {e}")
            return {'error': str(e)}