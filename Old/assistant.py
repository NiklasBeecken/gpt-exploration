import assistant
from tools import FileTools
import json

def main():

    # load tools from tools.json
    with open("tools.json", "r") as file:
        tools = json.load(file)
    
    messages = []
    while True:
        
        # If the last message is a tool message, the user doesnt have to input a message
        if len(messages)==0 or dict(messages[-1])["role"] == "assistant":
            message = input("* * *\t")
            # Wenn der User exit schreibt, beende den Prozess
            if message == "exit":
                break
        
            messages.append({"role": "user", "content": str(message)})

        response = assistant.chat(
            model="gpt-3.5-turbo-0125",
            system_message="Du bist ein hilfreicher Assistent. Du hältst deine Antworten so kurz, minimal und präzise wie möglich.",
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
            }

            print("Action:\t" + response.message.tool_calls[0].function.name + " " + response.message.tool_calls[0].function.arguments)
            messages.append(response_message)  # extend conversation with assistant's reply
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(function_args)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )  # extend conversation with function response
        else:
            print("GPT:\t" + response.message.content)
            messages.append(response_message)
            
        print("")

if __name__ == "__main__":
    main()