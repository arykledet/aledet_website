#!/usr/bin/python3
"""
Author: Aryk Ledet
Desc: Publish and organize markdown posts as blogs to website using pandocs to convert md to html
"""

import os
import sys

HEADER = """<!DOCTYPE html>
<html lang="en-US" data-color-mode="auto" data-light-theme="light" data-dark-theme="dark">
<head>
    <title>{}</title>
    <meta charset="utf-8"/>
    <link rel="shortcut icon" href="transistor.ico" type="image/x-icon" />
    <link rel="stylesheet" type="text/css" href="style.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<div class="main">
"""

FOOTER = """
</div>
</body>
</html>
"""

POST_HEADER = """<h2>Posts<h2>\n"""

POST_TEMPLATE = """
<div class="post"><a href="{}">{}</a></div>
<div class="post-meta">{}</div>

"""

def read_metadata(path: str, filename: str = None) -> dict:
    """Extract the metadata into a dict"""
    metadata = {}

    # Check if the file exists and is markdown
    if filename:
        assert filename[-3:] == ".md"
        metadata["filename"] = f"{filename[:-3]}.html"

    # Parse all lines with metadata from the md file
    # exit once line does not contain closed brakets
    # Meta data format:
    # [key]: <> (value)
    with open(path, 'r') as file:
        while True:
            line = file.readline()
            # Check if line has metadata bracket
            if line[0] == '[' and ']' in line:
                key = line[1:line.find(']')]
                val_start = line.find('(')+1
                val_end = line.find(')')

                # Category key can contain multiple categories 
                if key in ("category", "categories"):
                    metadata["categories"] = set(
                        [x.strip().lower() for x in line[val_start:val_end].split(',')]
                    )
                    assert '' not in metadata["categories"]
                else:
                    metadata[key] = line[val_start:val_end]
            else:
                break

    return metadata

def metadata_to_path(metadata:dict) -> str:
    """Generate a file path using the date"""
    return os.path.join("blogs",metadata["date"],metadata["filename"])

def get_printed_date(metadata:dict) -> str:
    """Convert the date into a prettier format""" 
    year, month, day = metadata["date"].split('/')
    month = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")[int(month)-1]
    return f"{month} {day} {year}"

def format_post(title:str) -> str:
    """Format the html code for the post"""
    with open("/tmp/temp.html", 'r') as file:
        body = file.read()
    return HEADER.format(title) + body + FOOTER

def make_post_template(metadata:dict) -> str:
    """Append the metadata to the index pages post template"""
    link = '/' + metadata_to_path(metadata)
    return POST_TEMPLATE.format(link, metadata['title'], get_printed_date(metadata))

def append_to_page(post_template:str=None, page:str="index.html"):
    """Appends after the poster header in the index page"""
    # Throw an error if no post_template
    assert isinstance(post_template, type(None)) is False

    with open(page, "r+") as file:
        data = file.read()
        index = data.find(POST_HEADER) + len(POST_HEADER)
        data = data[:index] + ''.join(post_template) + data[index:]
        # Go back to the begining of the file and write the new data
        file.seek(0)
        file.write(data)
        # Truncate just incase the file is somehow smaller
        file.truncate()

if __name__ == '__main__':
    try:
        file_path = sys.argv[1]
    except IndexError:
        print("Usage is: publish.py <post.md>")
        sys.exit()

    filename = os.path.split(file_path)[1]
    print(f"Appending {filename}")

    # Extract the metadata from the md file headers
    metadata = read_metadata(file_path, filename)
    # Use the date to format the file path
    path = metadata_to_path(metadata)

    # Use pandoc to convert md to html
    os.system(f"pandoc -o /tmp/temp.html {file_path}")

    # Format the pandoc page to sites format
    file_contents = format_post(metadata["title"])

    # Create the file path for the post
    truncated_path = os.path.split(path)[0]
    os.system(f"mkdir -p {truncated_path}")

    # Create the post html page
    with open(path, 'w') as out_file:
        out_file.write(file_contents)

    # Add post to the list of posts on main page
    append_to_page(make_post_template(metadata))
    