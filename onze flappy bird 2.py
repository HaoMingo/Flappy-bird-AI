import pygame
import random
import os
import time
import pickle
# variable van een python object

pygame.font.init()  # init font

WIN_WIDTH = 600
WIN_HEIGHT = 800
PIPE_VEL = 3
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)

gen = 0
    
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())


gen = 0

class Bird:
        
#Bird class representing the flappy bird
        
        WIN_HEIGHT = 0
        WIN_WIDTH = 0
        MAX_ROTATION = 25
        IMGS = bird_images
        ROT_VEL = 20
        ANIMATION_TIME = 5

        def __init__(self, x, y):
            """
            Initialize the object
            :param x: starting x pos (int)
            :param y: starting y pos (int)
            :return: None
            """
            self.x = x
            self.y = y
            self.gravity = 9.8
            self.tilt = 0  # degrees to tilt
            self.tick_count = 0
            self.vel = 0
            self.height = self.y
            self.img_count = 0
            self.img = self.IMGS[0]

        def jump(self):
            """
            make the bird jump
            :return: None
            """
            self.vel = -10.5
            self.tick_count = 0
            self.height = self.y

        def move(self):
            """
            make the bird move
            :return: None
            """
            self.tick_count += 1

            # for downward acceleration
            displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement

            # terminal velocity
            if displacement >= 16:
                displacement = (displacement/abs(displacement)) * 16

            if displacement < 0:
                displacement -= 2

            self.y = self.y + displacement

            if displacement < 0 or self.y < self.height + 50:  # tilt up
                if self.tilt < self.MAX_ROTATION:
                    self.tilt = self.MAX_ROTATION
            else:  # tilt down
                if self.tilt > -90:
                    self.tilt -= self.ROT_VEL

        def draw(self, win):
            """
            draw the bird
            :param win: pygame window or surface
            :return: None
            """
            self.img_count += 1

            # For animation of bird, loop through three images
            if self.img_count <= self.ANIMATION_TIME:
                self.img = self.IMGS[0]
            elif self.img_count <= self.ANIMATION_TIME*2:
                self.img = self.IMGS[1]
            elif self.img_count <= self.ANIMATION_TIME*3:
                self.img = self.IMGS[2]
            elif self.img_count <= self.ANIMATION_TIME*4:
                self.img = self.IMGS[1]
            elif self.img_count == self.ANIMATION_TIME*4 + 1:
                self.img = self.IMGS[0]
                self.img_count = 0

            # so when bird is nose diving it isn't flapping
            if self.tilt <= -80:
                self.img = self.IMGS[1]
                self.img_count = self.ANIMATION_TIME*2


            # tilt the bird
            blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

        def get_mask(self):
            """
            gets the mask for the current image of the bird
            :return: None
            """
            return pygame.mask.from_surface(self.img)


class Pipe():
        """
        represents a pipe object
        """
        WIN_HEIGHT = WIN_HEIGHT
        WIN_WIDTH = WIN_WIDTH
        GAP = 200
        VEL = 5

        def __init__(self, x):
            """
            initialize pipe object
            :param x: int
            :param y: int
            :return" None
            """
            self.x = x
            self.height = 0
            self.gap = 100  # gap between top and bottom pipe

            # where the top and bottom of the pipe is
            self.top = 0
            self.bottom = 0

            self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
            self.PIPE_BOTTOM = pipe_img

            self.passed = False

            self.set_height()

        def set_height(self):
            """
            set the height of the pipe, from the top of the screen
            :return: None
            """
            self.height = random.randrange(50, 450)
            self.top = self.height - self.PIPE_TOP.get_height()
            self.bottom = self.height + self.GAP

        def move(self):
            """
            move pipe based on vel
            :return: None
            """
            self.x -= self.VEL

        def draw(self, win):
            """
            draw both the top and bottom of the pipe
            :param win: pygame window/surface
            :return: None
            """
            # draw top
            win.blit(self.PIPE_TOP, (self.x, self.top))
            # draw bottom
            win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


        def collide(self, bird, win):
            """
            returns if a point is colliding with the pipe
            :param bird: Bird object
            :return: Bool
            """
            bird_mask = bird.get_mask()
            top_mask = pygame.mask.from_surface(self.PIPE_TOP)
            bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
            top_offset = (self.x - bird.x, self.top - round(bird.y))
            bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

            b_point = bird_mask.overlap(bottom_mask, bottom_offset)
            t_point = bird_mask.overlap(top_mask,top_offset)

            if b_point or t_point:
                return True

            return False

class Base:
        """
        Represnts the moving floor of the game
        """
        VEL = 5
        WIN_WIDTH = WIN_WIDTH
        WIDTH = base_img.get_width()
        IMG = base_img

        def __init__(self, y):
            """
            Initialize the object
            :param y: int
            :return: None
            """
            self.y = y
            self.x1 = 0
            self.x2 = self.WIDTH

        def move(self):
            """
            move floor so it looks like its scrolling
            :return: None
            """
            self.x1 -= self.VEL
            self.x2 -= self.VEL
            if self.x1 + self.WIDTH < 0:
                self.x1 = self.x2 + self.WIDTH

            if self.x2 + self.WIDTH < 0:
                self.x2 = self.x1 + self.WIDTH

        def draw(self, win):
            """
            Draw the floor. This is two images that move together.
            :param win: the pygame surface/window
            :return: None
            """
            win.blit(self.IMG, (self.x1, self.y))
            win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
        """
        Rotate a surface and blit it to the window
        :param surf: the surface to blit to
        :param image: the image surface to rotate
        :param topLeft: the top left position of the image
        :param angle: a float value for angle
        :return: None
        """
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

        surf.blit(rotated_image, new_rect.topleft)

