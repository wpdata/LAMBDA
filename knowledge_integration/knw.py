"""
Knowledge Integration
Attributes:
    knw (dict): Dictionary containing the knowledge integration information.
    name (str): Name of the knowledge integration.
"""

from utils.logger import logger
import inspect
import textwrap


KNW_INJECTION = {}
def knowledge_injection(name, allow_overwrite=False):

    def decorator(knw):
        if name in KNW_INJECTION:
            if allow_overwrite:
                logger.warning(f'Knowledge `{name}` already exists! Overwriting with class {knw}.')
            else:
                raise ValueError(f'Knowledge `{name}` already exists! Please ensure that the tool name is unique.')
        if knw.name and (knw.name != name):
            raise ValueError(f'{knw.__name__}.name="{knw.name}" conflicts with @knowledge_injection(name="{name}").')
        knw.name = name
        KNW_INJECTION[name] = knw

        return knw

    return decorator

class knw:
    def __init__(self):
        self.name = 'knowledge_integration'
        self.description = 'Integrate knowledge into the LLM.'
        self.core_function = 'core_function'
        self.test_case = 'test_case'
        self.runnable_function = 'runnable_function'
        self.mode = 'full'
        # self.internal_function = 'internal_function'
        # self.fixed_function = 'fixed_function'
        self.method_code = {}
        # self.get_all_function()
    # def entrance_function(self):
    #     print("Entrance function of the knowledge integration.")

    def get_core_function(self):
        """
        Core function of the knowledge integration.
        """
        function_name = self.core_function
        core_function = getattr(self, function_name, None)
        return textwrap.dedent(core_function())

        # return self.method_code[self.core_function]

    def get_runnable_function(self):
        """
        Runnable function of the knowledge integration.
        """
        function_name = self.runnable_function
        runnable_function = getattr(self, function_name, None)
        return textwrap.dedent(runnable_function())
        #return self.method_code[self.runnable_function]

    def get_all_code(self):
        return self.get_core_function(), self.get_runnable_function()
        #return "Core code:" + self.get_core_function() + "\nOther function code" + self.get_runnable_function()

    def get_test_case(self):
        """
        Test case for the knowledge integration.
        """
        return self.method_code[self.test_case]

    def get_internal_function(self):
        """
        All other functions of the core function.
        """
        internal_code = ""
        for name, code in self.method_code.items():
            if name not in [self.core_function, self.test_case]:
                internal_code += f"{code}\n"
        return internal_code


    def get_function_code(self, function_name):
        function = getattr(self, function_name, None)
        if function is None:
            logger.warning("Method not found.")
        else:
            inspect_function = inspect.getsource(function)
            return inspect_function.replace('self,', '').replace('self.', '').replace('self','')

    def get_all_function_code(self):
        all_code = "```python"
        for name, code in self.method_code.items():
            all_code += f"\n{code}\n"
        return all_code+"```"

    def get_all_function(self):
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        self.method_code = {name: self.get_function_code(name) for name, _ in methods if name not in ['__init__', 'get_all_function', 'get_all_function_code', 'get_core_function', 'get_function_code', 'get_test_case', 'get_internal_function', 'get_fixed_function']}
        return self.method_code

    def get_fix_function(self):
        return self.method_code

    def remove_outer_indentation(code_str):  # delete the outer indentation
        # 按行分割字符串
        lines = code_str.splitlines()

        # 过滤掉空行
        non_empty_lines = [line for line in lines if line.strip()]

        if not non_empty_lines:
            return code_str  # 如果没有非空行，返回原字符串

        # 找到最小缩进
        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)

        # 去掉最小缩进
        aligned_lines = [line[min_indent:] for line in lines]

        # 重新组合为字符串
        return '\n'.join(aligned_lines)

# def get_function_code(function_name):
#     function = globals().get(function_name)
#     if function is None:
#         logger.warning("Method not found.")
#     else:
#         return inspect.getsource(function)
# def instantiate_subclasses(parent_class):
#     instances = []
#     for subclass in parent_class.__subclasses__():
#         instances.append(subclass())
#     return instances

if __name__ == '__main__':
    kwn = knw()
    # print(kwn.get_entrance_function()) #缩进问题
    print(kwn.get_all_function_code())
    # print(instantiate_subclasses(knw))