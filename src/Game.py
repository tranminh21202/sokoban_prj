from pygame.locals import *
import sys
import pygame
import queue

class game:
    
    def is_valid_value(self,char):
        if ( char == ' ' or #nền
            char == '#' or #tường
            char == '@' or #người
            char == '.' or #vị trí cần đẩy thùng
            char == '*' or #thùng dúng vị trí
            char == '$' or #thùng
            char == '+' ): #người trên vị trí
            return True
        else:
            return False

    def __init__(self,filename,level):
        self.queue = queue.LifoQueue()
        self.matrix = []
        if level < 1:
            print ("ERROR: Level "+str(level)+" không có level nhỏ hơn 1")
            sys.exit(1)
        else:
            file = open(filename,'r')
            level_found = False
            for line in file:
                row = []
                if not level_found:
                    if  "Level "+str(level) == line.strip():
                        level_found = True
                else:
                    if line.strip() != "":
                        row = []
                        for c in line:
                            if c != '\n' and self.is_valid_value(c):
                                row.append(c)
                            elif c == '\n': #chuyển sang hàng tiếp theo khi xuống dòng
                                continue
                            else:
                                print( "ERROR: Level "+str(level)+" has invalid value "+c)
                                sys.exit(1)
                        self.matrix.append(row)
                    else:
                        break

    def load_size(self):
        x = 0
        y = len(self.matrix)
        for row in self.matrix:
            if len(row) > x:
                x = len(row)
        return (x * 32, y * 32)

    def get_matrix(self):
        return self.matrix

    def print_matrix(self):
        for row in self.matrix:
            for char in row:
                sys.stdout.write(char)
                sys.stdout.flush()
            sys.stdout.write('\n')

    def get_content(self,x,y):
        return self.matrix[y][x]

    def set_content(self,x,y,content):
        if self.is_valid_value(content):
            self.matrix[y][x] = content
        else:
            print ("ERROR: Value '"+content+"' to be added is not valid")

    def worker(self):
        x = 0
        y = 0
        for row in self.matrix:
            for pos in row:
                if pos == '@' or pos == '+':
                    return (x, y, pos)
                else:
                    x = x + 1
            y = y + 1
            x = 0

    def can_move(self,x,y):
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y) not in ['#','*','$']

    def next(self,x,y):
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y)

    def can_push(self,x,y):
        return (self.next(x,y) in ['*','$'] and self.next(x+x,y+y) in [' ','.'])

    def is_completed(self):
        for row in self.matrix:
            for cell in row:
                if cell == '$':
                    return False
        return True

    def move_box(self,x,y,a,b):
#        (x,y) -> move to do
#        (a,b) -> box to move
        current_box = self.get_content(x,y)
        future_box = self.get_content(x+a,y+b)
        if current_box == '$' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,' ')
        elif current_box == '$' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,' ')
        elif current_box == '*' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,'.')
        elif current_box == '*' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,'.')

    def unmove(self):
        if not self.queue.empty():
            movement = self.queue.get()
            if movement[2]:
                current = self.worker()
                self.move(movement[0] * -1,movement[1] * -1, False)
                self.move_box(current[0]+movement[0],current[1]+movement[1],movement[0] * -1,movement[1] * -1)
            else:
                self.move(movement[0] * -1,movement[1] * -1, False)

    def move(self,x,y,save):
        if self.can_move(x,y):
            current = self.worker()
            future = self.next(x,y)
            if current[2] == '@' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],' ')
                if save: self.queue.put((x,y,False))
            elif current[2] == '@' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],' ')
                if save: self.queue.put((x,y,False))
            elif current[2] == '+' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],'.')
                if save: self.queue.put((x,y,False))
            elif current[2] == '+' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],'.')
                if save: self.queue.put((x,y,False))
        elif self.can_push(x,y):
            current = self.worker()
            future = self.next(x,y)
            future_box = self.next(x+x,y+y)
            if current[2] == '@' and future == '$' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.queue.put((x,y,True))
            elif current[2] == '@' and future == '$' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.queue.put((x,y,True))
            elif current[2] == '@' and future == '*' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.queue.put((x,y,True))
            elif current[2] == '@' and future == '*' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.queue.put((x,y,True))
            if current[2] == '+' and future == '$' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.queue.put((x,y,True))
            elif current[2] == '+' and future == '$' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.queue.put((x,y,True))
            elif current[2] == '+' and future == '*' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.queue.put((x,y,True))
            elif current[2] == '+' and future == '*' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.queue.put((x,y,True))
                
