# Fourhills
Fourhills gives a DM a text-based interface so that you can move through locations, view location and character descriptions, and have quick access to monster stats during encounters. You can also use it to automatically play background music, so that the music changes depending on the location you're in.

The world is defined with a number of 'location' and 'character' files in a specially arranged directory structure. This is explained in the 'Creating the World' section.

## Using the Program

### Windows Users
I haven't tested this much on Windows. There are three things that might make it more difficult to get working:

1. The location and character files use Unix-style line endings, so you'll need a program like [Notepad++](http://notepad-plus-plus.org/) to create and edit them.
2. On my system, Python 3 didn't automatically make itself available via the command line (so number 3. from 'Getting it Running' didn't work). To get around this, you could try running it through IDLE.
3. I've never used mpd (or they Python library musicpd) with Windows, so I'm not sure whether the background music feature will work.

### Getting it Running
1. Make sure you have Python 3.6 or greater installed.
2. Execute the following commands in a terminal:
```bash
virtualenv venv  # Optional command
. venv/bin/activate  # Optional command for Mac/Linux
venv/Scripts/activate  # Optional command for Windows
pip install .  # Installs all packages and allows 'fourhills' and '4h' to execute program
```
3. If you want to use the automatic background music:
   - Make sure you have mpd installed
   - Install the Python library [musicpd](https://pypi.python.org/pypi/python-musicpd)
   - Use a text editor to open the file fourhills.py and change the line `MUSIC = False` to `MUSIC = True`
4. Test whether it's working, using the example world, by going to a command line and typing `4h --help`
5. Create your own world according the 'Creating the World' section.
6. If you're using the automatic background music controller, create mpd playlists for your locations. See the 'Playlists' section for more details.

### Controls
At each location, a list of characters and places you can go from there are given.

* To view a character description, type cn and press enter (where n is the list number of the character)
* To move to a different location, type ln and press enter (where n is the list number of the location)
* To view the 'battle screen' for the current location (which contains the monster stats for encounters) press b and enter
* To quit the program, press q and enter

## Creating the World

### Directory Structure
The 'World' folder contains the files which define the world and the characters in it. Don't rename that folder. Each location is specified with a .loc file and each character with a .cha file.

Here's how the directory structure works. Inside the 'World' directory should go the location files for each major location in the world. Each place which has more sub-locations (such as a city that has a number of important shops, markets etc.) then these should be contained in a folder with the same name as the city it's in. Characters at a location should also be put in the corresponding directory. Further subdirectories can be added as well because the directories are scanned recursively.

For example, in the example world, there is a file called 'Walton.loc' and a directory called 'Walton'. When you run the program you can move to the Walton location, and from there you can move to Lenson's house, The Copper Sword, or Silvanus's temple because these locations are contained within the 'Walton' folder. When you're in The Copper Sword you can see the 'Lenson' character because his file is contained in the TheCopperSword subdirectory.

### Location Files

Each location file must have five special lines in it, in the correct order, even if they're not all used:

1. The 'Name' of the location, given by ##NAME:Lenson's House for example. Don't put any spaces between the colon and the start of the name.
2. The name of the playlist for this location, given by ##PLAYLISTNAME:Tavern for example. If you want no music at a particular location, use 'None' as the playlist name. This line must be included even if you're not using the music-playing feature of the program.
3. The beginning of the location description, given by ##DESCRIPTION
4. The beginning of the battle screen stats, given by ##BATTLESCREEN
5. At the end of the file, ##END

The location description and battle screen can contain pretty much any text that you want, so just put whatever you think might be useful. I tend to use the description to remind myself of a location's history, appearance, and who important characters are. I usually use the battle screen to list monster stats.

### Character Files

The character files are similar. They have a .cha extension and have three special lines:

1. The character name, given by e.g. ##NAME:Lenson
3. The beginning of the character description, given by ##DESCRIPTION
5. At the end of the file, ##END

## Playlists
If you want to use this program to control the background music, its just a case of creating mpd playlists that you want and putting the relevant playlist name into the location description files, as described in 'Creating the World'. If you want a location to have no music, put the playlist name as 'None'.

When you're running the program, as you move to new locations, the playlist will change. If you move to a new location which has the same playlist then the music won't restart, it will just keep playing.
