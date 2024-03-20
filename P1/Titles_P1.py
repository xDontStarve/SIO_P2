import os
import csv
import glob
import ast


class Movie:
    def __init__(self, id, title, type, description, release_year, age_certification, runtime, genres,
                 production_countries, seasons, imdb_id, imdb_score, imdb_votes, tmdb_popularity, tmdb_score):
        self.id = id
        self.title = title
        self.type = type
        self.description = description
        self.release_year = release_year
        self.age_certification = age_certification
        self.runtime = runtime
        self.genres = genres
        self.production_countries = production_countries
        self.seasons = seasons
        self.imdb_id = imdb_id
        self.imdb_score = imdb_score
        self.imdb_votes = imdb_votes
        self.tmdb_popularity = tmdb_popularity
        self.tmdb_score = tmdb_score


def read_csv_files_return_titles_as_list(directory):
    titles = []
    for filename in os.listdir(directory):
        if filename.startswith("titles_output"):
            filepath = os.path.join(directory, filename)
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # skip header row
                for row in reader:
                    title = Movie(*row)
                    titles.append(title)
    return titles


def remove_empty_rows(input_file, output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as infile:
        lines = infile.readlines()

    # Remove empty lines
    non_empty_lines = [line for line in lines if line.strip()]

    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        outfile.writelines(non_empty_lines)


def delete_files_with_prefix(directory, prefix):
    for filename in os.listdir(directory):
        if filename.startswith(prefix):
            filepath = os.path.join(directory, filename)
            try:
                os.remove(filepath)
                print(f"Deleted file: {filename}")
            except OSError as e:
                print(f"Error deleting file {filename}: {e}")


def fix_duplicate_lines_and_fix_description_field(input_file, output_file):
    # Read the input CSV file
    with open(input_file, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)  # Skip the header row
        rows = list(reader)

    # Process the description field by replacing newline characters with spaces
    for row in rows:
        row[3] = row[3].replace('\n', ' ')

    # Remove duplicate rows
    unique_rows = []
    seen = set()
    for row in rows:
        row_tuple = tuple(row)
        if row_tuple not in seen:
            unique_rows.append(row)
            seen.add(row_tuple)

    # Write the cleaned data (without duplicates) to the output CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        writer.writerows(unique_rows)


def read_csv_files_with_prefix_as_list(directory, prefix):
    titles = []
    for filename in os.listdir(directory):
        if filename.startswith(prefix) and filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header row
                for row in reader:
                    title = Movie(*row)
                    titles.append(title)
    return titles

def read_movies_from_csv():
    files = glob.glob('sanitized_*.csv')
    movies = []

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row
            for row in reader:
                id, title, type, description, release_year, age_certification, runtime, genres, production_countries, seasons, imdb_id, imdb_score, imdb_votes, tmdb_popularity, tmdb_score = row
                movie = Movie(id, title, type, description, release_year, age_certification, runtime, genres,
                              production_countries, seasons, imdb_id, imdb_score, imdb_votes, tmdb_popularity,
                              tmdb_score)
                movies.append(movie)

    return movies


def merge_movies(movies):
    merged_movies = {}
    repeated_movies = []

    for movie in movies:
        if movie.id not in merged_movies:
            merged_movies[movie.id] = movie
        else:
            merged = merged_movies[movie.id]

            # Convert genres and production_countries to lists if they are strings
            if isinstance(merged.genres, str):
                merged.genres = ast.literal_eval(merged.genres)
            if isinstance(movie.genres, str):
                movie.genres = ast.literal_eval(movie.genres)
            if isinstance(merged.production_countries, str):
                merged.production_countries = ast.literal_eval(merged.production_countries)
            if isinstance(movie.production_countries, str):
                movie.production_countries = ast.literal_eval(movie.production_countries)

            # Convert age_certification to a list if it's a string
            if isinstance(merged.age_certification, str):
                merged.age_certification = [merged.age_certification]
            if isinstance(movie.age_certification, str):
                movie.age_certification = [movie.age_certification]

            # Criteria to detect same movie (repeated): it has same id and same imdb_id, if it is a remake, it should have a different imdb_id.
            # There can be a show released in different years because one provider has more recent seasons, but it has same id and imdb id.

            if merged.imdb_id == movie.imdb_id:
                # More seasons = more recent, more recent release year = more recent. SO we need to replace the old info.
                if (movie.seasons > merged.seasons or movie.release_year > merged.release_year):

                    # Fix seasons
                    merged.seasons = movie.seasons

                    # Leave the age restriction of the newer title, as it may add new seasons with more age restriction,
                    # a newer version of the same title shall not have less restriction as it also contains all episodes of previous seasons.
                    merged.age_certification = movie.age_certification

                    # Merge genres, production_countries
                    merged.genres = list(set(merged.genres + movie.genres))
                    merged.production_countries = list(set(merged.production_countries + movie.production_countries))

                    # Leave newest description
                    merged.description = movie.description

                    # Leave the most recent runtime
                    merged.runtime = movie.runtime

                    # Leave most recent tmdb information
                    merged.tmdb_popularity = movie.tmdb_popularity
                    merged.tmdb_score = movie.tmdb_score

                    # Leave most recent release_year
                    merged.release_year = movie.release_year


            # Check for different imdb_id, leave the one with most votes
            if movie.imdb_id != merged.imdb_id and movie.release_year == merged.release_year:
                # We take the one with more votes, as it means it is more recent.
                if movie.imdb_votes > merged.imdb_votes and movie.seasons >= merged.seasons:

                    merged.imdb_votes = movie.imdb_votes
                    merged.imdb_id = movie.imdb_id
                    merged.imdb_score = movie.imdb_score

                    # Fix seasons
                    merged.seasons = movie.seasons

                    # Leave the age restriction of the newer title, as it may add new seasons with more age restriction,
                    # a newer version of the same title shall not have less restriction as it also contains all episodes of previous seasons.
                    merged.age_certification = movie.age_certification

                    # Merge genres, production_countries
                    merged.genres = list(set(merged.genres + movie.genres))
                    merged.production_countries = list(set(merged.production_countries + movie.production_countries))
                    merged.age_certification = list(set(merged.age_certification + movie.age_certification))

                    # Leave newest description
                    merged.description = movie.description

                    # Leave the most recent runtime
                    merged.runtime = movie.runtime

                    # Leave most recent tmdb information
                    merged.tmdb_popularity = movie.tmdb_popularity
                    merged.tmdb_score = movie.tmdb_score

                    # Leave most recent release_year
                    merged.release_year = movie.release_year


            repeated_movies.append(movie)
    return list(merged_movies.values())

def remove_empty_lists_from_file(filename='final_titles.csv'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Remove empty lists from each line
        cleaned_lines = [line.replace('[]', '') for line in lines]
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        print(f"Empty lists removed from {filename}.")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")

def save_movies_to_csv(movies, filename='final_titles.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write the header
        writer.writerow(['id', 'title', 'type', 'description', 'release_year', 'age_certification', 'runtime', 'genres',
                         'production_countries', 'seasons', 'imdb_id', 'imdb_score', 'imdb_votes', 'tmdb_popularity',
                         'tmdb_score'])
        # Write the movie data
        for movie in movies:
            # Convert age_certification to a single string (if it's a list)
            if isinstance(movie.age_certification, list):
                age_cert_str = ', '.join(movie.age_certification)
            else:
                age_cert_str = movie.age_certification
            writer.writerow(
                [movie.id, movie.title, movie.type, movie.description, movie.release_year, age_cert_str, movie.runtime,
                 movie.genres, movie.production_countries, movie.seasons, movie.imdb_id, movie.imdb_score,
                 movie.imdb_votes, movie.tmdb_popularity, movie.tmdb_score])


def get_unique_ids_from_csv(filename):
    ids = set()  # Initialize an empty set to store unique ids

    # Get the full path to the CSV file
    file_path = os.path.join(os.path.dirname(__file__), filename)

    # Read the CSV file
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row if it exists
        for row in reader:
            ids.add(row[0])  # Add the id from each row to the set

    return ids


def create_provider_titles_csv(provider, providerId, titles_set):
    file_name = f"provider_{provider}_titles.csv"

    # Write to the CSV file
    with open(file_name, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Write the data rows
        for title_id in titles_set:
            id_value = f"{providerId}_{title_id}"
            writer.writerow([id_value, title_id, providerId])


def merge_provider_csv_files():
    # Define the output filename
    output_filename = "final_provider_movie.csv"

    # Get the list of files in the directory
    files = os.listdir()

    # Filter files with the "provider_" prefix
    provider_files = [file for file in files if file.startswith("provider_")]

    # Create an empty list to store all data rows
    all_rows = []

    # Iterate over each provider file
    for file in provider_files:
        with open(file, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                all_rows.append(row)

    # Write all data to the output file
    with open(output_filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Write the header row
        writer.writerow(['id', 'title_id', 'provider_id'])

        # Write all data rows
        writer.writerows(all_rows)

if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))
    prefix_to_match = "sanitized_"
    delete_files_with_prefix(script_directory, prefix_to_match)
    prefix_to_match = "final_csv"
    delete_files_with_prefix(script_directory, prefix_to_match)

    for filename in os.listdir(script_directory):
        if filename.endswith("Titles.csv"):
            input_filename = filename
            output_filename = "titles_wo_space_" + filename
            remove_empty_rows(input_filename, output_filename)
            input_filename = output_filename
            output_filename = "sanitized_" + filename
            fix_duplicate_lines_and_fix_description_field(input_filename, output_filename)

    prefix_to_match = "titles_wo_space_"
    delete_files_with_prefix(script_directory, prefix_to_match)

    movies = read_movies_from_csv()
    movies = merge_movies(movies)
    save_movies_to_csv(movies)
    remove_empty_lists_from_file()
    prefix_to_match = "sanitized"
    delete_files_with_prefix(script_directory, prefix_to_match)

    # get provider_movie table
    title_set = get_unique_ids_from_csv("Amazon_Prime_Titles.csv")
    create_provider_titles_csv("Amazon_Prime", 1, title_set)

    title_set = get_unique_ids_from_csv("HBOMax_Titles.csv")
    create_provider_titles_csv("hbo_max", 2, title_set)

    title_set = get_unique_ids_from_csv("Disney_Plus_Titles.csv")
    create_provider_titles_csv("disney_plus", 3, title_set)

    title_set = get_unique_ids_from_csv("HuluTV_Titles.csv")
    create_provider_titles_csv("hulutv", 4, title_set)

    title_set = get_unique_ids_from_csv("Netflix_Titles.csv")
    create_provider_titles_csv("netflix", 5, title_set)

    title_set = get_unique_ids_from_csv("ParamountTV_Titles.csv")
    create_provider_titles_csv("paramountTV", 6, title_set)

    title_set = get_unique_ids_from_csv("Rakuten_Viki_Titles.csv")
    create_provider_titles_csv("rakuten", 7, title_set)

    merge_provider_csv_files()

    prefix_to_match = "provider_"
    delete_files_with_prefix(script_directory, prefix_to_match)