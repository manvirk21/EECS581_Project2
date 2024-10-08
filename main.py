"""

Authors: Abhishek Bhatt [3086901], Samuel Buehler [3031928], Collins Gatimi [2791182], Mikaela Navarro [2998217], Andrew Vanderwerf [3075534]

Updated by: Matthew McManness [2210261], Manvir Kaur [3064194], Magaly Camacho [3072618], Mariam Oraby [3127776], Shravya Matta [3154808]
Date Created: 09/09/24
Date Last Modified: 09/29/24

Program Tile: Battleship
Program Description: Create a game where two players can place their ships on their grid and try to hit each other's ships by guessing the ships' location on the grid. The first player to sink all the opponent's ships wins.
Update Description: Added 3 AI difficulties and a persistant scoreboard.

Sources: YouTube, ChatGPT
Inputs: User mouse/key inputs
Output: Game screen

""" 
# Import modules
import pygame
import random
import os
import json

# Initialize pygame and pygame's mixer (for sound)
pygame.init() 
pygame.mixer.init()#Init for music/sound

# Load sound files for various in-game events (hits, misses, ship sinking, win)
hit_sound = pygame.mixer.Sound("assets/hit_sound.wav") #Sound for when a ship is hit
miss_sound = pygame.mixer.Sound("assets/miss_sound.wav") #Sound for when a miss happens
sunk_sound = pygame.mixer.Sound("assets/sunk_sound.wav") #Sound for when a ship is sunk
win_sound = pygame.mixer.Sound("assets/win_sound.wav") #Sound for when the game ends
# Set up the display/window dimensions and title
WIDTH, HEIGHT = 1200, 600 #Screen width/height
win = pygame.display.set_mode((WIDTH, HEIGHT)) #Sets the dimensions for the window
pygame.display.set_caption("2-Player Battleship") #Caption for the screen

# Define colors
WHITE = (255, 255, 255) 
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GREY = (169, 169, 169)
GHOST_COLOR = (200, 200, 200)
BLUE = (0, 0, 255)  # Color for sunk ships on the ship grids
# Grid settings
CELL_SIZE = 40 #Cell size for each cell in the grid
GRID_SIZE = 10 #10x10 grid for placing ships
MARGIN = 50 #Margin around the grid

# Load ship images for different ship sizes
ship_images = {
    1: pygame.image.load("assets/ship_1.png"), #1-cell ship
    2: pygame.image.load("assets/ship_2.png"), #2-cell ship
    3: pygame.image.load("assets/ship_3.png"), #3-cell ship
    4: pygame.image.load("assets/ship_4.png"), #4-cell ship
    5: pygame.image.load("assets/ship_5.png") #5-cell ship
}

# Resize the ship images to fit the grid cells
for key in ship_images:
    ship_images[key] = pygame.transform.scale(ship_images[key], (CELL_SIZE, CELL_SIZE)) 

# Initialize grids for both players
grid1 = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # Player 1 ship grid
missile_board1 = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # Player 1 missile grid
grid2 = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # Player 2 ship grid
missile_board2 = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # Player 2 missile grid

# Default ship lengths
default_ships = [1, 2, 3, 4, 5]

font = pygame.font.Font(None, 36) #Setting the font for text in the game

