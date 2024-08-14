from openai import OpenAI
import json
import sys
import datetime
from tools import FileTools, LifeManager

class Logger:
    def __init__(self, filename="log/log.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()  # Ensure the log is written to the file immediately

    def flush(self):
        pass

sys.stdout = Logger()

class MasterLogger:
    def __init__(self, filename="log/master_log.txt"):
        self.log = open(filename, "a")

    def log_message(self, role, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {role}: {message}\n"
        self.log.write(log_entry)
        self.log.flush()  # Ensure the log is written to the file immediately

master_logger = MasterLogger()

def append_log_to_system_message(system_message, log_filename="log/master_log.txt"):
    with open(log_filename, "r") as log_file:
        log_content = log_file.read()
    return system_message + "\n\nVerlauf:\n" + log_content

def prepend_basic_info(prompt):
    now = datetime.datetime.now()
    weekday = now.strftime("%A")
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S %Z")
    return f"{weekday}, {date} {time}\n\n{prompt}"

def chat(model, messages, max_tokens, seed, temperature=0.7, tools=None, tool_choice="auto",
         system_message="Du bist ein hilfreicher Assistent und hältst deine Antworten so kurz, minimal und präzise wie möglich."):

    # Add system message to messages if it is not already present
    if len(messages) == 0 or messages[0]["role"] != "system":
        messages.insert(0, {"role": "system", "content": system_message})

    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        seed=seed,
        temperature=temperature,
        tools=tools,
        tool_choice=tool_choice
    )
    return completion.choices[0]

def answer(message):
    # Load tools and system message
    with open("tools/Master_tools.json", "r") as file:
        tools = json.load(file)

    with open("sys_msgs/Master_system_message.txt", "r") as file:
        system_message = file.read()

    system_message = prepend_basic_info(system_message)
    system_message = append_log_to_system_message(system_message)

    messages = []
    messages.append({"role": "user", "content": str(message)})
    master_logger.log_message("User", message)

    while True:
        response = chat(
            model="gpt-4o-mini",
            system_message=system_message,
            tool_choice="auto",
            messages=messages,
            max_tokens=1000,
            seed=0,
            tools=tools
        )

        response_message = response.message
        tool_calls = response_message.tool_calls
        # Check if the model wanted to call a function
        if tool_calls:
            messages.append(response_message)  # extend conversation with assistant's reply
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                log_message = f"Master calls Function: {function_name}, Arguments: {tool_call.function.arguments}"
                print(log_message)

                task_response = call_tool(function_name, function_args)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(task_response),
                    }
                )
                log_message = f"Function {function_name} executed, Response: {task_response}"
                print(log_message)

        else:
            log_message = f"Master:\t{response.message.content}"
            print(log_message)
            master_logger.log_message("Master", response.message.content)
            messages.append(response_message)
            return response.message.content

def call_tool(function_name, function_args):
    # Define available tools
    available_functions = {
        "make_directory": FileTools.make_directory,
        "remove_directory": FileTools.remove_directory,
        "list_directory": FileTools.list_directory,
        "rename_file": FileTools.rename_file,
        "copy_file": FileTools.copy_file,
        "create_file": FileTools.create_file,
        "read_file": FileTools.read_file,
        "edit_file": FileTools.edit_file,
        "add_calendar_event": LifeManager.add_calendar_event,
        "remove_calendar_event": LifeManager.remove_calendar_event,
        "read_file": LifeManager.read_file
    }

    function_to_call = available_functions.get(function_name)
    if function_to_call:
        return function_to_call(function_args)
    else:
        return f"Function {function_name} not available."