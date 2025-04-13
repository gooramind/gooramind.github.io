import os, pygame, sys, random, time, math
from pygame.locals import *

# Pygame 초기화
pygame.init()

# 화면 설정
SCREEN_WIDTH = 144 * 4 # 화면 가로 크기 설정
SCREEN_HEIGHT = 288 * 3 # 화면 세로 크기 설정
fighter_sizeW = 50
fighter_sizeH = 50
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # 화면 생성

# 폰트 설정
font = pygame.font.Font(None, 30) # 일반 폰트 설정
final_font = pygame.font.Font(None, 50) # 일반 폰트 설정
gameover_font = pygame.font.Font(None, 80) # 게임 오버 폰트 설정

class GameObject:
    def __init__(self, x, y, image_path, size, colorkey=(0, 0, 0)):
        self.x = x # 객체의 x 좌표
        self.y = y # 객체의 y 좌표
        self.image = pygame.image.load(image_path).convert() # 이미지 로드 및 변환
        self.image = pygame.transform.scale(self.image, size) # 이미지 크기 조정
        self.image.set_colorkey(colorkey) # 특정 색상을 투명하게 설정

    def draw(self):
        screen.blit(self.image, (self.x, self.y)) # 객체를 화면에 그림

class Boss(GameObject):
    def __init__(self):
        super().__init__(random.randint(0, SCREEN_WIDTH - 150), -200, "image/boss.png", (150, 150), (255, 255, 255))
        self.hp = 500 # 보스의 체력
        self.atk = 500 # 보스의 공격력
        self.dy = 0.6 # 보스의 y축 이동 속도

    def move(self):
        self.y += self.dy # 보스를 아래로 이동

    def off_screen(self):
        return self.y > SCREEN_HEIGHT # 보스가 화면 밖으로 나갔는지 확인

    def touching(self, badguy):
        super_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        badguy_rect = pygame.Rect(badguy.x, badguy.y, badguy.image.get_width(), badguy.image.get_height())
        return super_rect.colliderect(badguy_rect) # 보스와 적이 충돌했는지 확인

class Badguy(GameObject):
    def __init__(self):
        super().__init__(random.randint(0, SCREEN_WIDTH - 70), -100, "image/badguy.png", (70, 70), (255, 255, 255))
        d = (math.pi / 2) * random.random() - (math.pi / 4) # 랜덤한 각도 생성
        speed = random.randint(2, 6) # 랜덤한 속도 생성
        self.dx = math.sin(d) * speed # x축 이동 속도
        self.dy = math.cos(d) * speed # y축 이동 속도
        self.hp = 20 # 적의 체력
        self.atk = 50 # 적의 공격력

    def move(self):
        if self.x < 0 or self.x > SCREEN_WIDTH - 70:
            self.dx *= -1 # 화면 경계에 닿으면 x축 이동 방향 반전
        self.x += self.dx # x축 이동
        self.dy += 0.1 # y축 이동 속도 증가
        self.y += self.dy # y축 이동

    def off_screen(self):
        return self.y > SCREEN_HEIGHT # 적이 화면 밖으로 나갔는지 확인

    def touching(self, missile):
        badguy_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        missile_rect = pygame.Rect(missile.x, missile.y, missile.image.get_width(), missile.image.get_height())
        return badguy_rect.colliderect(missile_rect) # 적과 미사일이 충돌했는지 확인

class MoonAttack(GameObject):
    def __init__(self, x, y):
        super().__init__(x-5, y, "image/moon.png", (30,30), (255, 255, 255))
        self.dy = 15 # y축 이동 속도
        self.atk = 10 # 공격력

    def move(self):
        self.y -= self.dy # 위로 이동

    def off_screen(self):
        return self.y < -30 # 화면 밖으로 나갔는지 확인

    def touching(self, target):
        moon_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        target_rect = pygame.Rect(target.x, target.y, target.image.get_width(), target.image.get_height())
        return moon_rect.colliderect(target_rect) # 충돌 여부 확인

