import random # For generating random numbers
import sys # We will use sys.exit to exit the program
import pygame
from pygame.locals import * # Basic pygame imports

# Global Variables for the game
FPS = 35
SCREENWIDTH = 1076
SCREENHEIGHT = 742
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'img/bird.png'
BACKGROUND = 'img/BG_real.png'
PIPE = 'img/pipe.png'
FOOD = 'img/food.png'

# power ups config
POWERUP_TYPES = ["gravity", "invincible", "auto"] 

POWERUP_DURATION = {
    "gravity": 8 * FPS,      # 8 seconds
    "invincible": 8 * FPS,  # 8 seconds
    "auto": 8 * FPS         # 8 seconds
}



def welcomeScreen():
    """
    Shows welcome images on the screen
    """

    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type==KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user presses space or up key, start the game for them
            elif event.type==KEYDOWN and (event.key==K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['Factory'], (0, 0))    
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))    
                SCREEN.blit(GAME_SPRITES['message'], (messagex,messagey ))  
                # SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))    
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def spawn_food(upperPipes, lowerPipes):
    max_attempts = 10
    for _ in range(max_attempts):
        y = random.randint(80, int(GROUNDY - 150))
        x = SCREENWIDTH + 20
        safe = True

        for u, l in zip(upperPipes, lowerPipes):
            pipe_width = GAME_SPRITES['pipe'][0].get_width()
            pipe_height_upper = u['y'] + GAME_SPRITES['pipe'][0].get_height()
            pipe_height_lower = l['y']

            # Check if food y overlaps with upper pipe
            if y < pipe_height_upper + 50:  # 50 px buffer
                safe = False
            # Check if food y overlaps with lower pipe
            if y + GAME_SPRITES['food'].get_height() > pipe_height_lower - 50:
                safe = False

        if safe:
            return {'x': x, 'y': y}

    return {'x': x, 'y': random.randint(80, int(GROUNDY - 150))}


def spawn_powerup(upperPipes, lowerPipes):
    
    y = random.randint(80, int(GROUNDY - 150))
    x = SCREENWIDTH + 20

    ptype = random.choice(POWERUP_TYPES)

    return {"x": x, "y": y, "type": ptype}




def draw_player_scores(score1, score2, food_score1, food_score2):
    # Draw numeric scores
    drawScore(score1, y=10, x=60)        # P1 score next to P1 label
    drawScore(score2, y=10, x=SCREENWIDTH - 40)  # P2 score next to P2 label

    drawScore(food_score1, y=50, x=100)  # P1 food
    drawScore(food_score2, y=50, x=SCREENWIDTH - 80)  # P2 food

def draw_power_timers(screen, font, p1_effects, p2_effects):
    # Text colors
    p1_color = (255, 50, 50)
    p2_color = (216, 52, 235)

    # Convert frames left → seconds left
    def effect_text(effects):
        active = [e for e in effects if effects[e] > 0]
        if not active:
            return ""
        e = active[0]  # Only show one at a time
        secs = effects[e] // FPS
        return f"{e.capitalize()}: {secs}s"

    # P1 timer text
    p1_text = effect_text(p1_effects)
    if p1_text:
        label = font.render(p1_text, True, p1_color)
        screen.blit(label, (20, 85))  # Below P1 food

    # P2 timer text
    p2_text = effect_text(p2_effects)
    if p2_text:
        label = font.render(p2_text, True, p2_color)
        screen.blit(label, (SCREENWIDTH - 160, 85))  # Below P2 food



def get_next_pipe(player_x, upperPipes, lowerPipes):
    for u, l in zip(upperPipes, lowerPipes):
        if u['x'] + GAME_SPRITES['pipe'][0].get_width() > player_x:
            return u, l
    return None, None



