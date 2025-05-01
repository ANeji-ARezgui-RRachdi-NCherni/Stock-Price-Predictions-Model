import pytest
import pandas as pd
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import os
import sys
from unittest.mock import patch

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.process_stock_data import fill_missing_dates_interpolation, process_all_raw_files

# Test data for fill_missing_dates_interpolation
@pytest.fixture
def sample_stock_data():
    """Sample stock data with missing dates"""
    return pd.DataFrame({
        'date': ['01/01/2023', '03/01/2023', '04/01/2023', '06/01/2023'],
        'ouverture': [100.0, 102.0, 103.0, 105.0],
        'haut': [101.0, 103.0, 104.0, 106.0],
        'bas': [99.0, 101.0, 102.0, 104.0],
        'cloture': [100.5, 102.5, 103.5, 105.5],
        'volume': [1000, 1200, 1100, 1300]
    })

@pytest.fixture
def sample_stock_data_with_commas():
    """Sample stock data with European decimal format"""
    return pd.DataFrame({
        'date': ['01/01/2023', '03/01/2023'],
        'ouverture': ['100,0', '102,5'],
        'haut': ['101,2', '103,8'],
        'bas': ['99,5', '101,2'],
        'cloture': ['100,5', '102,8'],
        'volume': ['1000', '1200']
    })

@pytest.fixture
def sample_stock_data_missing_columns():
    """Sample stock data missing some columns"""
    return pd.DataFrame({
        'date': ['01/01/2023', '02/01/2023'],
        'ouverture': [100.0, 101.0],
        'haut': [101.0, 102.0]
    })

@pytest.fixture
def temp_data_dirs():
    """Create temporary directories for raw and processed data"""
    base_dir = tempfile.mkdtemp()
    raw_dir = Path(base_dir) / 'data' / 'raw'
    processed_dir = Path(base_dir) / 'data' / 'processed'
    
    raw_dir.mkdir(parents=True)
    processed_dir.mkdir(parents=True)
    
    yield raw_dir, processed_dir
    
    # Cleanup
    shutil.rmtree(base_dir)

@pytest.fixture
def sample_csv_file(temp_data_dirs):
    """Create a sample CSV file in the raw directory"""
    raw_dir, _ = temp_data_dirs
    file_path = raw_dir / 'test_stock.csv'
    
    data = """date;ouverture;haut;bas;cloture;volume;symbole
01/01/2023;100,0;101,0;99,0;100,5;1000;TEST
03/01/2023;102,0;103,0;101,0;102,5;1200;TEST"""
    
    with open(file_path, 'w') as f:
        f.write(data)
    
    return file_path

class TestFillMissingDatesInterpolation:
    def test_basic_functionality(self, sample_stock_data):
        """Test that missing dates are filled with interpolated values"""
        result = fill_missing_dates_interpolation(sample_stock_data)
        
        # Check all dates are present
        expected_dates = ['01/01/2023', '02/01/2023', '03/01/2023', '04/01/2023', '05/01/2023', '06/01/2023']
        assert len(result) == 6
        assert all(result['date'].dt.strftime('%d/%m/%Y') == expected_dates)
        
        # Check interpolation
        assert result.loc[1, 'ouverture'] == pytest.approx(101.0)  # Between 100 and 102
        assert result.loc[4, 'cloture'] == pytest.approx(104.5)    # Between 103.5 and 105.5
        
        # Check volume for missing dates is filled with interpolated values
        assert result.loc[1, 'volume'] == pytest.approx(1100)
    
    def test_european_decimal_format(self, sample_stock_data_with_commas):
        """Test that European decimal format (commas) is handled correctly"""
        result = fill_missing_dates_interpolation(sample_stock_data_with_commas)
        
        # Check values were properly converted
        assert result.loc[0, 'ouverture'] == pytest.approx(100.0)
        assert result.loc[1, 'ouverture'] == pytest.approx(101.25)
        assert result.loc[2, 'ouverture'] == pytest.approx(102.5)
        
        # Check interpolation worked (average of 100.0 and 102.5)
        assert result.loc[1, 'date'].strftime('%d/%m/%Y') == '02/01/2023'
    
    def test_missing_columns(self, sample_stock_data_missing_columns):
        """Test function with missing some OHLC columns"""
        result = fill_missing_dates_interpolation(sample_stock_data_missing_columns)
        
        # Should still work with missing columns
        assert len(result) == 2  # No missing dates in input
        assert 'ouverture' in result.columns
        assert 'haut' in result.columns
        assert 'bas' not in result.columns
    
    def test_missing_date_column(self):
        """Test that function raises error when date column is missing"""
        df = pd.DataFrame({'wrong_col': ['01/01/2023'], 'ouverture': [100.0]})
        
        with pytest.raises(ValueError, match="Required column 'date' not found in DataFrame"):
            fill_missing_dates_interpolation(df, date_col='date')
    
    def test_empty_dataframe(self):
        """Test that function handles empty dataframe"""
        df = pd.DataFrame(columns=['date', 'ouverture'])
        
        with pytest.raises(ValueError):
            fill_missing_dates_interpolation(df)

