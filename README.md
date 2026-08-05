# AI Debate Arena

Two large language models debate any topic you give them. One argues for it, the other argues against it, and you decide who made the stronger case.

Live app: https://ai-debate-arena-vjsbxdo2xtepebx3n7vurq.streamlit.app/

## What it does

* You type in a resolution (for example: "Vibe coding destroys problem solving skills").
* Two separate Groq hosted models take opposite sides: Debate Model A argues in favor, Debate Model B argues against.
* The models take turns, each one reading and directly responding to the other's previous point.
* Every argument streams into the page as it is generated, so you can follow the debate live.
* Once the debate ends, you pick the winner yourself. There is no AI judge, only your own read of the arguments.

## Features

* Live streaming responses, one turn at a time
* A fixed number of rounds and a fixed word limit per turn, so debates stay focused and no side gets an unfair advantage
* Simple, plain language responses, written so a general reader can follow the argument on a first read
* A custom light and dark theme that adapts to the visitor's system preference
* A manual winner selection step at the end of every debate

## Built with

* Streamlit for the interface
* LangGraph for the turn taking state machine
* LangChain for prompting and model access
* Groq for model hosting

## Project structure

```
.
├── app.py              Streamlit interface
├── main.py              LangGraph debate graph: prompts, models, and state
├── .streamlit
│   └── config.toml       Custom light and dark theme
├── requirements.txt
├── img1.jpg
└── .gitignore
```

## Running it locally

### Prerequisites

* Python 3.10 or newer
* A Groq API key. 

### Steps

1. Clone the repository and move into it.
2. Create and activate a virtual environment.
   ```
   python -m venv venv
   source venv/bin/activate
   ```
   On Windows, activate it with `venv\Scripts\activate` instead.
3. Install the dependencies.
   ```
   pip install -r requirements.txt
   ```
4. Set up your environment variables.
   ```
   cp .env.example .env
   ```
   Then open `.env` and paste in your real Groq API key.
5. Start the app.
   ```
   streamlit run app.py
   ```

## Configuration

The number of rounds and the word limit per turn are fixed in `main.py` and are not exposed as controls in the interface. Open `main.py` and change `total_rounds` and `max_words` there if you want longer or shorter debates.

## License

No license has been added yet. Add one (for example MIT or Apache 2.0) before treating this as open source, if you want others to be free to reuse it.
