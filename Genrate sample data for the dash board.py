import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_supply_chain_data(n_days=365):
    # Set a seed for reproducibility
    np.random.seed(42)
    
    # Generate dates
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=n_days-1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Base values and trends
    base_order_volume = 1000
    base_inventory_levels = 5000
    base_shipping_delays = 2
    base_supplier_reliability = 0.9
    base_customer_satisfaction = 4

    # Generate data with trends and seasonality
    df = pd.DataFrame({
        'date': dates,
        'order_volume': [
            base_order_volume + 
            100 * np.sin(2 * np.pi * i / 365) +  # Yearly seasonality
            50 * np.sin(2 * np.pi * i / 7) +     # Weekly seasonality
            np.random.normal(0, 50)              # Random noise
            for i in range(n_days)
        ],
        'inventory_levels': [
            base_inventory_levels +
            500 * np.sin(2 * np.pi * i / 365) +  # Yearly seasonality
            np.random.normal(0, 200)             # Random noise
            for i in range(n_days)
        ],
        'shipping_delays': [
            base_shipping_delays +
            0.5 * np.sin(2 * np.pi * i / 365) +  # Yearly seasonality
            0.2 * np.sin(2 * np.pi * i / 7) +    # Weekly seasonality
            np.random.normal(0, 0.2)             # Random noise
            for i in range(n_days)
        ],
        'supplier_reliability': [
            min(1, max(0, base_supplier_reliability +
            0.05 * np.sin(2 * np.pi * i / 365) +  # Yearly seasonality
            np.random.normal(0, 0.02)))           # Random noise
            for i in range(n_days)
        ],
        'customer_satisfaction': [
            min(5, max(1, base_customer_satisfaction +
            0.2 * np.sin(2 * np.pi * i / 365) +   # Yearly seasonality
            np.random.normal(0, 0.1)))            # Random noise
            for i in range(n_days)
        ]
    })
    
    # Add some anomalies
    # Sudden spike in order volume
    df.loc[n_days//2, 'order_volume'] *= 3
    
    # Shipping delay issue
    df.loc[n_days//4:n_days//4+7, 'shipping_delays'] *= 2
    
    # Inventory stockout
    df.loc[3*n_days//4:3*n_days//4+14, 'inventory_levels'] *= 0.2
    
    # Supplier reliability issue
    df.loc[7*n_days//8:7*n_days//8+30, 'supplier_reliability'] *= 0.7
    
    # Customer satisfaction drop
    df.loc[5*n_days//6:5*n_days//6+14, 'customer_satisfaction'] -= 1
    
    # Ensure all values are within realistic ranges
    df['order_volume'] = df['order_volume'].clip(lower=0)
    df['inventory_levels'] = df['inventory_levels'].clip(lower=0)
    df['shipping_delays'] = df['shipping_delays'].clip(lower=0)
    df['supplier_reliability'] = df['supplier_reliability'].clip(lower=0, upper=1)
    df['customer_satisfaction'] = df['customer_satisfaction'].clip(lower=1, upper=5)
    
    # Round numeric columns to appropriate decimal places
    df['order_volume'] = df['order_volume'].round().astype(int)
    df['inventory_levels'] = df['inventory_levels'].round().astype(int)
    df['shipping_delays'] = df['shipping_delays'].round(2)
    df['supplier_reliability'] = df['supplier_reliability'].round(3)
    df['customer_satisfaction'] = df['customer_satisfaction'].round(2)
    
    return df

# Generate the data
data = generate_supply_chain_data(n_days=365)

# Save to CSV
data.to_csv('supply_chain_sample_data.csv', index=False)

print("Sample data has been generated and saved to 'supply_chain_sample_data.csv'")

# Display first few rows of the data
print(data.head())

# Display summary statistics
print(data.describe())