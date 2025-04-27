import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
import sys

# Add src to path for testing
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

# Import the functions to test
from utils.process_stock_data import fill_missing_dates_interpolation, process_all_raw_files

# Test data
TEST_DATA = """date,ouverture,haut,bas,cloture,volume
01/01/2023,10.5,11.0,10.0,10.75,1000
03/01/2023,10.8,11.2,10.5,11.0,1500
"""

EXPECTED_COLUMNS = ['date', 'ouverture', 'haut', 'bas', 'cloture', 'volume']

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        'date': ['01/01/2023', '03/01/2023'],
        'ouverture': [10.5, 10.8],
        'haut': [11.0, 11.2],
        'bas': [10.0, 10.5],
        'cloture': [10.75, 11.0],
        'volume': [1000, 1500]
    })

def test_fill_missing_dates_interpolation_basic(sample_dataframe):
    """Test basic interpolation functionality"""
    result = fill_missing_dates_interpolation(sample_dataframe)
    
    # Check we have all dates between 01/01 and 03/01
    assert len(result) == 3
    assert result['date'].tolist() == [
        pd.Timestamp('2023-01-01'),
        pd.Timestamp('2023-01-02'),
        pd.Timestamp('2023-01-03')
    ]
    
    # Check original values remain unchanged
    assert result.iloc[0]['ouverture'] == 10.5
    assert result.iloc[2]['ouverture'] == 10.8
    
    # Check interpolated values
    assert 10.5 < result.iloc[1]['ouverture'] < 10.8
    assert result.iloc[1]['volume'] == 0  # New row volume should be 0

def test_fill_missing_dates_with_european_decimals():
    """Test handling of European decimal format (comma)"""
    df = pd.DataFrame({
        'date': ['01/01/2023', '03/01/2023'],
        'ouverture': ['10,5', '10,8'],
        'haut': ['11,0', '11,2'],
        'volume': [1000, 1500]
    })
    
    result = fill_missing_dates_interpolation(df)
    assert result.iloc[0]['ouverture'] == 10.5
    assert result.iloc[2]['ouverture'] == 10.8

def test_fill_missing_dates_with_missing_columns(sample_dataframe):
    """Test handling when some OHLC columns are missing"""
    df = sample_dataframe.drop(columns=['haut', 'bas'])
    result = fill_missing_dates_interpolation(df)
    assert 'haut' not in result.columns
    assert 'bas' not in result.columns
    assert len(result) == 3  # Still fills dates

def test_fill_missing_dates_with_empty_dataframe():
    """Test handling of empty DataFrame"""
    df = pd.DataFrame(columns=EXPECTED_COLUMNS)
    result = fill_missing_dates_interpolation(df)
    assert result.empty

@patch('os.listdir')
@patch('pandas.read_csv')
@patch('pandas.DataFrame.to_csv')
def test_process_all_raw_files(mock_to_csv, mock_read_csv, mock_listdir, tmp_path):
    """Test the file processing pipeline"""
    # Setup mock environment
    mock_listdir.return_value = ['file1.csv', 'file2.csv']
    mock_read_csv.return_value = pd.DataFrame({
        'date': ['01/01/2023'],
        'ouverture': [10.5],
        'volume': [1000]
    })
    
    # Create temp directories
    input_dir = tmp_path / 'data' / 'raw'
    output_dir = tmp_path / 'data' / 'processed'
    input_dir.mkdir(parents=True)
    
    # Run the function
    with patch('utils.data_processing.Path') as mock_path:
        mock_path.return_value.parent.parent = tmp_path
        process_all_raw_files()
    
    # Verify behavior
    assert mock_listdir.called
    assert mock_read_csv.call_count == 2
    assert mock_to_csv.call_count == 2

def test_non_csv_files_are_ignored(tmp_path):
    """Test that non-CSV files are ignored"""
    # Create test files
    input_dir = tmp_path / 'data' / 'raw'
    input_dir.mkdir(parents=True)
    (input_dir / 'file1.csv').touch()
    (input_dir / 'file2.txt').touch()
    
    with patch('utils.data_processing.Path') as mock_path:
        mock_path.return_value.parent.parent = tmp_path
        with patch('utils.data_processing.logger') as mock_logger:
            process_all_raw_files()
    
    # Should only process 1 file (the CSV)
    mock_logger.info.assert_called_with("Found 1 CSV files to process")

def test_error_handling_during_file_processing(tmp_path):
    """Test error handling when processing fails"""
    input_dir = tmp_path / 'data' / 'raw'
    input_dir.mkdir(parents=True)
    (input_dir / 'file1.csv').touch()
    
    with patch('utils.data_processing.Path') as mock_path:
        mock_path.return_value.parent.parent = tmp_path
        with patch('pandas.read_csv', side_effect=Exception("Test error")):
            with patch('utils.data_processing.logger') as mock_logger:
                process_all_raw_files()
    
    # Verify error was logged
    mock_logger.error.assert_called_with("Error processing file1.csv: Test error")