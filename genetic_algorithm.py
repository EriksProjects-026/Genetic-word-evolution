import random
import sys
import time

TARGET = "ХОЧУ В ЦЕНТРАЛЬНЫЙ УНИВЕРСИТЕТ"
ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ "             # КОНСТАНТЫ

POPULATION_SIZE = 200          # размер популяции
ELITE_SIZE = 5                 # сколько лучших переходят без изменений
TOURNAMENT_SIZE = 15           # сколько особей участвуют в турнире за родителя

MUTATION_RATE_NORMAL = 0.01    # обычный шанс мутации (1%)
MUTATION_RATE_STAGNATION = 0.05  # повышенный шанс при стагнации(когда из поколения в поколение не происходит изменений) (5%)
STAGNATION_LIMIT = 30          # поколений без улучшения до повышения мутации

ATTEMPTS_PER_SECOND = 1_000_000  # допущение для расчёта времени ( когда сравнивать будем перебор с нашим ии)
SECONDS_IN_YEAR = 31_536_000     # 365 * 24 * 60 * 60

GREEN = "\033[92m"   # зелёный цвет для совпавших букв
RESET = "\033[0m"    # сброс цвета в терминале

def setup_console():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass        #просто что бы командная строка винды не шалила и использовала utf-8 а то подсветка текста и смайлики могут не выводится, ну и чтобы ошибки глупые фильтровать если вдруг совместимости не будет

def create_random_individual(length, alphabet):
    individual = ""
    for _ in range(length):
        individual += random.choice(alphabet)
    return individual    #создает нам случайных особей, 1 переменная длина строки(будет 30) 2 это алфавит

def calculate_fitness(individual, target):
    score = 0
    for i in range(len(target)):
        if individual[i] == target[i]:
            score += 1
    return score   #эта функция считает насколько особи приспособленны, на русском писать кринж а переводчик перевел приспособленный как фитнес) score это наш индекс приспособленности

def format_colored(individual, target):
    result = ""
    for i in range(len(target)):
        if individual[i] == target[i]:
            result += GREEN + individual[i] + RESET
        else:
            result += individual[i]
    return result   # перекрашивает совпавшие буковки в зеленый чтобы красиво было, грин и ресет константы сравнивает полученую 1 аргументом строку с другой строкой(с нашей целью)

def create_initial_population(size, length, alphabet):
    population = []
    for _ in range(size):
        individual = create_random_individual(length, alphabet)
        population.append(individual)
    return population       # генерит нашу первую популяцию пока что глупеньких особей ( рандомные фразы) аргументы размер списка, длина строки, то откуда брать буквы)

def evaluate_population(population, target):
    fitnesses = []
    for individual in population:
        fitness = calculate_fitness(individual, target)
        fitnesses.append(fitness)
    return fitnesses    # оценивает качество нашей популяции, возвращая списочек с оценкой особей(int) в том же порядке в котором они и стояли

def get_best(population, fitnesses):
    best_index = 0
    best_fitness = fitnesses[0]

    for i in range(1, len(fitnesses)):
        if fitnesses[i] > best_fitness:
            best_fitness = fitnesses[i]
            best_index = i

    best_string = population[best_index]
    return best_string, best_fitness, best_index          # считает и находит альфа-самца и выводит его(строчку) его оценку(фитнес этот) и его индекс


def get_elite(population, fitnesses, count):
    ranked = []
    for i in range(len(population)):
        ranked.append((fitnesses[i], population[i]))    #сортируем список лучших, добавляя туда кортеж с оценкой строки и строкой

    ranked.sort(reverse=True)

    elite = []
    seen = set()

    for fitness, individual in ranked:
        if individual not in seen:
            elite.append(individual)
            seen.add(individual)
        if len(elite) == count:
            break

    return elite       #здесь мы создаем последовательный список топ 5 самых лучших при это цикл откидывает дубликаты, я добавил множество seen потому что множества мгновенно проверятся на наличие(in not in) а списки линейно (Big 0(n) а множество - Big O(1)), да здесь не значительно но я хотел показать что шарю не зря же книги читал по алгоритмам

