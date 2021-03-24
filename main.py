import sys


def get_contributions(git_log_filename):
    log = open(git_log_filename, "r")

    contributions = {}
    contributions_per_file = {}

    author = ""
    while True:
        line = log.readline()

        # EOF check
        if line == "":
            break

        if line == "\n":
            continue

        author = line

        file = log.readline()
        while file != "\n" and file != "":
            if (author, file) in contributions:
                contributions[(author, file)] += 1
            else:
                contributions[(author, file)] = 1

            if file in contributions_per_file:
                contributions_per_file[file]["count"] += 1
            else:
                contributions_per_file[file] = {"creator": author, "count": 1}

            file = log.readline()

    return contributions, contributions_per_file


def get_file_creator(contributions, target_file):
    for author, file in contributions.keys():
        if file == target_file:
            return author

    return ""


def calculate_authorship_score(is_creator, author_modification_count, others_modification_count):
    creator_weight = 1 if is_creator else 0

    score = creator_weight + 0.5 * author_modification_count - \
        0.1 * others_modification_count

    if score < 0:
        score = 0

    return score


def get_files_and_authors(contributions):
    files = []
    authors = []
    for author, file in contributions.keys():
        if not (author in authors):
            authors.append(author)

        if not (file in files):
            files.append(file)

    return files, authors


def get_authorships(contributions, contributions_per_file):
    files, authors = get_files_and_authors(contributions)

    authorships = []
    for file in files:
        file_authorships = []

        total_score = 0
        for author in authors:
            is_creator = contributions_per_file[file]["creator"] == author

            author_modification_count = 0
            if (author, file) in contributions:
                author_modification_count = contributions[(author, file)]

            others_modification_count = contributions_per_file[file]["count"] - \
                author_modification_count

            score = calculate_authorship_score(
                is_creator, author_modification_count, others_modification_count)

            file_authorships.append((file, author, score))
            total_score += score

        if total_score > 0:
            file_authorships = [(file, author, score / total_score)
                                for file, author, score in file_authorships]

        authorships += file_authorships

    return authorships


def sort_ranking_by_score(raking_entry):
    return raking_entry[1]


def get_authors_ranking(authorships, contributions, ranking_size):
    files, authors = get_files_and_authors(contributions)

    ranking = []
    for target_author in authors:
        total_score = 0
        for _, author, score in authorships:
            if author == target_author:
                total_score += score
        ranking.append((target_author, total_score))

    ranking.sort(key=sort_ranking_by_score, reverse=True)

    return ranking[:ranking_size]


def main():
    if len(sys.argv) != 2:
        print("Wrong usage. Pass the git log output file name in the first parameter.")
        return

    _, filename = sys.argv

    contributions, contributions_per_file = get_contributions(filename)

    authorships = get_authorships(contributions, contributions_per_file)

    print(get_authors_ranking(authorships, contributions, 10))


if __name__ == "__main__":
    main()
