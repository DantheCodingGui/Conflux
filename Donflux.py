import pygame, sys, math
from pygame.locals import*

class Object():
    def __init__(self, ptype, image, startx, starty):
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect()
        self.move_image = self.image
        self.x = startx
        self.y = starty
        self.rect.center = (self.x, self.y)
        self.lxedge = 0
        self.rxedge = 0
        self.uyedge = 0
        self.dyedge = 0
        self.angle = 0
        self.ptype = ptype
        self.alive = True
        
    def get_rotation(self, px, py, ex, ey):    
        mousepos = pygame.mouse.get_pos()
        if self.ptype == 'player' or self.ptype == 'bullet':
            self.angle = math.atan2((mousepos[1] - py), (mousepos[0] - px))
        elif self.ptype == 'enemy':
            self.angle = math.atan2((ey - py), ((ex - px)))
        Object.move_image = pygame.transform.rotate(self.image, 360 - (self.angle * 57.27))      
        return Object.move_image, self.angle
    
    def update(self, surface, image, pos):
            surface.blit(image, pos)
        
class Player(Object, pygame.sprite.Sprite):
    def __init__(self, image, startx, starty):
        super(Player, self).__init__('player', image, startx, starty)
        pygame.sprite.Sprite.__init__(self)
        self.X_change = 0
        self.Y_change = 0
                
class Enemy(Object, pygame.sprite.Sprite):
    def __init__(self, image, startx, starty):
        super(Enemy, self).__init__('enemy', image, startx, starty)
        pygame.sprite.Sprite.__init__(self)
        self.a = ''

class Bullet(Object, pygame.sprite.Sprite):
    def __init__(self, image, startx, starty, uvectx, uvecty):
        super(Bullet, self).__init__('bullet', image, startx, starty)
        pygame.sprite.Sprite.__init__(self)        
        self.uvectx = uvectx
        self.uvecty = uvecty
        
    
    def move_bullet(self, x, y):
        self.x += self.uvectx*2
        self.y += self.uvecty*2
        
    def update(self, surface, image, pos):
        surface.blit(image, pos)
            
