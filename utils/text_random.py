# -*- coding: utf-8 -*-
import random
import pymorphy2

# Initialize the morphological analyzer
morph = pymorphy2.MorphAnalyzer()


def generate_random_text():
    templates = [
        "🗨️ Расскажите друзьям об этом {промокоде|коде|специальном предложении}, и получите замечательные возможности улучшить свои средства! 💫",
        "🗨️ Не забудьте поделиться этим {промокодом|кодом|купоном|бонусом} с {семьей|друзьями|близкими|знакомыми}, и вы получите уникальный шанс улучшить свои финансы! 💫",
        "🗨️ Расскажите всем об этом {промокоде|коде|специальном предложении}, и вы получите замечательные возможности улучшить свои средства! 💫",
        "🗨️ Разделитесь этим {промокодом|кодом|купоном} с {друзьями|близкими|подругами|коллегами}, и получите отличные возможности улучшить свой капитал! 💫",
        "🗨️ Не пропустите это {промо-код|купон|специальное предложение}, поделитесь с {близкими|друзьями|родными}, и у вас появится уникальный шанс увеличить свои сбережения! 💫",
        "🗨️ Расскажите о {промокоде|коде|специальном предложении} своим {коллегам|знакомым|подругам}, и они также смогут волшебным образом улучшить свои финансы! 💫",
        # Add more templates with alternatives...
    ]
    template = random.choice(templates)
    while '{' in template:
        start = template.find('{')
        end = template.find('}')
        options = template[start + 1:end].split('|')
        chosen_option = random.choice(options)
        template = template[:start] + chosen_option + template[end + 1:]
    return template
