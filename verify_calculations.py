
import pandas as pd

def calculate_changes():
    df = pd.read_csv('assets/Dataset/apple_emissions/greenhouse_gas_emissions.csv')
    df = df[df['Type'] == 'Gross emissions']
    
    categories = {
        "Transport": "Product transportation (upstream and downstream)",
        "Manufacturing": "Manufacturing (purchased goods and services)",
        "Business Travel": "Business travel"
    }
    
    results = {}
    
    for label, desc in categories.items():
        v2015 = df[(df['Fiscal Year'] == 2015) & (df['Description'] == desc)]['Emissions'].sum()
        v2022 = df[(df['Fiscal Year'] == 2022) & (df['Description'] == desc)]['Emissions'].sum()
        
        if v2015 != 0:
            change = ((v2022 - v2015) / v2015) * 100
        else:
            change = float('inf')
            
        print(f"{label}: 2015={v2015}, 2022={v2022}, Change={change:.1f}%")

if __name__ == "__main__":
    calculate_changes()
