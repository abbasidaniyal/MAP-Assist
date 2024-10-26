import pandas as pd
import random
import numpy as np
from faker import Faker

# Instantiate Faker for random data generation
fake = Faker()

# Define columns and example helps
columns = ["Name", "Phone", "Email", "Address", "Latitude", "Longitude", "Gender", "DOB", "Helps"]
helps_options = [
    "Awareness", "Training", "First Aid", "Evacuation", "Supplies", "Drills", "Sandbags", "Contacts", "Hazard Map",
    "Alerts", "Translation", "Collection", "Shelter", "Recruitment", "Food", "Water", "Medical", "Support",
    "Communication", "Rescue", "Clearance", "Assessment", "Childcare", "Lost & Found", "Housing", "Information",
    "Transport", "Hygiene", "Counseling", "Follow-up", "Relief", "Clean-up", "Legal", "Rebuild", "Financial", 
    "Recovery", "Job Aid", "School", "Mental Health", "Clothing", "Pet Care", "Relocation", "Documentation", 
    "Financial Aid", "Power Supply", "Waste Removal", "Trauma Support", "Helpline", "Triage", "Security", 
    "Blood Donation", "Coordination", "Cash Aid", "Resource Sharing", "Equipment", "Debris Removal", 
    "Temporary Shelter", "Medical Camps", "Language Help", "Needs Assessment", "Damage Reports", "Toolkits", 
    "Construction", "Psych Support", "Medication", "Vaccination", "Food Packs", "Emergency Kits", "Babysitting", 
    "Insurance", "Remapping", "Health Kits", "Sanitation", "Crowd Control", "Temporary Schools", "Life Skills"
]

# Gainesville Florida latitude and longitude bounds
latitude_min, latitude_max = 29.62, 29.68
longitude_min, longitude_max = -82.40, -82.30

# Define gender choices
gender_choices = ["Male", "Female", "Other"]

# Generate 2000+ entries
num_entries = 2000
data = []

for _ in range(num_entries):
    name = fake.name()
    # Generate phone in (XXX) XXX-XXXX format
    phone = fake.phone_number().replace(" ", "").replace("-", "")
    email = fake.email()
    address = f"{fake.street_address()}, Gainesville, FL"
    # Uniform distribution for latitude and longitude around Gainesville
    latitude = round(random.uniform(latitude_min, latitude_max), 6)
    longitude = round(random.uniform(longitude_min, longitude_max), 6)
    gender = random.choice(gender_choices)
    # DOB with a range before 2000
    dob = fake.date_of_birth(minimum_age=24, maximum_age=75).isoformat()
    # Random 3-7 helps
    helps = ",".join(random.sample(helps_options, random.randint(3, 7)))  
    
    data.append([name, phone, email, address, latitude, longitude, gender, dob, helps])

# Create DataFrame and save to CSV
df = pd.DataFrame(data, columns=columns)
df.to_csv("volunteers_gainesville.csv", index=False)

print("Data generation complete. Saved to 'volunteers_gainesville.csv'.")