class SuperAttack(GameObject):
    def __init__(self, x, y):
        super().__init__(x-50, y, "image/super.png", (50, 50), (255, 255, 255))
        self.dy = 10 # y축 이동 속도
        self.atk = 300 # 공격력

    def move(self):
        self.y -= self.dy # 위로 이동

    def off_screen(self):
        return self.y < -64 # 화면 밖으로 나갔는지 확인

    def touching(self, badguy):
        super_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        badguy_rect = pygame.Rect(badguy.x, badguy.y, badguy.image.get_width(), badguy.image.get_height())
        return super_rect.colliderect(badguy_rect) # 충돌 여부 확인

class Missile(GameObject):
    def __init__(self, x, y):
        super().__init__(x - 4, y, "image/missile.png", (10, 16), (255, 255, 255))
    
        self.atk = 10 # 공격력

    def move(self):
        self.y -= 5 # 위로 이동

    def off_screen(self):
        return self.y < -8 # 화면 밖으로 나갔는지 확인

class Heal(GameObject):
    def __init__(self, fighter):
        super().__init__(fighter.x, fighter.y, "image/heal.png", (160, 160), (255, 255, 255))
        self.fighter = fighter # 힐을 받는 전투기 객체
        self.active = False # 힐 활성화 여부
        self.start_time = 0 # 힐 시작 시간
        self.duration = 0.5 # 힐 지속 시간

    def activate(self):
        if not self.active:
            self.active = True
            self.start_time = time.time()
            self.fighter.hp += 50 # 전투기 체력 회복

    def deactivate(self):
        self.active = False # 힐 비활성화

    def draw(self):
        if self.active and time.time() - self.start_time < self.duration:
            screen.blit(self.image, (self.fighter.x - 50, self.fighter.y - 50)) # 힐 효과 그림
        elif self.active:
            self.deactivate() # 힐 지속 시간 종료 시 비활성화

class TrackingSuperAttack(GameObject):
    def __init__(self, x, y, target):
        super().__init__(x, y, "image/missile2.png", (50, 50), (0,0,0))
        self.dy = 10 # y축 이동 속도
        self.target = target # 추적 대상
        self.speed = 7 # 추적 속도

    def move(self):
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance != 0:
                self.x += self.speed * dx / distance # x축 추적 이동
                self.y += self.speed * dy / distance # y축 추적 이동
        else:
            self.y -= self.dy # 대상이 없으면 위로 이동

    def off_screen(self):
        return self.y < -64 # 화면 밖으로 나갔는지 확인

    def touching(self, target):
        super_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        target_rect = pygame.Rect(target.x, target.y, target.image.get_width(), target.image.get_height())
        return super_rect.colliderect(target_rect) # 충돌 여부 확인

class Fireball(GameObject):
    def __init__(self, fighter, offset_angle):
        radius = 60  # 전투기 중심으로 공전하는 거리
        angle = math.radians(offset_angle)
        x = fighter.x + fighter.image.get_width() // 2 + int(radius * math.cos(angle)) - 15  # 파이어볼 중심 조정
        y = fighter.y + fighter.image.get_height() // 2 + int(radius * math.sin(angle)) - 15 # 파이어볼 중심 조정
        super().__init__(x, y, "image/fireball.png", (30,30), (255,255,255))
        self.fighter = fighter
        self.offset_angle = offset_angle
        self.atk = 50

    def update_position(self):
        radius = 100
        angle = math.radians(self.offset_angle)
        self.x = self.fighter.x + self.fighter.image.get_width() // 2 + int(radius * math.cos(angle)) - 15
        self.y = self.fighter.y + self.fighter.image.get_height() // 2 + int(radius * math.sin(angle)) - 15

    def touching(self, target):
        fireball_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        target_rect = pygame.Rect(target.x, target.y, target.image.get_width(), target.image.get_height())
        return fireball_rect.colliderect(target_rect)
