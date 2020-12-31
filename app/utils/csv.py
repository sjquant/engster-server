import csv


def csv_to_dict(csvfile, delimiter=",", quotechar='"'):
    """Convert csv into list of dict"""
    reader = csv.DictReader(csvfile, delimiter=delimiter, quotechar=quotechar)

    data = {each: [] for each in reader.fieldnames}
    for i, row in enumerate(reader):
        for key, value in row.items():
            data[key].append(value)
    return data
