import openai
from prompt_engineering.prompts import SYSTEM_PROMPT
from knw_in import retrieval_knowledge
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class Programmer:

    def __init__(self, api_key, model="gpt-3.5-turbo-1106", base_url=None):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        # if base_url and model == "llama3":
        #     self.client = openai.OpenAI(api_key="none", base_url=base_url)
        # elif base_url and model == "qwen1.5":
        #     self.client = openai.OpenAI(api_key="none", base_url=base_url)
        # elif base_url and model == "qwen2":
        #     self.client = openai.OpenAI(api_key="none", base_url=base_url)
        # else:
        #     self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
        self.messages = []
        self.function_repository = {}
        self.last_snaps = None

    def add_functions(self, function_lib: dict) -> None:
        self.function_repository = function_lib

    def _call_chat_model(self, functions=None, include_functions=False, retrieval=True):
        if retrieval:
            snaps = retrieval_knowledge(self.messages[-1]["content"])
            if snaps:
                self.last_snaps = snaps
                self.messages[-1]["content"] += snaps
            else:
                self.last_snaps = None

        params = {
            "model": self.model,
            "messages": self.messages,
            "max_tokens": 4000,
            "temperature": 0.4,
        }

        if include_functions:
            params['functions'] = functions
            params['function_call'] = "auto"

        try:
            return self.client.chat.completions.create(**params)
        except Exception as e:
            print(f"Error calling chat model: {e}")
            return None

    def _call_chat_model_streaming(self, functions=None, include_functions=False, retrieval=False, kernel=None):
        temp = self.messages[-1]["content"]
        if retrieval:
            snaps = retrieval_knowledge(self.messages[-1]["content"], kernel=kernel)
            if snaps:
                for chunk in snaps:
                    yield chunk
                self.last_snaps = snaps
                self.messages[-1]["content"] += snaps  # already add retrieval code to chat history
            else:
                self.last_snaps = None

        params = {
            "model": self.model,
            "messages": self.messages,
            "stream": True
        }

        if include_functions:
            params['functions'] = functions
            params['function_call'] = "auto"

        try:
            stream = self.client.chat.completions.create(**params)
            self.messages[-1]["content"] = temp
            for chunk in stream:
                if hasattr(chunk, 'choices') and chunk.choices[0].delta.content is not None:
                    chunk_message = chunk.choices[0].delta.content
                    yield chunk_message
        except Exception as e:
            print(f"Error calling chat model: {e}")
            return None

    def run(self, function_lib=None):
        try:
            if function_lib is None:
                response = self._call_chat_model()
                final_response = response.choices[0].message.content
                return final_response

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def clear(self):
        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]
        self.function_repository = {}


if __name__ == '__main__':
    # with open('cache/conv_cache/a83d8d2e-176b-4f3d-bace-c7a070b5e9eb-2024-05-14/programmer_msg.json', 'r') as f:
    #     messages = json.load(f)
    # p = Programmer(model="llama3",base_url="http://10.21.6.105:6068/v1")
    # p.messages = [{"role":"user","content":"Repeat the retrieved code:\n Write code to calculate the nearest correlation matrix by semismooth newton method."}]
    # #Write code to calculate the nearest correlation matrix by semismooth newton method.
    # print(p._call_chat_model().choices[0].message.content)

    # msg = ''
    # p = Programmer(model="llama3", base_url="http://10.21.6.105:6068/v1")
    # p.messages = [{"role": "system", "content": "You are an data analysis assistant, your mission is help human to do data analysis autometicly and generate report."},
    #     {"role":"user","content":"Repeat the retrieved code:\n Write code to calculate the nearest correlation matrix by semismooth newton method."}]
    # for message in p._call_chat_model_streaming():
    #     msg += message
    # print(msg)

    # test of report
    # report = p._call_chat_model_streaming().choices[0].message.content
    # print(report)
    # with open('cache/conv_cache/a83d8d2e-176b-4f3d-bace-c7a070b5e9eb-2024-05-14/report(2).md', "w") as f:
    #     f.write(report)
    #     f.close()

    # test of knowledge_integration
    p = Programmer(api_key="sk-27d5127b532c42ec90e0ce927b892159", model="deepseek-coder", base_url="https://api.deepseek.com")
    p.messages = [{"role": "system",
                   "content": "You are an data analysis assistant, your mission is help human to do data analysis autometicly and generate report."},
                  {"role":"user","content":"Train a fixed points of nonnegative neural networks. Set parameters: networks: nn_sigmoid, learning rate: 5e-3, epochs: 1, wd: 0, b: 64。"}]
    print(p._call_chat_model())



