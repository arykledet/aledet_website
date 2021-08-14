import os, sys

def extract_metadata(fd, filename=None):
    metadata = {}
    if filename:
        assert filename[-3:] == '.md'
        metadata["filename"] = filename[:-3]+'.html'
    while True:
        line = fd.readline()
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
            break;
    print(metadata)
    return metadata
                


for file_location in sys.argv[1:]:
    filename = os.path.split(file_location)[1]
    print("Processing file: {}".format(filename))

    file_data = open(file_location).read()
    metadata = extract_metadata(open(file_location), filename)