class Button:
        def __init__(self, x, y, width, height, color, text):
            self.rect = pygame.Rect(x, y, width, height)
            self.color = color
            self.text = text
            self.font = pygame.font.SysFont('Times new roman', 24)

        def draw(self, screen):
            pygame.draw.rect(screen, self.color, self.rect)
            if self.text != '':
                text = self.font.render(self.text, True, (255, 255, 255))
                text_rect = text.get_rect(center=self.rect.center)
                screen.blit(text, text_rect)

        def is_clicked(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
                return True
            return False
        
def Draw_lable(hienthi,font,text,color,x,y):
    text = font.render(text,True,color)
    hienthi.blit(text,(x,y))

def Draw_panel(hienthi,color,x,y,a,b):
    panel = pygame.Surface((x,y))
    panel.fill(color)
    hienthi.blit(panel,(a,b))
background = (255, 226, 191)
black = (0,0,0)
white = (255,255,255)
vangcam = (255,204,0)
bluenhat = (153,255,255)
pink = (255,0,255)
level=1
somap=1
sonhanvat=1

def set_map():
    global level,somap,sonhanvat,box,wall,floor,box_docked,worker,worker_docked,docker
    box = pygame.image.load("images/box.png")
    wall = pygame.image.load("images/wall"+str(somap)+".png")
    floor = pygame.image.load("images/floor"+str(somap)+".png")
    box_docked = pygame.image.load("images/box_docked.png")
    docker = pygame.image.load("images/dock"+str(somap)+".png")
    worker = pygame.image.load("images/worker"+str(sonhanvat)+str(somap)+".png")
    worker_docked = pygame.image.load("images/worker"+str(sonhanvat)+str(somap)+".png")

def set_game():
    global level,somap,sonhanvat,box,wall,floor,box_docked,worker,worker_docked,docker,games,size,screen
    games = game("levels",level)
    size = games.load_size()
    screen = pygame.display.set_mode(size)

def print_game(matrix,screen):
    global level,somap,sonhanvat,box,wall,floor,box_docked,docker,worker,worker_docked,games,size
    screen.fill(background)
    x = 0
    y = 0
    for row in matrix:
        for char in row:
            if char == ' ': #nền
                screen.blit(floor,(x,y))
            elif char == '#': #tường
                screen.blit(wall,(x,y))
            elif char == '@': #người
                screen.blit(worker,(x,y))
            elif char == '.': #vị trí cần đẩy thùng đến
                screen.blit(docker,(x,y))
            elif char == '*': #thùng đã đúng vị trí
                screen.blit(box_docked,(x,y))
            elif char == '$': #thùng
                screen.blit(box,(x,y))
            elif char == '+': #người trong vị trí
                screen.blit(worker_docked,(x,y))
            x = x + 32
        x = 0
        y = y + 32

def hienthi_setmap(screen_start):
    set_map()
    for i in range(0,353,32):
        for j in range(100,453,32):
            if i >=320 or i<=32 or j <=132 or j >=420: 
                screen_start.blit(wall,(i,j))
            elif i<=160 and j== 260 or i>= 228 and j ==164 or j==260 and i >=256:
                screen_start.blit(wall,(i,j))
            elif i >=96 and j==324 and i <=128 or i==192 and j>=324 or i==256 and j ==356:
                screen_start.blit(wall,(i,j))
            elif i==160 and j==228:
                screen_start.blit(worker,(i,j))
            elif i==128 and j==388 or i==288 and j ==356 or j==228 and i ==224:
                screen_start.blit(docker,(i,j))
            elif i==96 and j==388 or i==256 and j ==324 or j==196 and i ==256:
                screen_start.blit(box,(i,j))
            else:
                screen_start.blit(floor,(i,j))

def display_end():
    global level,somap,sonhanvat,box,wall,floor,box_docked,worker,worker_docked,games,size,screen,docker
    pygame.display.set_caption("Game sokoban")
    icon = pygame.image.load(r"images\iconsokoban.png")
    pygame.display.set_icon(icon)
    screen_end = pygame.display.set_mode((500,300))
    Font_2 = pygame.font.SysFont('Times new roman',30)
# tạo các button
    button_mhchinh = Button(150, 200, 200, 50, vangcam, 'Màn hình chính')
    button_next = Button(350, 120, 100, 50, vangcam, 'Chơi tiếp')
    button_thoat = Button(50, 120, 150, 50, vangcam, 'Thoát game')
    while True:
        screen_end.fill(white)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: #nếu nhân nút thoát
                pygame.quit()
                sys.exit()
            if button_mhchinh.is_clicked(event):
                start_game()
            if button_next.is_clicked(event):
                level +=1
                games = game("levels",level)
                size = games.load_size()
                screen = pygame.display.set_mode(size)
                chay_game()
                pygame.quit()
                sys.exit()
            if button_thoat.is_clicked(event):
                pygame.quit()
                sys.exit()
        Draw_panel(screen_end,vangcam,500,100,0,0)
        Draw_panel(screen_end,bluenhat,500,300,0,100)
        Draw_lable(screen_end,Font_2,'LEVEL COMPLETED',black,110,30)
        button_mhchinh.draw(screen_end)
        button_next.draw(screen_end)
        button_thoat.draw(screen_end)    
        pygame.display.update()

def chay_game():
    global level,somap,sonhanvat,box,wall,floor,box_docked,worker,worker_docked,games,size,screen,docker
    while 1:
        if games.is_completed(): display_end()
        print_game(games.get_matrix(),screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: games.move(0,-1, True)
                elif event.key == pygame.K_DOWN: games.move(0,1, True)
                elif event.key == pygame.K_LEFT: games.move(-1,0, True)
                elif event.key == pygame.K_RIGHT: games.move(1,0, True)
                elif event.key == pygame.K_q: sys.exit(0)
                elif event.key == pygame.K_SPACE: games.unmove()
                elif event.key == pygame.K_r :
                    set_game()
                    set_map()
                    chay_game()
        pygame.display.update()

def start_game():
    global level,somap,sonhanvat,box,wall,floor,box_docked,worker,worker_docked,games,size,screen,docker
# thay titel va icon 
    pygame.display.set_caption("Game sokoban")
    icon = pygame.image.load(r"images\iconsokoban.png")
    pygame.display.set_icon(icon)
# tao cua so game
    screen_height = 600
    screen_width = 484
    screen_start = pygame.display.set_mode((screen_height,screen_width))
    Font_1 = pygame.font.SysFont('Times new roman',20)
    Font_2 = pygame.font.SysFont('Times new roman',30)
# tạo các button
    button = Button(450, 434, 100, 50, vangcam, 'Bắt đầu')
    button_map_tang = Button(405, 184, 60, 40, vangcam, 'Tăng')
    button_map_giam = Button(480, 184, 60, 40, vangcam, 'Giảm')
    button_nhanvat_tang = Button(405, 284, 60, 40, vangcam, 'Tăng')
    button_nhanvat_giam = Button(480, 284, 60, 40, vangcam, 'Giảm')
    button_level_tang = Button(405, 384, 60, 40, vangcam, 'Tăng')
    button_level_giam = Button(480, 384, 60, 40, vangcam, 'Giảm')
    def hienthi():
        Draw_lable(screen_start,Font_1,str(sonhanvat),black,500,234)  
        Draw_lable(screen_start,Font_1,str(sonhanvat),black,500,234)  
        Draw_lable(screen_start,Font_1,str(somap),black,500,134)  
        Draw_lable(screen_start,Font_1,str(level),black,500,334)    
        Draw_lable(screen_start,Font_1,'Map:',black,405,134)
        Draw_lable(screen_start,Font_1,'Nhân vật:',black,405,234)
        Draw_lable(screen_start,Font_1,'Level:',black,405,334)
        Draw_panel(screen_start,vangcam,600,100,0,0)
        Draw_lable(screen_start,Font_2,'SOKOBAN',black,200,50)
        button.draw(screen_start)
        button_map_tang.draw(screen_start)
        button_map_giam.draw(screen_start)
        button_nhanvat_tang.draw(screen_start)
        button_nhanvat_giam.draw(screen_start)
        button_level_tang.draw(screen_start)
        button_level_giam.draw(screen_start)
        hienthi_setmap(screen_start)
# vòng lặp xử lý màn hinh start
    while True:
        screen_start.fill(white)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: #nếu nhân nút thoát
                pygame.quit()
                sys.exit()
            if button.is_clicked(event):
                set_game()
                set_map()
                chay_game()  
            if button_nhanvat_tang.is_clicked(event):
                if sonhanvat < 4:
                    sonhanvat+=1
            if button_nhanvat_giam.is_clicked(event):
                if sonhanvat > 1:
                    sonhanvat-=1
            if button_map_tang.is_clicked(event):
                if somap < 4:
                    somap+=1
            if button_map_giam.is_clicked(event):
                if somap>1:
                    somap-=1
            if button_level_tang.is_clicked(event):
                if level < 52:
                    level+=1
            if button_level_giam.is_clicked(event):
                if level >1:
                    level-=1
        hienthi()
        pygame.display.update()
pygame.font.init()

start_game()