def select_parent(population, fitnesses, tournament_size):
    indices = random.sample(range(len(population)), tournament_size)

    best_index = indices[0]
    best_fitness = fitnesses[best_index]

    for index in indices[1:]:
        if fitnesses[index] > best_fitness:
            best_fitness = fitnesses[index]
            best_index = index

    return population[best_index]  # выбираем индексы без повторений и из этих участников выбираем самого сильного (турнирный отбор прям как в эволюции)

def crossover(parent1, parent2):
    cut_point = random.randint(1, len(parent1) - 1)
    child = parent1[:cut_point] + parent2[cut_point:]
    return child     #скрещивает родителей(победители турнира) и делай рандомных детей от первого и второго родителя с помощью среза - получаем новую строку уникальную почти

def mutate(individual, alphabet, rate):
    chars = list(individual)

    for i in range(len(chars)):
        if random.random() < rate:
            chars[i] = random.choice(alphabet)

    return "".join(chars) #из строки делаем список там проверяем если прокнул шанс в 1% то заменяем букву на рандомный символ из алфавита потом склеиваем в строку и возвращаем ее

def create_next_generation(population, fitnesses, alphabet, mutation_rate):
    new_population = []

    # Шаг 1: элита — топ-5 лучших переходят как есть
    elite = get_elite(population, fitnesses, ELITE_SIZE)
    for individual in elite:
        new_population.append(individual)

    # Шаг 2: добираем популяцию потомками
    while len(new_population) < POPULATION_SIZE:
        parent1 = select_parent(population, fitnesses, TOURNAMENT_SIZE)
        parent2 = select_parent(population, fitnesses, TOURNAMENT_SIZE)

        child = crossover(parent1, parent2)
        child = mutate(child, alphabet, mutation_rate)

        new_population.append(child)

    return new_population #создаем новую популяцию, сначала перегонем туда элиту, потом уже выбираем родителей делаем детей и даем им возможность мутировать

def format_time_human(seconds):
    if seconds < 60:
        return f"{seconds:.2f} секунд"
    if seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} минут"
    if seconds < SECONDS_IN_YEAR:
        hours = seconds / 3600
        return f"{hours:.2f} часов"

    years = seconds / SECONDS_IN_YEAR
    if years < 1_000_000:
        return f"{years:.6f} лет"
    return f"{years:.2e} лет"              #переводим время в понятные человеку еденицы измерения, чтобы можно было сравнить насколько мой ии обганяет ленейный перебор


def print_record(generation, individual, target, fitness):
    time.sleep(0.5)
    colored = format_colored(individual, target)
    target_length = len(target)
    print(f"Поколение {generation}: {colored}  (fitness: {fitness}/{target_length})")   #выписываем новый рекорд в терминал для отслежвания процесса, основной функционал как бы


def print_victory(individual, generation):
    time.sleep(0.5)
    print()
    print(f"🎉🏆 {individual} 🎉🏆")
    print(f"Фраза полностью собрана на поколении {generation}!")
    print()        # ура мы наконец эволюционировали и выводим факт о нашей победе в эволюции

