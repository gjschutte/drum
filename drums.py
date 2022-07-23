# Build your own drum beat maker
from re import L
import pygame
from pygame import mixer
import json
pygame.init()

WIDTH = 1400
HEIGHT = 800


black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)
light_grey = (170, 170, 170)
dark_gray = (50, 50, 50)
green = (0, 255, 0)
gold = (212, 175, 55)
blue = (0, 255, 255)

screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Beat Maker')
label_font = pygame.font.Font('Roboto-Bold.ttf', 32)
medium_font = pygame.font.Font('Roboto-Bold.ttf', 24)

index = 100
fps = 60 # Frame-rate, 60 times per second
timer = pygame.time.Clock()
beats = 8
instruments = 6
boxes = []
clicked = [[-1 for _ in range(beats)] for _ in range(instruments)]
active_list = [1 for _ in range(instruments)]
bpm = 240
playing = True
active_length = 0
active_beat = 1
beat_changed = True
save_menu = False
load_menu = False
saved_beats = []
# svd_beats = []
# file = open('saved_beats.txt', 'r')
# for line in file:
#    saved_beats.append(line)
# print(saved_beats)
beat_name = ''
typing = False
with open("saved_beats.txt", 'r') as read_beats:
    for line in read_beats:
        saved_beats.append(json.loads(line))

# Load in sounds
hi_hat = mixer.Sound('sounds/hi_hat.wav')
snare = mixer.Sound('sounds/snare.wav')
kick = mixer.Sound('sounds/kick.wav')
crash = mixer.Sound('sounds/crash.wav')
clap = mixer.Sound('sounds/clap.wav')
tom = mixer.Sound('sounds/tom.wav')
pygame.mixer.set_num_channels(instruments * 3)


def play_notes():
    for i in range(len(clicked)):
        if clicked[i][active_beat] == 1 and active_list[i] == 1:
            if i == 0:
                hi_hat.play()
            if i == 1:
                snare.play()
            if i == 2:
                kick.play()
            if i == 3:
                crash.play()
            if i == 4:
                clap.play()
            if i == 5:
                tom.play()

