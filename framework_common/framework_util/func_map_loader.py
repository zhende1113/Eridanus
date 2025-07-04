import os
import importlib
import traceback

from developTools.utils.logger import get_logger
import copy


def convert_gemini_to_openai(gemini_tools):
    openai_functions = []

    for tool in gemini_tools:
        #print(tool)
        openai_function = {
            "type": "function",
            "function": {
                "name": tool.get("name"),
                "description": tool.get("description", ""),
                "parameters": copy.deepcopy(tool.get("parameters", {}))
            }
        }

        # Ensure 'parameters' has all required fields for OpenAI format
        if "parameters" in openai_function["function"].keys():
            parameters = openai_function["function"]["parameters"]
            parameters.setdefault("type", "object")
            parameters.setdefault("properties", {})
            parameters.setdefault("required", [])
            parameters["additionalProperties"] = False

        openai_functions.append(openai_function)

    return openai_functions


logger = get_logger()
PLUGIN_DIR = "run"
dynamic_imports = {}
function_declarations = []

# **遍历 run 目录及子目录，查找 `__init__.py`**
for root, dirs, files in os.walk(PLUGIN_DIR):
    if "__init__.py" in files:
        module_name = root.replace(os.sep, ".")  # 转换为 Python 模块名
        try:
            module = importlib.import_module(module_name)  # 导入模块

            # **加载 dynamic_imports**
            if hasattr(module, "dynamic_imports"):
                dynamic_imports.update(module.dynamic_imports)
                #print(f"✅ 发现并加载 {module_name}.dynamic_imports")

            # **加载 function_declarations**
            if hasattr(module, "function_declarations"):
                function_declarations.extend(module.function_declarations)
                #print(f"✅ 发现并合并 {module_name}.function_declarations")

        except Exception as e:
            logger.error(f"❌ 无法导入 {module_name}: {e}")
            traceback.print_exc()


def openai_func_map():
    return convert_gemini_to_openai(function_declarations)


def gemini_func_map():
    return {"function_declarations": function_declarations}
