import pandas as pd
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fill_missing_dates_interpolation(stock_df, date_col='date'):
    """
    Fill missing dates in stock history DataFrame with:
    - ouverture, haut, bas, cloture = interpolated values (numeric)
    - volume = 0 (only for missing dates)
    Without altering existing non-null values.
    """
    try:
        df = stock_df.copy()

        # Check if date column exists
        if date_col not in df.columns:
            raise ValueError(f"Required column '{date_col}' not found in DataFrame")

        df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y', dayfirst=True)
        df = df.set_index(date_col).sort_index()
        all_dates = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')

        original_dates = df.index
        df = df.reindex(all_dates)
        is_new_row = ~df.index.isin(original_dates)

        # For OHLC columns, ensure numeric type before interpolation
        ohlc_columns = ['ouverture', 'haut', 'bas', 'cloture', 'volume']
        for col in ohlc_columns:
            if col in df.columns:
                # Convert to numeric, handling European decimal commas if needed
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
                # Create temporary series with interpolated values
                interpolated = df[col].interpolate(method='linear')
                # Only update the new rows with interpolated values
                df.loc[is_new_row, col] = interpolated.loc[is_new_row]

        return df.reset_index().rename(columns={'index': date_col})
    
    except Exception as e:
        raise ValueError(f"Error processing DataFrame: {str(e)}") from e

def process_all_raw_files():
    """
    Process all CSV files in the raw data directory, applying the fill_missing_dates_interpolation function,
    and save processed files to the processed data directory.
    """
    # Define paths relative to project root
    project_root = Path(__file__).parent.parent  # Assumes script is in stock-price-predictions/utils/
    input_dir = project_root / 'data' / 'raw'
    output_dir = project_root / 'data' / 'processed'
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get list of all CSV files in input directory
    raw_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    if not raw_files:
        logger.warning(f"No CSV files found in {input_dir}")
        return
    
    logger.info(f"Found {len(raw_files)} CSV files to process")
    
    success_count = 0
    for file_name in raw_files:
        try:
            # Process each file
            input_path = input_dir / file_name
            output_path = output_dir / file_name
            
            logger.info(f"Processing {file_name}...")
            
            # Read raw data with semicolon delimiter
            raw_df = pd.read_csv(input_path, sep=';')
            
            # Drop the 'symbole' column if it exists
            if 'symbole' in raw_df.columns:
                raw_df = raw_df.drop(columns=['symbole'])  # <-- THIS IS THE ADDED LINE
                logger.debug(f"Dropped 'symbole' column from {file_name}")
            
            # Apply processing function
            processed_df = fill_missing_dates_interpolation(raw_df)
            
            # Save processed data
            processed_df.to_csv(output_path, index=False, sep=';')
            logger.info(f"Successfully processed and saved to {output_path}")
            success_count += 1
            
        except Exception as e:
            logger.error(f"Error processing {file_name}: {str(e)}")
    
    logger.info(f"Processing complete! Successfully processed {success_count}/{len(raw_files)} files")

if __name__ == "__main__":
    # Run the processing pipeline
    process_all_raw_files()