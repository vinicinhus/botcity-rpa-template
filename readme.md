# BotCity RPA Automation Template

This repository provides a template for creating Robotic Process Automation (RPA) bots using the BotCity framework. It includes the necessary setup for integrating BotCity's BotMaestroSDK, Telegram, and logging, along with the foundational structure to quickly deploy RPA automation tasks.

## Features

- **BotMaestroSDK Integration:** Easily set up and run automation tasks with BotMaestroSDK.
- **Telegram Bot Integration:** Communicate with Telegram for notifications or interactions during bot execution.
- **Logging and Resource Tracking:** Full logging of bot execution with details on resource usage (CPU, RAM, GPU).
- **Template for Custom Automation:** A starting point for your own RPA bots, with the flexibility to extend and modify for your specific use cases.

## Getting Started

### Prerequisites

Before running the bot, ensure you have the following installed:

- **Python 3.8**+
- **Poetry** (for dependency management)
- **BotCity SDK** (BotCity Maestro)
- **Telegram Bot Token** (for bot interaction, if needed)

### Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/vinicinhus/botcity-rpa-template.git
    cd botcity-rpa-template
    ```

2. Install dependencies. You can choose one of the following methods:

    - **Using Poetry:**

        If you are using Poetry for dependency management, run:

        ```bash
        poetry install
        ```

    - **Using ``requirements.txt``**:

        Alternatively, if you prefer to use pip and a requirements.txt file, you can install the dependencies as follows:

        ```bash
        pip install -r requirements.txt
        ```

3. Set up your **Telegram Bot** token:

    - Create a bot via **BotFather** on Telegram.
    - Retrieve the token and ensure it’s available for the bot to use.

4. Update ``bot_runner.py`` with your desired bot configuration, such as bot name and any specific automation logic.

### Usage

To run the bot:

```bash
poetry run python bot.py
```

This will initialize the bot and start the automation process defined in ``bot_runner.py``.

### Configuration

- **bot_name:** This is the name of your bot, used for logging.
- **log_dir:** Directory where log files will be saved (default is ``logs``).
- **bot_maestro_sdk_raise:** Flag to indicate whether errors should be raised during BotMaestroSDK connection failures.

### How It Works

- The ``bot.py`` file initializes the ``BotRunner`` class from ``bot_runner.py`` and begins the bot execution process.
- The ``BotRunner`` class:

    - Handles the bot execution flow, logging, and interaction with the Telegram bot.
    - Initializes the **BotMaestroSDK** for running the automation task and retrieves the Telegram token.
    - Logs the bot’s execution details, including resource usage (CPU, RAM, GPU).
    - Allows for further customization to integrate other automation tools and processes.

### Logs

Logs are automatically generated and stored in the specified log directory. The log file includes:

- Bot execution start and end time.
- Detailed resource usage statistics.
- Any errors or exceptions that occur during the bot execution.

### Error Handling

If an error occurs during the bot execution, the bot will:

- Send a message to the designated Telegram group with the error details.
- Upload the log file to BotCity Maestro for further analysis.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/vinicinhus/botcity-rpa-template/blob/main/LICENSE) file for details.

## Contributing

1. Fork this repository.
2. Create a feature branch.
3. Make your changes.
4. Commit and push your changes.
5. Open a pull request.

## Acknowledgments

- [BotCity](https://documentation.botcity.dev/) for providing the powerful framework for automation.
- [Telegram Bot API](https://core.telegram.org/bots/api) for integrating with Telegram for bot interactions.
- [Poetry](https://python-poetry.org/) for managing project dependencies.