class TestProcessAllRawFiles:
    def test_process_new_file(self, temp_data_dirs, sample_csv_file):
        """Test processing a new file (no existing processed file)"""
        raw_dir, processed_dir = temp_data_dirs
        
        # Mock the project root to point to our temp directory
        with patch('utils.process_stock_data.PROJECT_ROOT', Path(temp_data_dirs[0]).parent.parent):
            process_all_raw_files()
        
        # Check output file was created
        output_file = processed_dir / 'test_stock.csv'
        assert output_file.exists()
        
        # Check content
        result = pd.read_csv(output_file, sep=';')
        assert len(result) == 3  # Original had 2 dates, should add 1 missing date
        
        # Check symbol column was removed
        assert 'symbole' not in result.columns
    
    def test_process_existing_file_no_updates(self, temp_data_dirs, sample_csv_file):
        """Test when processed file exists but no new data"""
        raw_dir, processed_dir = temp_data_dirs
        
        # Create processed file with all data
        output_file = processed_dir / 'test_stock.csv'
        test_data = """date;ouverture;haut;bas;cloture;volume
2023-01-01;100.0;101.0;99.0;100.5;1000
2023-01-03;102.0;103.0;101.0;102.5;1200"""
        
        with open(output_file, 'w') as f:
            f.write(test_data)
        
        # Mock the project root to point to our temp directory
        with patch('utils.process_stock_data.PROJECT_ROOT', Path(temp_data_dirs[0]).parent.parent):
            process_all_raw_files()
        
        # Verify file wasn't modified (still has 2 rows)
        result = pd.read_csv(output_file, sep=';')
        assert len(result) == 2
    
    def test_process_with_new_data(self, temp_data_dirs, sample_csv_file):
        """Test when processed file exists but raw has new data"""
        raw_dir, processed_dir = temp_data_dirs
        
        # Create processed file with partial data
        output_file = processed_dir / 'test_stock.csv'
        test_data = """date;ouverture;haut;bas;cloture;volume
2023-01-01;100.0;101.0;99.0;100.5;1000"""
        
        with open(output_file, 'w') as f:
            f.write(test_data)
        
        # Mock the project root to point to our temp directory
        with patch('utils.process_stock_data.PROJECT_ROOT', Path(temp_data_dirs[0]).parent.parent):
            process_all_raw_files()
        
        # Verify file was updated (now has 3 rows - original 1 + new 1 + interpolated 1)
        result = pd.read_csv(output_file, sep=';')
        assert len(result) == 3
    
    def test_no_raw_files(self, temp_data_dirs):
        """Test when no raw files exist"""
        raw_dir, processed_dir = temp_data_dirs
        
        # Mock the project root to point to our temp directory
        with patch('utils.process_stock_data.PROJECT_ROOT', Path(temp_data_dirs[0]).parent.parent):
            process_all_raw_files()
        
        # No files should be created in processed dir
        assert len(list(processed_dir.glob('*.csv'))) == 0
    
    def test_invalid_csv_file(self, temp_data_dirs):
        """Test with an invalid CSV file"""
        raw_dir, processed_dir = temp_data_dirs
        
        # Create invalid CSV
        invalid_file = raw_dir / 'invalid.csv'
        with open(invalid_file, 'w') as f:
            f.write("not;a;valid;csv;file")
        
        # Mock the project root to point to our temp directory
        with patch('utils.process_stock_data.PROJECT_ROOT', Path(temp_data_dirs[0]).parent.parent):
            process_all_raw_files()
        
        # No output file should be created
        assert not (processed_dir / 'invalid.csv').exists()
    
    def test_directory_structure(self, temp_data_dirs):
        """Test that the function creates the processed directory if it doesn't exist"""
        raw_dir, processed_dir = temp_data_dirs
        
        # Remove processed directory
        shutil.rmtree(processed_dir)
        assert not processed_dir.exists()
        
        # Mock the project root to point to our temp directory
        with patch('utils.process_stock_data.PROJECT_ROOT', Path(temp_data_dirs[0]).parent.parent):
            process_all_raw_files()
        
        # Verify directory was created
        assert processed_dir.exists()