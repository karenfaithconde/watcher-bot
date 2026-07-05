# main.py

This is the file I actually run when I want to start the bot, just python main.py in the terminal. It looks almost too simple for something that kicks off the whole project, and that confused me a bit at first, so let me walk through why it can afford to be this short.

## Walking through the code

```python
from bot_instance import bot
from config import TOKEN
```

These two imports pull in the bot object itself, and the secret token needed to log in. Nothing new is created here, both of these already exist elsewhere, I am just borrowing them.

```python
import events    # noqa: F401
import commands  # noqa: F401
```

This part surprised me the most when I first split my code into multiple files. I am importing these two modules, but I never actually call anything from them directly in this file. Turns out, just the act of importing them is enough, because both files are full of @bot.event and @bot.command decorators, and those decorators run and register themselves the instant the file they live in gets loaded. So simply writing import events is really saying, go run everything in that file right now, please.

The little # noqa: F401 comments are there for a linter, a tool that checks your code for common mistakes. Normally an unused import gets flagged as a warning, since it looks like a mistake. This comment tells the linter, I know this looks unused, but it is intentional, leave it alone.

```python
bot.run(TOKEN)
```

And this is the line that actually does something visible. Everything before it was just preparation, gathering the bot object and making sure every command and event got registered onto it. This line is what actually connects to Discord and keeps the program running.

## The one rule I had to learn the hard way

bot.run(TOKEN) is what is called a blocking call, meaning it does not return control back to the rest of the file until the bot shuts down. In practice that means it has to be the very last line in this file. Anything placed after it would just sit there waiting forever and never actually run.
