import os
import glob
import re
import stat

default_path = os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/")
icon_folder = os.path.expanduser("~/.var/app/com.valvesoftware.Steam/data/icons/hicolor/")
output_dir = os.path.expanduser("~/Desktop/")

desktop_entry_template = """
[Desktop Entry]
Name={name}
Comment=Play this game on Steam
Exec=flatpak run com.valvesoftware.Steam steam://rungameid/{appid}
Icon={icon_path}
Terminal=false
Type=Application
Categories=Game;
"""

def main():
    print(f"Enter to use default path: {default_path}")

    while True:
        root_dir = os.path.expanduser(input("Enter the root directory path: "))

        if root_dir == "":
            root_dir = default_path
            break
        elif not os.path.isdir(root_dir):
            os.system("clear")
            print("Invalid directory path. Please try again.")
        else:
            break

    # Check all libraries for games
    games = find_steam_games(find_library(root_dir))
    if not games:
        print("no find any games.")
        return

    # Create a menu of available games
    os.system("clear")
    while True:
        # use enumerate to display game list with index
        for idx, game in enumerate(games, 1):
            print(f"{idx}. {game['name']}")

        choice = input("choose a game from the list below: ")
        # Check if the input is digital and within the options
        if choice.isdigit() and 0 < int(choice) <= len(games):
            selected = games[int(choice) - 1]
            break
        else:
            os.system("clear")
            print("Invalid choice. Please enter a number from the list.")

    # find the largest icon for the selected game
    icon_path = get_largest_icon_path(selected['appid'])

    # create the desktop entry file
    desktop_file = os.path.join(
        output_dir,
        f"{selected['name'].replace(' ', '_')}.desktop"
    )

    # create the desktop entry content
    desktop_content = desktop_entry_template.format(
        name=selected['name'],
        appid=selected['appid'],
        icon_path=icon_path
    )

    # write the desktop entry to the file
    with open(desktop_file, 'w', encoding='utf-8') as f:
        f.write(desktop_content)
    # set the file as executable
    current_mode = os.stat(desktop_file).st_mode
    os.chmod(desktop_file, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    os.system("clear")
    print(f"Desktop entry created: {desktop_file}")

def find_library(root_dir):
    vdf_path = os.path.expanduser(f"{root_dir}libraryfolders.vdf")
    library_paths = []

    # Get all library paths from the libraryfolders.vdf file
    with open(vdf_path, encoding='utf-8') as vf:
        # Iterate through each line in the file
        for line in vf:
            # Organize each line and find the path
            line = line.strip()
            if line.startswith('"path"'):
                # Split and extract paths
                lib_root = line.split('"')[3]
                library_paths.append(os.path.join(lib_root, 'steamapps'))

    return library_paths

def find_steam_games(library_paths):
    games_list = []
    # Iterate through each library path and find .acf files
    for library_path in library_paths:
        # Iterate through all .acf files in the library path
        for acf_file in glob.glob(os.path.join(library_path, '*.acf')):
            appid = None
            name = None
            with open(acf_file, encoding='utf-8') as f:
                for line in f:
                    # Organize each line and find the appid and name
                    line = line.strip()
                    if line.startswith('"appid"'):
                        appid = line.split('"')[3]
                    elif line.startswith('"name"'):
                        name = line.split('"')[3]
                    if appid and name:
                        break
            if not appid or not name:
                continue

            # Format the name and replace steam and proton
            lower_name = name.casefold()
            if 'steam' in lower_name or 'proton' in lower_name:
                continue
            games_list.append({'name': name, 'appid': appid})
    return games_list

def get_largest_icon_path(appid):
    sizes = []
    for entry in os.listdir(icon_folder):
        # Match directories named like 'WIDTHxHEIGHT'
        if re.match(r'\d+x\d+', entry):
            apps_dir = os.path.join(icon_folder, entry, 'apps')
            # Proceed only if 'apps' is a directory
            if os.path.isdir(apps_dir):
                # Extract width and height as integers
                w, h = map(int, entry.split('x'))
                # Append max dimension along with directory name
                sizes.append((max(w, h), entry))
    # Sort the collected sizes in descending order (largest first)
    sizes.sort(reverse=True)
    # Look for the icon file in each size directory
    for _, size_dir in sizes:
        candidate = os.path.join(
            icon_folder,
            size_dir,
            'apps',
            f"steam_icon_{appid}.png"
        )
        if os.path.isfile(candidate):
            return candidate
    return None

if __name__ == "__main__":
    main()