import os.path
import traceback

import openai

from app import app
from function_calling.function_calling import functions
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
from tqdm import tqdm
import random
from conversation import Conversation
# from app import app
from cache import oss


def call_llm(messages, function_lib, model="llama3"):
    if model == "llama3": #http://10.21.6.105:6075
        client = openai.OpenAI(api_key="none", base_url='http://10.21.6.105:6068/v1')
    elif model == "gpt-3.5-turbo-1106":
        client = openai.OpenAI(api_key="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")
    elif model == "qwen1.5":
        client = openai.OpenAI(api_key="none", base_url="http://10.21.6.105:6069/v1")
    elif model == "deepseek-chat":
        client = openai.OpenAI(api_key="sk-27d5127b532c42ec90e0ce927b892159", base_url="https://api.deepseek.com/beta")
    if function_lib:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            function_call="auto",
            functions=function_lib
        )
    else:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
    return response


def filter_case():
    # filter the case that the function_calling prompts contained the functions list and item does not have instruction
    with open('../function_calling/test_instruction.json', 'r') as f:
        case = json.load(f)
    filter_case = []
    for i in case:
        for j in functions:
            if 'instruction' in i and i['function_call']['name'] == j['name']:
                filter_case.append(i)

    print(len(filter_case))
    for i in range(len(filter_case)):
        if 'arguments' in filter_case[i]['function_call']:
            if filter_case[i]['function_call']['arguments'] == {}:
                filter_case[i]['function_call'].pop('arguments')

    with open('../function_calling/test_instruction_filtered.json', 'w') as f:
        json.dump(filter_case, f, indent=4)
        f.close()


# def split_case(sample_num):
#     with open('function_calling/test_instruction_filtered.json', 'r') as f:
#         inst = json.load(f)
#     selected_functions = random.sample(functions, sample_num)
#     selected_inst = []
#     for i in selected_functions:
#         for j in inst:
#             if i['name'] == j['function_call']['name']:
#                 selected_inst.append(j)
#     with open(f'function_calling/split_case/function_{sample_num}.json', 'w') as f:
#         f.write(json.dumps(selected_functions, indent=4))
#     with open(f'function_calling/split_case/instruction_{sample_num}.json', 'w') as f:
#         f.write(json.dumps(selected_inst, indent=4))
#     print(f'length of functions: {len(selected_functions)}')
#     print(f'length of instructions_r2: {len(selected_inst)}')


def generate_subsets(function_list, test_data, start=10, end=100, step=10, sample_size=100):
    for num_functions in range(start, end + 1, step):
        subsets = []
        # Randomly select functions
        selected_functions = random.sample(function_list, num_functions)
        selected_function_names = [func['name'] for func in selected_functions]

        while True:
            # Select samples that use the selected functions
            selected_samples = [sample for sample in test_data if
                                sample['function_call']['name'] in selected_function_names]
            if len(selected_samples) >= sample_size:
                break
        # If there are more samples than needed, randomly select the required number of samples

        selected_samples = random.sample(selected_samples, sample_size)
        selected_samples_names = [sample['function_call']['name'] for sample in selected_samples]
        while not all(elem in selected_samples_names for elem in selected_function_names):
            selected_samples = random.sample(selected_samples, sample_size)
            selected_samples_names = [sample['function_call']['name'] for sample in selected_samples]
        subsets.append(selected_samples)
        with open(f'function_calling/subsets/function_{num_functions}.json', 'w') as f:
            json.dump(selected_functions, f, indent=4)
        with open(f'function_calling/subsets/instruction_{num_functions}.json', 'w') as f:
            json.dump(selected_samples, f, indent=4)


def generate_subsets2(function_list, test_data, start=10, end=100, step=10, sample_size=100):
    # subsets = []

    for num_functions in tqdm(range(start, end + 1, step)):
        # Randomly select functions
        selected_functions = random.sample(function_list, num_functions)
        selected_function_names = [func['name'] for func in selected_functions]

        # Select at least one sample for each function name
        selected_samples = []
        for function_name in selected_function_names:
            function_samples = [sample for sample in test_data if sample['function_call']['name'] == function_name]
            if function_samples:
                selected_samples.append(random.choice(function_samples))

        # If there are more samples than needed, randomly select the required number of samples
        remaining_samples = [sample for sample in test_data if
                             sample not in selected_samples and sample['function_call'][
                                 'name'] in selected_function_names]
        if len(selected_samples) < sample_size and remaining_samples:
            selected_samples += random.sample(remaining_samples,
                                              min(sample_size - len(selected_samples), len(remaining_samples)))
        selected_samples_names = [sample['function_call']['name'] for sample in selected_samples]
        print(
            f"all functions in instructions_r2: {all(elem in selected_samples_names for elem in selected_function_names)}")
        print(
            f"all instructions_r2 in functions: {all(elem in selected_function_names for elem in selected_samples_names)}")
        print(f"sample_size:{len(selected_samples)}")
        with open(f'function_calling/subsets/function_{num_functions}.json', 'w') as f:
            json.dump(selected_functions, f, indent=4)
        with open(f'function_calling/subsets/instruction_{num_functions}.json', 'w') as f:
            json.dump(selected_samples, f, indent=4)


