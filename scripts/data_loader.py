"""
Module for loading CRM data and marketing campaign planning data.
"""
import pandas as pd
import os
from datetime import datetime


def load_crm_data(file_path):
    """
    Loads leads and enrollments data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file with CRM data.
        
    Returns:
        pandas.DataFrame: DataFrame with the loaded data.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file format is not as expected.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Load data
        df = pd.read_csv(file_path)
        
        # Verify required columns
        required_columns = ['Brand', 'Channel', 'Campaign ID', 'Date', 'Leads', 'Enrollments']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns in the file: {missing_columns}")
            
        # Convert date columns
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Ensure data types
        df['Leads'] = df['Leads'].astype(int)
        df['Enrollments'] = df['Enrollments'].astype(int)
        
        return df
    
    except pd.errors.ParserError:
        raise ValueError("The file does not have the expected CSV format")
    except Exception as e:
        raise ValueError(f"Error loading data: {str(e)}")


def load_planning_data(file_path):
    """
    Loads campaign planning data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file with planning data.
        
    Returns:
        pandas.DataFrame: DataFrame with the planning data.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file format is not as expected.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Load data
        df = pd.read_csv(file_path)
        
        # Verify required columns
        required_columns = [
            'Brand', 'Channel', 'Campaign ID', 'Start Date', 'End Date',
            'Assigned Budget (USD)', 'Lead Target', 'Enrollment Target'
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns in the file: {missing_columns}")
            
        # Convert date columns
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        df['End Date'] = pd.to_datetime(df['End Date'])
        
        # Ensure data types
        df['Assigned Budget (USD)'] = df['Assigned Budget (USD)'].astype(float)
        df['Lead Target'] = df['Lead Target'].astype(int)
        df['Enrollment Target'] = df['Enrollment Target'].astype(int)
        
        return df
    
    except pd.errors.ParserError:
        raise ValueError("The file does not have the expected CSV format")
    except Exception as e:
        raise ValueError(f"Error loading data: {str(e)}")


if __name__ == "__main__":
    # Usage example
    try:
        print("Loading CRM data...")
        crm_data = load_crm_data("../data/actual_leads_enrollments.csv")
        print(f"Data loaded: {len(crm_data)} records")
        print(crm_data.head())
        
        print("\nLoading planning data...")
        planning_data = load_planning_data("../data/biweekly_planning.csv")
        print(f"Data loaded: {len(planning_data)} records")
        print(planning_data.head())
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 