def mainGame():
    # Player positions
    p1x = int(SCREENWIDTH/5)
    p1y = int(SCREENWIDTH/2)

    p2x = int(SCREENWIDTH/5) - 80   # Slight shift left so birds don't overlap
    p2y = int(SCREENWIDTH/2)

    # Velocities
    p1VelY = -9
    p2VelY = -9

    playerMaxVelY = 10
    playerFlapAccv = -8
    playerAccY = 1

    # Alive states
    p1_alive = True
    p2_alive = True

    # Scores
    score1 = 0
    score2 = 0

    # Food system
    foods = []            # stores active food objects
    food_spawn_timer = 0  # timer for spawning food
    food_spawn_rate = 80  # frames between new food
    foodVelX = -5         # moves same as pipes
    food_score1 = 0       # extra food score for P1
    food_score2 = 0       # extra food score for P2


    # POWERUPS
    powerups = []
    powerup_spawn_timer = 625
    powerup_spawn_rate = 350  # ~15 seconds

    # Power-Up active effect timers
    p1_effects = {"gravity": 0, "invincible": 0, "auto": 0}
    p2_effects = {"gravity": 0, "invincible": 0, "auto": 0}

    # Pipes
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']}
    ]
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']}
    ]

    pipeVelX = -5
    basex = -41

    while True:

        #  CONTROLS 
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:

                # Player 1 controls (SPACE / UP)
                if p1_alive and (event.key == K_SPACE or event.key == K_UP):
                    p1VelY = playerFlapAccv
                    GAME_SOUNDS['wing'].play()

                # Player 2 controls (W / LSHIFT)
                if p2_alive and (event.key == K_w or event.key == K_LSHIFT):
                    p2VelY = playerFlapAccv
                    GAME_SOUNDS['wing'].play()


        #  COLLISION CHECK 
        
            # PLAYER 1 COLLISION skip if invincible
        if p1_alive and p1_effects["invincible"] == 0:
            if isCollide(p1x, p1y, upperPipes, lowerPipes):
                p1_alive = False


        # PLAYER 2 COLLISION (skip if invincible)
        if p2_alive and p2_effects["invincible"] == 0:
            if isCollide(p2x, p2y, upperPipes, lowerPipes):
                p2_alive = False


        # End game only when both birds die
        if not p1_alive and not p2_alive:
            return



        # Reduce effect timers
        for key in p1_effects:
            if p1_effects[key] > 0:
                p1_effects[key] -= 1

        for key in p2_effects:
            if p2_effects[key] > 0:
                p2_effects[key] -= 1


        #  SCORE 
        for pipe in upperPipes:
            pipeMid = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2

            p1Mid = p1x + GAME_SPRITES['player'].get_width()/2
            p2Mid = p2x + GAME_SPRITES['player'].get_width()/2

            if pipeMid <= p1Mid < pipeMid + 4 and p1_alive:
                score1 += 1
                GAME_SOUNDS['point'].play()

            if pipeMid <= p2Mid < pipeMid + 4 and p2_alive:
                score2 += 1
                GAME_SOUNDS['point'].play()

        #  GRAVITY WRT to og game
        ### PLAYER 1 MOVEMENT & EFFECTS
        if p1_alive:
            g = playerAccY
            if p1_effects["gravity"] > 0:
                g = playerAccY + 1.5

            p1VelY = min(p1VelY + g, playerMaxVelY)

            ### AUTO PILOT FOR PLAYER 1 ###
            
            if p1_alive and p1_effects["auto"] > 0:
                u, l = get_next_pipe(p1x, upperPipes, lowerPipes)
                if u and l:
                    pipe_gap_top = u['y'] + GAME_SPRITES['pipe'][0].get_height()
                    pipe_gap_bottom = l['y']
                    pipe_center = (pipe_gap_top + pipe_gap_bottom) / 2

                    # Decision: Go upward when below safe zone
                    if p1y > pipe_center + 15:
                        p1VelY = playerFlapAccv
                    # glide slightly if too high
                    elif p1y < pipe_center - 30:
                        p1VelY += 0.4  #  push downward 


            p1y += p1VelY

        ### PLAYER 2 MOVEMENT & EFFECTS
        if p2_alive:
            g = playerAccY
            if p2_effects["gravity"] > 0:
                g = playerAccY + 1.5

            p2VelY = min(p2VelY + g, playerMaxVelY)

            ### AUTO PILOT FOR PLAYER 2 
            if p2_alive and p2_effects["auto"] > 0:
                u, l = get_next_pipe(p2x, upperPipes, lowerPipes)
                if u and l:
                    pipe_gap_top = u['y'] + GAME_SPRITES['pipe'][0].get_height()
                    pipe_gap_bottom = l['y']
                    pipe_center = (pipe_gap_top + pipe_gap_bottom) / 2

                    if p2y > pipe_center + 15:
                        p2VelY = playerFlapAccv
                    elif p2y < pipe_center - 30:
                        p2VelY += 0.4


            p2y += p2VelY


        #  PIPE MOVEMENT 
        for u, l in zip(upperPipes, lowerPipes):
            u['x'] += pipeVelX
            l['x'] += pipeVelX

        #  FOOD MOVEMENT 
        for f in foods:
            f['x'] += foodVelX

        # POWER-UP MOVEMENT
        for pu in powerups:
            pu['x'] += pipeVelX

        powerups = [pu for pu in powerups if pu['x'] > -40]

        # POWER-UP SPAWNING
        powerup_spawn_timer += 1
        if powerup_spawn_timer >= powerup_spawn_rate:
            powerup_spawn_timer = 0
            powerups.append(spawn_powerup(upperPipes, lowerPipes))


        # Remove food that leaves the screen
        foods = [f for f in foods if f['x'] > -50]


        # Add pipes
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # Remove pipes
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
        
        #  FOOD SPAWNING 
        food_spawn_timer += 1
        if food_spawn_timer >= food_spawn_rate:
            food_spawn_timer = 0
            foods.append(spawn_food(upperPipes, lowerPipes))
        
            
            
        #  FOOD COLLECTION 
        player_width = GAME_SPRITES['player'].get_width()
        player_height = GAME_SPRITES['player'].get_height()

        food_width = GAME_SPRITES['food'].get_width()
        food_height = GAME_SPRITES['food'].get_height()

        for f in foods[:]:
            # Player 1 eats food
            if p1_alive and abs((p1x + player_width/2) - (f['x'] + food_width/2)) < 35 \
            and abs((p1y + player_height/2) - (f['y'] + food_height/2)) < 35:
                food_score1 += 1
                foods.remove(f)
                GAME_SOUNDS['eat'].play()

            # Player 2 eats food
            if p2_alive and abs((p2x + player_width/2) - (f['x'] + food_width/2)) < 35 \
            and abs((p2y + player_height/2) - (f['y'] + food_height/2)) < 35:
                food_score2 += 1
                foods.remove(f)
                GAME_SOUNDS['eat'].play()


       ### POWER-UP COLLECTION 
        for pu in powerups[:]:
            px, py = pu['x'], pu['y']
            sprite = GAME_SPRITES["power_" + pu['type']]
            w, h = sprite.get_width(), sprite.get_height()

            # PLAYER 1 GETS POWERUP
            if p1_alive and abs((p1x + player_width/2) - (px + w/2)) < 35 and \
            abs((p1y + player_height/2) - (py + h/2)) < 35:

                effect = pu['type']
                powerups.remove(pu)

                if effect == "gravity":
                    p2_effects["gravity"] = POWERUP_DURATION["gravity"]  # Debuff P2
                else:
                    p1_effects[effect] = POWERUP_DURATION[effect]

                GAME_SOUNDS['power'].play()
                continue  # avoid checking P2 after removal

            # PLAYER 2 GETS POWERUP
            if p2_alive and abs((p2x + player_width/2) - (px + w/2)) < 35 and \
            abs((p2y + player_height/2) - (py + h/2)) < 35:

                effect = pu['type']
                powerups.remove(pu)

                if effect == "gravity":
                    p1_effects["gravity"] = POWERUP_DURATION["gravity"]
                else:
                    p2_effects[effect] = POWERUP_DURATION[effect]

                GAME_SOUNDS['power'].play()



        #  DRAW 
        SCREEN.blit(GAME_SPRITES['Factory'], (0, 0))

        # Draw pipes
        for u, l in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (u['x'], u['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (l['x'], l['y']))

        # Draw food
        for f in foods:
            SCREEN.blit(GAME_SPRITES['food'], (f['x'], f['y']))

        # Draw power-ups
        for pu in powerups:
            SCREEN.blit(GAME_SPRITES["power_" + pu['type']], (pu['x'], pu['y']))


        # Draw ground
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))

        # Draw players
        if p1_alive:
            SCREEN.blit(GAME_SPRITES['player'], (p1x, p1y))
        if p2_alive:
            SCREEN.blit(GAME_SPRITES['player'], (p2x, p2y))

       #Draw score and food score
        draw_labels(SCREEN, font)  
        draw_player_scores(score1, score2, food_score1, food_score2)
        draw_power_timers(SCREEN, font, p1_effects, p2_effects) # for powerups



        pygame.display.update()
        FPSCLOCK.tick(FPS)


