import pandas as pd
import os
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent

def fill_missing_dates_interpolation(stock_df, date_col='date'):
    """
    Fill missing dates in stock history DataFrame with:
    - ouverture, haut, bas, cloture, volume = interpolated values (numeric)
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
    and save processed files to the processed data directory. Only appends new data if needed.
    """
    # Define paths relative to project root
    project_root = PROJECT_ROOT
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
                raw_df = raw_df.drop(columns=['symbole'])
                logger.debug(f"Dropped 'symbole' column from {file_name}")
            
            # Convert date column to datetime for comparison
            raw_df['date'] = pd.to_datetime(raw_df['date'], format='%d/%m/%Y', dayfirst=True)
            
            # Check if processed file exists
            if os.path.exists(output_path):
                # Read existing processed file
                processed_df = pd.read_csv(output_path, sep=';')
                processed_df['date'] = pd.to_datetime(processed_df['date'], format='%Y-%m-%d', dayfirst=True)
                
                # Get last dates from both files
                last_processed_date = processed_df['date'].max()
                last_raw_date = raw_df['date'].max()
                
                if last_raw_date <= last_processed_date:
                    logger.info(f"No new data in {file_name}, skipping update")
                    success_count += 1
                    continue
                
                # Find new rows (dates after last processed date)
                new_rows = raw_df[raw_df['date'] > last_processed_date].copy()
                
                if not new_rows.empty:
                    logger.info(f"Found {len(new_rows)} new rows to append")
                    
                    # Combine old processed data with new rows
                    combined_df = pd.concat([processed_df, new_rows], ignore_index=True)
                    
                    # Apply interpolation on the combined dataframe
                    processed_df = fill_missing_dates_interpolation(combined_df)
                else:
                    logger.info("No new rows found despite date difference, skipping update")
                    success_count += 1
                    continue
            else:
                # No existing file, process entire raw file
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