class Fighter(GameObject):
    def __init__(self):
        super().__init__(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, "image/fighter.png", (fighter_sizeH,fighter_sizeW), (0, 0, 0))
        self.hp = 100 # 전투기 체력
        self.atk = 10 # 전투기 공격력
        self.last_super_time = 0 # 마지막 슈퍼 공격 시간
        self.super_cooldown = 10 # 슈퍼 공격 쿨다운
        self.last_moon_time = 0 # 마지막 달 공격 시간
        self.moon_cooldown = 18 # 달 공격 쿨다운
        self.moon_active = False # 달 공격 활성화 여부
        self.moon_start_time = 0 # 달 공격 시작 시간
        self.shield = Shield(self) # 방어막 객체
        self.heal = Heal(self) # 힐 객체
        self.last_tracking_super_time = 0 # 마지막 추적 슈퍼 공격 시간
        self.tracking_super_cooldown = 8 # 추적 슈퍼 공격 쿨다운
        self.fireballs = []

    def touching(self, obj):
        fighter_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        obj_rect = pygame.Rect(obj.x, obj.y, obj.image.get_width(), obj.image.get_height())
        return fighter_rect.colliderect(obj_rect) # 충돌 여부 확인

    def move(self, keys):
        if keys[K_LEFT] and self.x > 0:
            self.x -= 7 # 왼쪽으로 이동
        if keys[K_RIGHT] and self.x < SCREEN_WIDTH - 50:
            self.x += 7 # 오른쪽으로 이동
        if keys[K_UP] and self.x > 0:
            self.y -= 7 # 위으로 이동
        if keys[K_DOWN] and self.x < SCREEN_HEIGHT - 100:
            self.y += 7 # 아래로 이동
    def fire(self, missiles):
        missiles.append(Missile(self.x + (fighter_sizeW/2), self.y)) # 미사일 발사

    def can_use_super(self):
        return time.time() - self.last_super_time > self.super_cooldown # 슈퍼 공격 쿨다운 확인

    def use_super(self, super_attacks):
        if self.can_use_super():
            super_attacks.append(SuperAttack(self.x + 50, self.y)) # 슈퍼 공격 발사
            self.last_super_time = time.time() # 마지막 슈퍼 공격 시간 갱신

    def can_use_moon(self):
        return time.time() - self.last_moon_time > self.moon_cooldown # 달 공격 쿨다운 확인

    def use_moon(self, moon_attacks):
        if self.can_use_moon():
            self.moon_active = True # 달 공격 활성화
            self.moon_start_time = time.time() # 달 공격 시작 시간 갱신
            self.last_moon_time = time.time() # 마지막 달 공격 시간 갱신

        if self.moon_active:
            if time.time() - self.moon_start_time < 5:
                moon_attacks.append(MoonAttack(self.x + 15, self.y)) # 달 공격 발사
            else:
                self.moon_active = False # 달 공격 비활성화

    def can_use_tracking_super(self):
        return time.time() - self.last_tracking_super_time > self.tracking_super_cooldown # 추적 슈퍼 공격 쿨다운 확인

    def use_tracking_super(self, tracking_super_attacks, badguys):
        if self.can_use_tracking_super() and badguys:
            closest_badguy = None
            closest_distance = float('inf')
            for badguy in badguys:
                distance = math.sqrt((badguy.x - self.x)**2 + (badguy.y - self.y)**2)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_badguy = badguy

            if closest_badguy:
                tracking_super_attacks.append(TrackingSuperAttack(self.x + 50, self.y, closest_badguy)) # 추적 슈퍼 공격 발사
                self.last_tracking_super_time = time.time() # 마지막 추적 슈퍼 공격 시간 갱신

    def update_fireballs(self):
        for i, fireball in enumerate(self.fireballs):
            fireball.offset_angle += 2  # 공전 속도 조절
            fireball.offset_angle %= 360
            fireball.update_position()

    def draw_fireballs(self):
        for fireball in self.fireballs:
            fireball.draw()

class Shield(GameObject):
    def __init__(self, fighter):
        super().__init__(fighter.x, fighter.y, "image/shield.png", (70, 70), (0,0,0))
        self.fighter = fighter # 방어막을 사용하는 전투기 객체
        self.active = False # 방어막 활성화 여부
        self.last_activation_time = 0 # 마지막 방어막 활성화 시간
        self.cooldown = 28 # 방어막 쿨다운
        self.image.set_alpha(80) # 방어막 투명도 설정

    def activate(self):
        if time.time() - self.last_activation_time > self.cooldown:
            self.active = True # 방어막 활성화
            self.last_activation_time = time.time() # 마지막 방어막 활성화 시간 갱신

    def deactivate(self):
        self.active = False # 방어막 비활성화

    def draw(self):
        if self.active:
            screen.blit(self.image, (self.fighter.x - 10, self.fighter.y - 10)) # 방어막 그림