class Barrier(pygame.sprite.Sprite):
    def __init__(self, tcx, tcy, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.topcornerx = tcx
        self.topcornery = tcy
        self.width = width
        self.height = height
        
    def player_detection(self, pcx, pcy, pl, pr, pu, pd, x_change, y_change):
        if pr > self.topcornerx and pl < (self.topcornerx + self.width) and pu < (self.topcornery + self.height) and pd > self.topcornery:
            if pcx < self.topcornerx:
                if x_change > 0:
                    x_change = 0
            if pcx > (self.topcornerx + self.width):
                if x_change < 0:
                    x_change = 0
            if pcy > (self.topcornery + self.height):
                if y_change < 0:
                    y_change = 0
            if pcy < self.topcornery:
                if y_change > 0:
                    y_change = 0
                                
        return x_change, y_change
        
    def update(self, surface, colour):
        pygame.draw.rect(surface, colour, (self.topcornerx, self.topcornery, self.width, self.height), 4)

class Door():
    def __init__(self, x, starty, endy):
        self.x = x + 20
        self.starty = starty
        self.endy = endy
        self.thickness = 5
        
    def door_detection(self, playeredge, x_change):
        if playeredge >= self.x:
            if x_change > 0:
                x_change = 0
        return x_change
    
    def update(self, display, colour):
        pygame.draw.line(display, colour, (self.x, self.starty), (self.x, self.endy), self.thickness)
        
class Game():
    def __init__(self):
        pygame.init()

        self.title = 'Donflux'
        self.window_width = 1000
        self.window_height = 600
        self.border_size = 65
        self.border_step = 2.4
        self.display = pygame.display.set_mode((self.window_width, self.window_height))
        self.game_icon('Game_Icon.png')
        pygame.display.set_caption(self.title)
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.pause = False

        self.font = 'freesansbold.ttf'
        self.background = pygame.transform.scale(pygame.image.load('DonandFriend.png'), (1000, 600))
        

        self.game_state = 'Start'
        self.player = None
        self.room_number = 1

    def state_manager(self):
        states = ['Start','Pause','End','Play','Quit','Scores','Playing']

        if not self.game_state in states:
            self.game_state = 'Start'

        game_state_loop = True
        while game_state_loop:
            if self.game_state == 'Start':
                self.start_menu()
            elif self.game_state == 'Pause':
                print()
            elif self.game_state == 'End':
                self.end_menu()
            elif self.game_state == 'Play':
                self.game_state = 'Playing'
                self.play_game()
            elif self.game_state == 'Scores':
                self.view_high_scores()
            elif self.game_state == 'Quit':
                game_state_loop = False
            else:
                self.game_state = 'Start'

    def start_menu(self):

        pygame.mouse.set_visible(1)
        intro = True
        while intro:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.game_state = 'Quit'
                    intro = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.game_state = 'Quit'
                        intro = False
            self.display.blit(self.background, (0, 0))
            button_play = self.create_button('Play', self.colour_code('white'), 500, 325, 150, 50, 'Play')
            button_scores = self.create_button('View High Scores', self.colour_code('white'), 500, 400, 150, 50, 'Scores')
            button_exit = self.create_button('Exit', self.colour_code('red'), 500, 475, 150, 50, 'Quit')
            self.message_display(self.title, self.font, 150, self.colour_code('white'), 500, 150)
            pygame.display.update()
            self.clock.tick(self.fps)

            if not button_play == None:
                print('Start Menu - Button: Play')
                self.game_state = 'Play'
                intro = False
            elif not button_scores == None:
                print('Start Menu - Button: Scores')
                self.game_state = 'Scores'
                intro = False
            elif not button_exit == None:
                print('Start Menu - Button: Quit')
                self.game_state = 'Quit'
                intro = False

    def end_menu(self):
        pygame.mouse.set_visible(1)
        self.player_name = ''
        prescence_error = False
        end = True
        while end:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.game_state = 'Quit'
                    end = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.game_state = 'Quit'
                        end = False
                    elif event.key == K_a:
                        self.player_name += 'a'
                    elif event.key == K_b:
                        self.player_name += 'b' 
                    elif event.key == K_c:
                        self.player_name += 'c'
                    elif event.key == K_d:
                        self.player_name += 'd'
                    elif event.key == K_e:
                        self.player_name += 'e'
                    elif event.key == K_f:
                        self.player_name += 'f' 
                    elif event.key == K_g:
                        self.player_name += 'g'
                    elif event.key == K_h:
                        self.player_name += 'h'   
                    elif event.key == K_i:
                        self.player_name += 'i'
                    elif event.key == K_j:
                        self.player_name += 'j' 
                    elif event.key == K_k:
                        self.player_name += 'k'
                    elif event.key == K_l:
                        self.player_name += 'l'
                    elif event.key == K_m:
                        self.player_name += 'm'
                    elif event.key == K_n:
                        self.player_name += 'n' 
                    elif event.key == K_o:
                        self.player_name += 'o'
                    elif event.key == K_p:
                        self.player_name += 'p'     
                    elif event.key == K_q:
                        self.player_name += 'q'   
                    elif event.key == K_r:
                        self.player_name += 'r'
                    elif event.key == K_s:
                        self.player_name += 's' 
                    elif event.key == K_t:
                        self.player_name += 't'
                    elif event.key == K_u:
                        self.player_name += 'u'
                    elif event.key == K_v:
                        self.player_name += 'v'
                    elif event.key == K_w:
                        self.player_name += 'w' 
                    elif event.key == K_x:
                        self.player_name += 'x'
                    elif event.key == K_y:
                        self.player_name += 'y' 
                    elif event.key == K_z:
                        self.player_name += 'z'
                    elif event.key == K_0:
                        self.player_name += '0'   
                    elif event.key == K_1:
                        self.player_name += '1'
                    elif event.key == K_2:
                        self.player_name += '2' 
                    elif event.key == K_3:
                        self.player_name += '3'
                    elif event.key == K_4:
                        self.player_name += '4'
                    elif event.key == K_5:
                        self.player_name += '5'
                    elif event.key == K_6:
                        self.player_name += '6' 
                    elif event.key == K_7:
                        self.player_name += '7'
                    elif event.key == K_8:
                        self.player_name += '8' 
                    elif event.key == K_9:
                        self.player_name += '9'   
                    elif event.key == K_SPACE:
                        self.player_name += ' '
                    elif event.key == K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                        
            self.validate_player_name()
            self.display.fill(self.colour_code('black'))
            pygame.draw.rect(self.display, self.colour_code('white'), (100, 100, 800, 400), 0)
            self.message_display('Enter your name', self.font, 20, self.colour_code('black'), 275, 300)
            pygame.draw.rect(self.display, self.colour_code('black'), (150, 350, 250, 50), 2)
            self.message_display(self.player_name, self.font, 20, self.colour_code('black'), 275, 375)
            button_play = self.create_button('Play again', self.colour_code('black'), 650, 300, 150, 50, 'Play')
            button_start = self.create_button('Exit to main menu', self.colour_code('red'), 650, 400, 150, 50, 'Start')
            if self.player.alive:
                self.message_display('You Won!', self.font, 50, self.colour_code('green'), 500, 200)
            else:
                self.message_display('You Died!', self.font, 50, self.colour_code('red'), 500, 200)
            if prescence_error:
                self.message_display('Name empty', self.font, 20, self.colour_code('red'), 275, 425)
        
            
            if not button_play == None: #new game
                if self.player_name != '':
                    print('End Menu - Button: Play')
                    self.game_state = 'Play'
                    end = False
                prescence_error = True
            elif not button_start == None:
                if self.player_name != '':
                    print('End Menu - Button: Start Menu')
                    self.game_state = 'Start'
                    end = False
                prescence_error = True
            pygame.display.update()
            self.clock.tick(self.fps)            

    def play_game(self):
        pygame.mouse.set_visible(0)
        pygame.mouse.set_pos([500, 300])
        player_start = [100,300]
        cursor = pygame.image.load('Game_cursor.png')
        self.player = Player('Player_Sprite.png', player_start[0], player_start[1])
        door = Door(self.window_width-self.border_size, self.border_size*self.border_step, self.window_height-self.border_size*self.border_step)
        self.enemies_list = pygame.sprite.Group()
        self.barriers_list = pygame.sprite.Group()
        self.bullets_list = pygame.sprite.Group()
        click = pygame.mouse.get_pressed()
        self.room_number = 1
        reset_player = False
        direction = ''
        self.bullets_list.empty()
        while self.game_state == 'Playing':
            if reset_player: #Place player back at start point
                self.player.x = player_start[0]
                self.player.y = player_start[1]
                reset_player = False
            mousepos = pygame.mouse.get_pos()
            self.display.fill(self.colour_code('white'))
            self.load_map()
            button_pause = self.create_button('][', self.colour_code('white'), 30, 30, 30, 30, 'Pause')
            if not button_pause == None:
                self.pause_menu()
            pygame.mouse.set_visible(0)
            room_number_msg = 'Room No. ' + str(self.room_number)
            self.message_display(room_number_msg, self.font, 15, self.colour_code('white'), 475, 25)
            self.player.move_image, self.player.angle = self.player.get_rotation(self.player.x, self.player.y, 0, 0)
            for enemy in self.enemies_list:
                enemy.move_image, enemy.angle = enemy.get_rotation(self.player.x, self.player.y, enemy.x, enemy.y)
            for bullet in self.bullets_list:
                bullet.move_image, bullet.angle = bullet.get_rotation(self.player.x, self.player.y, 0, 0)
            unitv_x, unitv_y = self.get_uvector(self.player.x, self.player.y, self.player.angle)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.game_state = 'Quit'
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.game_state = 'Quit'
                    elif event.key == K_w:
                        direction = 'w'
                    elif event.key == K_s:
                        direction = 's'
                    elif event.key == K_d:
                        direction = 'd'
                    elif event.key == K_a:
                        direction = 'a'
                elif event.type == KEYUP:
                    direction = ''
                    

            if direction == 'w':
                self.player.X_change = unitv_x*3
                self.player.Y_change = unitv_y*3
            elif direction == 's':
                self.player.X_change = unitv_x*-2
                self.player.Y_change = unitv_y*-2
            elif direction == 'd':
                self.player.X_change = unitv_y*-2.5
                self.player.Y_change = unitv_x*2.5
            elif direction == 'a':
                self.player.X_change = unitv_y*2.5
                self.player.Y_change = unitv_x*-2.5
            else:
                self.player.X_change = 0
                self.player.Y_change = 0
            
            if click[0] == 1:
                bullet = Bullet('Bullet_sprite.png', self.player.x, self.player.y, unitv_x, unitv_y)
                self.bullets_list.add(bullet)
                
            for bullet in self.bullets_list:
                bullet.move_bullet(bullet.x, bullet.y)
            
            self.player.lxedge, self.player.uyedge, self.player.rxedge, self.player.dyedge = self.get_edges(self.player, self.player.move_image)
            for enemy in self.enemies_list:
                enemy.lxedge, enemy.uyedge, enemy.rxedge, enemy.dyedge = self.get_edges(enemy, enemy.move_image)
            for bullet in self.bullets_list:
                bullet.lxedge, bullet.uyedge, bullet.rxedge, bullet.dyedge = self.get_edges(self.player, bullet.move_image)

            self.player.X_change, self.player.Y_change = self.boundary_detection(self.player.uyedge, self.player.dyedge, self.player.lxedge, self.player.rxedge, self.player.X_change, self.player.Y_change)
            for barrier in self.barriers_list:
                self.player.X_change, self.player.Y_change = barrier.player_detection(self.player.x, self.player.y, self.player.lxedge, self.player.rxedge, self.player.uyedge, self.player.dyedge, self.player.X_change, self.player.Y_change)
            if len(self.enemies_list) != 0:
                self.player.X_change = door.door_detection(self.player.rxedge, self.player.X_change)
                door.update(self.display, self.colour_code('black'))
            if pygame.sprite.spritecollideany(self.player, self.enemies_list):
                self.player.alive = False
                self.game_state = 'End'

            self.player.x += self.player.X_change
            self.player.y += self.player.Y_change
            self.player.rect.center = (self.player.x, self.player.y) 
            for enemy in self.enemies_list:
                enemy.rect.center = (enemy.x, enemy.y)
            for bullet in self.bullets_list:
                bullet.rect.center = (bullet.x, bullet.y)
                            
            for enemy in self.enemies_list:
                enemy.update(self.display, enemy.move_image, (enemy.lxedge, enemy.uyedge))
            self.player.update(self.display, self.player.move_image, (self.player.lxedge, self.player.uyedge))
            self.display.blit(cursor, (mousepos[0]-11, mousepos[1]-11))
            for barrier in self.barriers_list:
                barrier.update(self.display, self.colour_code('black'))
            for bullet in self.bullets_list:
                bullet.update(self.display, bullet.move_image, (bullet.lxedge, bullet.uyedge)) 


            pygame.display.update()
            self.clock.tick(self.fps)

            if self.player.rxedge >= self.window_width - 20: #Level up when at edge of screen
                self.increase_level()
                reset_player = True

    def increase_level(self):
        print('Level Up ' + str(self.room_number))
        self.room_number += 1
        
    def validate_player_name(self):
        if len(self.player_name) > 15:
            self.player_name = self.player_name[:-1]

    def pause_menu(self):

        pygame.mouse.set_visible(1)
        self.pause = True
        while self.pause:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.game_state = 'Quit'
                    self.pause = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.game_state = 'Quit'
                        self.pause = False

            self.display.fill(self.colour_code('black'))
            pygame.draw.rect(self.display, self.colour_code('white'), (100, 100, 800, 400), 0)
            button_continue = self.create_button('Continue', self.colour_code('green'), 300, 400, 150, 50, 'Unpause')
            button_restart = self.create_button('Restart', self.colour_code('black'), 500, 400, 150, 50, 'Play')
            button_exit = self.create_button('Exit to main menu', self.colour_code('red'), 700, 400, 150, 50, 'Start')
            self.message_display('Paused', self.font, 50, self.colour_code('blue'), 500, 200)
            pygame.display.update()
            self.clock.tick(self.fps)

            if not button_continue == None: #new game
                print('Pause Menu - Button: Unpause')
                self.unpause()
            elif not button_restart == None: #new game
                print('Pause Menu - Button: New Game')
                self.game_state = 'Play'
                self.unpause()
            elif not button_exit == None:
                print('Pause Menu - Button: Quit')
                self.game_state = 'Start'
                self.unpause()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def view_high_scores(self):
        
        pygame.mouse.set_visible(1)
        viewscores = True
        while viewscores:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.game_state = 'Quit'
                    viewscores = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.game_state = 'Quit'
                        viewscores = False
            self.display.fill(self.colour_code('white'))
            self.message_display('High Scores', self.font, 50, self.colour_code('black'), 500, 100)
            button_main_menu = self.create_button('Back to main menu', self.colour_code('black'), 150, 200, 150, 50, 'Start')
            pygame.display.update()
            self.clock.tick(self.fps)

            if not button_main_menu == None:
                print('Start Menu - Button: Back to main menu')
                self.game_state = 'Start'
                viewscores = False
        

    def unpause(self):
        self.pause = False

    def game_icon(self, icon):
        game_icon = pygame.image.load(icon).convert_alpha()
        pygame.display.set_icon(game_icon)

    def colour_code(self, colour):
        #               R     G    B
        cols = {
            'white' :   (255, 255, 255),
            'black' :   (  0,   0,   0),
            'green' :   (  0, 200,   0),
            'blue'  :   (  0,   0, 255),
            'red'   :   (255,   0,   0)
        }

        if colour in cols:
            return cols[colour]
        return None

    def create_button(self, text, colour, posx, posy, width, height, action):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        outline_thickness = 1
        self.message_display(text, self.font, 15, colour, posx, posy)
        if (mouse[0] > posx-(width/2) and mouse[0] < ((posx-(width/2) + width)) and (mouse[1] >  posy-(height/2) and mouse[1] < (posy-(height/2)) + height)):
            outline_thickness += 2
            pygame.draw.rect(self.display, colour, (posx-(width/2), posy-(height/2), width, height), outline_thickness)
            if click[0] == 1:
                return action
        else:
            pygame.draw.rect(self.display, colour, (posx-(width/2), posy-(height/2), width, height), outline_thickness)
        return None

    def message_display(self, text, font, font_size, colour, posx, posy):
        Text = pygame.font.Font(font, font_size)
        TEXTSURF = Text.render(text, True, colour)
        TextRect = TEXTSURF.get_rect()
        TextRect.center = (posx, posy)
        self.display.blit(TEXTSURF, TextRect)

    def load_map(self):
        pygame.draw.rect(self.display, self.colour_code('black'), (0, 0, self.window_width, self.border_size)) #top
        pygame.draw.rect(self.display, self.colour_code('black'), (0, self.window_height-self.border_size, self.window_width, self.border_size)) #bottom
        pygame.draw.rect(self.display, self.colour_code('black'), (0, 0, self.border_size, self.border_size*self.border_step)) #topleft
        pygame.draw.rect(self.display, self.colour_code('black'), (0, self.window_height-(self.border_size*self.border_step), self.border_size, self.border_size*self.border_step)) #bottomleft
        pygame.draw.rect(self.display, self.colour_code('black'), (self.window_width-self.border_size, 0, self.border_size, self.border_size*self.border_step)) #topright
        pygame.draw.rect(self.display, self.colour_code('black'), (self.window_width-self.border_size, self.window_height-(self.border_size*self.border_step), self.border_size, self.border_size*self.border_step)) #bottomright
        
        if self.room_number == 1:
            self.enemies_list.empty()
            self.barriers_list.empty()
            self.bullets_list.empty()
            enemy1 = Enemy('Enemy_Sprite.png', 800, 300)
            self.enemies_list.add(enemy1)
        elif self.room_number == 2:
            self.enemies_list.empty()
            self.barriers_list.empty()
            self.bullets_list.empty()
            enemy1 = Enemy('Enemy_Sprite.png', 800, 200)
            enemy2 = Enemy('Enemy_Sprite.png', 800, 400)
            self.enemies_list.add(enemy1, enemy2) 
            barrier1 = Barrier(300, 200, 100, 200)
            self.barriers_list.add(barrier1)
        elif self.room_number == 3:
            self.enemies_list.empty()
            self.barriers_list.empty()
            self.bullets_list.empty()
            enemy1 = Enemy('Enemy_Sprite.png', 700, 100)
            enemy2 = Enemy('Enemy_Sprite.png', 700, 200)
            enemy3 = Enemy('Enemy_Sprite.png', 700, 300)
            enemy4 = Enemy('Enemy_Sprite.png', 700, 400)
            enemy5 = Enemy('Enemy_Sprite.png', 700, 500)
            self.enemies_list.add(enemy1, enemy2, enemy3, enemy4, enemy5)
            barrier1 = Barrier(300, 100, 50, 100)
            barrier2 = Barrier(300, 400, 50, 100)
            self.barriers_list.add(barrier1, barrier2)            
        
    def get_uvector(self, x, y, angle):
        unitv_x = math.cos(angle)
        unitv_y = math.sin(angle)
        return unitv_x, unitv_y

    def boundary_detection(self, topedge, bottomedge, leftedge, rightedge, x_change, y_change):
        if topedge < self.border_size:
            if y_change < 0:
                y_change = 0
        if bottomedge > self.window_height-self.border_size:
            if y_change > 0:
                y_change = 0

        if (topedge > (self.border_size*self.border_step)) and \
            (bottomedge < (self.window_height - (self.border_size*self.border_step))):
            if leftedge <= 0 and x_change <= 0:
                x_change = 0
            if rightedge >= self.window_width and x_change >= 0:
                x_change = 0
        else:
            if rightedge > self.window_width-self.border_size:
                if x_change > 0:
                    x_change = 0
                if topedge < (self.border_size*self.border_step):
                    if y_change < 0:
                        y_change = 0
                if bottomedge > (self.window_height - (self.border_size*self.border_step)):
                    if y_change > 0:
                        y_change = 0                    
            if leftedge < self.border_size:
                if x_change < 0:
                    x_change = 0
                if topedge < (self.border_size*self.border_step):
                    if y_change < 0:
                        y_change = 0
                if bottomedge > (self.window_height - (self.border_size*self.border_step)):
                    if y_change > 0:
                        y_change = 0                
                
        return x_change, y_change

    def get_edges(self, item, image):
        lxedge = item.x - image.get_rect().width/2 
        uyedge = item.y - image.get_rect().height/2
        rxedge = item.x + image.get_rect().width/2
        dyedge = item.y + image.get_rect().height/2 

        return lxedge, uyedge, rxedge, dyedge

if __name__ == "__main__":
    game = Game()
    game.state_manager()
    game.quit_game()