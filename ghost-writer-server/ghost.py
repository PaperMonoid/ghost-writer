import os


GHOST_DIRECTORY = 'ghosts'


def ghost_list():
    directory_list = []

    for filename in os.listdir(GHOST_DIRECTORY):
        path = os.path.join(GHOST_DIRECTORY, filename)
        if os.path.isdir(path):
            directory_list.append(filename)

    return directory_list