def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True
    
    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if playery + GAME_SPRITES['player'].get_height() > pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True
    

    return False


def getRandomPipe():
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT/5
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.1 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1}, #upper Pipe
        {'x': pipeX, 'y': y2} #lower Pipe
    ]
    return pipe

    # font = pygame.font.SysFont('Arial', 28, bold=True)  # or any font you like



def draw_labels(screen, font):
    # Player labels
    p1_label = font.render("P1", True, (255, 50, 50))  # Red
    p2_label = font.render("P2", True, (216, 52, 235))  # purpule

    # Food labels
    p1_food_label = font.render("Food:", True, (255, 50, 50))
    p2_food_label = font.render("Food:", True, (216, 52, 235))

    screen.blit(p1_label, (20, 10))
    screen.blit(p2_label, (SCREENWIDTH - 90, 10))

    screen.blit(p1_food_label, (20, 50))
    screen.blit(p2_food_label, (SCREENWIDTH - 140, 50))





def drawScore(score, y, x=None):
    digits = [int(d) for d in str(score)]
    if x is None:
        total_width = sum(GAME_SPRITES['numbers'][d].get_width() for d in digits)
        x = (SCREENWIDTH - total_width) / 2

    for d in digits:
        SCREEN.blit(GAME_SPRITES['numbers'][d], (x, y))
        x += GAME_SPRITES['numbers'][d].get_width()







