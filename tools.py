import os
import shutil
import json
from datetime import datetime

class FileTools:
    @staticmethod
    def make_directory(params):
        """Creates a new directory at the specified path."""
        path = params.get('path')
        try:
            os.makedirs(path)
            return True
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False

    @staticmethod
    def remove_directory(params):
        """Removes the directory at the specified path."""
        path = params.get('path')
        try:
            shutil.rmtree(path)
            return True
        except Exception as e:
            print(f"Error removing directory: {e}")
            return False

    @staticmethod
    def list_directory(params):
        """Lists all files and directories within the specified path."""
        path = params.get('path')
        try:
            return os.listdir(path)
        except Exception as e:
            print(f"Error listing directory contents: {e}")
            return f"Error listing directory contents: {e}"

    @staticmethod
    def rename_file(params):
        """Renames a file from old_path to new_path."""
        old_path = params.get('old_path')
        new_path = params.get('new_path')
        try:
            os.rename(old_path, new_path)
            return True
        except Exception as e:
            print(f"Error renaming file: {e}")
            return False

    @staticmethod
    def copy_file(params):
        """Copies a file from source_path to destination_path."""
        source_path = params.get('source_path')
        destination_path = params.get('destination_path')
        try:
            shutil.copy2(source_path, destination_path)
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
            return False

    @staticmethod
    def create_file(params):
        """Creates a new file and writes content to it."""
        path = params.get('path')
        content = params.get('content', '')
        try:
            with open(path, 'w') as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"Error creating file: {e}")
            return False

    @staticmethod
    def read_file(params):
        """Reads content from a file."""
        path = params.get('path')
        try:
            with open(path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return f"Error reading file: {e}"

    @staticmethod
    def edit_file(params):
        """Edits a file by appending or overwriting content."""
        path = params.get('path')
        content = params.get('content', '')
        mode = params.get('mode', 'a')  # Default mode is 'a' (append). Use 'w' for overwrite.
        try:
            with open(path, mode) as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"Error editing file: {e}")
            return False


class LifeManager:
    base_path = "/Users/niklas/Desktop/Assistant/"

    @staticmethod
    def _get_file_path(file_name):
        return os.path.join(LifeManager.base_path, file_name)

    @staticmethod
    def update_facts(facts):
        path = LifeManager._get_file_path("facts.json")
        try:
            if os.path.exists(path):
                with open(path, 'r') as file:
                    data = json.load(file)
            else:
                data = {}
            data.update(facts)
            with open(path, 'w') as file:
                json.dump(data, file, indent=4)
            return True
        except Exception as e:
            print(f"Error updating facts: {e}")
            return False

    @staticmethod
    def update_status(status):
        path = LifeManager._get_file_path("status.txt")
        try:
            with open(path, 'w') as file:
                file.write(status)
            return True
        except Exception as e:
            print(f"Error updating status: {e}")
            return False

    @staticmethod
    def add_diary_entry(entry):
        path = LifeManager._get_file_path("diary.json")
        try:
            if os.path.exists(path):
                with open(path, 'r') as file:
                    diary = json.load(file)
            else:
                diary = []
            diary.append(entry)
            with open(path, 'w') as file:
                json.dump(diary, file, indent=4)
            return True
        except Exception as e:
            print(f"Error adding diary entry: {e}")
            return False

    @staticmethod
    def add_calendar_event(event):
        path = LifeManager._get_file_path("calendar.json")
        #try:
        if os.path.exists(path):
            with open(path, 'r') as file:
                calendar = json.load(file)
        else:
            calendar = []
        calendar.append(event)
        with open(path, 'w') as file:
            json.dump(calendar, file, indent=4)
        return True
        #except Exception as e:
        #    print(f"Error adding calendar event: {e}")
        #    return False
        
    @staticmethod
    def remove_calendar_event(rm_event):
        path = LifeManager._get_file_path("calendar.json")
        try:
            if os.path.exists(path):
                with open(path, 'r') as file:
                    calendar = json.load(file)
            else:
                print("Calendar file does not exist.")
                return False
            
            updated_calendar = [event for event in calendar if not (event.get('datum') == rm_event["date"] and event.get('name') == rm_event["name"])]
            
            with open(path, 'w') as file:
                json.dump(updated_calendar, file, indent=4)
            return True
        except Exception as e:
            print(f"Error removing calendar event: {e}")
            return False

    @staticmethod
    def update_todos(todos):
        path = LifeManager._get_file_path("todos.json")
        try:
            if os.path.exists(path):
                with open(path, 'r') as file:
                    data = json.load(file)
            else:
                data = {"todos": [], "completed": []}
            data.update(todos)
            with open(path, 'w') as file:
                json.dump(data, file, indent=4)
            return True
        except Exception as e:
            print(f"Error updating todos: {e}")
            return False
    @staticmethod
    def read_file(args):
        
        file_key = args.get("file_key")

        file_map = {
            "facts": "facts.json",
            "status": "status.txt",
            "diary": "diary.json",
            "calendar": "calendar.json",
            "todos": "todos.json"
        }
        if file_key in file_map:
            path = LifeManager._get_file_path(file_map[file_key])
            try:
                if (os.path.exists(path)):
                    with open(path, 'r') as file:
                        content = file.read()
                    return content
                else:
                    print(f"File for {file_key} does not exist.")
                    return None
            except Exception as e:
                print(f"Error reading file for {file_key}: {e}")
                return None
        else:
            print(f"Invalid file key: {file_key}")
            return None