class Game:
    def __init__(self):
        self.background = pygame.image.load("image/background.png").convert() # 배경 이미지 로드
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT)) # 배경 이미지 크기 조정
        self.fighter = Fighter() # 전투기 객체 생성
        self.badguys = [] # 적 객체 리스트
        self.missiles = [] # 미사일 객체 리스트
        self.bosses = [] # 보스 객체 리스트
        self.super_attacks = [] # 슈퍼 공격 객체 리스트
        self.score = 0 # 점수
        self.last_spawn_time = 0 # 마지막 적 생성 시간
        self.last_boss_time = time.time() # 마지막 보스 생성 시간
        self.game_over = False # 게임 오버 여부
        self.moon_attacks = [] # 달 공격 객체 리스트
        self.last_heal_score = 0 # 마지막 힐 점수
        self.moon_active_time = 0 # 달 공격 활성화 시간
        self.tracking_super_attacks = [] # 추적 슈퍼 공격 객체 리스트
        self.bg_y = 0 # 배경 y축 위치
        self.last_fireball_score = 0 # 마지막 파이어볼 생성 점수

class Game:
    def __init__(self):
        self.background = pygame.image.load("image/background.png").convert() # 배경 이미지 로드
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT)) # 배경 이미지 크기 조정
        self.fighter = Fighter() # 전투기 객체 생성
        self.badguys = [] # 적 객체 리스트
        self.missiles = [] # 미사일 객체 리스트
        self.bosses = [] # 보스 객체 리스트
        self.super_attacks = [] # 슈퍼 공격 객체 리스트
        self.score = 0 # 점수
        self.last_spawn_time = 0 # 마지막 적 생성 시간
        self.last_boss_time = time.time() # 마지막 보스 생성 시간
        self.game_over = False # 게임 오버 여부 추가 및 초기화
        self.moon_attacks = [] # 달 공격 객체 리스트
        self.last_heal_score = 0 # 마지막 힐 점수
        self.moon_active_time = 0 # 달 공격 활성화 시간
        self.tracking_super_attacks = [] # 추적 슈퍼 공격 객체 리스트
        self.bg_y = 0 # 배경 y축 위치
        self.last_fireball_score = 0 # 마지막 파이어볼 생성 점수
        self.paused = False # 일시 정지 상태 추가

    def reset(self):
        self.__init__() # 게임 초기화

    def run(self):
        clock = pygame.time.Clock() # 게임 클럭 생성
        while True:
            clock.tick(60) # 초당 60프레임으로 설정
            self.handle_events() # 이벤트 처리
            if not self.game_over and not self.paused: # 일시 정지 상태 확인
                self.update() # 게임 상태 업데이트
            self.render() # 화면 렌더링

    def handle_events(self):
        global pressed_keys
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit() # 게임 종료
            if event.type == KEYDOWN:
                if self.game_over and (event.key == K_RETURN or event.key == K_SPACE):
                    # 게임 오버 상태에서 엔터 또는 스페이스 키를 누르면 게임 재시작
                    self.reset()
                elif event.key == K_q and not self.game_over:
                    self.fighter.use_super(self.super_attacks) # 슈퍼 공격 사용
                elif event.key == K_w and not self.game_over:
                    self.fighter.use_moon(self.moon_attacks) # 달 공격 사용
                elif event.key == K_e and not self.game_over:
                    self.fighter.shield.activate() # 방어막 활성화
                elif event.key == K_r and not self.game_over and self.score >= 5000:
                    self.fighter.use_tracking_super(self.tracking_super_attacks, self.badguys) # 추적 슈퍼 공격 사용
                elif event.key == K_TAB: # TAB 키를 누르면
                    self.paused = not self.paused # 일시 정지 상태 토글
        pressed_keys = pygame.key.get_pressed() # 눌린 키 상태 저장
    def update(self):
        if self.score >= self.last_heal_score + 2000:
            self.fighter.heal.activate() # 힐 활성화
            self.last_heal_score = self.score # 마지막 힐 점수 갱신

        # 점수가 8000의 배수가 될 때마다 파이어볼 생성
        fireball_level = self.score // 8000
        num_fireballs = len(self.fighter.fireballs)
        if fireball_level > num_fireballs:
            for i in range(fireball_level - num_fireballs):
                offset_angle = i * (360 / fireball_level) if fireball_level > 0 else 0
                self.fighter.fireballs.append(Fireball(self.fighter, offset_angle))
        elif fireball_level < num_fireballs:
            self.fighter.fireballs = self.fighter.fireballs[:fireball_level]

        for moon_attack in self.moon_attacks[:]:
            moon_attack.move() # 달 공격 이동
            if moon_attack.off_screen():
                self.moon_attacks.remove(moon_attack) # 화면 밖으로 나가면 제거

        for tracking_super_attack in self.tracking_super_attacks[:]:
            tracking_super_attack.move() # 추적 슈퍼 공격 이동
            if tracking_super_attack.off_screen():
                self.tracking_super_attacks.remove(tracking_super_attack) # 화면 밖으로 나가면 제거
            for badguy in self.badguys[:]:
                if tracking_super_attack.touching(badguy):
                    self.badguys.remove(badguy) # 적 제거
                    self.tracking_super_attacks.remove(tracking_super_attack) # 추적 슈퍼 공격 제거
                    self.score += 400 # 점수 증가
                    break
            for boss in self.bosses[:]:
                if tracking_super_attack.touching(boss):
                    self.bosses.remove(boss) # 보스 제거
                    self.tracking_super_attacks.remove(tracking_super_attack) # 추적 슈퍼 공격 제거
                    self.score += 1000 # 점수 증가
                    break

        for moon_attack in self.moon_attacks[:]:
            for badguy in self.badguys[:]:
                if moon_attack.touching(badguy):
                    self.badguys.remove(badguy) # 적 제거
                    self.moon_attacks.remove(moon_attack) # 달 공격 제거
                    self.score += 300 # 점수 증가
                    break

        for moon_attack in self.moon_attacks[:]:
            for boss in self.bosses[:]:
                if moon_attack.touching(boss):
                    boss.hp -= moon_attack.atk # 보스 체력 감소
                    self.moon_attacks.remove(moon_attack) # 달 공격 제거
                    if boss.hp <= 0:
                        self.bosses.remove(boss) # 보스 제거
                        self.score += 2000 # 점수 증가
                    break

        for super_attack in self.super_attacks[:]:
            for badguy in self.badguys[:]:
                if super_attack.touching(badguy):
                    self.badguys.remove(badguy) # 적 제거
                    self.super_attacks.remove(super_attack) # 슈퍼 공격 제거
                    self.score += 200 # 점수 증가
                    break

        for super_attack in self.super_attacks[:]:
            for boss in self.bosses[:]:
                if super_attack.touching(boss):
                    boss.hp -= super_attack.atk # 보스 체력 감소
                    self.super_attacks.remove(super_attack) # 슈퍼 공격 제거
                    if boss.hp <= 0:
                        self.bosses.remove(boss) # 보스 제거
                        self.score += 1000 # 점수 증가
                    break

        for super_attack in self.super_attacks[:]:
            super_attack.move() # 슈퍼 공격 이동
            if super_attack.off_screen():
                self.super_attacks.remove(super_attack) # 화면 밖으로 나가면 제거

        if time.time() - self.last_spawn_time > 0.5:
            self.badguys.append(Badguy()) # 적 생성
            self.last_spawn_time = time.time() # 마지막 적 생성 시간 갱신

        if time.time() - self.last_boss_time > 10:
            self.bosses.append(Boss()) # 보스 생성
            self.last_boss_time = time.time() # 마지막 보스 생성 시간 갱신

        self.fighter.move(pressed_keys) # 전투기 이동
        self.fighter.update_fireballs() # 파이어볼 위치 업데이트

        for badguy in self.badguys[:]:
            badguy.move() # 적 이동
            if badguy.off_screen():
                self.badguys.remove(badguy) # 화면 밖으로 나가면 제거
            for fireball in self.fighter.fireballs:
                if fireball.touching(badguy):
                    self.badguys.remove(badguy)
                    self.score += 150
                    break

        for boss in self.bosses[:]:
            boss.move() # 보스 이동
            if boss.off_screen():
                self.bosses.remove(boss) # 화면 밖으로 나가면 제거
            for fireball in self.fighter.fireballs:
                if fireball.touching(boss):
                    boss.hp -= fireball.atk
                    if boss.hp <= 0:
                        self.bosses.remove(boss)
                        self.score += 1000
                    break

        for missile in self.missiles[:]:
            missile.move() # 미사일 이동
            if missile.off_screen():
                self.missiles.remove(missile) # 화면 밖으로 나가면 제거

        for badguy in self.badguys[:]:
            for missile in self.missiles[:]:
                if badguy.touching(missile):
                    badguy.hp -= missile.atk # 적 체력 감소
                    self.missiles.remove(missile) # 미사일 제거
                    if badguy.hp <= 0:
                        self.badguys.remove(badguy) # 적 제거
                        self.score += 100 # 점수 증가
                    break

        if not self.game_over and time.time() - getattr(self, 'last_missile_time', 0) > 0.15 and not self.fighter.moon_active:
            self.fighter.fire(self.missiles) # 미사일 발사
            self.last_missile_time = time.time() # 마지막 미사일 발사 시간 갱신

        for boss in self.bosses[:]:
            for missile in self.missiles[:]:
                if boss.touching(missile):
                    boss.hp -= missile.atk # 보스 체력 감소
                    self.missiles.remove(missile) # 미사일 제거
                    if boss.hp <= 0:
                        self.bosses.remove(boss) # 보스 제거
                        self.score += 500 # 점수 증가
                    break

        for badguy in self.badguys[:]:
            if self.fighter.touching(badguy):
                if self.fighter.shield.active:
                    self.fighter.shield.deactivate() # 방어막 비활성화
                    self.badguys.remove(badguy) # 적 제거
                else:
                    self.fighter.hp -= badguy.atk # 전투기 체력 감소
                    self.badguys.remove(badguy) # 적 제거
                    if self.fighter.hp <= 0:
                        self.game_over = True # 게임 오버

        for boss in self.bosses[:]:
            if self.fighter.touching(boss):
                self.fighter.hp -= boss.atk # 전투기 체력 감소
                self.bosses.remove(boss) # 보스 제거
                if self.fighter.hp <= 0:
                    self.game_over = True # 게임 오버

        self.bg_y += 1 # 배경 y축 이동
        if self.bg_y > SCREEN_HEIGHT:
            self.bg_y = 0 # 배경 y축 초기화

    def render(self):
        screen.blit(self.background, (0, self.bg_y)) # 배경 그림
        screen.blit(self.background, (0, self.bg_y - SCREEN_HEIGHT)) # 배경 그림 (반복)

        if not self.game_over:
            self.fighter.draw() # 전투기 그림
            self.fighter.shield.draw() # 방어막 그림
            self.fighter.heal.draw() # 힐 효과 그림
            self.fighter.draw_fireballs() # 파이어볼 그림
            for badguy in self.badguys:
                badguy.draw() # 적 그림
            for boss in self.bosses:
                boss.draw() # 보스 그림
            for missile in self.missiles:
                missile.draw() # 미사일 그림
            for super_attack in self.super_attacks:
                super_attack.draw() # 슈퍼 공격 그림
            for moon_attack in self.moon_attacks:
                moon_attack.draw() # 달 공격 그림

            score_text = font.render(f"Score: {self.score}", True, (255, 255, 255)) # 점수 텍스트 생성
            screen.blit(score_text, (5, 5)) # 점수 텍스트 그림
            hp_text = font.render(f"HP: {self.fighter.hp}", True, (255, 255, 255)) # 체력 텍스트 생성
            screen.blit(hp_text, (5, 25)) # 체력 텍스트 그림
            for tracking_super_attack in self.tracking_super_attacks:
                tracking_super_attack.draw() # 추적 슈퍼 공격 그림

            if self.score >= 5000:
                if not self.fighter.can_use_tracking_super():
                    remaining_time = self.fighter.tracking_super_cooldown - (time.time() - self.fighter.last_tracking_super_time) # 남은 쿨다운 시간 계산
                    ts_cooldown_text = font.render(f"Tracking Super: {remaining_time:.1f}", True, (255, 255, 255)) # 추적 슈퍼 공격 쿨다운 텍스트 생성
                    screen.blit(ts_cooldown_text, (5, 45)) # 추적 슈퍼 공격 쿨다운 텍스트 그림
                else:
                    ts_cooldown_text = font.render("Tracking Super: Ready", True, (0, 255, 0)) # 추적 슈퍼 공격 준비 완료 텍스트 생성
                    screen.blit(ts_cooldown_text, (5, 45)) # 추적 슈퍼 공격 준비 완료 텍스트 그림

            if not self.fighter.can_use_super():
                remaining_time = self.fighter.super_cooldown - (time.time() - self.fighter.last_super_time) # 남은 쿨다운 시간 계산
                s_cooldown_text = font.render(f"Super: {remaining_time:.1f}", True, (255, 255, 255)) # 슈퍼 공격 쿨다운 텍스트 생성
                screen.blit(s_cooldown_text, (SCREEN_WIDTH - 150, 5)) # 슈퍼 공격 쿨다운 텍스트 그림
            else:
                s_cooldown_text = font.render("Super: Ready", True, (0, 255, 0)) # 슈퍼 공격 준비 완료 텍스트 생성
                screen.blit(s_cooldown_text, (SCREEN_WIDTH - 150, 5)) # 슈퍼 공격 준비 완료 텍스트 그림

            if not self.fighter.can_use_moon():
                remaining_time = self.fighter.moon_cooldown - (time.time() - self.fighter.last_moon_time) # 남은 쿨다운 시간 계산
                m_cooldown_text = font.render(f"Moon: {remaining_time:.1f}", True, (255, 255, 255)) # 달 공격 쿨다운 텍스트 생성
                screen.blit(m_cooldown_text, (SCREEN_WIDTH - 150, 25)) # 달 공격 쿨다운 텍스트 그림
            else:
                m_cooldown_text = font.render("Moon: Ready", True, (0, 255, 0)) # 달 공격 준비 완료 텍스트 생성
                screen.blit(m_cooldown_text, (SCREEN_WIDTH - 150, 25)) # 달 공격 준비 완료 텍스트 그림

            if self.fighter.shield.active:
                shield_cooldown_text = font.render("Shield: Active", True, (65, 105, 225)) # 방어막 활성화 텍스트 생성
                screen.blit(shield_cooldown_text, (SCREEN_WIDTH - 150, 45)) # 방어막 활성화 텍스트 그림
            else:
                if self.fighter.shield.last_activation_time is None:
                    shield_cooldown_text = font.render(f"Shield: {self.fighter.shield.cooldown:.1f}", True, (255, 255, 255)) # 방어막 쿨다운 텍스트 생성
                else:
                    remaining_time = self.fighter.shield.cooldown - (time.time() - self.fighter.shield.last_activation_time) # 남은 쿨다운 시간 계산
                    remaining_time = max(0, remaining_time) # 남은 쿨다운 시간이 음수가 되지 않도록 함
                    shield_cooldown_text = font.render(f"Shield: {remaining_time:.1f}", True, (255, 255, 255)) # 방어막 쿨다운 텍스트 생성
                screen.blit(shield_cooldown_text, (SCREEN_WIDTH - 150, 45)) # 방어막 쿨다운 텍스트 그림

        if self.game_over:
            gameover_text = gameover_font.render("Game Over", True, (255, 0, 0)) # 게임 오버 텍스트 생성
            gameover_rect = gameover_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)) # 게임 오버 텍스트 위치 설정
            screen.blit(gameover_text, gameover_rect) # 게임 오버 텍스트 그림
            final_score_text = final_font.render(f"Final Score: {self.score}", True, (255, 255, 255)) # 최종 점수 텍스트 생성
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)) # 최종 점수 텍스트 위치 설정
            screen.blit(final_score_text, final_score_rect) # 최종 점수 텍스트 그림
            restart_text = font.render("Press Enter or Space to restart", True, (255, 255, 255)) # 재시작 안내 텍스트 생성
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)) # 재시작 안내 텍스트 위치 설정
            screen.blit(restart_text, restart_rect) # 재시작 안내 텍스트 그림
        pygame.display.update() # 화면 업데이트

if __name__ == "__main__":
    Game().run() # 게임 실행
    