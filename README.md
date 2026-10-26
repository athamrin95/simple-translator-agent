A simple translator agent using OpenRouter API.

Note:
This project has been tested with Python 3.15<br>
Dependencies required can be found in the file "requirements.txt"<br>
Rename the file ".env.example" to ".env" and fill in OPENROUTER_API_KEY with your actual api key<br>
You may change the AI model with a different one that's available in OpenRouter by changing the value of OPENROUTER_MODEL 

This script will translate the user's input (in Bahasa Indonesia) to English and Japanese. The script will do a maximum of 2 attempts to translate the input before giving up should it encounter some troubles during the translation progress. 
This current version of the script do not remember your previously sent messages.

For testing purposes, typing exactly these sentences will result in the following outcome:<br>
"JSON salah" -> JSONDecodeError exception is triggered for the first attempt<br>
"hilang kunci" -> KeyError exception is triggered for the first attempt<br>
"Jepang kosong" -> The Japanese translation will be empty/None