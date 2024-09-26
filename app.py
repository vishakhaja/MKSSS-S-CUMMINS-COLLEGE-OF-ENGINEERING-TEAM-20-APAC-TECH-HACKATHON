from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load exchange rate data into a dictionary with the year as the key
data_files = {}
for year in range(2012, 2023):  # Change the range as needed
    df = pd.read_csv(f'./data/Processed_Exchange_Rate_{year}.csv')
    
    # Clean up the column names
    df.columns = df.columns.str.strip()  # Remove leading and trailing spaces
    df.columns = df.columns.str.replace(' ', '_')  # Replace spaces with underscores
    df.columns = df.columns.str.replace('(', '').str.replace(')', '')  # Remove parentheses

    data_files[str(year)] = df
for year, df in data_files.items():
    print(f"Valid currencies for {year}: {df.columns.tolist()}")
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/exchange_rates', methods=['GET'])
def get_exchange_rates():
    currency1 = request.args.get('currency1')
    currency2 = request.args.get('currency2')
    duration = request.args.get('duration').capitalize()  # Capitalize for consistency
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        start_year, _, _ = start_date.split('-')  # Extract the year from start_date

        # Check if the extracted year is valid
        if start_year not in data_files:
            return jsonify({'error': 'Invalid year selected'}), 400

        # Load the DataFrame for the selected year
        df = data_files[start_year]

        # Rename columns to remove spaces and parentheses
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

        # Ensure the 'Date' column is parsed correctly
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')

        # Validate currency columns
        valid_currencies = set(df.columns)  # Get valid currencies from the DataFrame
        if currency1 not in valid_currencies or currency2 not in valid_currencies:
            return jsonify({'error': 'Invalid currency selection'}), 400

        # Convert start_date and end_date to datetime for filtering
        start_date_dt = pd.to_datetime(start_date, format='%Y-%m-%d', errors='coerce')
        end_date_dt = pd.to_datetime(end_date, format='%Y-%m-%d', errors='coerce')

        # Filter by date range
        df_filtered = df[(df['Date'] >= start_date_dt) & (df['Date'] <= end_date_dt)]

        # Group by the desired duration (monthly or quarterly)
        df_filtered.set_index('Date', inplace=True)
        if duration == 'Monthly':
            df_grouped = df_filtered.resample('M').mean()
        elif duration == 'Quarterly':
            df_grouped = df_filtered.resample('Q').mean()
        else:
            return jsonify({'error': 'Invalid duration selected'}), 400

        # Prepare the response data
        response_data = df_grouped[[currency1, currency2]].rename(
            columns={currency1: currency1, currency2: currency2}
        ).reset_index()

        return jsonify(response_data.to_dict(orient='records'))

    except Exception as e:
        return jsonify({'error': f'Error processing data: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)

