levels = {
    0: {
        'name': 'Роддом 🤰',
        'doxod': 0
    },
    1: {
        'name': 'Саддик 👶',
        'doxod': 0
    },
    2: {
        'name': 'Саддик средняя группа 👦',
        'doxod': 0
    },
    3: {
        'name': 'Саддик Старшая група 📕',
        'doxod': 0
    },
    4: {
        'name': 'Школьник 🎒',
        'doxod': 0
    },
    5: {
        'name': '1⃣ Класс',
        'doxod': 0
    },
    6: {
        'name': '2️⃣ Класс',
        'doxod': 0
    },
    7: {
        'name': '3️⃣ Класс',
        'doxod': 0
    },
    8: {
        'name': '4️⃣ Класс',
        'doxod': 0
    },
    9: {
        'name': '5️⃣ Класс',
        'doxod': 0
    },
    10: {
        'name': '6️⃣ Класс',
        'doxod': 0
    },
    11: {
        'name': '7⃣ Класс',
        'doxod': 0
    },
    12: {
        'name': '8️⃣ Класс',
        'doxod': 0
    },
    13: {
        'name': '9️⃣ Класс',
        'doxod': 0
    },
    14: {
        'name': '🔟 Класс',
        'doxod': 0
    },
    15: {
        'name': '1⃣1⃣  Класс 👦',
        'doxod': 1000
    },
    16: {
        'name': '🏢 1-Курс',
        'doxod': 1000
    },
    17: {
        'name': '🏢 2-Курс',
        'doxod': 3000
    },
    18: {
        'name': '🏢 3-Курс',
        'doxod': 5000
    },
    19: {
        'name': '💓 Жизнь',
        'doxod': 0
    }
}

jobs = {
    1: {
        'name': '🕵️‍♂️ адвокат',
        'doxod': 120000,
        'level': 41
    },
    2: {
        'name': '🎪️ актер',
        'doxod': 90000,
        'level': 38
    },
    3: {
        'name': '🧑‍⚖️ Судья',
        'doxod': 85000,
        'level': 35
    },
    4: {
        'name': '👮 Мент',
        'doxod': 64500,
        'level': 32
    },
    5: {
        'name': '🧑‍🏫 Учитель',
        'doxod': 53500,
        'level': 29
    },
    6: {
        'name': '🪚 Автослесарь',
        'doxod': 42500,
        'level': 26
    },
    7: {
        'name': '👨‍🔬 Биолог',
        'doxod': 31500,
        'level': 23
    },
    8: {
        'name': '👨‍💻 Программист',
        'doxod': 20500,
        'level': 20
    }
}


class Job:
    def __init__(self, index: int):
        self.json = jobs[index]

        self.name: str = self.json['name']
        self.index = index
        self.doxod: int = self.json['doxod']