if __name__ == "__main__":
    # This will be the main point from where our game will start
    pygame.init() # Initialize all pygame's modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird By SANDEEP and Friends')
    font = pygame.font.SysFont('Arial', 28, bold=True)
    GAME_SPRITES['numbers'] = ( 
        pygame.image.load('img/0.png').convert_alpha(),
        pygame.image.load('img/1.png').convert_alpha(),
        pygame.image.load('img/2.png').convert_alpha(),
        pygame.image.load('img/3.png').convert_alpha(),
        pygame.image.load('img/4.png').convert_alpha(),
        pygame.image.load('img/5.png').convert_alpha(),
        pygame.image.load('img/6.png').convert_alpha(),
        pygame.image.load('img/7.png').convert_alpha(),
        pygame.image.load('img/8.png').convert_alpha(),
        pygame.image.load('img/9.png').convert_alpha(),
    )
    GAME_SPRITES['food'] = pygame.image.load(FOOD).convert_alpha()

    #power ups
    GAME_SPRITES['power_gravity'] = pygame.image.load('img/power_gravity.png').convert_alpha()
    GAME_SPRITES['power_invincible'] = pygame.image.load('img/power_invincible.png').convert_alpha()
    GAME_SPRITES['power_auto'] = pygame.image.load('img/power_auto.png').convert_alpha()


    GAME_SPRITES['message'] =pygame.image.load('img/message.png').convert_alpha()
    GAME_SPRITES['base'] =pygame.image.load('img/base.png').convert_alpha()
    GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load( PIPE).convert_alpha(), 180), 
    pygame.image.load(PIPE).convert_alpha()
    )

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('audio/wing.wav')
    GAME_SOUNDS['eat'] = pygame.mixer.Sound('audio/eat.wav')
    GAME_SOUNDS['power'] = pygame.mixer.Sound('audio/power.wav')

    GAME_SPRITES['Factory'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    while True:
        welcomeScreen() # Shows welcome screen to the user until he presses a button
        mainGame() # This is the main game function 