def print_complexity_analysis(generations, population_size, alphabet_size, target_length):
    #Случайный перебор: O(A^L) должен быть O(n^n) но это обстрактный пример ( я читал в книге что незаписываются в о большое всякие множители  ток константы) но так гораздо нагляднее и мы получаем ответ в секундах
    random_attempts = alphabet_size ** target_length
    random_seconds = random_attempts / ATTEMPTS_PER_SECOND
    random_years = random_seconds / SECONDS_IN_YEAR

    #Генетический алгоритм: O(G × P × L) тоже самое что и в первом случае, хочу наглядно показать
    ga_operations = generations * population_size * target_length
    ga_seconds = ga_operations / ATTEMPTS_PER_SECOND
    ga_years = ga_seconds / SECONDS_IN_YEAR

    print("=" * 50)
    print("  СРАВНЕНИЕ СЛОЖНОСТИ АЛГОРИТМОВ")
    print("=" * 50)
    print()

    print("1) Случайный перебор — O(A^L)")
    print(f"   Формула:  O({alphabet_size}^{target_length})")
    print(f"   Попыток:  {random_attempts:,}")
    print(f"             (≈ {random_attempts:.2e})")
    print(f"   При {ATTEMPTS_PER_SECOND:,} попыток/сек:")
    print(f"   Время:    ≈ {format_time_human(random_seconds)}")
    print(f"             (≈ {random_years:.2e} лет)")
    print(f"             (возраст Вселенной ≈ 1.4 × 10^10 лет)")
    print()

    print("2) Генетический алгоритм — O(G × P × L)")
    print(f"   Формула:  O({generations} × {population_size} × {target_length}) "
          f"= O({ga_operations:,})")
    print(f"   Операций: {ga_operations:,}")
    print(f"   При той же скорости ({ATTEMPTS_PER_SECOND:,} оп/сек):")
    print(f"   Время:    ≈ {format_time_human(ga_seconds)} (≈ {ga_years:.2e} лет)")
    print()

    print("-" * 50)
    print("Рандомной подстановке потребовалось бы")
    print(f"~{random_attempts:.2e} попыток (~{random_years:.2e} лет),")
    print(f"а наша эволюция справилась за {generations} поколений")
    print(f"(~{ga_operations:,} операций, ~{format_time_human(ga_seconds)})!")
    print("=" * 50)
#  Красивый вывод, люблю такое

def run_evolution(target, alphabet):
    target_length = len(target)

    # Создаём начальную популяцию из 200 случайных особей
    population = create_initial_population(POPULATION_SIZE, target_length, alphabet)

    # Первая строка — для баннера «от [...] до [...]»
    first_random = population[0]
    print(f"ЭВОЛЮЦИЯ: от {first_random} до {target}")
    print()

    # Состояние алгоритма
    best_fitness = -1
    generations_without_improvement = 0
    current_mutation_rate = MUTATION_RATE_NORMAL

    generation = 0

    while True:
        # Оцениваем всё поколение
        fitnesses = evaluate_population(population, target)
        best_string, best_fitness_now, _ = get_best(population, fitnesses)

        # Если fitness вырос — это новый рекорд, показываем прогресс
        if best_fitness_now > best_fitness:
            best_fitness = best_fitness_now
            print_record(generation, best_string, target, best_fitness_now)
            generations_without_improvement = 0
            current_mutation_rate = MUTATION_RATE_NORMAL
        else:
            # Рекорд не бился — считаем стагнацию
            generations_without_improvement += 1

        # Полная победа — все буквы на месте
        if best_fitness_now == target_length:
            print_victory(best_string, generation)
            return generation

        # 30 поколений без роста — временно повышаем мутацию до 5%
        if generations_without_improvement >= STAGNATION_LIMIT:
            current_mutation_rate = MUTATION_RATE_STAGNATION

        # Формируем следующее поколение
        population = create_next_generation(
            population, fitnesses, alphabet, current_mutation_rate
        )

        generation += 1 #главная функция где мы из всех функций сделали последовательность,  делаем первое поколение потом цикл где мы оцениваем и если надо выводим лучшего в поколении и и если совпадение 30 из 30 символов - победа! а так дальше цикл идет и растет счетчик стагнации если не было изменений лучших показателей, + счетчик поколений возвращает количество поколений на победном поколении


def main():
    setup_console()
    generations = run_evolution(TARGET, ALPHABET)

    print_complexity_analysis(
        generations=generations,
        population_size=POPULATION_SIZE,
        alphabet_size=len(ALPHABET),
        target_length=len(TARGET),
    )
#наша главная функция, собираем и запускаем код

if __name__ == "__main__":     # хоть этот файл никуда не импортируется, я все равно решил добавить эту команду, вдруг его кто то будет импортировать и код запуститься,
    main()                      # да и вообще это правильно вроде писать эту команду, чтобы запускалась то по нажатию кнопки. Здесь хоть и не нужно я стараюсь с самого начала прививать себе то, как правильно писать код, чтобы он потом легко маштабировался и т.д.




































































































































































































































































































