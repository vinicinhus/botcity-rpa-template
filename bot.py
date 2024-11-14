from botcity_aux.bot_runner import BotRunner

if __name__ == "__main__":
    bot_runner = BotRunner(bot_name="My Bot", telegram_group="My Group")
    bot_runner.run()
