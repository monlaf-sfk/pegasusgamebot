from aiogram.types import Message

from utils.main.db import sql


class Minesweeper:
    @staticmethod
    def create(game_id, user_id, field_size, victory):
        res = (game_id, user_id, field_size, victory)
        sql.insert_data([res], 'minesweeper')
        return True

    @staticmethod
    def show_stats(message: Message):
        """
        Get player personal statistics

        """
        game_data = sql.select_data(table='minesweeper', title='user_id', name=message.from_user.id, row_factor=False)
        if len(game_data) == 0:
            return "💣 У тебя еще нет статистики!"
        user_data = {}
        # Gather wins and loses, grouping them by field size locally
        for item in list(game_data):
            user_data.setdefault(item[2], {"wins": 0, "loses": 0})
            if item[3] is True:
                user_data[item[2]]["wins"] += 1
            else:
                user_data[item[2]]["loses"] += 1
        # Calculate total games for each mode along with winrate.
        result_text_array = []
        total_games = 0
        for field_size, field_data in user_data.items():
            total_current = field_data["loses"] + field_data["wins"]
            total_games += total_current

            if field_data["loses"] == 0:
                winrate = 100
            else:
                winrate = field_data["wins"] / total_current * 100

            result_text_array.append(
                "💣 Поле <b>{size}×{size}</b>:\nИгр: <b>{total}</b>. "
                "Побед: <b>{wins}</b> (<b>{winrate:.0f}%</b>)".format(
                    size=field_size,
                    total=total_current,
                    wins=field_data["wins"],
                    winrate=winrate
                ))
        # Add a header to the beginning of result message
        result_text_array.insert(0, f"📊 <u>Твоя личная статистика</u>:\nВсего игр: <b>{total_games}</b>")
        text = "\n\n".join(result_text_array)
        return text