def fc_reliability(model, function_path, instruction_path):
    with open(function_path, 'r') as f:
        funcs = json.load(f)
    with open(instruction_path, 'r') as f:
        inst = json.load(f)
    total = len(inst)
    correct = 0
    msg_record = []
    for i in tqdm(range(total)):
        try:
            prompt = inst[i]['instruction']
            messages = [
                {
                    "role": "system",
                    "content": "You are a data scientist and your mission is help human to do task related to data science. You should choose tools to use."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            response_message = call_llm(messages, funcs, model).choices[0].message
            msg_record.append({"ground_truth": inst[i], "response": str(response_message)})
            if response_message.function_call:
                if response_message.function_call.name == inst[i]['function_call']['name']:
                    correct += 1
                # elif response_message.function_call.name == inst[i]['function_call']['name'] and \
                #         response_message.function_call.arguments == inst[i]['function_call']['arguments'] and consider_parameters:
                #     correct += 1
                else:
                    continue
        except Exception as e:
            print(e)
            traceback.print_exc()
            continue
    accuracy = correct / total
    print(f'Experiments of {os.path.basename(function_path)}\n'
          f'Total: {total}\nCorrect: {correct}\nAccuracy: {accuracy}')
    with open(f'function_calling/subsets/test_result_{model}_{os.path.basename(function_path)[0:-5]}.txt', 'w') as f:
        f.write(f'Experiments of {os.path.basename(function_path)}\n'
                f'Total: {total}\nCorrect: {correct}\n'
                f'Accuracy: {accuracy}\n')
    with open(f'function_calling/subsets/test_reponse_{model}_{os.path.basename(function_path)[0:-5]}.json', 'w') as f:
        json.dump(msg_record, f, indent=4)


def filter_inst_for_code_interpreter():
    with open('../function_calling/test_instruction_filtered.json', 'r') as f:
        inst = json.load(f)

    instructions_tabular = []
    for i in tqdm(range(len(inst))):
        prompt = inst[i]['instruction']
        messages = [
            {
                "role": "system",
                "content": "Here is an instruction, you should classify is the instruction can be used to do task on iris dataset (tabular data) and give decision in yes/no. Use the following example format strictly:\n"
                           "Here is an example:\nAugment the dataset by rotating images 10 degrees.\n"
                           "Thought: This instruction can only be used on image dataset, so it can not used on iris dataset.\n"
                           "Decision: no\n"
            },
            {"role": "user", "content": prompt}
        ]
        response = call_llm(messages, function_lib=None, model="gpt-3.5-turbo-1106").choices[0].message.content
        messages.append({"role": "assistant", "content": response})
        if "Yes" in response or "yes" in response or "YES" in response:
            inst[i]['filter_msg'] = response
            instructions_tabular.append(inst[i])

    with open('experiments/code_interpreter/test_instruction_code_interpreter.json', 'w') as f:
        json.dump(instructions_tabular, f, indent=4)
    print(instructions_tabular)
    print(f"Tabular instructions_r2: {len(instructions_tabular)}")


import itertools

def get_all_combinations(lst):
    all_combinations = []
    for r in range(1, len(lst) + 1):
        combinations = itertools.combinations(lst, r)
        all_combinations.extend(combinations)
    return all_combinations

# my_list = [1, 2, 3]
# combinations = get_all_combinations(my_list)
# print(combinations)

def generate_instruction():
    # for i in range(19):
    #     exist_ins = functions[i]['instruction']
    prompt_list = []
    # for i in range(50):
    #     show_ins = f'show {i} rows of the dataset.'
    #     delete_ins = f'delete the {i} rows of the dataset.'
    #     prompt_list.append(show_ins)
    #     prompt_list.append(delete_ins)
    # for col in ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']:
    #     prompt_list.append(f'standardize the column {col}')
    #     prompt_list.append(f'normalize the column {col}')
    import pandas as pd
    from cache.cache import get_general_info
    data = pd.read_csv('../application/heart_disease.csv', encoding='gbk')
    general_info = get_general_info(data)
    general_info["num_rows"], general_info["num_features"], general_info["features"], \
        general_info["col_type"], general_info["missing_val"] = general_info["num_rows"], \
        general_info["num_features"], general_info["features"], general_info["col_type"], general_info[
        "missing_val"]

    gen_info_prompt = f"This is general information of the dataset:\n{str(general_info)}\n"
    instruct = ("You should write 10 instructions_r2 of task related to the dataset without any explanation strictly, you can't repeat with example or history."
                "There is an example:\n"
                "1.Show 5 rows of the dataset."
                "2.Delete the column sex."
                "3.Standardize the dataset."
                "4.Normalize the column trestbps."
                "5.Split the dataset into training and testing set with a proportion of 8:2."
                "6.draw a correlation matrix of the dataset."
                "7.train a logistic regression model."
                "8.train a decision tree model."
                "9.train a random forest model."
                "10.train a support vector machine model."
                "begin"
                )
    messages = [
        {
            "role": "system",
            "content": gen_info_prompt
        }
    ]
    for i in tqdm(range(50)):
        messages.append({"role": "user", "content": instruct})
        response = call_llm(messages, None, model="qwen1.5").choices[0].message.content
        print(response)
        messages.append({"role": "assistant", "content": response})


    with open('../experiments/code_interpreter/generated_ins.json', 'w') as f:
        json.dump(messages, f, indent=4)


def process_generate_ci():

    gen_ins = json.load(open('../experiments/code_interpreter/generated_ins.json', 'r'))
    gen_txt = ''
    for s in gen_ins:
        if s['role'] == 'assistant':
            gen_txt += s['content'] + '\n'
    with open('../experiments/code_interpreter/generated_ins.txt', 'w') as f:
        f.write(gen_txt)



def code_interpreter_reliability():
    with open('../experiments/code_interpreter/generated_ins.txt', 'r') as file:
        lines = file.readlines()

    # 去除每行的换行符
    inst = [line.strip() for line in lines]
    total = len(inst)
    correct = 0
    # mimic the chatbot
    dataset = "application/heart_disease.csv"
    my_app = app()
    my_app.cache_file(dataset)
    system_msg = my_app.conv.programmer.messages[0][
                     "content"] + ("\nThe traget of dataset is num, it can be used to do both classification and regression task. For the following instructions_r2, you should try to write all the code that can be "
                                   "run directly, and I will directly submit it to the computer to execute. If there are "
                                   "variables or requirements you are unsure, you can define those your\n"
                                   "If there is missing any packages, you can install it by using '!pip install package_name'.\n")
    chat_history = []
    for i in tqdm(range(total)):
        my_app.conv.programmer.messages = [{"role": "system", "content": system_msg}]
        prompt = inst[i]
        chat_history = my_app.call_llm(prompt, chat_history)[1]
        print(f'Error number:{my_app.conv.error_count}, Repair number:{my_app.conv.repair_count}')
    error = my_app.conv.error_count
    error_repaired = my_app.conv.repair_count
    correct = total - (error - error_repaired)
    accuracy = correct / total
    print(
        f'Experiments of code_interpreter on {total} instructions_r2:\nError number:{error}\nRepair number:{error_repaired}\nCorrect number:{correct}\nAccuracy:{accuracy}')
    # with open('experiments/code_interpreter/chat_history.json', 'w') as f:
    #     f.write(str(chat_history))
    with open('../experiments/code_interpreter/result.txt', 'w') as f:
        f.write(
            f'Experiments of code_interpreter on {total} instructions_r2:\nError number:{error}\nRepair number:{error_repaired}\nCorrect number:{correct}\nAccuracy:{accuracy}')
    my_app.save_dialogue(chat_history)
    print('finished')


if __name__ == '__main__':
    # filter_case()
    # with open('function_calling/test_instruction_filtered.json', 'r') as f:
    #     inst = json.load(f)
    # print(len(inst))
    # generate_subsets2(functions, inst, start=10, end=100, step=10, sample_size=100)
    # fc_reliability("qwen1.5", function_path='function_calling/subsets/function_10.json',
    #               instruction_path='function_calling/subsets/instruction_10.json')
    # #ile = os.listdir('function_calling/subsets')
    # for i in range(20, 101, 10):
    #     fc_reliability("qwen1.5", function_path=f'function_calling/subsets/function_{i}.json',
    #                    instruction_path=f'function_calling/subsets/instruction_{i}.json')

    code_interpreter_reliability()
   # filter_inst_for_code_interpreter()
    #generate_instruction()
    #process_generate_ci()