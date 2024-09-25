import os

def import_extra_context(directory_str):
    directory = os.fsencode(directory_str)
    result = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".txt"):
            with open(os.path.join(directory_str, filename), "r") as f:
                content = f.read().splitlines()
                result.append([content[0], content[1:]])
        else:
            continue

    return result

