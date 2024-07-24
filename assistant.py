from openai import OpenAI
import json
import sys
import datetime
from tools import FileTools, LifeManager

class Logger:
    def __init__(self, filename="log.txt"):
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
    def __init__(self, filename="master_log.txt"):
        self.log = open(filename, "a")

    def log_message(self, role, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {role}: {message}\n"
        self.log.write(log_entry)
        self.log.flush()  # Ensure the log is written to the file immediately

master_logger = MasterLogger()

def append_log_to_system_message(system_message, log_filename="log.txt"):
    with open(log_filename, "r") as log_file:
        log_content = log_file.read()
    return system_message + "\n\nLog:\n" + log_content

def chat(model, messages, max_tokens, seed, temperature=0.7, tools=None, tool_choice="auto",
         system_message="Du bist ein hilfreicher Assistent und hältst deine Antworten so kurz, minimal und präzise wie möglich."):

    # Append log to system message
    system_message = append_log_to_system_message(system_message)

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
    # load tools from tools.json
    with open("Master_tools.json", "r") as file:
        tools = json.load(file)

    with open("Master_system_message.txt", "r") as file:
        system_message = file.read()

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
        # Step 2: check if the model wanted to call a function
        if tool_calls:
            messages.append(response_message)  # extend conversation with assistant's reply
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if(function_name == "call_expert"):
                    log_message = f"Calling expert for task: {function_args['task']} with expert: {function_args['expert']}"
                    print(log_message)
                    task_response = complete_task(function_args["task"], function_args["expert"])
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(task_response),
                        }
                    ) 
                    log_message = f"Task completed by expert {function_args['expert']}, Response: {task_response}"
                    print(log_message)
        else:
            log_message = f"Master:\t{response.message.content}"
            print(log_message)
            master_logger.log_message("Master", response.message.content)
            messages.append(response_message)
            return response.message.content

def complete_task(task, expert="Master"):
    # Load tools for expert
    with open(expert + "_tools.json", "r") as file:
        tools = json.load(file)

    system_message = "Du bist ein Experte und erhältst eine bestimmte Aufgabe, die du so gut wie möglich erfüllen sollst. Sobald die Aufgabe abgeschlossen ist, oder du feststellst, dass sie nicht lösbar ist, führe die 'completed_task'-function aus."

    with open(expert + "_system_message.txt", "r") as file:
        system_message += file.read()

    messages = []
    
    messages.insert(0, {"role": "system", "content": system_message})

    messages.append({"role": "user", "content": str(task)})

    i = 0

    # While there were fewer than 50 iterations and the task is not completed
    while i < 50:
        i += 1

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
        # Step 2: check if the model wanted to call a function
        if tool_calls:
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "make_directory": FileTools.make_directory,
                "remove_directory": FileTools.remove_directory,
                "list_directory": FileTools.list_directory,
                "rename_file": FileTools.rename_file,
                "copy_file": FileTools.copy_file,
                "create_file": FileTools.create_file,
                "read_file": FileTools.read_file,
                "edit_file": FileTools.edit_file,
                "update_facts": LifeManager.update_facts,
                "update_status": LifeManager.update_status,
                "add_diary_entry": LifeManager.add_diary_entry,
                "add_calendar_event": LifeManager.add_calendar_event,
                "update_todos": LifeManager.update_todos
            }  # only one function in this example, but you can have multiple
            # For each tool call, print the function name and arguments
            for tool_call in tool_calls:
                log_message = f"Function: {tool_call.function.name}, Arguments: {tool_call.function.arguments}"
                print(log_message)
            
            messages.append(response_message)  # extend conversation with assistant's reply
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                if(function_name == "completed_task"):
                    log_message = f"Task completed, Response: {function_args['response']}"
                    print(log_message)
                    return function_args["response"]
                function_to_call = available_functions[function_name]
                function_response = function_to_call(function_args)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                ) 
                log_message = f"Function: {function_name}, Response: {function_response}"
                print(log_message)

        else:
            log_message = f"Expert:\t{response.message.content}"
            print(log_message)
            messages.append(response_message)

    return "Task not completed because of too many iterations."