# New Functions:
#function to display the main menu
def display_menu():
    """Menu to select between playing or showing leaderboard"""
    # Default selection
    menu_selection = "Leaderboard"
    menu_running = True

    while menu_running:
        win.fill(BLACK) #clear the screen with black background

        # Display menu options
        draw_text("Main Menu", WIDTH // 2 - 100, HEIGHT // 2 - 100) #title
        draw_text(f"Current selection: {menu_selection}", WIDTH // 2 - 150, HEIGHT // 2)# show current selection
        draw_text("Use LEFT/RIGHT arrows to change selection", WIDTH // 2 - 200, HEIGHT // 2 + 50) #Instructions
        draw_text("Press ENTER to confirm", WIDTH // 2 - 100, HEIGHT // 2 + 100) #Instruction to confirm

        pygame.display.flip()#Update the display

        #handle menu input(navigation and selection)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #if user clicks the close button
                pygame.quit() #quit the game
                quit()

            if event.type == pygame.KEYDOWN: #Key press event
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:  #toggle between options
                    # Toggle between 'Leaderboard' and 'Game'
                    if menu_selection == "Leaderboard":
                        menu_selection = "Game" #switch to game mode
                    else:
                        menu_selection = "Leaderboard" #switch back to leaderboard

                if event.key == pygame.K_RETURN: #if Enter key is pressed
                    # Confirm selection and exit menu
                    if menu_selection == "Leaderboard":
                        display_leaderboard()  # Call the leaderboard function to display the leaderboard
                    # Exit menu and continue to the game
                    menu_running = False

#Function to add the player's score to the leaderboard 
def add_score_to_leaderboard(player_score):
    """Adds the winning player's score to the leaderboard"""
    player_name = ""  # To store the player's name input
    name_entered = False
    input_active = True

    #Loop for handling name input
    while input_active:
        win.fill(BLACK) #Clear the screen
        
        # Display instructions and current input
        draw_text("Enter your name: " + player_name, WIDTH // 2 - 150, HEIGHT // 2 - 50)# show name input
        draw_text("Press ENTER to submit", WIDTH // 2 - 150, HEIGHT // 2 + 50) #instruction to submit
        pygame.display.flip() #update display

        #Handle input events for typing and name entry
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: #If enter key is pressed
                    name_entered = True  # Finish name input
                    input_active = False

                elif event.key == pygame.K_BACKSPACE: #if backspace is pressed
                    # Remove the last character from the name
                    player_name = player_name[:-1]
                else:
                    # Add the pressed key to the player_name string
                    player_name += event.unicode

    # Once name is entered, proceed to save the score
    if name_entered:
        # Assuming leaderboard is stored as a list of dictionaries in a file or a global list
        leaderboard = []  # Load existing leaderboard data from a file or global variable

        try:
            # Open the leaderboard file and load the existing scores (JSON format for simplicity)
            with open("leaderboard.json", "r") as f:
                leaderboard = json.load(f)
        except FileNotFoundError:
            # If no leaderboard exists, create a new empty leaderboard
            leaderboard = []

        # Add the new score to the leaderboard
        new_entry = {"name": player_name, "score": player_score}
        leaderboard.append(new_entry)

        # Sort the leaderboard by score in descending order (highest scores first)
        leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)

        # Save the updated leaderboard back to the file
        with open("leaderboard.json", "w") as f:
            json.dump(leaderboard, f)

        print(f"Added {player_name}'s score of {player_score} to the leaderboard!")

#function to select the game mode (pass and play or AI mode)
def select_game_mode():
    """
    Present a menu to select between pass and play mode or AI mode.
    Returns a string (either "pass_and_play" or "AI")
    """
    game_mode = "pass_and_play" # Default
    menu_running = True

    while menu_running:
        win.fill(BLACK) #clear the screen

        # Display menu options:
        draw_text("Select Game Mode", WIDTH // 2 - 150, HEIGHT // 2 - 100)
        draw_text(f"Current selection: {game_mode}", WIDTH // 2 - 100, HEIGHT // 2)
        draw_text("Use LEFT/RIGHT arrows to change mode", WIDTH // 2 - 200, HEIGHT // 2 + 50)
        draw_text("Press ENTER to confirm", WIDTH // 2 - 100, HEIGHT // 2 + 100)

        pygame.display.flip()

        # Handle input events for navigating and selecting game mode
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        # Toggle between 'pass_and_play' and 'AI'
                        if game_mode == "pass_and_play":
                            game_mode = "AI" #switch to AI mode
                        else:
                            game_mode = "pass_and_play" # Switch back to pass and play


                    if event.key == pygame.K_RETURN: # If Enter key is pressed
                        # Confirm selection and exit menu
                        menu_running = False

    return game_mode #return the selected game mode

def select_ai_difficulty():
    """"
    Presents a menu to select the AI Level
    Returns: A string indicating the AI difficulty ("easy", "medium", "hard")
    """

    ai_difficulty = "easy"  # Default AI difficulty is set to "easy".
    menu_running = True # This flag controls whether the difficulty selection menu is running.

    while menu_running:
        win.fill(BLACK) #clear the screen

        # Display the difficulty selection menu
        draw_text("Select AI Difficulty", WIDTH // 2 - 150, HEIGHT // 2 - 100)
        draw_text(f"Current selection: {ai_difficulty}", WIDTH // 2 - 100, HEIGHT // 2)
        draw_text("Use LEFT/RIGHT arrows to change difficulty", WIDTH // 2 - 200, HEIGHT // 2 + 50)
        draw_text("Press ENTER to confirm", WIDTH // 2 - 100, HEIGHT // 2 + 100)

        pygame.display.flip() # Update the screen to show the menu.

        # Event handling to change the AI difficulty or quit the game.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Handle window close event.
                pygame.quit()  # Quit pygame.
                quit()  # Exit the program.

            if event.type == pygame.KEYDOWN:  # If a key is pressed.
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    # Cycle through the AI difficulty levels.
                    if ai_difficulty == "easy":
                        ai_difficulty = "medium"  # Change from easy to medium.
                    elif ai_difficulty == "medium":
                        ai_difficulty = "hard"  # Change from medium to hard.
                    else:
                        ai_difficulty = "easy"  # Reset to easy from hard.

                if event.key == pygame.K_RETURN:  # Confirm the selection with ENTER key.
                    menu_running = False  # Exit the menu loop once a selection is made.

    return ai_difficulty  # Return the selected AI difficulty.

def place_ai_ships(grid, ships_to_place, player2_ships):
    """
    Automatically places the AI's ships on the grid.
    Arguments:
         - grid: The AI's grid where ships will be placed.
         - ships_to_place: List of ship lengths to be placed.
         - player2_ships: A list to store the AI's ship positions and states.
    """
    
    # Loop over each ship's length to place them on the grid.
    for ship_len in ships_to_place:
        placed = False  # Flag to indicate whether the ship was successfully placed.
        while not placed:
            # Randomly choose between horizontal ('H') or vertical ('V') orientation.
            orientation = random.choice(["H", "V"])

            if orientation == "H":  # For horizontal placement.
                row = random.randint(0, GRID_SIZE - 1)  # Random row.
                col = random.randint(0, GRID_SIZE - ship_len)  # Ensure the ship fits horizontally.
            else:  # For vertical placement.
                row = random.randint(0, GRID_SIZE - ship_len)  # Ensure the ship fits vertically.
                col = random.randint(0, GRID_SIZE - 1)  # Random column.

            # Check if the selected area on the grid is free to place the ship.
            if check_area_is_free(grid, row, col, ship_len, orientation):
                # Place the ship on the grid and store its coordinates.
                ship_coordinates = []
                place_ship(grid, row, col, ship_len, orientation, player2_ships)

                # Store the coordinates of the placed ship for tracking.
                if orientation == "H":  # Horizontal ship coordinates.
                    ship_coordinates = [(row, col + i) for i in range(ship_len)]
                else:  # Vertical ship coordinates.
                    ship_coordinates = [(row + i, col) for i in range(ship_len)]

                print(f"AI Ships: {ship_coordinates}")

                # Store the ship's information (coordinates and hit status).
                player2_ships.append({
                    'coordinates': ship_coordinates,
                    'hits': []  # Initialize an empty list to track hits.
                })
                placed = True  # Mark the ship as successfully placed.

def check_area_is_free(grid, start_row, start_col, ship_len, orientation):
    """
    Helper function to check if the area is free to place a ship.
    Returns True if the ship can be placed, False if there's an overlap or out of bounds.
    """
    
    if orientation == "H":  # For horizontal placement.
        for i in range(ship_len):
            if grid[start_row][start_col + i] != 0:  # Check for occupied cells.
                return False  # If any cell is occupied, return False.
    else:  # For vertical placement.
        for i in range(ship_len):
            if grid[start_row + i][start_col] != 0:  # Check for occupied cells.
                return False  # If any cell is occupied, return False.

    return True  # Return True if all cells are free.

# Shravya Matta
def update_scoreboard(player_hits, player_misses, player, hit):
    """
    Updates the scoreboard based on player's hits and misses.
    
    player_hits: dictionary storing player hits (e.g., {1: hits_player1, 2: hits_player2}).
    player_misses: dictionary storing player misses (e.g., {1: misses_player1, 2: misses_player2}).
    player: the player number (1 or 2).
    hit: boolean indicating if the player hit (True) or missed (False).
    """

    if hit:  # If the player hit a target.
        player_hits[player] += 1  # Increase hit count for the player.
    else:  # If the player missed.
        player_misses[player] += 1  # Increase miss count for the player.
        

def calculate_score(player_hits, player_misses):
    """
    Calculates the total score for each player.

    player_hits: dictionary storing player hits.
    player_misses: dictionary storing player misses.

    Returns:
        A dictionary with total scores for each player.
    """
    player_scores = {}
    for player in player_hits.keys():
        # Total score is calculated as hits * 100 - misses
        score = (player_hits[player] * 100) - player_misses[player]
        player_scores[player] = max(0, score)  # Ensure score is not negative
    return player_scores

def display_scoreboard(player_hits, player_misses):
    """
    Displays the scoreboard on the screen.

    player_hits: dictionary storing player hits.
    player_misses: dictionary storing player misses.
    """
    win.fill(BLACK)  # Clear the screen

    # Calculate scores for both players.
    scores = calculate_score(player_hits, player_misses)
    print(f"Updating scores: {scores}")  # Output score to console.
    player_score_1 = scores[1]  # Player 1's score.
    player_score_2 = scores[2]  # Player 2's score.

    # Display player 1's stats
    draw_text(f"Player 1 - Total Score: {scores[1]}, Hits: {player_hits[1]}, Misses: {player_misses[1]}", WIDTH // 2, HEIGHT // 2 - 50)

    # Display player 2's stats
    draw_text(f"Player 2 - Total Score: {scores[2]}, Hits: {player_hits[2]}, Misses: {player_misses[2]}", WIDTH // 2, HEIGHT // 2 + 50)

    # Display a message to instruct the player to click to continue
    draw_text("Press any key to continue...", WIDTH // 2, HEIGHT // 2 + 150)

    pygame.display.flip()  # Update the display

    # Wait for a mouse click or key press to continue
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False # Exit the loop if a key or mouse button is pressed.

# Function to add score to leaderboard
def add_score_to_leaderboard(player_score):
    player_name = ""  # To store the player's name input
    input_active = True

    while input_active:
        win.fill(BLACK)
        draw_text("Enter your name: " + player_name, WIDTH // 2 - 150, HEIGHT // 2 - 50)
        draw_text("Press ENTER to submit", WIDTH // 2 - 150, HEIGHT // 2 + 50)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False  # Finish name input
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]  # Remove last character
                else:
                    player_name += event.unicode  # Add character to name

    # Once name is entered, save the score to the leaderboard
    leaderboard = []  # Load existing leaderboard data from a file

    leaderboard_file = "leaderboard.json"
    if os.path.exists(leaderboard_file):
        with open(leaderboard_file, "r") as f:
            leaderboard = json.load(f)

    # Add new score to the leaderboard
    new_entry = {"name": player_name, "score": player_score}
    leaderboard.append(new_entry)
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)

    with open(leaderboard_file, "w") as f:
        json.dump(leaderboard, f)

    print(f"Added {player_name}'s score of {player_score} to the leaderboard!")

# Function to display leaderboard
def display_leaderboard():
    """
    Displays the top five scores stored in the leaderboard
    """
    leaderboard = []
    leaderboard_file = "leaderboard.json"

    if os.path.exists(leaderboard_file):
        with open(leaderboard_file, "r") as f:
            leaderboard = json.load(f)

    win.fill(BLACK)

    if leaderboard:
        draw_text("Leaderboard", WIDTH // 2 - 100, HEIGHT // 2 - 150)
        for index, entry in enumerate(leaderboard[:5]):  # Display top 5 players
            name = entry["name"]
            score = entry["score"]
            draw_text(f"{index + 1}. {name}: {score}", WIDTH // 2 - 100, HEIGHT // 2 - 50 + index * 30)
    else:
        draw_text("Leaderboard is empty", WIDTH // 2 - 100, HEIGHT // 2)

    draw_text("Press ENTER to return to the main menu", WIDTH // 2 - 100, HEIGHT // 2 + 150)
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Return to main menu
                    waiting_for_input = False

# Matthew McManness
def display_leaderboard():
    """Display the leaderboard, or show a blank menu if no file exists"""
    leaderboard = []
    leaderboard_file = "leaderboard.json"

    # Check if the leaderboard file exists
    if os.path.exists(leaderboard_file):
        # Load the leaderboard data from the file
        try:
            with open(leaderboard_file, "r") as f:
                leaderboard = json.load(f)
        except json.JSONDecodeError:
            # If the file exists but is corrupted or empty, set an empty leaderboard
            leaderboard = []
    else:
        # No file exists, so start with an empty leaderboard
        leaderboard = []

    # Display the leaderboard on the screen
    win.fill(BLACK)

    if leaderboard:
        # Sort the leaderboard in descending order by score
        leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)

        draw_text("Leaderboard", WIDTH // 2 - 100, HEIGHT // 2 - 150)

        # Display the top 5 players (or fewer if there aren't that many)
        for index, entry in enumerate(leaderboard[:5]):
            name = entry["name"]
            score = entry["score"]
            draw_text(f"{index + 1}. {name}: {score}", WIDTH // 2 - 100, HEIGHT // 2 - 50 + index * 30)

    else:
        # If no leaderboard data exists, display a blank message
        draw_text("Leaderboard is empty", WIDTH // 2 - 100, HEIGHT // 2)

    draw_text("Press ENTER to return to the main menu", WIDTH // 2 - 100, HEIGHT // 2 + 150)
    pygame.display.flip()

    # Wait for the user to press ENTER to go back to the menu
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() # Quit if window is closed
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Return to main menu on ENTER
                    waiting_for_input = False

# Manvir Kaur  
def ai_easy_turn(player_grid, missile_board):
    """AI randomly chooses a cell that hasn't been hit before"""
    # Keep choosing random cells until a valid (not previously fired at) cell is found
    valid_shot = False
    while not valid_shot:
        row = random.randint(0, GRID_SIZE - 1)
        col = random.randint(0, GRID_SIZE - 1)
        
        if missile_board[row][col] == 0:  # 0 means no shot has been fired at this cell
            valid_shot = True  # A valid cell was found

    # Now the AI fires at this cell
    return row, col


# Magaly Camacho
def ai_medium_turn(player_grid:list[int], missile_board:list[int], ship_hit_tiles:list[dict]) -> list[int]:
    """Returns row and col to attack, if a ship has been previously hit then it attacks tiles near it, otherwise it attacks a random tile"""
    # helpers
    tile_not_found = True # if tile to hit has been found or not
    dir_shifts = {
        "Right": [0,1], 
        "Left": [0,-1], 
        "Up": [-1,0], 
        "Down": [1,0]
    } # [y,x] shifts based on direction
    
    # first check around previously hit tiles
    for index, tile in enumerate(ship_hit_tiles):
        # if tile is part of sunk ship
        if player_grid[tile["x"]][tile["y"]] == 3:
            ship_hit_tiles.pop(index) # remove from list
            continue # move on to next tile

        # otherwise check directions around that tile
        for dir, check in tile["dirs"].items():
            # if direction dir isn't a dead-end, look in that direction
            if check and tile_not_found:
                shift = dir_shifts[dir] # get shift for direction
                temp_row, temp_col = tile["x"], tile["y"] # start at previously hit tile

                # look for new tile in direction dir
                while True:
                    temp_row += shift[0]
                    temp_col += shift[1]

                    # if temp tile is out of bounds, stop checking in that direction
                    if temp_row < 0 or temp_row >= GRID_SIZE or temp_col < 0 or temp_col >= GRID_SIZE:
                        tile["dirs"][dir] = False
                        break
                    
                    # get tile state
                    tile_state = missile_board[temp_row][temp_col]

                    # if tile hasn't been hit before, hit it
                    if tile_state == 0:
                        row, col = temp_row, temp_col
                        tile_not_found = False
                        break

                    # if tile was a miss, stop looking in that direction
                    elif tile_state == 1:
                        tile["dirs"][dir] = False
                        break

    # look for a random tile 
    if tile_not_found:
        while True: 
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)

            # if tile hasn't been attacked before, ai will hit it
            if missile_board[row][col] == 0:
                break

    # check if there's a ship to attack at [row, col], if so save tile
    if player_grid[row][col] == 1:
        tile = {
            "x": row,
            "y": col,
            "dirs": {
                "Up": True,
                "Down": True,
                "Left": True,
                "Right": True
            } # directions to look in relative to tile, False=dead-end, True=keep looking
        }
        ship_hit_tiles.append(tile) 

    return row, col # return tile coords to attack

# Mariam Oraby
def ai_hard_turn(player_grid, missile_board, player1_ships):
    """
    AI 'hard' difficulty function.
    Targets unhit ships and updates the game board accordingly.
    Returns the row and column that it hit, and a boolean indicating if the game is over.
    """
    # Check for any unhit ships and target them
    for row in range(len(player_grid)):
        for col in range(len(player_grid[row])):
            print(f"Checking position {row},{col} on player grid... Ship present: {player_grid[row][col]}, Missile board status: {missile_board[row][col]}")
            
            # Target unhit ship
            if player_grid[row][col] == 1 and missile_board[row][col] == 0:
                print(f"AI targets ship at {row},{col}")
                missile_board[row][col] = 2  # Mark missile board as hit
                player_grid[row][col] = 2    # Mark player grid to show ship was hit

                for ship in player1_ships:
                    if (row, col) in ship['coordinates']:
                        ship['hits'].append((row, col))  # Add hit
                        break
                    
                # Check if all ships are sunk after the hit
                if all_ships_sunk(player1_ships):
                    print("All ships sunk! Ending game.")
                    return row, col  # Game over, all ships sunk
                return row, col  # Return hit without game over

    # Fallback to random shot if no ship targets are available
    print("No ships found to target. Switching to random shot...")
    while True:
        row = random.randint(0, len(player_grid) - 1)
        col = random.randint(0, len(player_grid[0]) - 1)
        if missile_board[row][col] == 0:  # Only fire at unhit locations
            missile_board[row][col] = 1  # Mark this location as a miss
            print(f"AI randomly misses at {row},{col}")
            return row, col, False  # Return miss without game over


def draw_grid(grid, x_offset, y_offset, player_grid=True, ghost_positions=None):
    """Draw the game grid, including ships, hits, misses, and ghost ship if present."""
    
    for row in range(GRID_SIZE):
        draw_text(str(row), x_offset-20, y_offset + row * CELL_SIZE + (CELL_SIZE / 4)) # Draws row label
        for col in range(GRID_SIZE):
            draw_text(chr(65+col), x_offset + col * CELL_SIZE + (CELL_SIZE / 3), y_offset-25) # Draws col label
            color = WHITE #Default color before hit/miss or a ship is white
            if player_grid:  # For the player's own grid
                if grid[row][col] == 1:  # Placeholder, would color black for ships, but we filled in with png instead below
                    color = BLACK
                elif grid[row][col] == 2:  # Color red for hit
                    color = RED
                elif grid[row][col] == 3:  # #Color blue for sunk ship
                    color = BLUE
            else:  # For the missile board
                if grid[row][col] == 1:  # Color grey for miss
                    color = GREY
                elif grid[row][col] == 2:  # Color red for hit
                    color = RED
                elif grid[row][col] == 3:  # Color green for sunk enemy ship
                    color = GREEN

            if ghost_positions and (row, col) in ghost_positions: #Colors the grid grey for placement so that players can see where the ship is placed before placing it
                color = GHOST_COLOR

            pygame.draw.rect(win, color, (x_offset + col * CELL_SIZE, y_offset + row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)#draws the cells into the grid based on their color determined above
            pygame.draw.rect(win, BLACK, (x_offset + col * CELL_SIZE, y_offset + row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

            if player_grid and grid[row][col] == 1:  # Draw ship images only on player's own grid
                ship_len = get_ship_length_from_position(grid, row, col) #finds value of ship length
                if ship_len and ship_len in ship_images: #checks if there is a ship in ship_images corresponding to the length of the given ship
                    win.blit(ship_images[ship_len], (x_offset + col * CELL_SIZE, y_offset + row * CELL_SIZE))#puts in the pngs into the given cells

def get_ship_length_from_position(grid, row, col):
    """Return the length of the ship at the given grid position, if any."""
    if grid[row][col] == 1: #If there is a ship value, which is 1 on the grid
        for ship_len in default_ships: #either 1,2,3,4,5 length ship based on battleship game
            if all(
                (col + i < GRID_SIZE and grid[row][col + i] == 1) or #Checks for length of ship vertically
                (row + i < GRID_SIZE and grid[row + i][col] == 1) #Checks for length of ship horizontally
                for i in range(ship_len) 
            ):
                return ship_len #Returns back ship length
    return None

def place_ship(grid, start_row, start_col, ship_len, orientation, ship_list):
    """Place a ship manually based on the start position and orientation and track the ship coordinates."""
    ship_coordinates = []
    if orientation == "H": #If player selects horizontal placement
        if start_col + ship_len <= GRID_SIZE: #Checks if valid placement
            if all(grid[start_row][start_col + i] == 0 for i in range(ship_len)): #checks if ship is already there
                for i in range(ship_len): #Replaces values in grid with 1 to mark player ship
                    grid[start_row][start_col + i] = 1
                    ship_coordinates.append((start_row, start_col + i)) #Coordinates of length of ship
                ship_list.append({'coordinates': ship_coordinates, 'hits': []}) #Appends shiplist with info on ship
                return True
    else: #If player selects vertical placement
        if start_row + ship_len <= GRID_SIZE: #Checks if valid placement
            if all(grid[start_row + i][start_col] == 0 for i in range(ship_len)): #checks if ship is already there
                for i in range(ship_len): #replaces values in grid with 1 to mark player ship
                    grid[start_row + i][start_col] = 1
                    ship_coordinates.append((start_row + i, start_col)) #Coordinates of length of ship
                ship_list.append({'coordinates': ship_coordinates, 'hits': []}) #Appends shiplist with info on ship
                return True
    return False

def get_ghost_positions(grid, start_row, start_col, ship_len, orientation):
    """Calculate the ghost ship positions based on mouse hover."""
    ghost_positions = []
    if orientation == "H": #If player is in horizontal placement mode
        if start_col + ship_len <= GRID_SIZE:
            ghost_positions = [(start_row, start_col + i) for i in range(ship_len)]#Marks positions where ghost cell should be present
    else: #If player is in vertical placement mode
        if start_row + ship_len <= GRID_SIZE:
            ghost_positions = [(start_row + i, start_col) for i in range(ship_len)]#Marks position where ghost cell should be present
    return ghost_positions

def ship_placement_menu(player_grid, player_number, ship_list, ships_to_place):
    """Allow player to place ships manually with a ghost version of the ship."""
    placing_ships = True #Process still ongoing
    ship_idx = 0 #Counting variable 
    orientation = "H" #Default placement orientation is horizontal
    ghost_positions = []

    while placing_ships: #While player is still in the process of placing ships
        win.fill(BLACK) 
        draw_text(f"Player {player_number}: Place your ships", WIDTH // 2 - 100, 50) #Which player is placing ships
        draw_text(f"Current ship length: {ships_to_place[ship_idx]}", WIDTH // 2 - 100, 100) #Displays current ship length
        draw_text("Press 'H' for Horizontal, 'V' for Vertical", WIDTH // 2 - 100, 150) #Displays info for player so they know what to press to change orientation

        mouse_x, mouse_y = pygame.mouse.get_pos() #Get position of player mouse
        if MARGIN < mouse_x < MARGIN + GRID_SIZE * CELL_SIZE and MARGIN < mouse_y < MARGIN + GRID_SIZE * CELL_SIZE: #Basically just means "if player is hoveirng over the placement grid"
            row = (mouse_y - MARGIN) // CELL_SIZE #Finds which row player is hovering over
            col = (mouse_x - MARGIN) // CELL_SIZE #Finds which col player is hovering over
            ghost_positions = get_ghost_positions(player_grid, row, col, ships_to_place[ship_idx], orientation) #Feeds those to ghost position function so it can draw those on the grid

        draw_grid(player_grid, MARGIN, MARGIN, ghost_positions=ghost_positions) #Draw the placement grid

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #If player quits game
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN: #If player touches any key
                if event.key == pygame.K_h: #If that key is an H
                    orientation = "H"
                if event.key == pygame.K_v:#If that key is a V
                    orientation = "V"
            if event.type == pygame.MOUSEBUTTONDOWN: #If player places
                if ghost_positions: #If player is hovering over grid
                    start_row, start_col = ghost_positions[0] #Coordinates to place based on player mouse position
                    if place_ship(player_grid, start_row, start_col, ships_to_place[ship_idx], orientation, ship_list): #if player places a ship and it was valid and went through
                        ship_idx += 1 #Increments every time player places a ship to track number of ships placed
                        if ship_idx == len(ships_to_place): #If player has placed the number of ships for the game
                            placing_ships = False #Stop process
                            break

def check_hit(ship_grid, missile_board, row, col, ship_list):
    """Check if a ship is hit and update both the missile board and the player's ship grid.
       If a ship is sunk, mark it differently.
       Returns if it was a hit or a miss   
    """
    #if missile_board[row][col] != 0:  # If the cell has already been targeted, return False
        #return False

    if ship_grid[row][col] == 1:  # A ship is hit
        missile_board[row][col] = 2  # Mark hit on the missile board
        hit_sound.play()
        ship_grid[row][col] = 2  # Mark hit on the player's ship grid

        # Check if the hit was on a specific ship and append the hit to the ship's 'hits' list
        for ship in ship_list:
            if (row, col) in ship['coordinates']:
                if (row, col) not in ship['hits']:  # Avoid double-counting hits
                    ship['hits'].append((row, col))
                    print(f"AI hit registered on Player's ship at {row}, {col}")  # Debug: AI hit

                # Check if the ship is sunk
                if len(ship['hits']) == len(ship['coordinates']):
                    print(f"AI sunk Player's ship at {ship['coordinates']}!")  # Debug: AI ship sunk
                    for (r, c) in ship['coordinates']:
                        missile_board[r][c] = 3  # Mark the ship as sunk on the missile board
                        ship_grid[r][c] = 3  # Mark the ship as sunk on the player's ship grid
                    sunk_sound.play()
        return True  # A ship was hit
    else:
        missile_board[row][col] = 1  # Mark miss on the missile board
        miss_sound.play()
        return False  # Return False since it was a miss

# Function for the main menu where the player can select the number of ships
def main_menu():
    """
    Displays the main menu to allow the user to select the number of ships for the game.
    """
    
    selected_ships = 3  # Default number of ships set to 3
    menu_running = True  # Flag to keep the menu running

    # Main loop for the menu, continues until the player starts the game or quits
    while menu_running:
        win.fill(BLACK)  # Fill the screen with a black background
        draw_text("Welcome to Battleship", WIDTH // 2 - 150, HEIGHT // 2 - 100)  # Title displayed at the top of the screen
        draw_text(f"Number of Ships: {selected_ships}", WIDTH // 2 - 100, HEIGHT // 2)  # Shows current selection of ships
        draw_text("Use UP and DOWN arrow keys to select the number of ships.", WIDTH // 2 - 300, HEIGHT // 2 + 50)  # Instructions for how to change the number of ships
        draw_text("Press ENTER to start", WIDTH // 2 - 100, HEIGHT // 2 + 200)  # Instruction to press ENTER to start the game

        pygame.display.flip()  # Update the display with the drawn text

        # Event handling loop to listen for user inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the window is closed
                pygame.quit()  # Close the game
                quit()  # Stop the program
            if event.type == pygame.KEYDOWN:  # If a key is pressed
                # If the UP arrow is pressed and the number of ships is less than the max (assumed to be len(default_ships))
                if event.key == pygame.K_UP and selected_ships < len(default_ships):
                    selected_ships += 1  # Increase the number of ships by 1
                # If the DOWN arrow is pressed and the number of ships is greater than 1 (minimum limit)
                elif event.key == pygame.K_DOWN and selected_ships > 1:
                    selected_ships -= 1  # Decrease the number of ships by 1
                # If the ENTER key is pressed, exit the menu and start the game
                elif event.key == pygame.K_RETURN:
                    menu_running = False  # Stop the menu loop
                    break  # Exit the event loop

    return selected_ships  # Return the selected number of ships for the game


def display_winner(winner, game_mode, player_score_1, player_score_2):
    """Display the winner and wait for user input. Only add score if a human player wins"""
    win.fill(BLACK)
    if winner == 2 and game_mode == "AI":
        draw_text("AI Wins!", WIDTH // 2 - 100, HEIGHT // 2 - 50)  # Display "AI Wins"
        draw_text("Press ENTER to continue", WIDTH // 2 - 100, HEIGHT // 2 + 50)
    else:
        draw_text(f"Player {winner} Wins!", WIDTH // 2 - 100, HEIGHT // 2 - 50)  # Display player winner
        draw_text("Press ENTER to add your score", WIDTH // 2 - 100, HEIGHT // 2 + 50)

    pygame.display.flip()

    if winner == 1 or (winner == 2 and game_mode != "AI"):
        score = player_score_1 if winner == 1 else player_score_2  # Determine correct score
        print(type(score), score)

    waiting_for_input = True
    while waiting_for_input:  # Wait for keyboard input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if winner == 1 or (winner == 2 and game_mode != "AI"):
                        add_score_to_leaderboard(score)  # Only add human player's score
                    waiting_for_input = False  # Exit the loop after adding score or skipping

def display_turn_screen(player_number, game_mode=None):
    """Screen in between turns to hide board info from other player."""
    
    if game_mode == "AI" and player_number == 2:
        turn_text = "AI's Turn"
    else:
        turn_text = f"Player {player_number}'s Turn"
    
    win.fill(BLACK)
    draw_text(turn_text, WIDTH // 2 - 150, HEIGHT // 2 - 50)  # Display the appropriate turn text
    draw_text("Please wait for the other player to finish their turn.", WIDTH // 2 - 300, HEIGHT // 2 + 10)
    draw_text("Press any key to continue...", WIDTH // 2 - 150, HEIGHT // 2 + 70)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:  # any key is pressed
                waiting = False  # Stop waiting, go on to next turn
                break

def draw_text(text, x, y):
    """Utility function to draw text on the screen."""
    text_surface = font.render(text, True, WHITE) #White text
    win.blit(text_surface, (x, y))#Draws on window the text, with coordinates

def all_ships_sunk(ship_list):
    """Check if all ships in the list are sunk."""
    result = all(len(ship['hits']) == len(ship['coordinates']) for ship in ship_list)
    print(f"All ships sunk check: {result}")  # Debug: Win condition check
    return result
   
def instructions_page():
    """Display the game instructions to the player."""
    instructions_running = True
    while instructions_running:#While player hasn't moved on from instructions by pressing enter
        win.fill(BLACK)

        # Display the instructions, just explains game mechanics and what colors mean
        draw_text("Instructions", WIDTH // 2 - 100, 50)
        draw_text("1. Place your ships on the grid.", WIDTH // 2 - 300, 150)
        draw_text("2. On your turn, try to hit the enemy's ships by clicking on the missile board.", WIDTH // 2 - 300, 200)
        draw_text("3. Colors:", WIDTH // 2 - 300, 250)
        draw_text("- Purple: Your ship", WIDTH // 2 - 300, 300)
        draw_text("- Grey: Missed shot", WIDTH // 2 - 300, 350)
        draw_text("- Red: Hit", WIDTH // 2 - 300, 400)
        draw_text("- Green: Sunk enemy ship", WIDTH // 2 - 300, 450)
        draw_text("- Blue: Sunk friendly ship", WIDTH // 2 - 300, 500)
        draw_text("Press ENTER to continue...", WIDTH // 2 - 100, HEIGHT - 50)

        pygame.display.flip()

        # Wait for the player to press a key to proceed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: #If player presses enter to move on 
                    instructions_running = False  # Exit the instruction page
                    break

def game_loop():
    """Main game loop where players place ships and play the game."""
    instructions_page()  # Start instructions page
    display_menu()  # Call the menu function before starting the game loop
    game_mode = select_game_mode()  # Select game mode (AI or pass-and-play)
    if game_mode == "AI":
        ai_difficulty = select_ai_difficulty()  # Select AI difficulty

    num_ships = main_menu()  # Select number of ships
    player1_ships = []
    player2_ships = []
    ships_to_place = default_ships[:num_ships]

    # Player 1 places ships
    ship_placement_menu(grid1, 1, player1_ships, ships_to_place)

    if game_mode == "pass_and_play":
        # Player 2 places ships manually
        ship_placement_menu(grid2, 2, player2_ships, ships_to_place)
    elif game_mode == "AI":
        # AI places ships automatically
        place_ai_ships(grid2, ships_to_place, player2_ships)

    # Initialize hit/miss counters
    player_hits = {1: 0, 2: 0}
    player_misses = {1: 0, 2: 0}

    # Initialize score trackers
    player_score_1 = 0
    player_score_2 = 0

    # For Medium AI, tracks tiles where ships have been hit
    ai_med_ship_hit_tiles = [] 

    running = True
    turn = 1  # Player 1 starts

    while running:
        win.fill(BLACK)
        
        # Handle Player 1's turn
        if turn == 1:
            draw_text("Player 1's Turn", WIDTH // 2 - 130, 20)
            draw_grid(missile_board1, WIDTH // 2 + MARGIN, MARGIN, player_grid=False)
            draw_grid(grid1, MARGIN, MARGIN, player_grid=True)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:  # Player 1 fires
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if (WIDTH // 2 + MARGIN < mouse_x < WIDTH // 2 + MARGIN + GRID_SIZE * CELL_SIZE and
                            MARGIN < mouse_y < MARGIN + GRID_SIZE * CELL_SIZE):
                        row = (mouse_y - MARGIN) // CELL_SIZE
                        col = (mouse_x - (WIDTH // 2 + MARGIN)) // CELL_SIZE
                        if check_hit(grid2, missile_board1, row, col, player2_ships):
                            update_scoreboard(player_hits, player_misses, 1, True)  # Hit
                        else:
                            update_scoreboard(player_hits, player_misses, 1, False)  # Miss

                        scores = calculate_score(player_hits, player_misses) # update scores 
                        player_score_1 = scores[1]
                        player_score_2 = scores[2]

                        if all_ships_sunk(player2_ships):  # Player 1 wins
                            win_sound.play()
                            display_scoreboard(player_hits, player_misses)
                            display_winner(1, game_mode, player_score_1, player_score_2)
                            running = False
                        else:
                            display_turn_screen(2, game_mode)  # Switch to Player 2
                            turn = 2

        # Handle Player 2's turn (pass-and-play mode)
        elif turn == 2 and game_mode == "pass_and_play":
            draw_text("Player 2's Turn", WIDTH // 2 - 130, 20)
            draw_grid(missile_board2, WIDTH // 2 + MARGIN, MARGIN, player_grid=False)
            draw_grid(grid2, MARGIN, MARGIN, player_grid=True)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:  # Player 2 fires
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if (WIDTH // 2 + MARGIN < mouse_x < WIDTH // 2 + MARGIN + GRID_SIZE * CELL_SIZE and
                            MARGIN < mouse_y < MARGIN + GRID_SIZE * CELL_SIZE):
                        row = (mouse_y - MARGIN) // CELL_SIZE
                        col = (mouse_x - (WIDTH // 2 + MARGIN)) // CELL_SIZE
                        if check_hit(grid1, missile_board2, row, col, player1_ships):
                            update_scoreboard(player_hits, player_misses, 2, True)  # AI Hit
                        else:
                            update_scoreboard(player_hits, player_misses, 2, False)  # AI Miss
                        
                        scores = calculate_score(player_hits, player_misses) # update scores 
                        player_score_1 = scores[1]
                        player_score_2 = scores[2]

                        if all_ships_sunk(player1_ships):  # Player 2 wins
                            win_sound.play()
                            display_scoreboard(player_hits, player_misses)
                            display_winner(2, game_mode, player_score_1, player_score_2)
                            running = False
                        else:
                            display_turn_screen(1, game_mode)  # Switch back to Player 1
                            turn = 1

        # Handle AI's turn
        elif turn == 2 and game_mode == "AI":
            # AI chooses a move based on difficulty
            if ai_difficulty == "easy":
                row, col = ai_easy_turn(grid1, missile_board2)
            elif ai_difficulty == "medium":
                row, col = ai_medium_turn(grid1, missile_board2, ai_med_ship_hit_tiles)
            elif ai_difficulty == "hard":
                row, col = ai_hard_turn(grid1, missile_board2, player1_ships)

            print(f"AI: row {row}, col {col}")

            # AI fires at Player 1's ships
            if check_hit(grid1, missile_board2, row, col, player1_ships):
                update_scoreboard(player_hits, player_misses, 2, True)  # AI Hit
            else:
                update_scoreboard(player_hits, player_misses, 2, False)  # AI Miss

            scores = calculate_score(player_hits, player_misses) # update scores 
            player_score_1 = scores[1]
            player_score_2 = scores[2]
            
            if all_ships_sunk(player1_ships):  # AI wins
                win_sound.play()
                print("AI wins!")  # Debug: AI wins
                display_scoreboard(player_hits, player_misses)
                display_winner(2, game_mode, player_score_1, player_score_2)
                running = False
            else:
                display_turn_screen(1)  # Switch back to Player 1
                turn = 1

    pygame.quit()


if __name__ == "__main__":
    game_loop()





