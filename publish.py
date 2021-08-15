#!/usr/bin/python3
import os, sys

HEADER = """
<!DOCTYPE html>
<html lang="en-US" data-color-mode="auto" data-light-theme="light" data-dark-theme="dark">

    <head>
        <title>Aryk P. Ledet</title>
        <meta charset="utf-8"/>
        <link rel="shortcut icon" href="transistor.ico" type="image/x-icon" />
        <link rel="stylesheet" type="text/css" href="/style.css">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
"""

SIDEBAR = """
        <div class="sidebar">
            <a href="/index.html">Home</a>
            <a href="/about_me.html">About me</a>
            <a href="https://github.com/arykledet">GitHub</a>
            <hr>
        </div>

        <div class="main">
"""

TOC_HEADER = """
        <div class="sidebar">
            <a href="index.html">Home</a>
            <a href="about_me.html">About me</a>
            <a href="https://github.com/arykledet">GitHub</a>
            <hr>
            <!-- <br> -->
            <a id="blogs">Blogs - </a>
"""

TOC_FOOTER = """
        </div>

        <div class="main">
"""

FOOTER = """        
        </div>
    </body>
</html>
"""

INDEX = """
        <header><h1>Aryk P. Ledet</h1></header>
        <hr>
        <img src="imgs/dachshund.png" width=200px height=100px alt="me.png" class="left">

        <p>
            <h2>Oh hai there</h2>

            Hello I'm Aryk and welcome to my webpage. This site is still a work in progress, but I plan on writing mini technology blogs going over old personal projects and topics I find interesting.
        </p>
"""

# File location, Data, Title
TOC_ITEM_TEMPLATE = """
<a href="{}">{} - {}</a>
"""

def extract_metadata(fd, filename=None):
    metadata = {}

    if filename:
        # Make sure file is a markdown
        assert filename[-3:] == '.md'
        metadata["filename"] = filename[:-3]+'.html'
    
    while True:
        line = fd.readline()
        # Find keywords and values
        if line and line[0] == '[' and ']' in line:
            key = line[1:line.find(']')]
            value_start = line.find('(')+1
            value_end = line.rfind(')')

            if key in ('category', 'categories'):
                metadata['categories'] = set([ x.strip().lower() for x in line[value_start:value_end].split(',')])
                assert '' not in metadata['categories']
            else:
                metadata[key] = line[value_start:value_end]
        else:
            break

    return metadata

def metadata_to_path(metadata):
    return os.path.join(
        "blogs",metadata['date'],metadata['filename']
    )

def get_printed_date(metadata):
    year, month, day = metadata['date'].split('/')
    month = 'JanFebMarAprMayJunJulAugSepOctNovDec'[int(month)*3-3:][:3]
    return year + ' ' + month + ' ' + day

def make_toc_item(metadata):
    link = '/' + metadata_to_path(metadata)
    return TOC_ITEM_TEMPLATE.format(link, get_printed_date(metadata), metadata['title'])

def make_sidebar(toc_items):
    return(
        TOC_HEADER + 
        ''.join(toc_items) +
        TOC_FOOTER
    )

def make_toc(toc_items):
    sidebar = make_sidebar(toc_items)
    return (
        HEADER +
        sidebar +
        INDEX +
        FOOTER
    )


if __name__ == '__main__':

    file_location = sys.argv[1]

    filename = os.path.split(file_location)[1]
    print("processing: " + filename)

    metadata = extract_metadata(open(file_location), filename)
    path = metadata_to_path(metadata)

    os.system('pandoc -o /tmp/temp.html {}'.format(file_location))

    # file_contents = (
    #     HEADER + SIDEBAR + open('/tmp/temp_output.html').read() + FOOTER
    # )

    # print("Selected path: " + path)

    # truncated_path = os.path.split(path)[0]

    # print(truncated_path)
    # os.system('mkdir -p {}'.format(os.path.join(truncated_path)))

    # out_location = os.path.join(path)
    # open(out_location, 'w').write(file_contents)

    # Append Table of Contents
    metadatas = []
    categories = set()

    for filename in os.listdir('posts'):
        metadatas.append(extract_metadata(open(os.path.join('posts', filename)), filename))
        categories = categories.union(metadatas[-1]['categories'])

    print("Detected categories: {}".format(' '.join(categories)))

    sorted_metadatas = sorted(metadatas, key=lambda x: x['date'], reverse=True)
    toc_items = [make_toc_item(metadata) for metadata in sorted_metadatas]

    os.system('mkdir -p {}'.format(os.path.join('site', 'categories')))

    file_contents = (
        HEADER + make_sidebar(toc_items) + open('/tmp/temp_output.html').read() + FOOTER
    )

    print("Selected path: " + path)

    truncated_path = os.path.split(path)[0]

    print(truncated_path)
    os.system('mkdir -p {}'.format(os.path.join(truncated_path)))

    out_location = os.path.join(path)
    open(out_location, 'w').write(file_contents)

    open("index.html", 'w').write(make_toc(toc_items))
