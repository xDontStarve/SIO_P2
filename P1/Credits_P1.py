import csv
import itertools
import os
import pandas as pd
from unidecode import unidecode

class Person_Title:
    def __init__(self, title_ID, person_id, actor, director, character):
        self.id = person_id + "_" + title_ID
        self.title_ID = title_ID
        self.person_id = person_id
        self.actor = actor
        self.director = director
        self.character = character


def remove_hyphens(text):
    return text.replace("-", "") if isinstance(text, str) else text

def normalize_text(text):
    return unidecode(text.lower()) if isinstance(text, str) else text

#de-duplicate lines
def remove_duplicates_from_csv(csv_file):
    # Create a set to store unique lines
    unique_lines = set()

    # Create a temporary file to store unique lines
    temp_file = csv_file + '.tmp'

    # Open the CSV file for reading and the temporary file for writing
    with open(csv_file, mode='r', newline='', encoding='utf-8') as infile, \
            open(temp_file, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Iterate over each line in the CSV file
        for line in reader:
            # Convert the line to a tuple to make it hashable
            line_tuple = tuple(line)
            # Check if the line is unique
            if line_tuple not in unique_lines:
                # If unique, add it to the set and write it to the temporary file
                unique_lines.add(line_tuple)
                writer.writerow(line)

    # Replace the original file with the temporary file
    os.replace(temp_file, csv_file)

#De-duplicate CSV further with panda
def process_csv(file_path):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    full_file_path = os.path.join(script_directory, file_path)
    df = pd.read_csv(full_file_path)

    df["name"] = df["name"].apply(remove_hyphens)
    df["character"] = df["character"].apply(remove_hyphens)
    df["name"] = df["name"].apply(normalize_text)
    df["character"] = df["character"].apply(normalize_text)

    df.drop_duplicates(subset=["person_id", "id", "name", "character", "role"], inplace=True, ignore_index=True)
    return df

def read_csv_and_create_objects(filename):
    person_title_set = set()  # Initialize an empty set to store Person_Title objects

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title_ID = row['id']
            person_id = row['person_id']
            actor = True if row["role"] == "ACTOR" else False
            director = True if row["role"] == "DIRECTOR" else False
            character = row['character']

            # Create a Person_Title object
            person_title = Person_Title(title_ID, person_id, actor, director, character)

            # Add the object to the set
            person_title_set.add(person_title)

    return person_title_set

def save_person_titles_to_csv(person_titles, csv_file):
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'title_id', 'person_id', 'actor', 'director'])
        for person_title in person_titles:
            writer.writerow([person_title.id, person_title.title_ID, person_title.person_id, person_title.actor, person_title.director])


def save_persons_to_csv(unique_persons_set, csv_file):
    # Open the CSV file in write mode
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        # Define the field names for the CSV header
        fieldnames = ['id', 'name']

        # Create a CSV writer object
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Iterate over the set and write each element as a row
        for person_id, name in unique_persons_set.items():
            writer.writerow({'id': person_id, 'name': name})

def save_person_character_to_csv(person_character_set, csv_file):
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'person_title_id', 'character'])
        for (id, person_title_id, character) in person_character_set:
            writer.writerow([id, person_title_id, character])

#Function to read list of people
def read_unique_persons_from_csv(csv_file):
    unique_persons_set = {}

    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            person_id = row['person_id']
            name = row['name']
            unique_persons_set[person_id] = name

    return unique_persons_set

# remove almost identical lines of person_titles (to merge actor, director values)
def merge_actor_director_lines(csv_file):
    # Create a dictionary to store merged lines
    merged_lines = {}

    # Open the CSV file for reading
    with open(csv_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        # Iterate over each line in the CSV file
        for row in reader:
            # Create a unique identifier for the line based on id, title_id, and person_id
            identifier = (row['id'], row['title_id'], row['person_id'])

            # Check if the identifier already exists in the merged lines dictionary
            if identifier in merged_lines:
                # If it exists, update the actor and director values
                if row['actor'] == 'True':
                    merged_lines[identifier]['actor'] = 'True'
                if row['director'] == 'True':
                    merged_lines[identifier]['director'] = 'True'
            else:
                # If it doesn't exist, add the row to the merged lines dictionary
                merged_lines[identifier] = row

    # Write the merged lines to a temporary file
    temp_file = csv_file + '.tmp'
    with open(temp_file, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['id', 'title_id', 'person_id', 'actor', 'director']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in merged_lines.values():
            writer.writerow(row)

    # Replace the original file with the temporary file
    os.replace(temp_file, csv_file)

def read_person_character_from_csv(csv_file):
    person_character_set = set()

    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            person_id = row['person_id']
            character = row['character']
            title = row['id']
            person_character_set.add((person_id+"_"+character, person_id+"_"+title, character))

    return person_character_set

def delete_files_with_prefix(directory, prefix):
    for filename in os.listdir(directory):
        if filename.startswith(prefix):
            filepath = os.path.join(directory, filename)
            try:
                os.remove(filepath)
                print(f"Deleted file: {filename}")
            except OSError as e:
                print(f"Error deleting file {filename}: {e}")

# Process all "Credits.csv" files in the same directory
merged_df = pd.DataFrame()
for filename in os.listdir():
    if filename.lower().endswith("credits.csv"):
        df = process_csv(filename)
        merged_df = pd.concat([merged_df, df], ignore_index=True)

# Save the merged data to "merged_raw_csv.csv"
merged_file_path = "Credits_merged_raw_csv.csv"
merged_df.to_csv(merged_file_path, index=False)
print(f"Merged data saved to {merged_file_path}")

# Remove duplicates from the merged data
deduplicated_df = process_csv(merged_file_path)
script_directory = os.path.dirname(os.path.abspath(__file__))
delete_files_with_prefix(script_directory, "Credits_merged_raw")
# Save the cleaned data to "deduplicated_csv.csv"
deduplicated_file_path = "Credits_deduplicated_csv.csv"
deduplicated_df.to_csv(deduplicated_file_path, index=False)

print(f"Deduplicated data saved to {deduplicated_file_path}")

csv_filename = "Credits_deduplicated_csv.csv"
person_titles = read_csv_and_create_objects(csv_filename)

# save person_titles
save_person_titles_to_csv(person_titles, 'person_titles.csv')
# De-duplicate person_titles
remove_duplicates_from_csv('person_titles.csv')
merge_actor_director_lines('person_titles.csv')

# Load person table
unique_persons = read_unique_persons_from_csv(csv_filename)
save_persons_to_csv(unique_persons, 'unique_persons.csv')

# Load Person Character table
person_character_set = read_person_character_from_csv(csv_filename)
save_person_character_to_csv(person_character_set, 'person_characters.csv')