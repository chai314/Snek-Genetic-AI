import pygame
import random

pygame.font.init()
pygame.init()

DRAW_LINES = True
STAT_FONT = pygame.font.SysFont(None, 36)
gen = 0

# Set up the game window
width, height = 300,300
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("snek gaym")

# Define colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Define the snake class
class Snake:
    def __init__(self):
        self.size = 1
        self.positions = [(width // 2, height // 2)]
        self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.vx = 1 if self.direction == "RIGHT" else -1 if self.direction == "LEFT" else 0
        self.vy = 1 if self.direction == "DOWN" else -1 if self.direction == "UP" else 0

    def move(self):
        x, y = self.positions[0]

        match self.direction:
            case "UP":
                y = max(0, y - 10)
            case "DOWN":
                y = min(height-10, y + 10)
            case "LEFT":
                x = max(0, x - 10)
            case "RIGHT":
                x = min(width-10, x + 10)

        self.positions.insert(0, (x, y))

        if len(self.positions) > self.size:
            self.positions.pop()

    def change_direction(self, direction):
        self.direction = direction
        if direction == "UP":
            self.vy = -1
            self.vx = 0
        elif direction == "DOWN" and self.direction != "UP":
            self.vy = 1
            self.vx = 0
        elif direction == "LEFT" and self.direction != "RIGHT":
            self.vx = -1
            self.vy = 0
        elif direction == "RIGHT" and self.direction != "LEFT":
            self.vx = 1
            self.vy = 0
        self.move()

    def draw(self, window):
        for position in self.positions:
            pygame.draw.rect(window, GREEN, (position[0], position[1], 10, 10))
    
    def x(self):
        return self.positions[0][0]
    
    def y(self):
        return self.positions[0][1]
    
# Define the food class
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.spawn()

    def spawn(self):
        self.position = (random.randrange(0, width, 10), random.randrange(0, height, 10))

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.position[0], self.position[1], 10, 10))

    def x(self):
        return self.position[0]
    
    def y(self):
        return self.position[1]


def draw_window(window, snakes, foods):
    window.fill(BLACK)


    for snake in snakes:
        sfood = foods[snakes.index(snake)]
        if DRAW_LINES:
            try: pygame.draw.line(window, (255,0,0), (snake.x(), snake.y()), (sfood.x(), sfood.y()), 5)
            except: pass
        # draw snake
        snake.draw(window)

    for food in foods:
        food.draw(window)

    # score
    score = max(snake.size for snake in snakes) if snakes else 0
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    window.blit(score_label, (height - score_label.get_width() - 15, 10))

    # tb
    try:
        score_label = STAT_FONT.render("TimeBomb: " + str(timebomb[0]),1,(255,255,255))
        window.blit(score_label, (10, 50))
    except: pass

    # fitn
    score_label = STAT_FONT.render("Fitness: " + str(fitness),1,(255,255,255))
    window.blit(score_label, (10, 70))

    pygame.display.update()



run = True
while run:

    foods = [Food()]
    snakes = [Snake()]
    moved = [1]*len(snakes)

    clock = pygame.time.Clock()

    run = True
    timebomb = [0]*len(snakes)
    max_time = 100
    fitness = 0

    while run and snakes:
        clock.tick(20)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        rem = []

        for snek_ind, snake in enumerate(snakes):
            sfood = foods[snek_ind]
            df = (snake.vx * (sfood.x()-snake.x()) + snake.vy * (sfood.y()-snake.y())) / ((sfood.x()-snake.x())**2 + (sfood.y()-snake.y())**2)
            fitness += 10 * df * moved[snek_ind]
            timebomb[snek_ind] += 1+(df<=0)

            keys = pygame.key.get_pressed()
            moved[snek_ind] = 0
            if keys[pygame.K_UP]:
                snake.change_direction("UP")
                moved[snek_ind] = 1

            elif keys[pygame.K_DOWN]:
                snake.change_direction("DOWN")
                moved[snek_ind] = 1
                # if snake.y() == height - 10: timebomb[snek_ind] += 50
            
            elif keys[pygame.K_LEFT]:
                snake.change_direction("LEFT")
                moved[snek_ind] = 1
                # if snake.x() == 0: timebomb[snek_ind] += 50

            elif keys[pygame.K_RIGHT]:
                snake.change_direction("RIGHT")
                moved[snek_ind] = 1
                # if snake.x() == width - 10: timebomb[snek_ind] += 50

            for snek_ind, sfood in enumerate(foods):
                if sfood.position in snakes[snek_ind].positions:
                    fitness += 2
                    snakes[snek_ind].size += 1
                    timebomb[snek_ind] = 0
                    sfood.spawn()

            if timebomb[snek_ind] > max_time:# or snake.positions[0] in snake.positions[1:]:
                rem.append(snek_ind)

        snakes = [snake for i, snake in enumerate(snakes) if i not in rem]
        foods = [food for i, food in enumerate(foods) if i not in rem]
        timebomb = [time for i, time in enumerate(timebomb) if i not in rem]
        moved = [move for i, move in enumerate(moved) if i not in rem]

        draw_window(window, snakes, foods)
