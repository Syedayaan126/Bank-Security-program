from faker import Faker
import pandas as pd
import random
import openpyxl
import time  # NEW: Needed for the delay
import os    # NEW: Needed to check if the file exists

fake = Faker()
file_name = "D://Python//28.py//Mashreq//Mashreq_SignIn_Data.xlsx"

def generate_single_log():
    """Generates exactly one new sign-in attempt."""
    is_suspicious = random.random() < 0.1 # 10% chance of a Signal
    return {
        "User_ID": fake.uuid4()[:8],
        "IP_Address": fake.ipv4(),
        "Location": fake.city(),
        "Login_Attempts": random.randint(1, 3) if not is_suspicious else random.randint(20, 100),
        "Device": fake.android_platform_token(),
        "Timestamp": fake.date_time_this_month().isoformat(),
        "Risk_Level": "High" if is_suspicious else "Low",
        "Contacted_User": "No",
        "Contact_Number": fake.phone_number(),
        "Contact_Email": fake.email()
    }

def highlight(row):
    if row['Risk_Level'] == 'High':
        return ['background-color: yellow'] * len(row)
    else:
        return [''] * len(row)

print("Starting Live Monitoring... Press Ctrl+C to stop.")



def main():
    # --- THE AUTOMATION LOOP ---
    while True:
        try:
            # 1. Generate one new piece of data
            new_data = generate_single_log()
            new_df = pd.DataFrame([new_data])

            # 2. Check if the file already exists to append the new data
            if os.path.exists(file_name):
                existing_df = pd.read_excel(file_name, engine='openpyxl')
                df_logs = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                df_logs = new_df

            # 3. Sort so High Risk is at the top (as you requested)
            df_logs['Risk_Level'] = pd.Categorical(df_logs['Risk_Level'], categories=["High", "Low"], ordered=True)
            df_logs = df_logs.sort_values(by='Risk_Level')

            # 4. Apply your highlight and Save
            df_style = df_logs.style.apply(highlight, axis=1)
            df_style.to_excel(file_name, engine='openpyxl', index=False)

            print(f"Update Successful at {time.strftime('%H:%M:%S')} - Added user: {new_data['User_ID']}")

            # 5. Wait for 5 seconds before checking/generating again
            time.sleep(5)
        except Exception as e:
            print(f"Error Occurred: Retrying in 5 seconds... {e}")
            time.sleep(5)  # Wait before retrying in case of error
