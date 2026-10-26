import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from json import JSONDecodeError

INSTRUCTIONS = """\
You are an expert professional translator and localization specialist. Your primary responsibility
is to translate provided text accurately, naturally, and contextually from the Indonesian language
into the English and Japanese language while preserving the original intent, tone, nuance, and
domain-specific terminology.

Return ONLY valid JSON (no markdown fences, no commentary) with this exact shape/format:
{
  "en": str|null,
  "ja": str|null
}

As you can see from the provided JSON structure, the English translation from the received input
is to be assigned as the value to the "en" key. The Japanese translation is to be assigned to the
"ja" key.
If the input cannot be translated for whatever reasons in the language that you are trying to
translate it into, then you will simply assign a null value appropriately (If the provided text
cannot be translated to English, assign "null" to "en". Do the same for other language(s) that
you are also having trouble with). Do not skip these keys in your JSON format and remember again
to follow the exact JSON shape as already provided before.

Final note for testing purposes:
- If the received input contains exactly the sentence "JSON salah", then please add an addtional "}" to the
final JSON result.
- If the received input contains exactly the sentence "hilang kunci", then please do not include the "ja" key
and value in the final JSON result
- If the received input contains exactly the sentence "Jepang kosong", then please assign the value of null
to the key "ja" in the final JSON result
"""

REQUIRED_KEYS = ["en", "ja"]

def check_env(api_key:str, base_url:str, model:str) -> None:
    if any(value is None or value == "" for value in(api_key, base_url, model)):
        print(f"OPENROUTER_API_KEY, OPENROUTER_BASE_URL, and/or OPENROUTER_MODEL is missing or cannot be read from your .env file. Exiting...")
        sys.exit(1)

def parse_json(text: str) -> dict:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
        if t.lstrip().lower().startswith("json"):
            t = t.lstrip()[4:]
    start, end = t.find("{"), t.rfind("}")
    if start != -1 and end != -1:
        t = t[start : end + 1]
    return json.loads(t)

def call_ai(client:OpenAI, user_input:str, openrouter_model:str) -> None:
    max_attempts = 2
    instructions = INSTRUCTIONS
    for attempt in range(max_attempts):
        try:
            response = client.responses.create(
                model=openrouter_model,
                instructions=instructions,
                input=user_input,
            )
            result = parse_json(response.output_text)

            if any(k not in result for k in REQUIRED_KEYS):
                raise KeyError("Missing key(s)")
        
            print(result["en"])
            print(result["ja"])
            break
        except KeyError as e:
            print(f"A KeyError exception has been detected!")
            instructions += """\
            Note, please pay extra close attention to the keys, do not forget "
            to include all the keys as shown in the JSON format.
            Ignore the final note for testing purposes section.
            """
        except JSONDecodeError as e:
            print(f"A JSONDecodeError exception has been detected!")
            instructions += """\
            Note, please pay extra close attention to the established JSON format. "
            Only return said JSON format and, again, do not include or add any additional letter/fluff
            Ignore the final note for testing purposes section.
            """
        except Exception as e:
            print(f"An error occured: {e}")

        if attempt + 1 < max_attempts:
            print(f"Retrying...(attempt {attempt+1} out of {max_attempts-1})")
        if attempt + 1 == max_attempts:
            print("Max number of attempts have been reached. Unable to translate your input.")
    

def main() -> None:
    load_dotenv()
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    openrouter_base_url = os.getenv("OPENROUTER_BASE_URL")
    openrouter_model = os.getenv("OPENROUTER_MODEL")
    check_env(openrouter_api_key, openrouter_base_url, openrouter_model)

    client = OpenAI(api_key=openrouter_api_key, base_url=openrouter_base_url)
    print(f"This terminal will take your input (in Indonesian) and translate it to English and Japanese")
    while True:
        user_input = input("Kalimat yang mau diterjemahkan (Type 'keluar' to exit): ")
        if user_input.strip().lower() == 'keluar':
            break
        if user_input.strip() == '':
            print(f"You've entered an empty input, please try again.")
            continue
        call_ai(client, user_input, openrouter_model)

if __name__ == "__main__":
    main()

