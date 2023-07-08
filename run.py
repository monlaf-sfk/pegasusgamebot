import asyncio
import logging
import subprocess
import sys
from aiogram.filters import Command
from aiogram.fsm.strategy import FSMStrategy
from aiogram_dialog import setup_dialogs

import app
import config
from filters.admin import IsOwner
from filters.triggers import Trigger
from filters.users import IsAdmin, IsElite, IsBan
from handlers import my_chat_member
from handlers.admins import ban, rass, wdz
from aiogram import Dispatcher, F, Router
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.admins.gifts import gift_get_handler, gift_handler, gift_step1_handler, gift_step2_handler, \
    gift_finish_handler, gift_participate_handler, Gift, gift_step3_handler, gift_step4_handler
from handlers.admins.main import profile_handler_admin, givebalance_handler, takebalance_handler, multibalance_handler, \
    devidebalance_handler, givebalance_admin_handler, stats_handler, stats_dop_call, wdzy_info, get_chat_list, plan_bd, \
    plan_bd_step1, plan_bd_step2, plan_bd_finish, givedonate_handler, privilegia_handler_admin, other_handler, \
    admin_nickname_handler, other_callhandler, other_kurs_handler, other_bonus_handler, other_zarefa_handler, \
    other_credit_handler, other_credit_percent_handler
from handlers.admins.obnyl import obnyn_user_handler, obnyn_property_handler, obnyn_handler
from handlers.admins.promo import promo_check_handler, promo_switch_callback
from handlers.admins.wdz import chat_add_handler
from handlers.users import exceptions
from handlers.users.auction.category import category_auction_dialog, coins_auction_dialog
from handlers.users.auction.infolot import infolot_window, auction_lotinfo_handler
from handlers.users.auction.main import main_auction_dialog, start_auction, auction_lot_handler, auction_help_handler
from handlers.users.auction.mybet import bets_auction_dialog
from handlers.users.auction.mylots import lots_auction_dialog
from handlers.users.bitcoin.main import bitcoin_handler, videocards_handler, ferma_handler
from handlers.users.bonus import bonus_handler
from handlers.users.bosses.armory.arsenal import arsenal_dialog
from handlers.users.bosses.armory.craft import craft_dialog
from handlers.users.bosses.armory.improvement import improvement_armory_dialog
from handlers.users.bosses.armory.main import start_armory, main_armory_dialog
from handlers.users.bosses.armory.parsing import parsing_armory_dialog
from handlers.users.bosses.armory.shop import shop_armory_dialog
from handlers.users.bosses.main import bosses_handler, BosseAttackData, bosses_callbackatttack_handler, \
    bosses_callbackinfo_handler, BosseInfoData
from handlers.users.businesses.businesses import business_handler
from handlers.users.cars.airplanes import airplanes_handler
from handlers.users.cars.cars import cars_handler
from handlers.users.cars.computers import computers_handler, computers_hand
from handlers.users.cars.moto import moto_handler
from handlers.users.cars.vertoleti import vertoleti_handler
from handlers.users.cars.yaxti import yaxti_handler
from handlers.users.cash.bank import bank_handler, credit_handler
from handlers.users.cash.deposit import deposit_handler
from handlers.users.cash.euro import euro_handler
from handlers.users.cash.pay import pay_handler
from handlers.users.cash.rob import rob_handler, shield_handler
from handlers.users.cash.uah import uah_handler
from handlers.users.city.main import city_handler, city_info_handler
from handlers.users.clan import clan_war, clan_war_group
from handlers.users.clan.clan import clan_handler, info_callback_invate, invate_solution, mamber_handler, \
    info_callback_user
from handlers.users.clan.list_clans import clan_list_handler, clan_dialog
from handlers.users.donate import donate_help_handler, zadonatit_handler, donate_help_call_handler, \
    percent_buy_handler, cobmen_handler, other_method_handler, check_handler_qiwi, qiwi_info_handler, qiwi_buy_handler, \
    check_handler_crypto, crypto_info_handler, crypto_buy_handler, CryptoBot, check_handler_crystal, \
    crystal_buy_handler, crystal_info_handler, CrystalPay, payok_buy_handler, check_handler_payok, payok_info_handler