def draw_grid(clicks, beat, actives):
    left_box = pygame.draw.rect(screen, gray, [0, 0, 200, HEIGHT - 200], 5)
    bottom_box = pygame.draw.rect(screen, gray, [0, HEIGHT - 200, WIDTH, 200], 5)
    boxes = []
    colors = [gray, white, gray]
    hi_hat_text = label_font.render('Hi Hat', True, colors[actives[0]]) # Color depends of index of active
    screen.blit(hi_hat_text, (30, 30))
    snare_text = label_font.render('Snare', True, colors[actives[1]])
    screen.blit(snare_text, (30, 130))
    kick_text = label_font.render('Bass Drum', True, colors[actives[2]])
    screen.blit(kick_text, (30, 230))
    crash_text = label_font.render('Crash', True, colors[actives[3]])
    screen.blit(crash_text, (30, 330))
    clap_text = label_font.render('Clap', True, colors[actives[4]])
    screen.blit(clap_text, (30, 430))
    floor_text = label_font.render('Floor Tom', True, colors[actives[5]])
    screen.blit(floor_text, (30, 530))
    for i in range(instruments):
        pygame.draw.line(screen, gray, (0, (i * 100) + 100), (200, (i * 100) + 100), 3)

    for i in range(beats):
        for j in range(instruments):
            if clicks[j][i] == -1:
                color = gray
            else:
                if actives[j] == 1: 
                    color = green
                else:
                    color = dark_gray
            rect = pygame.draw.rect(screen, color, 
               [i * ((WIDTH - 200) // beats) + 200, (j * 100) + 5, ((WIDTH - 200) // beats) - 10, 
               ((HEIGHT - 200) // instruments) - 10], 0, 3)
            pygame.draw.rect(screen, gold, 
               [i * ((WIDTH - 200) // beats) + 200, (j * 100), ((WIDTH - 200) // beats), 
               ((HEIGHT - 200) // instruments)], 5, 5)
            pygame.draw.rect(screen, black, 
               [i * ((WIDTH - 200) // beats) + 200, (j * 100), ((WIDTH - 200) // beats), 
               ((HEIGHT - 200) // instruments)], 2, 5)
            boxes.append((rect, (i, j)))
        active = pygame.draw.rect(screen, blue, [beat * ((WIDTH - 200) // beats) + 200, 0, ((WIDTH - 200) // beats), instruments * 100], 5, 3)
    return boxes

def draw_save_menu(beat_name, typing):
    pygame.draw.rect(screen, black, [0, 0, WIDTH, HEIGHT])
    menu_text = label_font.render('SAVE MENU: Enter a name for current beat:', True, white)
    screen.blit(menu_text, (400, 40))
    saving_btn = pygame.draw.rect(screen, gray, [WIDTH // 2 - 200, HEIGHT * 0.75, 400, 100], 0, 5)
    saving_txt = label_font.render('Save Beat', True, white)
    screen.blit(saving_txt, (WIDTH // 2 - 70, HEIGHT * 0.75 + 30))
    exit_btn = pygame.draw.rect(screen, gray, [WIDTH - 200, HEIGHT - 100, 180, 90], 0, 5)
    exit_text = label_font.render('Close', True, white)
    screen.blit(exit_text, (WIDTH - 160, HEIGHT - 70))
    if typing:
        pygame.draw.rect(screen, dark_gray, [400, 200, 600, 200], 0, 5)
    entry_rect = pygame.draw.rect(screen, gray, [400, 200, 600, 200], 5, 5)
    entry_text = label_font.render(f'{beat_name}', True, white)
    screen.blit(entry_text, (430, 250))
    return exit_btn, saving_btn, entry_rect

def draw_load_menu(index):
    loaded_clicked = []
    loaded_beats = 0
    loaded_bpm = 0
    pygame.draw.rect(screen, black, [0, 0, WIDTH, HEIGHT])
    menu_text = label_font.render('LOAD MENU: Select A Beat To Load:', True, white)
    screen.blit(menu_text, (400, 40))
    loading_btn = pygame.draw.rect(screen, gray, [WIDTH // 2 - 200, HEIGHT * 0.87, 400, 100], 0, 5)
    loading_txt = label_font.render('Load Beat', True, white)
    screen.blit(loading_txt, (WIDTH // 2 - 70, HEIGHT * 0.87 + 30))
    delete_btn = pygame.draw.rect(screen, gray, [WIDTH // 2 - 500, HEIGHT * .87, 200, 100], 0, 5)
    delete_text = label_font.render('Delete Beat', True, white)
    screen.blit(delete_text, (WIDTH // 2 - 485, HEIGHT * .87 + 30))
    exit_btn = pygame.draw.rect(screen, gray, [WIDTH - 200, HEIGHT - 100, 180, 90], 0, 5)
    exit_text = label_font.render('Close', True, white)
    screen.blit(exit_text, (WIDTH - 160, HEIGHT - 70))
    loaded_rectangle = pygame.draw.rect(screen, gray, [190, 90, 1000, 600], 5, 5)
    if 0 <= index < len(saved_beats):
        pygame.draw.rect(screen, light_grey, [190, 100 + index * 50, 1000, 50])
    for beat in range(len(saved_beats)):
        if beat < 10:
            beat_clicked = []
            row_text = medium_font.render(f'{beat + 1}', True, white)
            screen.blit(row_text, (200, 100 + beat * 50))
            name_text = medium_font.render(saved_beats[beat]['name'], True, white)
            screen.blit(name_text, (240, 100 + beat * 50))
        if 0 <= index < len(saved_beats) and beat == index:
            loaded_beats = saved_beats[beat]['beats']
            loaded_bpm = saved_beats[beat]['bpm']
            loaded_clicked = saved_beats[beat]['selected']
    loaded_info = [loaded_beats, loaded_bpm, loaded_clicked]
    return exit_btn, loading_btn, delete_btn, loaded_rectangle, loaded_info

def save_function(beat_array):
    with open('saved_beats.txt', 'w') as json_file:
        for i in range(len(beat_array)):
            json.dump(beat_array[i], json_file)
            if i < (len(beat_array) - 1):
                json_file.write('\n')

run = True
while run:
    timer.tick(fps)
    screen.fill(black)
    boxes = draw_grid(clicked, active_beat, active_list)
    # Lower menu buttons
    play_pause = pygame.draw.rect(screen, gray, [50, HEIGHT - 150, 200, 100], 0, 5)
    play_text = label_font.render('Play/Pause', True, white)
    screen.blit(play_text, (70, HEIGHT - 130))
    if playing: 
        play_text2 = medium_font.render('Playing', True, dark_gray)
    else: 
        play_text2 = medium_font.render('Paused', True, dark_gray)
    screen.blit(play_text2, (70, HEIGHT - 100))
    # BPM stuff
    bpm_rect = pygame.draw.rect(screen, gray, [300, HEIGHT - 150, 200, 100], 5, 5)
    bpm_text = medium_font.render('Beats Per Minute', True, white)
    screen.blit(bpm_text, (308, HEIGHT - 130))
    bpm_text2 = label_font.render(f'{bpm}', True, white)
    screen.blit(bpm_text2, (370, HEIGHT - 100))
    bpm_add_rect = pygame.draw.rect(screen, gray, [510, HEIGHT - 150, 48, 48], 0, 5)
    bpm_sub_rect = pygame.draw.rect(screen, gray, [510, HEIGHT - 100, 48, 48], 0, 5)
    add_text = medium_font.render('+5', True, white)
    sub_text = medium_font.render('-5', True, white)
    screen.blit(add_text, (520, HEIGHT - 140))
    screen.blit(sub_text, (520, HEIGHT - 90))
    # Beats stuff
    beats_rect = pygame.draw.rect(screen, gray, [600, HEIGHT - 150, 200, 100], 5, 5)
    beats_text = medium_font.render('Beats In Loop', True, white)
    screen.blit(beats_text, (618, HEIGHT - 130))
    beats_text2 = label_font.render(f'{beats}', True, white)
    screen.blit(beats_text2, (680, HEIGHT - 100))
    beats_add_rect = pygame.draw.rect(screen, gray, [810, HEIGHT - 150, 48, 48], 0, 5)
    beats_sub_rect = pygame.draw.rect(screen, gray, [810, HEIGHT - 100, 48, 48], 0, 5)
    add_text2 = medium_font.render('+1', True, white)
    sub_text2 = medium_font.render('-1', True, white)
    screen.blit(add_text2, (820, HEIGHT - 140))
    screen.blit(sub_text2, (820, HEIGHT - 90))
    # Instruments rects. Not showing on the screen, just for clicking
    instrments_rects = []
    for i in range(instruments):
        rect = pygame.rect.Rect((0, i * 100), (200, 100))
        instrments_rects.append(rect)
    # Save and load stuff
    save_button = pygame.draw.rect(screen, gray, [900, HEIGHT - 150, 200, 48], 0, 5)
    save_text = label_font.render('Save beat', True, white)
    screen.blit(save_text, (920, HEIGHT - 140))
    load_button = pygame.draw.rect(screen, gray, [900, HEIGHT - 100, 200, 48], 0, 5)
    load_text = label_font.render('Load beat', True, white)
    screen.blit(load_text, (920, HEIGHT - 90))

    # Clear board
    clear_button = pygame.draw.rect(screen, gray, [1150, HEIGHT - 150, 200, 100], 0, 5)
    clear_text = label_font.render('Clear Board', True, white)
    screen.blit(clear_text, (1160, HEIGHT - 120))

    if save_menu:
        exit_button, saving_button, entry_rectangle = draw_save_menu(beat_name, typing)
    if load_menu:
        exit_button, loading_button, delete_button, loaded_rectangle, loaded_info = draw_load_menu(index)

    if beat_changed:
        play_notes()
        beat_changed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not save_menu and not load_menu:
            for i in range(len(boxes)):
                if boxes[i][0].collidepoint(event.pos):
                    coords = boxes[i][1]
                    clicked[coords[1]][coords[0]] *= -1
        if event.type == pygame.MOUSEBUTTONUP and not save_menu and not load_menu:
            if play_pause.collidepoint(event.pos):
                if playing:
                    playing = False
                elif not playing:
                    playing = True
            elif bpm_add_rect.collidepoint(event.pos):
                bpm += 5
            elif bpm_sub_rect.collidepoint(event.pos):
                bpm -= 5
            elif beats_add_rect.collidepoint(event.pos):
                beats += 1
                for i in range(len(clicked)):
                    clicked[i].append(-1) # -1 means at the end
            elif beats_sub_rect.collidepoint(event.pos):
                beats -= 1
                for i in range(len(clicked)):
                    clicked[i].pop(-1) # -1 means at the end
            elif clear_button.collidepoint(event.pos):
                clicked = [[-1 for _ in range(beats)] for _ in range(instruments)]
            elif save_button.collidepoint(event.pos):
                save_menu = True
            elif load_button.collidepoint(event.pos):
                load_menu = True
            for i in range(len(instrments_rects)):
                if instrments_rects[i].collidepoint(event.pos):
                    active_list[i] *= -1
        elif event.type == pygame.MOUSEBUTTONUP: # load or saved clicked
            if exit_button.collidepoint(event.pos):
                save_menu = False
                load_menu = False
                playing = True
                beat_name = ''
                typing = False
            if load_menu:
                if loaded_rectangle.collidepoint(event.pos):
                    index = (event.pos[1] - 100) // 50
                if delete_button.collidepoint(event.pos):
                    if 0 <= index < len(saved_beats):
                        saved_beats.pop(index)
                        save_function(saved_beats)
                if loading_button.collidepoint(event.pos):
                    if 0 <= index < len(saved_beats):
                        beats = loaded_info[0]
                        bpm = loaded_info[1]
                        clicked = loaded_info[2]
                        index = 100
                        load_menu = False
            if save_menu:
                if entry_rectangle.collidepoint(event.pos):
                    if typing:
                        typing = False
                    elif not typing:
                        typing = True
                if saving_button.collidepoint(event.pos):
                    beat_to_save = {
                        "name": beat_name,
                        "beats": beats,
                        "bpm": bpm,
                        "selected": clicked,
                    }
                    saved_beats.append(beat_to_save)
                    save_function(saved_beats)
                    save_menu = False
                    typing = False
                    beat_name = ''
        if event.type == pygame.TEXTINPUT and typing:
            beat_name += event.text
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and len(beat_name) > 0 and typing:
                beat_name = beat_name[:-1] # whole string minus last character


    beat_length = 3600 // bpm # 3600 = fps * 60 (seconds)

    if playing:
        if active_length < beat_length:
            active_length += 1
        else:
            active_length = 0
            if active_beat < beats - 1:
                active_beat += 1
                beat_changed = True
            else:
                active_beat = 0
                beat_changed = True


    pygame.display.flip()
pygame.quit()

