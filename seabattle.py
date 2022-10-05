from random import randint


# Создаем класс точка
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # Сравниваем координаты точек
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot ({self.x}, {self.y})"


# Создаем собственные классы исключений
class BoardException(Exception):  # Общий класс, который будет содержать в себе все остальнные исключения
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUserException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


# Описываем конструктор корабля
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow  # Нос корабля
        self.l = l  # Длина корабля
        self.o = o  # Ориентация корабля
        self.lives = l  # hp корабля

    # Создаем метод Dots
    @property
    def dots(self):
        ships_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y  # Получаем список точек корабля

            if self.o == 0:
                cur_x += i  # Ориентация корабля по оси х
            elif self.o == 1:
                cur_y += 1  # Ориентация корабля по оси y

            ships_dots.append(Dot(cur_x, cur_y))

        return ships_dots  # Возвращаем размер корабля в виде списка, с указанием его положения по оси х или у

    def shooten(self, shot):  # Метод показывает попали ли к корабль или нет
        return shot in self.dots


# Описываем конструкцию игрового поля
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size  # Размер поля
        self.hid = hid  # Видимость поля
        self.count = 0  # Переменная по учету количества пораженных кораблей

        self.field = [["O"] * size for _ in range(size)]  # Сетка значений

        self.busy = []  # Список занятых точек
        self.ships = []  # Список кораблей

    def __str__(self):  # Вывод корабля на доску
        res = ""
        res += "   | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n {i + 1} | " + " | ".join(row) + " |"
        if self.hid:  # Скрывает корабли на доске
            res = res.replace("■", "O")
        return res

    def out(self, d):  # Метод определяет, находится ли точка за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # Описываем конструкцию формирования контура корабля и добавление его на доску
    def countour(self, ship, verb=False):  # Метод который занимает все точки рядом с кораблем
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "+"
                    self.busy.append(cur)

    def add_ship(self, ship):  # Проверка расположения точки в пределах границы поля или не занята
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()  # Исключение занятых точек(мест)
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.countour(ship)

    # Метод который делает выстрел по доске
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()  # Исключение, выходит ли выстрел за границы поля

        if d in self.busy:
            raise BoardUserException()  # Исключение, о занятой точке(месте)

        self.busy.append(d)

        for ship in self.ships:  # Цикл проверки принадлежности точки к кораблю
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.countour(ship, verb=True)
                    print("Корабль уничтожен")
                else:
                    print("Корабль ранен")
                    return True
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):  # Обнуляем список busy для точек куда стрелял игрок
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


# Класс игрока
class Player:
    def __init__(self, board, enemy):  # Передаем в качесве аргумента две доски
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):  # Выстрел
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


# Классы "Игрок-компьютер" "Игрок-пользователь"
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1}{d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()  # Запрос координат
            if len(cords) != 2:
                print("Введите две координаты!!! ")
                continue
            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)  # Вывод пользователю списка "1", а не "0"


# Класс "Игра и генерация досок"
class Game:
    def __init__(self, size=6):  # Данные для генерации досок для компьютера и для игрока
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True  # скрывает корабли для компьтера

        self.ai = AI(co, pl)  # Игрок ИИ
        self.us = User(pl, co)  # Игрок пользователь

    def try_board(self):  # Создание доски. Растановка кораблей
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:  # Исключение по растановке кораблей
                    pass
        board.begin()
        return board

    def random_board(self):  # Метод который гарантировано генерирует случайную доску
        board = None
        while board is None:
            board = self.try_board()
        return board

    # Конструктор прветствия
    def greet(self):
        print("----------------")
        print("Приветствуем Вас")
        print("     в игре     ")
        print("  морской бой   ")
        print("--------------- ")
        print("Формат ввода: ху ")
        print("х - номер строки ")
        print("у - номер стобца ")

    # Игровой цикл
    def loop(self):
        num = 0  # Номер хода
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьтера:")
            print(self.ai.board)
            print("-" * 20)

            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()

            if repeat:  # Повтор хода при поадании в корабль
                num -= 1

            if self.ai.board.defeat():
                print("-" * 20)
                print("Пользователь выйграл!")
                break

            if self.us.board.defeat():
                print("-" * 20)
                print("Компьтер выйграл!")
                break
            num += 1

    # Метод Start
    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