from handlers.users.funny import globus_handler, chance_handler, choice_handler
from handlers.users.games import tictactoe
from handlers.users.games.basketball import basketball_handler
from handlers.users.games.blackjack import blackjack, blackjack_ls
from handlers.users.games.bowling import bowling_handler
from handlers.users.games.cases import cases_handler
from handlers.users.games.casino import casino_handler
from handlers.users.games.darts import darts_handler
from handlers.users.games.dice import dice_handler
from handlers.users.games.footbal import footbal_handler
from handlers.users.games.minesweeper.game import stats_minesweeper, show_newgame_msg, Mine_help_handler1, \
    Mine_help_handler, show_newgame_cb
from handlers.users.games.minesweeper.handler import callbacks
from handlers.users.games.ruletka.ruletka import ruletka_handler, rulet_stop_handler, rulet_push_handler, \
    rulet_handler_call, rulet_call
from handlers.users.games.ruletka.ruletka_group import ruletka_handler_group, rulet_stop_handler_group, \
    rulet_push_handler_group

from handlers.users.games.spin import spin_handler
from handlers.users.games.tictactoe import join_game, process_callback_game
from handlers.users.houses.houses import house_handler
from handlers.users.items import item_handler
from handlers.users.jobs.jobs import jobs_handler
from handlers.users.main import start_handler, ref_call_handler, dialog, help_handler, help_call_handler
from handlers.users.marries import marry_handler, marry_call_handler
from handlers.users.me import balance_handler, profile_handler, nickname_handler, notifies_handler, imush_user_handler, \
    status_handler
from handlers.users.nalogs import nalogs_handler, autonalog_handler

from handlers.users.prefixes import prefix_handler
from handlers.users.promo import activatepromo_handler
from handlers.users.ref import refferal_handler
from handlers.users.rp import rp_commands_handler, emojis

from handlers.users.shop.shop import shop_dialog, shop_list_handler

from handlers.users.top import topback_handler_call, top_handler_call, top_handler
from handlers.users.works.mine import mine_handler
from handlers.users.works.zavod import zavod_handler
from loader import bot
from middlewares.Throttling import ThrottlingCallMiddleware, ThrottlingMiddleware
from states.admins import ABD
from states.donates import PayokPay


async def on_shutdown():
    print("[red]Bot finished! [blue][•-•][/blue]")
    await bot.send_message(
        chat_id=config.owner_id,
        text=f"<b>🪄 Бот СПИТ!</b> ",
    )


async def on_startup(bot):
    print("[green]Bot started! [blue][•-•][/blue]")

    await bot.send_message(
        chat_id=config.owner_id,
        text=f"<b>🪄 Бот запущен!</b> ",
    )


dialog_router = Router()
dialog_router.include_routers(
    clan_dialog,
    shop_dialog,

    main_auction_dialog,
    category_auction_dialog,
    coins_auction_dialog,
    bets_auction_dialog,
    lots_auction_dialog,
    infolot_window,

    main_armory_dialog,
    arsenal_dialog,
    craft_dialog,
    parsing_armory_dialog,
    improvement_armory_dialog,
    shop_armory_dialog
)


