

from tkinter import Tk
from tkinter import Canvas
from tkinter import Button
from PIL import ImageTk,Image
win = Tk()
win.title("Racing Games")
win.geometry('500x500')

def game_1():
    import pygame
    import time
    import math
    from pygame import image
    from pygame import mixer
    from utils2 import scale_image, blit_rotate_center, blit_text_center
    pygame.font.init()
    pygame.mixer.init()

    mixer.music.load('bgm.wav')
    mixer.music.play(-1)

    GRASS = scale_image(image.load("imgs/grass.jpg"), 2.5)
    TRACK = scale_image(image.load("imgs/track.png"), 0.9)

    TRACK_BORDER = scale_image(image.load("imgs/track-border.png"), 0.9)
    TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

    FINISH = image.load("imgs/finish.png")
    FINISH_MASK = pygame.mask.from_surface(FINISH)
    FINISH_POSITION = (130, 250)

    RED_CAR = scale_image(image.load("imgs/red-car.png"), 0.55)
    GREEN_CAR = scale_image(image.load("imgs/green-car.png"), 0.55)

    WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CIRCUIT 0")

    MAIN_FONT = pygame.font.SysFont("Aerial", 44)

    FPS = 60
    PATH = [(175, 119), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551), (613, 715), (736, 713),
            (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377), (176, 388), (178, 260)]


    class GameInfo:
        LEVELS = 10

        def __init__(self, level=1):
            self.level = level
            self.started = False
            self.level_start_time = 0

        def next_level(self):
            self.level += 1
            self.started = False

        def reset(self):
            self.level = 1
            self.started = False
            self.level_start_time = 0

        def game_finished(self):
            return self.level > self.LEVELS

        def start_level(self):
            self.started = True
            self.level_start_time = time.time()

        def get_level_time(self):
            if not self.started:
                return 0
            return round(time.time() - self.level_start_time)


    class AbstractCar:
        def __init__(self, max_vel, rotation_vel):
            self.img = self.IMG
            self.max_vel = max_vel
            self.vel = 0
            self.rotation_vel = rotation_vel
            self.angle = 0
            self.x, self.y = self.START_POS
            self.acceleration = 0.7

        def rotate(self, left=False, right=False):
            if left:
                self.angle += self.rotation_vel
            elif right:
                self.angle -= self.rotation_vel

        def draw(self, win):
            blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

        def move_forward(self):
            self.vel = min(self.vel + self.acceleration, self.max_vel)
            self.move()

        def move_backward(self):
            self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
            self.move()

        def move(self):
            radians = math.radians(self.angle)
            vertical = math.cos(radians) * self.vel
            horizontal = math.sin(radians) * self.vel

            self.y -= vertical
            self.x -= horizontal

        def collide(self, mask, x=0, y=0):
            car_mask = pygame.mask.from_surface(self.img)
            offset = (int(self.x - x), int(self.y - y))
            poi = mask.overlap(car_mask, offset)
            return poi

        def reset(self):
            self.x, self.y = self.START_POS
            self.angle = 0
            self.vel = 0


    class PlayerCar(AbstractCar):
        IMG = RED_CAR
        START_POS = (180, 200)

        def reduce_speed(self):
            self.vel = max(self.vel - self.acceleration / 2, 0)
            self.move()

        def bounce(self):
            self.vel = -self.vel/2
            self.move()


    class ComputerCar(AbstractCar):
        IMG = GREEN_CAR
        START_POS = (150, 200)

        def __init__(self, max_vel, rotation_vel, path=[]):
            super().__init__(max_vel, rotation_vel)
            self.path = path
            self.current_point = 0
            self.vel = max_vel

        def draw_points(self, win):
            for point in self.path:
                pygame.draw.circle(win, (255, 0, 0), point, 5)

        def draw(self, win):
            super().draw(win)
            # self.draw_points(win)

        def calculate_angle(self):
            target_x, target_y = self.path[self.current_point]
            x_diff = target_x - self.x
            y_diff = target_y - self.y

            if y_diff == 0:
                desired_radian_angle = math.pi / 2
            else:
                desired_radian_angle = math.atan(x_diff / y_diff)

            if target_y > self.y:
                desired_radian_angle += math.pi

            difference_in_angle = self.angle - math.degrees(desired_radian_angle)
            if difference_in_angle >= 180:
                difference_in_angle -= 360

            if difference_in_angle > 0:
                self.angle -= min(self.rotation_vel, abs(difference_in_angle))
            else:
                self.angle += min(self.rotation_vel, abs(difference_in_angle))

        def update_path_point(self):
            target = self.path[self.current_point]
            rect = pygame.Rect(
                self.x, self.y, self.img.get_width(), self.img.get_height())
            if rect.collidepoint(*target):
                self.current_point += 1

        def move(self):
            if self.current_point >= len(self.path):
                return

            self.calculate_angle()
            self.update_path_point()
            super().move()

        def next_level(self, level):
            self.reset()
            self.vel = self.max_vel + (level - 1) * 0.2
            self.current_point = 0


    def draw(win, images, player_car, computer_car, game_info):
        for img, pos in images:
            win.blit(img, pos)

        level_text = MAIN_FONT.render(
            f"Level {game_info.level}", 1, (255, 255, 255))
        win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

        time_text = MAIN_FONT.render(
            f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
        win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

        vel_text = MAIN_FONT.render(
            f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
        win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 100))

        player_car.draw(win)
        computer_car.draw(win)
        pygame.display.update()


    def move_player(player_car):
        keys = pygame.key.get_pressed()
        moved = False

        if keys[pygame.K_a]:
            player_car.rotate(left=True)
        if keys[pygame.K_d]:
            player_car.rotate(right=True)
        if keys[pygame.K_w]:
            moved = True
            player_car.move_forward()
        if keys[pygame.K_s]:
            moved = True
            player_car.move_backward()

        if not moved:
            player_car.reduce_speed()


    def handle_collision(player_car, computer_car, game_info):
        if player_car.collide(TRACK_BORDER_MASK) != None:
            player_car.bounce()

        computer_finish_poi_collide = computer_car.collide(
            FINISH_MASK, *FINISH_POSITION)
        if computer_finish_poi_collide != None:
            blit_text_center(WIN, MAIN_FONT, "You lost!")
            pygame.display.update()
            pygame.time.wait(5000)
            game_info.reset()
            player_car.reset()
            computer_car.reset()

        player_finish_poi_collide = player_car.collide(
            FINISH_MASK, *FINISH_POSITION)
        if player_finish_poi_collide != None:
            if player_finish_poi_collide[1] == 0:
                player_car.bounce()
            else:
                game_info.next_level()
                player_car.reset()
                computer_car.next_level(game_info.level)


    run = True
    clock = pygame.time.Clock()
    images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
              (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
    player_car = PlayerCar(5, 5)
    computer_car = ComputerCar(2, 4, PATH)
    game_info = GameInfo()

    while run:
        clock.tick(FPS)

        draw(WIN, images, player_car, computer_car, game_info)

        while not game_info.started:
            blit_text_center(WIN, MAIN_FONT, f"CIRCUIT 0: Press any key to start level {game_info.level}!")
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break

                if event.type == pygame.KEYDOWN:
                    game_info.start_level()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        move_player(player_car)
        computer_car.move()

        handle_collision(player_car, computer_car, game_info)

        if game_info.game_finished():
            blit_text_center(WIN, MAIN_FONT, "You won the game!")
            pygame.time.wait(5000)
            game_info.reset()
            player_car.reset()
            computer_car.reset()


    pygame.quit()



def game_2():	
	import pygame
	from random import randint
	from pygame import image
	from pygame import font
	from pygame import transform
	pygame.init()
	def display_score():
		global current_time
		current_time = int(pygame.time.get_ticks() / 1000) - start_time
		score_surf = test_font.render(f'Score: {current_time}',True,(64,64,64))
		score_rect = score_surf.get_rect(topleft = (600,0))
		screen.blit(score_surf,score_rect)
		return current_time
	def collisions(player,obstacles):
		if obstacles:
			for obstacle_rect in obstacles: 
				if player.colliderect(obstacle_rect) : 
					crash_music = pygame.mixer.Sound('imgs2/crash_sound.wav')
					crash_music.play(0)
					crash_music.set_volume(0.3)
					return False
		return True
	test_font =font.Font(None, 50)
	start_time = 0
	#music
	bg_music = pygame.mixer.Sound('imgs2/bg_sound.mp3')
	bg_music.play()
	bg_music.set_volume(0.09)
	
	game_active = False
	def scale_image(img, factor):
		size = round(img.get_width() * factor), round(img.get_height() * factor)
		return transform.scale(img, size)
	def obstacles_movement(obstacle_list):
		if obstacle_list:
			for obstacle_rect in obstacle_list:
				if display_score()>30:
					obstacle_rect.y+=12
				elif display_score()>10:
					obstacle_rect.y+=5
				elif display_score()>40:
					obstacle_rect.y+=15
				elif display_score()>15:
					obstacle_rect.y+=9
				else:
					obstacle_rect.y += 2
				if obstacle_rect.right >= 330 and obstacle_rect.right <= 450 :
					screen.blit(taxi,obstacle_rect)
				elif obstacle_rect.right >= 460 and obstacle_rect.right <= 550:
					screen.blit(truck,obstacle_rect)
				else:
					screen.blit(green_car,obstacle_rect)
			obstacle_list = [obstacle for obstacle in obstacle_list if obstacle.y >= -50]
			return obstacle_list
		else : return []
	screen = pygame.display.set_mode((800,400))
	pygame.display.set_caption('Super Sprint Racing')
	clock = pygame.time.Clock()
	left_part = pygame.Surface((200,400)) 
	left_part.fill('bisque1')
	center = pygame.Surface((400,400))
	center.fill('antiquewhite4')
	right_part = pygame.Surface((200,400))
	right_part.fill('bisque1')
	bush = scale_image(image.load('imgs2/bush.png'),0.22)
	bush_rect = bush.get_rect(midbottom = (50,220))
	bush_rect2 = bush.get_rect(midbottom = (150,80))
	bush_rect3 = bush.get_rect(midbottom = (650,50))
	bush_rect4 = bush.get_rect(midbottom = (750,190))
	red_car = pygame.image.load('imgs2/red_car.png')
	rc_rect = red_car.get_rect(midbottom = (300,390))
	green_car = pygame.image.load('imgs2/green_car.png')
	
	taxi = scale_image(pygame.image.load('imgs2/taxi.png'),0.62)
	truck = scale_image(pygame.image.load('imgs2/truck.png'),0.62)
	
	f1 = pygame.image.load('imgs2/f1.png')
	f1 = pygame.transform.scale2x(f1)
	f1_rect = f1.get_rect(center = (400,200))
	game_name = test_font.render('Circuit0',False,'cyan3')
	game_name_rect = game_name.get_rect(topleft = (350,100))
	run = test_font.render('Click on space to run',False,'cyan3')
	over = test_font.render('Game Over',False,'black')
	over_rect = over.get_rect(center = (400,150))
	run_rect = run.get_rect(topleft = (250,300))
	score = 0
	obstacles_rect_list = []
	obstacle_timer = pygame.USEREVENT + 1
	pygame.time.set_timer(obstacle_timer,1200)
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			if game_active :
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_w:
						rc_rect.y -= 50
						if rc_rect.top <= 0 : rc_rect.top <= 0
						  #bg_music = pygame.mixer.Sound('imgs2/acc_sound.mp3')
						  #bg_music.play(loops = 0)
						  #bg_music.set_volume(0.1)
					if event.key == pygame.K_s:
						rc_rect.y += 50
						if rc_rect.bottom >= 400 : rc_rect.bottom = 400
					if event.key == pygame.K_d:
						rc_rect.x += 50
						if rc_rect.right >=600 : rc_rect.right = 600
					if event.key == pygame.K_a:
						rc_rect.x -= 50
						if rc_rect.left <=200 : rc_rect.left = 200
			else:
				if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE :
					rc_rect.x +=50
					game_active = True 
					start_time = int(pygame.time.get_ticks() / 1000)
			if event.type == obstacle_timer and game_active:
				if randint(1,5) == 2:
					obstacles_rect_list.append(green_car.get_rect(midtop = (randint(230,330),-50)))
				elif randint(1,5) == 3:
					obstacles_rect_list.append(taxi.get_rect(midtop = (randint(340,450),-50)))
				else :
					obstacles_rect_list.append(truck.get_rect(midtop = (randint(460,570),-50)))


		if game_active :
			screen.blit(left_part,(0,0))
			screen.blit(right_part,(600,0))
			bush_rect.y += 3 
			if bush_rect.top >=400: bush_rect.top = 0
			screen.blit(bush,bush_rect)
			bush_rect2.y +=3
			if bush_rect2.top >=400: bush_rect2.top = 0
			screen.blit(bush,bush_rect2)
			bush_rect3.y +=3
			if bush_rect3.top >=400 : bush_rect3.top = 0
			screen.blit(bush,bush_rect3)
			bush_rect4.y += 3
			if bush_rect4.top >= 400 : bush_rect4.top = 0
			screen.blit(bush,bush_rect4)
			screen.blit(center,(200,0))
			screen.blit(red_car,rc_rect)
			obstacles_rect_list = obstacles_movement(obstacles_rect_list)
			score = display_score() 
			# bg_music = pygame.mixer.Sound('acc_sound.mp3')
			# bg_music.set_volume(0.1)
			game_active = collisions(rc_rect,obstacles_rect_list)

		else:
			obstacles_rect_list.clear()
			q = rc_rect.x - 50
			w = rc_rect.y -50 
			crash = image.load('imgs2/crash.png')
			screen.blit(crash,(q,w))
			play_again = test_font.render('Play Again',True,'black')
			play_again_rect = play_again.get_rect(center = (400,250))
			game_score = test_font.render(f'Your score : {score}',False,'black').convert_alpha()
			game_score_rect = game_score.get_rect(center = (400,100))
			if score == 0:
				screen.blit(f1,f1_rect)
				screen.blit(game_name,game_name_rect)
				screen.blit(run,run_rect)
			else : 
				screen.blit(over,over_rect)
				screen.blit(game_score,game_score_rect)
				screen.blit(play_again,play_again_rect)
		pygame.display.update()
		clock.tick(50)

bg = ImageTk.PhotoImage(file = r"C:\Users\suket\imgs2\bg.png")
my_canvas = Canvas(win,width=500,height=500)
my_canvas.pack(fill="both",expand=True)
my_canvas.create_image(0,0,image = bg,anchor="nw")
my_canvas.create_text(600,400,text="CIRCUIT O",font=("Georgia",50),fill="white")
my_canvas.create_text(650,500,text = "CHOOSE A GAME",font=("Georgia",50),fill="white")
btn_1 = Button(text = "Track racing",font=("Georgia",20),padx= 10,pady = 10,bg ='VioletRed2',fg = 'black',activebackground='black',activeforeground='white',command =game_1)
btn_1_win =  my_canvas.create_window(400,400,anchor="nw",window=btn_1)
btn_2 = Button(text = "Arcade game",font=("Georgia",20),padx= 10,pady = 10,bg ='VioletRed2',fg = 'black',activebackground='black',activeforeground='white',command =game_2)
btn_2_win =  my_canvas.create_window(200,400,anchor="nw",window=btn_2)
def resizer(e):
    global bg1 ,resized_image,new_bg
    bg1 = Image.open(r"C:\Users\suket\imgs2\bg.png")
    resized_image = bg1.resize((e.width,e.height))
    new_bg = ImageTk.PhotoImage(resized_image)
    my_canvas.create_image(0,0,image = new_bg,anchor="nw")
    my_canvas.create_text(800,100,text="CIRCUIT-ZERO",font=("Georgia",50),fill="blue")
    my_canvas.create_text(800,250,text = "CHOOSE A GAME",font=("Georgia",50),fill="blue")

win.bind('<Configure>',resizer)
win.mainloop()