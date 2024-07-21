import pygame
import random
import os
import neat
import pickle
from math import atan2

pygame.font.init()
pygame.init()

DRAW_LINES = False
game_active = False
STAT_FONT = pygame.font.SysFont(None, 36)
gen = 0

width, height = 300,300
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("snek gaym")

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

button_width, button_height = 200, 100
button_x = (width - button_width) // 2
button_y = (height - button_height) // 2



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
                y = y - 10
            case "DOWN":
                y = y + 10
            case "LEFT":
                x = x - 10
            case "RIGHT":
                x = x + 10

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


def draw_window(window, snakes, foods, gen):
    """
    :param window: pygame window surface
    :param snakes: sneks
    :param foods: snaks
    :param gen: current generation
    """

    window.fill(BLACK)


    for snake in snakes:
        sfood = foods[snakes.index(snake)]
        if DRAW_LINES:
            try: pygame.draw.line(window, (255,0,0), (snake.x(), snake.y()), (sfood.x(), sfood.y()), 5)
            except: pass
        snake.draw(window)

    for food in foods:
        food.draw(window)

    # score
    score = max(snake.size for snake in snakes) if snakes else 0
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    window.blit(score_label, (height - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    window.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(snakes)),1,(255,255,255))
    window.blit(score_label, (10, 50))

    pygame.display.update()


def draw_start_screen(window):
    window.fill(BLACK)
    pygame.draw.rect(window, GREEN, (button_x, button_y, button_width, button_height))
    text = STAT_FONT.render("Start", True, BLACK)
    text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    window.blit(text, text_rect)
    pygame.display.update()



def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    snakes and sets their fitness based on the distance they
    reach in the game.
    """
    global window, gen, game_active
    gen += 1

    nets = []
    foods = []
    snakes = []
    ge = []
    moved = []
    explored = []
    score = 0

    for genome_id, genome in genomes:
        genome.fitness = 0 
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        snakes.append(Snake())
        snakes[-1].size+=2
        foods.append(Food())
        ge.append(genome)
        moved.append(1)
        explored.append([])

    clock = pygame.time.Clock()

    run = True
    timebomb = [0]*len(snakes)
    max_time = 200

    while run and snakes:
        clock.tick(15)
        if not game_active:
                draw_start_screen(window)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()
                        exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                            game_active = True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()
            
            for snake in snakes:
                snek_ind = snakes.index(snake)
                sfood = foods[snek_ind]
                timebomb[snek_ind] += 1

                inputs = (snake.vx, snake.vy, sfood.x()-snake.x(), sfood.y()-snake.y())
                outputs = nets[snek_ind].activate(inputs)
                max_output = max(outputs)

                if max_output > 0.5:
                    match outputs.index(max_output):
                        case 0: snake.change_direction("UP")
                        case 1: snake.change_direction("DOWN")
                        case 2: snake.change_direction("LEFT")
                        case 3: snake.change_direction("RIGHT")
                snake.move()

                for snek_ind, sfood in enumerate(foods):
                    if sfood.position in snakes[snek_ind].positions:
                        ge[snek_ind].fitness += snakes[snek_ind].size
                        snakes[snek_ind].size += 1
                        timebomb[snek_ind] -= max_time #+ 2**(snake.size-15)
                        sfood.spawn()

                if timebomb[snek_ind] > max_time or snake.positions[0] in snake.positions[1:] or not (0<=snake.x()<=width-10) or not (0<=snake.y()<=height-10):
                # if snake.positions[0] in snake.positions[1:] or not (0<=snake.x()<=width-10) or not (0<=snake.y()<=height-10):
                    nets.pop(snek_ind)
                    ge.pop(snek_ind)
                    snakes.pop(snek_ind)
                    foods.pop(snek_ind)
                    timebomb.pop(snek_ind)
                    moved.pop(snek_ind)
                    explored.pop(snek_ind)

            draw_window(window, snakes, foods, gen)

            # # break if score gets large enough
            # score = max(score, max(snake.size for snake in snakes)) if snakes else score
            # if score >= 25:
            #     pickle.dump(nets,open("best.pickle", "wb")) # or is it nets[0]?
            #     break


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play snake.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 100 generations.
    winner = p.run(eval_genomes, 100)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)