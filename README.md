# Discord-Bot-Manager

### Description
This is a tool to help you monitor your bots remotely. You need to change one line of code to indicate the scripts you wish to run, and the bot will handle the rest.

### Supported Commands
- **status:**   Shows the status of the bots
- **start:**    Starts the selected bot
- **kill:**     Kills the selected bot
- **restart:**  Restarts the selected bot

### Usage
The scripts.txt file contains a colon (:) separated key:value pair, where the key is the bot name and the value is the python script. The provided example is valid.
Once you've adjusted this config for your own setup, you must update the .env file with your own token. Optionally, you can change the prefix as well.
Finally, you can run the bot: `python3 botmanager.py`. The bot will bring up your other bots, and you can start interacting with it on discord.



## License
MIT