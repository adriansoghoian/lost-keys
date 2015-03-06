def read_patterns(file_path):
    patterns = []

    with open(file_path, "rb") as f:
        for line in f.xreadlines():
            patterns.append(line.rstrip())

    return patterns

file_paths_patterns = read_patterns("patterns/file_paths.txt")
file_type_patterns = read_patterns("patterns/file_type.txt")
extensions_patterns = read_patterns("patterns/extensions.txt")
