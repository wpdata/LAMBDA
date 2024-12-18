#config of the model

#model related "gpt-3.5-turbo-1106"
# conv_model = "llama3"
# programmer_model = "gpt-3.5-turbo-1106"
# inspector_model = "gpt-3.5-turbo-1106"
# conv_model = "llama3"
# programmer_model = "llama3"
# inspector_model = "llama3"
conv_model = "llama3"
programmer_model = "qwen2"
inspector_model = "qwen2"
#openai_api_key = "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"
# openai_api_key = "sk-proj-4J5yzo9EJE5rbIAnRXtvT3BlbkFJlLlcxzEkhiOBxgIUzZiX"
openai_api_key = "sk-proj-AgY2zu8TgnYoJw5SRcQvT3BlbkFJMuO0CbE6GVZxkgffG1Ah"
base_url_programmer = 'http://10.21.6.105:6068/v1'
base_url_inspector = 'http://10.21.6.105:6067/v1'
# base_url_programmer = 'http://10.21.6.105:6068/v1'
# base_url_inspector = 'http://10.21.6.105:6068/v1'
# base_url_programmer = 'http://10.21.6.105:6069/v1'
# base_url_inspector = 'http://10.21.6.105:6069/v1'

# if programmer_model == "llama3":
#     base_url_programmer = 'http://10.21.6.105:6068/v1'
#     base_url_inspector = 'http://10.21.6.105:6068/v1'
# if programmer_model == "qwen1.5":
#     base_url_programmer = 'http://10.21.6.105:6069/v1'
#     base_url_inspector = 'http://10.21.6.105:6069/v1'

#cache_related
proj_base = "/Users/stephensun/Desktop/pypro/LAMBDA"
cache_dir = "/Users/stephensun/Desktop/pypro/LAMBDA/cache/conv_cache/"
# proj_base = "/home/maojsun/proj/LAMBDA"
# cache_dir = "/home/maojsun/proj/LAMBDA/cache/conv_cache/application/"
streaming = True
# 6068:llama3, 6069:qwen1.5_32b

retrieval = False
rag_mode = "fixed"

maximum_waiting_time = 18000 #seconds