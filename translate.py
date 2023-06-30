import argparse, tiktoken, openai, math, concurrent.futures, uuid

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, required=True, help='TXT File path that will be translated')
parser.add_argument('--lang-out', type=str, default='English', help='Directory for storing model')
parser.add_argument('--length-limit', type=int, default=4000, help='Max Length of the prompt')
parser.add_argument('--openai-key', type=str, required=False, help='OpenAI API Key')
parser.add_argument('--openai-model', type=str, default='gpt-3.5-turbo', help='OpenAI API Engine') # gpt-3.5-turbo, text-davinci-003, gpt-4
args = parser.parse_args()
openai.api_key = args.openai_key

# Language Coefficient are the coefficients that allow to estimate the number of output tokens of the translation
LANGUAGE_COEF = {
    "French" : 0.7, # JP In : [1935, 1942, 1919, 1925, 1894, 1938, 1938] | FR Out : [1359, 1244, 1208, 1208, 1258, 1221, 1115] | AVG : 0.6385
    "English": 0.5 # JP In : [1935, 1942, 1919, 1925, 1894, 1938] | EN Out : [917, 918, 868, 861, 930, 932] | AVG : 0.4697
}

CHOOSED_COEF = LANGUAGE_COEF.get(args.lang_out) if LANGUAGE_COEF.get(args.lang_out) else exit(f"Language not supported, please choose one language of the list : {list(LANGUAGE_COEF.keys())}")
MODEL_ENCODER = tiktoken.encoding_for_model(args.openai_model)
PROMPT_TEMPLATE = f"""I want you to act as an {args.lang_out} translator, spelling corrector and improver. I will speak to you in any language and you will detect the language, translate it and answer in the corrected and improved version of my text, in {args.lang_out}. I want you to replace my simplified A0-level words and sentences with more beautiful and elegant, upper level {args.lang_out} words and sentences. Keep the meaning same, but make them more literary. I want you to only reply the correction, the improvements and nothing else, do not write explanations. Don't forget to skip lines to space the text"""
MAX_PROMPT_TOKEN = math.ceil(args.length_limit / (1 + CHOOSED_COEF))
CHAT_BASED_MODEL = ["gpt-3.5-turbo", "gpt-4"]

def getTokensCountFromString(string):
    return len(MODEL_ENCODER.encode(string))

def getTokensCountFromChatBased(messages):
    num_tokens = 0
    for message in messages:
        num_tokens += 4
        for key, value in message.items():
            num_tokens += getTokensCountFromString(value)
            if key == "name": 
                num_tokens += -1
    num_tokens += 2
    return num_tokens

def craftMessageWithPrompt(prompt):
    return [
        {"role": "system", "content": PROMPT_TEMPLATE},
        {"role": "user", "content": prompt}
    ]

def translate(content):
    index, message = content
    print(f"Starting translation task #{index}")
    response = openai.ChatCompletion.create(
        model=args.openai_model,
        messages=message,
        temperature=0.7,
        request_timeout=1200
    )
    if response['usage']['total_tokens'] < args.length_limit + 97:
        print(f"Finished translation task #{index} with {response['usage']['total_tokens']} tokens used")
    else:
        print(f"Warning for Translation task #{index} : Used {response['usage']['total_tokens']} tokens : the prompt is too long, the translation will miss some words")
    with open(f"{index}.txt", "w", encoding="utf-8", errors="ignore") as writer:
        writer.write(response['choices'][0]['message']['content'])
    return response['choices'][0]['message']['content']

text_parts = []
prompt = ""
num_line = len(open(args.input, "r", encoding="utf-8", errors="ignore").readlines())
for c, line in enumerate(open(args.input, "r", encoding="utf-8", errors="ignore")):
    if args.openai_model in CHAT_BASED_MODEL: 
        messages= craftMessageWithPrompt(prompt)
        next_messages= craftMessageWithPrompt(prompt + line)
        if getTokensCountFromChatBased(messages) <= MAX_PROMPT_TOKEN and getTokensCountFromChatBased(next_messages) <= MAX_PROMPT_TOKEN:
            prompt += line
            if c == num_line - 1:
                text_parts.append(prompt)
        else:
            text_parts.append(prompt)
            prompt = line
    else:
        exit("Model not supported, please use a chat based model")

print(f"Text divided in {len(text_parts)} parts, starting translation with {args.openai_model} model")

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    translated_messages = list(executor.map(translate, [(index, craftMessageWithPrompt(text_part)) for index, text_part in enumerate(text_parts)]))

with open("output.txt", "w", encoding="utf-8", errors="ignore") as writer:
    for part in translated_messages:
        writer.write(part)