def menu_screen(win):
        """
        the menu screen that will start the game
        :param win: the pygame window surface
        :return: None
        """
        pass

def end_screen(win):
        """
        display an end screen when the player loses
        :param win: the pygame window surface
        :return: None
        """
        run = True
        text_label = END_FONT.render("Press Space to Restart", 1, (255,255,255))
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:
                    main(win)

            win.blit(text_label, (WIN_WIDTH/2 - text_label.get_width()/2, 500))
            pygame.display.update()

        pygame.quit()
        quit()

def draw_window(win, birds, pipes, base, score, gen):

        #van bird naar birds, want zo tekent het alle vogels.
  
        win.blit(bg_img, (0,0))

        for pipe in pipes:
            pipe.draw(win)

        base.draw(win)
        for bird in birds:
            bird.draw(win)

        # score
        score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
        win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))
        score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
        win.blit(score_label, (10, 10))
        

        pygame.display.update()


def main(genomes,config):
        global gen 
        gen += 1
         #evalueert de genomes
        nets = []
        ge = []
        birds = []
     # een lijst van 3 variablen om de fitness van de birds te volgen

        for _,g in genomes :
            g.fitness = 0  
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            birds.append(Bird(230,350))
            ge.append(g)
# het creëert een neuraal netwerk en een bird en voegt het toe aan de lijst met dezelfde genomes
            
        """
        Runs the main game loop
        :param win: pygame window surface
        :return: None
        """
        bird = Bird(230,350)
        base = Base(FLOOR)
        pipes = [Pipe(700)]
        score = 0

        clock = pygame.time.Clock()
        start = False
        lost = False

        run = True
        while run:
            pygame.time.delay(30)
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()
                    

                if event.type == pygame.KEYDOWN and not lost:
                    if event.key == pygame.K_SPACE:
                        if not start:
                            start = True
                        bird.jump()

            # Move Bird, base and pipes
            if start:
                bird.move()
            if not lost:
                base.move()
              
                pipe_ind = 0
                if len(birds) > 0:
                    if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                        pipe_ind = 1
                      
               
               
                            #bepaald om welke pijp op het scherm te gebruiken. de eerste of de tweede pijp dus.
                        

            
            for x,bird in enumerate(birds):
                    bird.move()
                    ge[x].fitness += 0.1
                    # dit stimuleert de vogel om niet helemaal omhoog of omlaag te vliegen.
               
                
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5: 
                    bird.jump()
     # dit stuurt een signaal naar het netwerk. deze signaal geeft aan of de vogel omhoog of omlaag te vliegen om de pijp te vermijden.

                
            if start:
                    rem = []
                    add_pipe = False
                    for pipe in pipes:
                        for x, bird in enumerate(birds):      
                            if pipe.collide(bird):
                                ge[x].fitness -= 1
                                birds.pop(x)
                                nets.pop(x)
                                ge.pop(x)
                                
#elke keer als een vogel een pijp raakt, wordt er 1 fitness van die vogel verminderd. Dit zorgt ervoor dat vogels die ver komen maar dan nogsteeds tegen een pijp gaan, geen voorkeur krijgen. Vogels op hetzelfde level hebben dan een hogere fitness.
                                
    #als een vogel de grond of een pijp raakt, verdwijnt de vogel uit het spel
                        pipe.move()
                        # check for collision
                        if pipe.collide(bird, win):
                            lost = True

                        if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                            rem.append(pipe)

                        if not pipe.passed and pipe.x < bird.x:
                            pipe.passed = True
                            add_pipe = True

                    if add_pipe:
                        score += 1
                        pipes.append(Pipe(WIN_WIDTH))
                    for g.fitness in ge:
                        g.fitness += 5
# dit zorgt ervoor dat de vogels een hogere fitness krijgen nadat ze door een pijp zijn gegaan. Dit moedigt de vogels aan om verder te gaan in het spel.
                    for r in rem:
                        pipes.remove(r)

        for x,bird in enumerate(birds):    
            if bird.y + bird_images[0].get_height() - 10 >= FLOOR or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
               

            draw_window(WIN, birds, pipes, base, score, gen)

        end_screen(WIN)

if score > 20:
            pickle.dump(nets[0],open("best.pickle", "wb"))


main(WIN)

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
         neat.DefaultSpeciesSet, neat.DefaultStagnation,
         config_file)
#het maakt een populatie van birds. 
    p = neat.Population(config)

    #Stats recorder
    p.add_reporter(neat.StdOutReporter(True))
    #geeft informatie over de generaties
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
#hoeveel generaties er komen
    winner = p.run(main,25)
#de "main" gaat terug naar de main functie en de genomes gaat terug naar de main functie. 

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
