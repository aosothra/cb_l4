# cb_l4 - Quiz Bots

This project implements quiz bots ([VK](https://vk.com/club211678335), [Telegram](https://t.me/quiz_dev_test_113_bot)) working on the predefined set of questions.

## Installation and Environment setup

You must have Python3 installed on your system.

You may use `pip` (or `pip3` to avoid conflict with Python2) to install dependencies.
```
pip install -r requirements.txt
```
It is strongly advised to use [virtualenv/venv](https://docs.python.org/3/library/venv.html) for project isolation.

This script uses `.env` file in root folder to store variables necessary for operation. So, do not forget to create one!

Inside your `.env` file you can specify following settings:

| Key | Type | Required by | Description |
| - | - | - | - |
| `QUIZ_JSON_PATH` | `str` | `tg_bot.py`, `vk_bot.py` | Path to JSON file with question-answer pairs
| `TG_BOT_TOKEN` | `str` | `tg_bot.py` | Your Telegram bot API token to handle conversations in Telegram. 
| `VK_BOT_TOKEN` | `str` | `vk_bot.py` | Your VK token for group messages access to handle conversations in VK.
| `REDIS_HOST` | `str` | `tg_bot.py`, `vk_bot.py` | Host address of your Redis database server.
| `REDIS_PORT` | `int` | `tg_bot.py`, `vk_bot.py` | Port number of your Redis database server.
| `REDIS_PASSWORD` | `str` | `tg_bot.py`, `vk_bot.py` | Password for auth purposes for your Redis database.
| `TEST_ANSWERS` | `bool` | `tg_bot.py`, `vk_bot.py` | Flag, that will allow hinting of quiz answers for testing purposes.

If you do not know how to acquire Telegram Bot token, you can follow official guidelines [here](https://core.telegram.org/bots#3-how-do-i-create-a-bot).

If you do not know how to acquire VK group access token, you can find it in [here](https://dev.vk.com/api/community-messages/getting-started#Получение%20ключа%20доступа%20в%20настройках%20сообщества).

Present implementation of the bots partially rely on Redis database for user data persistence. So you will have to set up one.
The easiest way is to register free plan on [Redis Enterprise](https://redis.com/try-free/) cloud platform. Once registered, use host address, port and default user password provided for `REDIS_HOST`, `REDIS_PORT` and `REDIS_PASSWORD`.

In order to have a proper quiz experience, you'll need dem questions and answers. There are several ways to approach this problem.

- You may create `quiz.json` file and manually input question-answer pairs in following manner: 
```JavaScript
{
    "Is JSON a proper way to store questions and answers?": "Certainly",
    "What is an answer to the Ultimate Question of Life, The Universe, and Everything?": "41",
    ...
}
```
- Use provided `parse_question.py` utility script. It allows parsing of `.txt` history data of other quizes, that may be obtained elsewhere. The utility script expects `.txt` file that respects following format:

```
Вопрос
question-line 1
question-line 2
....
question-line n
Ответ
single-word-answer
Вопрос
question-line 1
question-line 2
....
```

To get specifics about `parse_question.py` you can prompt a help message with following command:

```sh
py parse_question.py -h
```

In both cases, make sure to specify path to your JSON file in `QUIZ_JSON_PATH`.
  
## Basic usage

Use `tg_bot.py` to start Telegram bot:

```
py tg_bot.py 
```

Use `vk_bot.py` to start VK Group bot:

```
py vk_bot.py 
```

## Project goals

This project was created for educational purposes as part of [dvmn.org](https://dvmn.org/) Backend Developer course.