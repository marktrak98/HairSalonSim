# HairSalonSim
A Haircut Game!

![image](https://github.com/marktrak98/HairSalonSim/assets/59167428/a58dec90-04fb-4e32-94e9-ad07b8527d89)

![image](https://github.com/marktrak98/HairSalonSim/assets/59167428/af9494ee-6ebb-4807-92ba-d0211bea6355)

![image](https://github.com/marktrak98/HairSalonSim/assets/59167428/db15a468-079c-4590-9b08-54fca1761876)

Note: If run on windows, the man and woman icons are replaced by X and Y respectively. windows-curses seems unable to handle UNICODE icons ¯\\_(ツ)_/¯.

# How to run

1) Install Python3.x (I used Python3.8)
2) Install curses (comes preinstalled for macos and linux, for windows use the following code)

`python -m pip install windows-curses`

OR 

`python3 -m pip install windows-curses`

3) Clone the repository/download and unzip it
4) run main.py in the terminal
   
`python main.py`

OR

`python3 main.py`

# How to play
1) 'wasd' to move around

2) 'shift+n' to summon a new character to your barbershop. They will move to sit in one of the waiting chairs.
   
4) 'n' to call out "next!", i.e make one of the customer's sitting in the waiting chairs to move to the haircutting chair.
   
6) You can 'bump' into a character sitting on the haircutting chair to open the haircutting menu. Use 'e' to exit from the haircutting menu
   
8) You can open one of the categories- 'p' for prep, 'c' for cut and 'f' for finish. After pressing one of those keys you can use x to go back to earlier menu.
   
10) In each menu you can perform the corresponding actions by their hotkeys, specified in brackets, eg: (w)ash has hotkey 'w'.
    
12) For actions such as (s)cissors, you are brought to yet another menu. Use 't' and 'g' to adjust how much you are cutting off and 'wasd' to choose the section of hair you want to cut. Enter key confirms the cut and does the action. Use 'x' to go back to earlier menu. precise, wide, bulk option doesn't work right now. Razor has not been implemented yet.

13) 'q' to quit.
    
14) Have fun!


Note: This is currently a demo, and I have intentions to work on this prototype to make a proper game out of it(with character's having moods, expectations, reactions, etc(I believe I have the background knowledge to implement this using state machines and such). And I'm posting this up in hopes of getting an artist to help with game art so I can possibly redesign it with actual graphics.


# Debug
If the game lines seem all over the place, try increasing the size of your terminal window and reloading the game.
