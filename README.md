# GPT-LN-Translator 💬📚

This is a command-line tool for translating novels using OpenAI's GPT language models. The tool allows you to translate a TXT file from any language to English using the OpenAI API.

## Usage 🚀

To use the tool, you will need to provide the following arguments:

- `--input`: The path to the TXT file that you want to translate.
- `--lang-out`: The language of the output text (default: English).
- `--length-limit`: The maximum length of the prompt (default: 4000).
- `--openai-key`: Your OpenAI API key (optional).
- `--openai-model`: The OpenAI API engine to use (default: gpt-3.5-turbo, other options: text-davinci-003, gpt-4).

Here's an example of how to use the tool:
```python translate.py --input novel.txt --lang-out English --length-limit 5000 --openai-key <your-api-key> --openai-model gpt-3.5-turbo```

## Installation 🛠️

1. Clone the repository:
```git clone https://github.com/Snowad14/GPT-LN-Translator.git```

2. Install the dependencies:
```pip install -r requirements.txt```
