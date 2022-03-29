[category]: <> (General)
[date]: <> (2022/03/28)
[title]: <> (How These Posts Work)

# My first post... Hello World!
This post is a test for my python publisher and also a break down of how it works! The publisher takes posts made in markdown and then converts them into html using pandoc before appending the link to my main page. I was inspired by [Vitalik Buterins website](https://vitalik.ca/) and made my own (simpler) version of his python script. This website was mostly an excuse for me to practice my html and css skills but I've decided to also make it a place for me to write mini blogs.

## Breaking down the publisher

I first declare several string constants with pythons string formatting braces. These constants are used to style each post so that they follow the main pages themes.
```python
HEADER = """
<!DOCTYPE html>
<html lang="en-US" data-color-mode="auto" data-light-theme="light" data-dark-theme="dark">
<head>
    <title>{}</title>
    <meta charset="utf-8"/>
    <link rel="shortcut icon" href="transistor.ico" type="image/x-icon" />
    <link rel="stylesheet" type="text/css" href="../../../../style.css">
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

POST_HEADER = """<h2>Posts<h2>\n<ul>"""

POST_TEMPLATE = """
<div class="post"><a href="{}">{}</a></div>
<div class="post-meta">{}</div>
"""
```
Next I get the filename from the file path and pass that to the read_metadata() function

```python
try:
    file_path = sys.argv[1]
except IndexError:
    print("Usage is: publish.py <post.md>")
    sys.exit()

filename = os.path.split(file_path)[1]
print(f"Appending {filename}")

# Extract the metadata from the md file headers
metadata = read_metadata(file_path, filename)
```

The read_metadata() functions first job is to make sure the file is a markdown file. It then parses the words within closed brackets as keys for the *metadata* dictionary. The values for each key is on the same line in closed parentheses, so we use a couple of start and end indices to help parse the data. 

```python
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
```

The metadata is then used to create the posts final path.

```python
    def metadata_to_path(metadata:dict) -> str:
    """Generate a file path using the date"""
    return os.path.join("blogs",metadata["date"],metadata["filename"])
```

The magic of transforming md to html code is handled by pandocs, because no one has time write their own (good) md to html converter.

```python
os.system(f"pandoc -o /tmp/temp.html {file_path}")
```

Now I take all those long constants from before and format them into the posts html source.

```python
def format_post(title:str) -> str:
    """Format the html code for the post"""
    with open("/tmp/temp.html", 'r') as file:
        body = file.read()
    return HEADER.format(title) + body + FOOTER
```

Now we need to make sure the path for the post exists and then write to it.

```python
    truncated_path = os.path.split(path)[0]
    os.system(f"mkdir -p {truncated_path}")

    # Create the post html page
    with open(path, 'w') as out_file:
        out_file.write(file_contents)
```

Lastly we must append the link to the new post the main page. I'm lazy and decided to just use the posts header on my mainpage as a token to tell my script where to append the posts. This way if I ever want to change my homepage I only need to change the html code in one place.

```python
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
```