async def main():
    dp = Dispatcher(bot=bot, storage=MemoryStorage(), fsm_strategy=FSMStrategy.GLOBAL_USER)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.include_routers(my_chat_member.router)
    dp.message.register(app.forward_from, F.forward_from)
    dp.message.register(app.sql_handler, Command("sql"), IsOwner())
    dp.message.register(donate_help_handler, Trigger(
        ["donate", "донат", "прива", "привы", "привилегии", "привилегия", "донаты", "donates", "donats", ]))
    dp.message.register(app.ban_handler, F.text, IsBan())
    dp.include_routers(app.router)
    dp.include_routers(ban.router)
    dp.include_routers(tictactoe.router)
    dp.include_router(callbacks.router)
    dp.include_router(exceptions.router)
    dp.include_router(rass.router)
    dp.include_router(wdz.router)
    dp.include_router(blackjack_ls.router)
    dp.include_router(blackjack.router)
    dp.include_router(clan_war.router)
    dp.include_router(clan_war_group.router)
    dp.callback_query.register(show_newgame_cb, F.data == "choose_newgame")
    dp.message.register(stats_minesweeper, Trigger(
        ["стат сапер", "стат сапёр", 'статистика сапер', 'статистика сапёр', "стат саппер", "стат саппёр",
         'статистика саппер', 'статистика саппёр']))
    dp.message.register(show_newgame_msg, Trigger(["сапер", "сапёр", "саппер", "саппёр"]))
    dp.callback_query.register(Mine_help_handler, F.data.startswith("mineorder_"))
    dp.callback_query.register(join_game, F.data.startswith("tic_"))
    dp.callback_query.register(process_callback_game, F.data.startswith("tictac_"))
    dp.message.register(promo_check_handler, Command("promo_check"))
    dp.callback_query.register(promo_switch_callback, F.data.startswith("promo_"))
    dp.message.register(admin_nickname_handler, IsOwner(), Command("nick"))
    dp.message.register(obnyn_user_handler, IsOwner(), Command("reset_user"))
    dp.message.register(obnyn_property_handler, IsOwner(), Command("reset_property"))
    dp.message.register(profile_handler_admin, IsAdmin(), Trigger(["инфо", "info"]))
    dp.message.register(givebalance_handler, IsOwner(), Trigger(["выдать", "give"]))
    dp.message.register(takebalance_handler, IsOwner(), Trigger(["забрать", "take"]))
    dp.message.register(multibalance_handler, IsOwner(), Trigger(["умножить", "multi"]))
    dp.message.register(devidebalance_handler, IsOwner(), Trigger(["разделить", "devide"]))
    dp.message.register(givebalance_admin_handler, Trigger(["выдать", "give"]), IsElite())
    dp.message.register(other_handler, Trigger(["other"]), IsOwner())
    dp.callback_query.register(other_callhandler, F.data.startswith("other_"))
    dp.message.register(other_kurs_handler, Trigger(["kurs"]), IsOwner())
    dp.message.register(other_bonus_handler, Trigger(["bonus"]), IsOwner())
    dp.message.register(other_zarefa_handler, Trigger(["zarefa"]), IsOwner())
    dp.message.register(other_credit_handler, Trigger(["credit_limit"]), IsOwner())
    dp.message.register(other_credit_percent_handler, Trigger(["credit_percent"]), IsOwner())

    # Last
    dp.message.register(app.logs_handler, Trigger(["logs"]), IsOwner())
    dp.message.register(obnyn_handler, Trigger(["reset_bot"]), IsOwner())
    dp.message.register(chat_add_handler, Trigger(["вдзу"]), IsOwner())

    dp.message.register(
        stats_handler, Trigger(["стата бота", "статистика бота", "stat bot", "stats bot"])
    )

    dp.callback_query.register(
        stats_dop_call, IsOwner(), F.data == "statsdop"
    )

    dp.callback_query.register(
        stats_dop_call, IsOwner(), F.data == "statsdop"
    )
    dp.callback_query.register(
        wdzy_info, IsOwner(), F.data == "wdzy"
    )
    # dp.callback_query.register(
    #     get_db, IsOwner(), text="get_db"
    # )

    dp.callback_query.register(
        get_chat_list, IsOwner(), F.data == "allchats",
    )
    # razd
    dp.message.register(gift_get_handler, IsOwner(), Command("раздать"))
    dp.message.register(gift_handler, IsOwner(), Command("gift"))
    dp.message.register(gift_step1_handler, IsOwner(), Gift.text)
    dp.message.register(gift_step2_handler, IsOwner(), Gift.winners)
    dp.message.register(gift_step3_handler, IsOwner(), Gift.type_reward)
    dp.message.register(gift_step4_handler, IsOwner(), Gift.count_reward)
    dp.message.register(gift_finish_handler, IsOwner(), Gift.text_button)
    dp.callback_query.register(gift_participate_handler, F.data == "raz")

    dp.callback_query.register(plan_bd, IsOwner(), F.data == "plan", )
    dp.message.register(plan_bd_step1, IsOwner(), ABD.start)
    dp.message.register(plan_bd_step2, IsOwner(), ABD.step_1)
    dp.message.register(plan_bd_finish, IsOwner(), ABD.step_2)

    dp.message.register(
        givedonate_handler, IsOwner(), Trigger(["ддонат"])
    )
    dp.message.register(
        privilegia_handler_admin,
        IsOwner(),
        Trigger(["дприву"]))

    # Main commands

    dp.message.register(
        start_handler, Command("start")
    )
    dp.callback_query.register(
        ref_call_handler, F.data.startswith("check"), dialog.captcha
    )
    # help
    dp.message.register(
        auction_help_handler, Trigger(['помощь аукцион'])
    )
    dp.message.register(Mine_help_handler1, Trigger(["помощь сапёр", "помощь сапер", "помощь саппёр", "помощь саппер"]))
    dp.message.register(help_handler, Trigger(["помощь", "команды", "help"]))
    dp.callback_query.register(
        help_call_handler, F.data.startswith("help_")
    )
    dp.message.register(app.calc_handler, Trigger(["calc", "реши", "cl"]))

    # Exceptions

    # Profile commands

    dp.message.register(balance_handler, Trigger(["б", "баланс", "balance", "b"]))
    dp.message.register(
        profile_handler, Trigger(["профиль", "me", "профайл", "п"])
    )
    dp.message.register(
        nickname_handler, Trigger(["+ник", "+nick", "+nickname", "+name", "+никнейм"])
    )
    dp.message.register(
        notifies_handler, Trigger(["ник вкл", "ник выкл"])
    )

    dp.callback_query.register(imush_user_handler, F.data.startswith("imush:"))
    dp.callback_query.register(profile_handler, F.data.startswith("imushback_"))
    dp.callback_query.register(status_handler, F.data.startswith("status:"))
    dp.callback_query.register(balance_handler, F.data.startswith("status_back_"))
    # Top system
    dp.callback_query.register(topback_handler_call, F.data.startswith("topback_"))
    dp.callback_query.register(top_handler_call, F.data.startswith("top_"))
    dp.message.register(top_handler, Trigger(["топ", "top"]))
    # Bank commands
    dp.message.register(bank_handler, Trigger(["банк", "bank"]))
    dp.message.register(credit_handler, Trigger(["кредит", "credit", "займ"]))

    # Deposit commands
    dp.message.register(
        deposit_handler, Trigger(["деп", "депозит", "dep", "deposit"])
    )

    # Item commands
    dp.message.register(
        item_handler,
        Trigger(
            [
                "предмет",
                "предметы",
                "item",
                "items",
                "инв",
                "инвентарь",
                "inv",
                "inventory",
                "продать",
            ]
        ),
    )

    # Pay commands
    dp.message.register(pay_handler, Trigger(["pay", "передать", "дать"]))

    # Games

    dp.message.register(dice_handler, Trigger(["кубик", "dice"]))
    dp.message.register(bowling_handler, Trigger(["боулинг", "bowling"]))
    dp.message.register(basketball_handler, Trigger(["баскетбол", "basketball"]))
    dp.message.register(footbal_handler, Trigger(["футбол", "footbal"]))
    dp.message.register(darts_handler, Trigger(["дартс", "darts"]))

    dp.message.register(ruletka_handler, Trigger(["рулетка"]), F.chat.type.in_({"private"}))
    dp.message.register(rulet_stop_handler, Trigger(["ррулетка"]), F.chat.type.in_({"private"}))
    dp.message.register(rulet_push_handler, Trigger(["выстрел"]), F.chat.type.in_({"private"}))

    dp.message.register(ruletka_handler_group, Trigger(["рулетка"]), F.chat.type.in_({"group", "supergroup"}))
    dp.message.register(rulet_stop_handler_group, Trigger(["ррулетка"]), F.chat.type.in_({"group", "supergroup"}))
    dp.message.register(rulet_push_handler_group, Trigger(["выстрел"]), F.chat.type.in_({"group", "supergroup"}))

    dp.callback_query.register(rulet_handler_call, F.data.startswith("return_ruletka"))
    dp.callback_query.register(rulet_call, F.data.startswith("rulet"))

    dp.message.register(spin_handler, Trigger(["спин", "spin"]))
    dp.message.register(casino_handler, Trigger(["казино", "casino"]))

    #    Кейсы
    dp.message.register(
        cases_handler, Trigger(["кейс", "кейсы", "case", "cases"])
    )

    # Promo-code command
    dp.message.register(
        activatepromo_handler, Trigger(["promo", "promocode", "промокод", "промо"])
    )

    # Bonus command
    dp.message.register(
        bonus_handler, Trigger(["бонус", "подарок", 'ежедневный бонус'])
    )

    # Referral system
    dp.message.register(refferal_handler, Trigger(["Рефералка", "Ref", "Реф"]))

    # Houses system
    dp.message.register(house_handler, Trigger(["дом", "house", "дома"]))

    # Business system
    dp.message.register(
        business_handler,
        Trigger(["бизнес", "бизнесса", "бизнеса", "бизнесс", "business", "биз"]),
    )

    # Cars system
    dp.message.register(
        cars_handler, Trigger(["car", "cars", "машина", "машины", "карс", "кар"], )
    )

    # Yaxti system
    dp.message.register(yaxti_handler, Trigger(["яхта", "яхты"]))

    # Airplanes system
    dp.message.register(
        airplanes_handler, Trigger(["airplane", "airplanes", "самолёт", "самолёты", "самолет"])
    )

    # Vertoleti system
    dp.message.register(
        vertoleti_handler,
        Trigger(
            ["вертолёт", "вертушка", "вертушки", "вертолёты", "вертолет", "вертолёты"]
        ),
    )

    # Moto system
    dp.message.register(
        moto_handler, Trigger(["moto", "мото", "мотоцикл", "motorcycle", "мотоциклы"])
    )
    # computer system
    dp.message.register(
        computers_handler, Trigger(["computer", "pc", "пк", "компьютер", "компьютеры", "комп"])
    )
    dp.callback_query.register(
        computers_hand, F.data.startswith('computer_')
    )
    # Mine system
    dp.message.register(mine_handler, Trigger(["шахта", "копать"]))

    # Zavod system
    dp.message.register(zavod_handler, Trigger(["фабрика", "работать"]))

    # Job system
    dp.message.register(
        jobs_handler,
        Trigger(
            [
                "job",
                "работа",
                "jobs",
                "работы",
                "професия",
                "проффесия",
                "профессии",
                "професии",
                "проффессии",
                "профессия",
            ]
        ),
    )
    #  CITY
    dp.message.register(city_handler, Trigger(["город"]))
    dp.message.register(city_info_handler, F.text.lower() == "хелп город")
    # Family system
    dp.message.register(
        marry_handler, Trigger(["marry", "семья", "брак", "браки", "marries"])
    )
    dp.callback_query.register(marry_call_handler, F.data.startswith("maccept_"))
    dp.callback_query.register(marry_call_handler, F.data.startswith("mdecline_"))
    # clan system
    dp.message.register(
        clan_list_handler, (F.text.lower() == "клан список") | (F.text.lower() == "кланы"))
    dp.message.register(
        clan_handler, Trigger(["клан"])
    )
    dp.callback_query.register(info_callback_invate, F.data.startswith("invite_"))
    dp.callback_query.register(invate_solution, F.data.startswith("clan_"))
    dp.callback_query.register(mamber_handler, F.data.startswith("members_"))
    dp.callback_query.register(info_callback_user, F.data.startswith("claninfo_"))

    # Nalogs
    dp.message.register(nalogs_handler, Trigger(["налог", "налоги"]))
    dp.message.register(
        autonalog_handler,
        Trigger(
            ["автоналоги", "авто-налоги", "autonalogi", "autonalogs", "autoналоги"]
        ),
    )

    # Donate

    dp.callback_query.register(donate_help_call_handler, F.data.startswith("priv_"))
    dp.message.register(zadonatit_handler, Trigger(["задонатить", "donatit"]))
    dp.message.register(cobmen_handler, Trigger(["кобмен", "Кобмен"]))
    dp.message.register(percent_buy_handler, Trigger(["процент", "percent"]))

    dp.callback_query.register(zadonatit_handler, F.data == "donate")
    dp.callback_query.register(other_method_handler, F.data == "donate_other")

    dp.callback_query.register(qiwi_info_handler, F.data == "donate_qw")
    dp.message.register(qiwi_buy_handler, Trigger(["пополнить"]))
    dp.callback_query.register(check_handler_qiwi, F.data.startswith("check2_"))

    dp.callback_query.register(crystal_info_handler, F.data == "donate_crystal")
    dp.message.register(crystal_buy_handler, CrystalPay.start)
    dp.callback_query.register(check_handler_crystal, F.data.startswith("crystal"))

    dp.callback_query.register(crypto_info_handler, F.data == "donate_crypto")
    dp.message.register(crypto_buy_handler, CryptoBot.start)
    dp.callback_query.register(check_handler_crypto, F.data.startswith("crypto"))

    dp.callback_query.register(payok_info_handler, F.data == "donate_payok")
    dp.message.register(payok_buy_handler, PayokPay.start)
    dp.callback_query.register(check_handler_payok, F.data.startswith("payok"))
    #    # Moderation

    # dp.message.register(mute_handler,IsOwner(), commands=['заткнуть', 'заткн'])

    # dp.message.register(ban_handler_chat,IsOwner(), commands=['гбан'])

    # dp.message.register(unmute_handler,IsOwner(), Trigger(['unmute', 'анмут', 'размут']))

    # dp.message.register(unban_handler, IsOwner(),Trigger(['unban', 'разбан', 'анбан']))

    # dp.callback_query.register(unban_handler,IsOwner(), text_startswith='unban', state='*', chat_type=['group', 'supergroup'])
    # dp.callback_query.register(unmute_handler, IsOwner(),text_startswith='unmute', state='*', chat_type=['group','supergroup'])

    # Prefixes
    dp.message.register(
        prefix_handler,
        Trigger(
            [
                "преф",
                "префы",
                "префиксы",
                "префикс",
                "pref",
                "prefs",
                "prefix",
                "prefixes",
            ]
        ),
    )

    # Bitcoin
    dp.message.register(
        bitcoin_handler, Trigger(["btc", "биткоин", "бтс", "бтц", "биткоины"])
    )
    dp.message.register(
        videocards_handler,
        Trigger(["видео", "видеокарт", "видеокарта", "видеокарты", "видюха", "видюхи"]),
    )
    dp.message.register(
        ferma_handler, Trigger(["ферма", "майнинг", "ferma", "ferm", "фермы"])
    )
    dp.message.register(bitcoin_handler, Trigger(["курс"]))

    # Rob
    dp.message.register(
        rob_handler,
        Trigger(["rob", "огра", "ограбление", "украсть", "ограбить", "ограба"]),
    )
    dp.message.register(shield_handler, Trigger(["щит", "щиты", "shield"]))

    # Euro
    dp.message.register(euro_handler, Trigger(["euro", "евро", "эвро", "еуро"]))
    dp.message.register(
        uah_handler, Trigger(["юан", "юаны", "юани", "юань"])
    )

    # Боссы
    dp.message.register(
        bosses_handler, Trigger(["босс", "боссы", "босы", "бос"]))
    dp.message.register(
        start_armory, Trigger(["оружейная"]))

    dp.callback_query.register(bosses_callbackatttack_handler, BosseAttackData.filter())
    dp.callback_query.register(bosses_callbackinfo_handler, BosseInfoData.filter())
    # Shop
    dp.message.register(shop_list_handler, Trigger(["shop", "шоп", "магазин"]))

    # RP
    dp.message.register(
        rp_commands_handler, Trigger(["рп"] + list(emojis.keys()))
    )
    # fun
    dp.message.register(
        globus_handler, Trigger(["Шар"])
    )
    dp.message.register(
        chance_handler, Trigger(["Шанс"])
    )
    dp.message.register(
        choice_handler, Trigger(["Выбери"])
    )
    # aукцион
    dp.message.register(
        start_auction, Trigger(["аукцион"])
    )
    dp.message.register(
        auction_lot_handler, Trigger(["lot", 'лот'])
    )
    dp.message.register(
        auction_lotinfo_handler, F.text.startswith("/lot_")
    )

    import utils.schedulers

    dp.include_router(dialog_router)
    setup_dialogs(dp)
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingCallMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    useful_updates = dp.resolve_used_update_types()
    await dp.start_polling(bot, allowed_updates=useful_updates)


if __name__ == "__main__":
    # logging.info(f"Обновляю модули...")
    # subprocess.check_call([sys.executable, "-m", "pip", "install", '-U', "-r", "requirements.txt"])
    # logging.info('Модули обновлены!')
    logging.getLogger('apscheduler.executors.default').propagate = False
    logging.getLogger('apscheduler.scheduler').propagate = False
    logging.getLogger('aiogram.event').propagate = False
    logging.getLogger('pyrogram').propagate = False
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
