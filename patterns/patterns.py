def read_patterns():
    pattern_files = ["patterns/file_paths.txt", "patterns/file_type.txt", "patterns/extensions.txt"]
    patterns = []

    for file_path in pattern_files:
        with open(file_path, "rb") as f:
            for line in f.xreadlines():
                patterns.append(line.rstrip())

    return patterns

patterns = read_patterns()
