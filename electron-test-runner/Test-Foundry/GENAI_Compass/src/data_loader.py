import pandas as pd
import os
from typing import Dict, List, Optional, Tuple

class DataLoader:
    """
    Handles loading and validation of input Excel data
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.required_columns = ['Prompt', 'Reference_Response', 'Generated_Response']
        self.optional_columns = ['Context', 'Enable_Flag']
        
    def load_data(self) -> pd.DataFrame:
        """
        Load data from Excel file and validate structure
        
        Returns:
            pd.DataFrame: Loaded and validated data
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Input file not found: {self.file_path}")
            
        try:
            df = pd.read_excel(self.file_path)
            print(f"Loaded {len(df)} rows from {self.file_path}")
            
            # Validate required columns
            self._validate_columns(df)
            
            # Clean and process data
            df = self._clean_data(df)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def _validate_columns(self, df: pd.DataFrame) -> None:
        """
        Validate that required columns exist
        
        Args:
            df: Input dataframe
        """
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
            
        print(f"✓ All required columns present: {self.required_columns}")
        
        # Check for optional columns
        present_optional = [col for col in self.optional_columns if col in df.columns]
        if present_optional:
            print(f"✓ Optional columns found: {present_optional}")
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess the data
        
        Args:
            df: Input dataframe
            
        Returns:
            pd.DataFrame: Cleaned dataframe
        """
        # Remove rows where required columns are null
        initial_count = len(df)
        df = df.dropna(subset=self.required_columns)
        dropped_count = initial_count - len(df)
        
        if dropped_count > 0:
            print(f"⚠ Dropped {dropped_count} rows with missing required data")
        
        # Convert text columns to string and strip whitespace
        text_columns = ['Prompt', 'Reference_Response', 'Generated_Response']
        if 'Context' in df.columns:
            text_columns.append('Context')
            
        for col in text_columns:
            df[col] = df[col].astype(str).str.strip()
        
        # Handle Enable_Flag column
        if 'Enable_Flag' not in df.columns:
            df['Enable_Flag'] = 'Y'  # Default to enabled
        else:
            df['Enable_Flag'] = df['Enable_Flag'].fillna('Y').str.upper()
            
        # Add Context column if missing
        if 'Context' not in df.columns:
            df['Context'] = ''
            
        print(f"✓ Data cleaned and preprocessed")
        return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics of the loaded data
        
        Args:
            df: Input dataframe
            
        Returns:
            Dict: Summary statistics
        """
        summary = {
            'total_rows': len(df),
            'enabled_tests': len(df[df['Enable_Flag'] == 'Y']),
            'disabled_tests': len(df[df['Enable_Flag'] == 'N']),
            'has_context': len(df[df['Context'] != '']),
            'average_prompt_length': df['Prompt'].str.len().mean(),
            'average_reference_length': df['Reference_Response'].str.len().mean(),
            'average_generated_length': df['Generated_Response'].str.len().mean()
        }
        
        return summary
    
    def validate_data_quality(self, df: pd.DataFrame) -> List[str]:
        """
        Validate data quality and return warnings
        
        Args:
            df: Input dataframe
            
        Returns:
            List[str]: List of warning messages
        """
        warnings = []
        
        # Check for very short responses
        short_ref = df[df['Reference_Response'].str.len() < 10]
        if len(short_ref) > 0:
            warnings.append(f"{len(short_ref)} reference responses are very short (< 10 chars)")
            
        short_gen = df[df['Generated_Response'].str.len() < 10]
        if len(short_gen) > 0:
            warnings.append(f"{len(short_gen)} generated responses are very short (< 10 chars)")
        
        # Check for very long responses
        long_ref = df[df['Reference_Response'].str.len() > 5000]
        if len(long_ref) > 0:
            warnings.append(f"{len(long_ref)} reference responses are very long (> 5000 chars)")
            
        long_gen = df[df['Generated_Response'].str.len() > 5000]
        if len(long_gen) > 0:
            warnings.append(f"{len(long_gen)} generated responses are very long (> 5000 chars)")
        
        # Check for identical responses
        identical = df[df['Reference_Response'] == df['Generated_Response']]
        if len(identical) > 0:
            warnings.append(f"{len(identical)} cases have identical reference and generated responses")
        
        return warnings