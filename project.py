from datetime import datetime, timedelta, date
from colorama import Fore
from texttable import Texttable
import sys
import csv
import os
import json

activity_file_path = "data/activities.csv"
todo_file_path = "data/todo.csv"
timer_history_file_path = "data/timer_history.csv"
current_timer_file_path = "data/current_timer.json"
# --------------------------------------------------


class Timer:
    def __init__(self, current_timer_fp):
        self.status = "Stopped"
        self.dict_exists = False
        self.FORMAT = "%Y-%m-%d %H:%M:%S"
        self.current_timer_data = {}

        if os.path.exists(current_timer_fp):
            with open(current_timer_fp, "r", encoding="utf-8") as file:
                try:
                    current=json.load(file)

                except json.JSONDecodeError:
                    current={}

                required_keys = {"status", "date", "sessions"}

                if required_keys.issubset(current):
                    self.status = current["status"]

                    self.current_timer_data = current
                    self.dict_exists = True

        check_folder()
                    
            
    def start(self, fp_current_timer, activity_fp, selected_id = None):     
        check_folder()

        if self.status == "Stopped" or self.status == "Pause":
            if self.status == "Stopped":
                activity_lines, _ = reader(activity_fp)
                
                if selected_id == None:
                    list_activity(activity_fp)
                    activity_ids = get_all_ids(activity_lines)
                    activity_ids.append("none")

                    selected_id = get_validated_value("Enter the activity ID you want to connect to this timer, if you want ('none' to skip): ", activity_ids)

                connected_to_id = selected_id if selected_id != "none" else None
                connected_to_name = None  

                if connected_to_id != None:
                    for line in activity_lines:
                        if line["id"] == connected_to_id:
                            connected_to_name = line["name"]


            now = datetime.now().strftime(self.FORMAT)

            dictionary = {
                "status": "Running",
                "connected_to": connected_to_name if self.status == "Stopped" else self.current_timer_data["connected_to"],
                "connected_to_id": connected_to_id if self.status == "Stopped" else self.current_timer_data["connected_to_id"],
                "date": datetime.now().date().isoformat(),
                "sessions": [
                    {
                        "start": now,
                        "end": None
                    }
                ]
            }

            with open(fp_current_timer, "w", newline="", encoding="utf-8") as file:
                if self.dict_exists and self.current_timer_data["date"] != None:
                    dictionary = self.current_timer_data
                    dictionary["status"] = "Running"
                    dictionary["sessions"].append({"start": now, "end": None})

                self.status = "Running"
                self.dict_exists = True
                self.current_timer_data = dictionary
                json.dump(dictionary, fp=file)


            print()
            print(Fore.MAGENTA + "---------- Timer started ----------" + Fore.RESET)
            print(Fore.CYAN + " - Timer was connected to", dictionary["connected_to"] if dictionary["connected_to"] != None else "nothing" + Fore.RESET)
            return True

        else:
            print()
            print(Fore.BLUE + "Timer is already running" + Fore.RESET)
            return False


    def stop(self, fp_current_timer, fp_timer_history, fp_activity):
        check_folder()

        new_dictionary = {
            "status": "Stopped",
            "connected_to": None,
            "connected_to_id": None,
            "date": None,
            "sessions": []
        }
        

        if self.status == "Running" or self.status == "Pause":
            total_hours = 0
            total_time = timedelta()
            connected_to_name = None
            connected_to_id = None

            with open(fp_current_timer, "r", encoding="utf-8") as current_file:
                dictionary = json.load(current_file)
                connected_to_name = dictionary["connected_to"]
                connected_to_id = dictionary["connected_to_id"]

                for session in dictionary["sessions"]:
                    raw_start = session.get("start")
                    raw_end = session.get("end")

                    if session.get("end") == None:
                        raw_end = datetime.now().strftime(self.FORMAT)
                        session["end"] = raw_end

                    start, end = datetime.strptime(raw_start, self.FORMAT), datetime.strptime(raw_end, self.FORMAT)

                    total_time += end - start
                    total_seconds = (end - start).total_seconds()
                    total_hours += total_seconds / 3600

                total_hours = round(total_hours, 2)

                with open(fp_timer_history, "a", newline="", encoding="utf-8") as history_file:
                    fieldnames = ["date", "total_time", "total_hours", "connected_to", "connected_to_id", "sessions"]
                    writer = csv.DictWriter(history_file, fieldnames=fieldnames)

                    history_dict = {
                        "date": dictionary["date"],
                        "total_time": total_time,
                        "total_hours": total_hours if total_hours > 0.01 else '< 0.01',
                        "connected_to": connected_to_name,
                        "connected_to_id": connected_to_id,
                        "sessions": dictionary["sessions"]
                    }

                    if history_file.tell() == 0:
                        writer.writeheader()

                    writer.writerow(history_dict)

            with open(fp_current_timer, "w", newline="", encoding="utf-8") as new_current_file:
                json.dump(new_dictionary, fp=new_current_file)

            if connected_to_id != None:
                lines, fieldnames = reader(fp_activity)
                with open(fp_activity, "w", newline="", encoding="utf-8") as activity_file:
                    writer = csv.DictWriter(activity_file, fieldnames)

                    for line in lines:
                        if line["id"] == connected_to_id:
                            remaining_time = string_to_timedelta(line["remaining"])
                            remaining_time -= total_time

                            if remaining_time.total_seconds() <= 0:
                                line["remaining"] = "00:00:00"
                            else:
                                total_seconds = int(remaining_time.total_seconds())

                                hours = total_seconds // 3600
                                minutes = (total_seconds % 3600) // 60
                                seconds = total_seconds % 60

                                line["remaining"] = f"{hours:02}:{minutes:02}:{seconds:02}"

                            break


                    writer.writeheader()
                    writer.writerows(lines)

            self.status = "Stopped"
            self.current_timer_data = new_dictionary

            print()
            print(Fore.MAGENTA + "---------- Timer stopped ----------" + Fore.RESET)
            print(Fore.CYAN + " - Timer was connected to", connected_to_name if connected_to_name != None else "nothing" + Fore.RESET)
            print()
            print(Fore.BLUE + f" - Total time: {total_time}" + Fore.RESET)
            print()
            print(Fore.BLUE + f" - Total hours: {total_hours if float(total_hours) > 0.01 else '< 0.01'}" + Fore.RESET)
            return True          
            
        else:
            print()
            print(Fore.RED + "No timer is running" + Fore.RESET)
            return False


    def pause(self, fp_current_timer):
        check_folder()

        now = datetime.now().strftime(self.FORMAT)
        
        if self.status == "Running":
            dictionary = None
            with open(fp_current_timer, "r", encoding="utf-8") as file:
                dictionary = json.load(file)

            with open(fp_current_timer, "w", newline="", encoding="utf-8") as file:
                dictionary["sessions"][-1]["end"] = now 
                dictionary["status"] = "Pause"               

                self.status = "Pause"
                self.dict_exists = True
                self.current_timer_data = dictionary

                json.dump(dictionary, fp=file)

            print()
            print(Fore.MAGENTA + "==== Timer paused ====" + Fore.RESET)
            return True

        else:
            print()
            print(Fore.RED + "No timer is running" + Fore.RESET)
            return False


# --------------------------------------------------


#  MAIN SECTION
def main():
    check_folder()

    timer = Timer(current_timer_file_path)

    while True:
        print()
        print(Fore.MAGENTA + "----------- Home ----------" + Fore.RESET)
        print(Fore.GREEN + "Possible commands: " + Fore.RESET)
        print(Fore.BLUE + "-  Activity :==> Enter activity section")
        print("-  ToDo :==> Enter todo section")
        print("-  Timer :==> Enter timer section" + Fore.RESET)
        print()
        command = get_command(Fore.YELLOW + "Command: " + Fore.RESET)
    
        match command:
            case "activity":
                activity_section(file_path=activity_file_path)
                
            case "todo":
                todo_section(todo_file_path)
            
            case "timer":
                timer_section(timer, current_timer_file_path, timer_history_file_path, activity_file_path)

            case _:
                print()
                print(Fore.RED + "Invalid command" + Fore.RESET)


# --------------------------------------------------


# Activity Section
def activity_section(file_path):
    print_helper_data("activity")

    while True:
        print()
        activity_command = get_command("Activity command: ")

        match activity_command:
            case "add" | "a":
                print()
                print(Fore.MAGENTA + "---- Name ----" + Fore.RESET)
                name = get_validated_value("  Enter the name: ", str)

                print()
                print(Fore.MAGENTA + "---- Due ----" + Fore.RESET)
                due = get_validated_value("  Enter the due (Format: YYYY-MM-NN): ", date) 

                print()
                print(Fore.MAGENTA + "---- Priority ----" + Fore.RESET)
                priority = get_validated_value("  Enter the priority (High, Medium, or Low): ", ["high", "medium", "low"])

                print()
                print(Fore.MAGENTA + "---- Duration ----" + Fore.RESET)
                hours = get_validated_value("  Enter hours: ", int, time_validator_hours)
                minutes = get_validated_value("  Enter minutes: ", int, time_validator)
                seconds = get_validated_value("  Enter seconds: ", int, time_validator)
                duration = f"{hours:02d}:{int(minutes):02d}:{int(seconds):02d}"

                add_state = add_activity(filepath=file_path, name=name, duration=duration, due=due, priority=priority)

                if add_state:
                    print()
                    print(Fore.LIGHTGREEN_EX + "Activity created" + Fore.RESET)

                else:
                    print()
                    print(Fore.RED + "Failed to create a new activity" + Fore.RESET)

            case "delete" | "d":
                    lines, fieldnames = reader(file_path) 
                    list_state = list_activity(file_path)

                    if list_state == False:
                        print()
                        print(Fore.RED + "Failed to print the list of activities" + Fore.RESET)

                    if list_state != None:
                        selected_id = get_validated_value("Enter the activity ID that you want to delete: ", get_all_ids(lines))

                        delete_state = delete_item(file_path,selected_id, lines, fieldnames)

                        if delete_state:    
                            print()
                            print(Fore.GREEN + selected_id, "was successfully deleted" + Fore.RESET)

                        else:
                            print()
                            print(Fore.RED + "Failed to delete the activity" + Fore.RESET)
            
            case "list" | "l":
                list_state = list_activity(file_path)

                if list_state == False: 
                    print()
                    print(Fore.RED + "Failed to list activities" + Fore.RESET)

            case "markasdone" | "mad":
                lines, fieldnames = reader(file_path)
                list_state = list_activity(file_path)

                if list_state == False:
                    print()
                    print(Fore.RED + "Failed to print the list of activities" + Fore.RESET)
                    
                if list_state != None:
                    selected_id = get_validated_value("Enter the activity ID that you want to mark as done: ", get_all_ids(lines))

                    mad_state = mark_activity_as_done(file_path, selected_id, lines, fieldnames)

                    if mad_state:
                        print()
                        print(Fore.GREEN + selected_id, "has been marked as done." + Fore.RESET)

                    else:
                        print()
                        print(Fore.GREEN + "Activity is already done" + Fore.RESET)
                
            case "help" | "commands":
                print_helper_data("activity")

            case "home" | "h":
                break

            case _:
                print()
                print(Fore.RED + "Invalid activity command" + Fore.RESET)

# Activity Section Functions
def add_activity(filepath, name: str, duration: str, due: str, priority: str):
    check_folder()
    try:

        if filepath == None or not isinstance(filepath, str):
            raise ValueError("File path not given or wrong file path")

        if (name == None) or (duration == None) or (due == None) or (priority == None):
            raise ValueError("Missing argument")

        if priority not in ["high", "medium", "low"]:
            raise ValueError("Wrong priority")

        activity_list = {
            "id": get_next_id(filepath), 
            "name": name, 
            "due": due,
            "priority": priority,
            "duration": duration,
            "remaining": duration,
            "state": "Undone"
        }

        with open(filepath, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file, 
                fieldnames=["id", "name", "due", "priority", "duration",  "remaining", "state"]
            )

            if file.tell() == 0:
                writer.writeheader()

            writer.writerow(activity_list)

            return True

    except ValueError:
        return False

def list_activity(filepath):
    lines, fieldnames = reader(filepath)
    priorities = {
        "high": 0,
        "medium": 1,
        "low": 2
    }

    if len(lines) == 0:
        print()
        print(Fore.RED + "No activity exists" + Fore.RESET)
        return None

    else:
        try:
            t = Texttable()
            t.header(fieldnames)

            sorted_lines = sorted(
                lines, 
                key= lambda row: priorities.get(row["priority"].lower(), 99)
            )

            for line in sorted_lines:
                t.add_row(line.values())

            print()
            print(t.draw())

        except (KeyError, TypeError, ValueError) as e:
            print(Fore.RED + "ERROR:" + Fore.RESET, e)
            return False
        
        return True

def mark_activity_as_done(filepath, selected_id, lines, fieldnames):
    check_folder()

    found = False
    
    try:
        for line in lines:
            if line["id"] == selected_id:
                found = True

                if line["state"].lower() == "done":
                    return False
                else:
                    line["state"] = "Done"

        if found: 
            with open(filepath, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames)

                writer.writeheader()
                writer.writerows(lines)

            return True

        else:
            raise ValueError("Selected ID not found")

    except (KeyError, ValueError, TypeError) as e:
        print(Fore.RED + "ERROR:" + Fore.RESET, e)
        return 


# --------------------------------------------------


# Todo Section 
def todo_section(file_path):
    print_helper_data("todo")

    while True:
        print()
        todo_command = get_command("Todo command: ")

        match todo_command:
            case "add" | "a":
                name = get_validated_value("Enter the name: ", str)
                priority = get_validated_value("Enter the priority (High, Medium, or Low): ", ["high", "medium", "low"])

                add_state = add_todo(filepath=file_path, name=name, priority=priority)

                if add_state:
                    print()
                    print(Fore.GREEN + "ToDo created" + Fore.RESET)
                else:
                    print()
                    print(Fore.RED + "Failed to create a new todo" + Fore.RESET)

            case "delete" | "d":
                lines, fieldnames = reader(file_path)
                list_state = list_todo(file_path)

                if list_state == False:
                    print()
                    print(Fore.RED + "Failed to print the list of todos" + Fore.RESET)

                if list_state != None:
                    selected_id = get_validated_value("Enter the activity ID that you want to delete: ", get_all_ids(lines))

                    delete_state = delete_item(file_path, selected_id, lines, fieldnames)

                    if delete_state:
                        print()
                        print(Fore.GREEN + selected_id, "was successfully deleted" + Fore.RESET)
                    else:
                        print()
                        print(Fore.RED + "Failed to delete the selected todo" + Fore.RESET)

            case "list" | "l":
                list_state = list_todo(file_path)

                if list_state == False:
                    print()
                    print(Fore.RED + "Failed to list todos" + Fore.RESET)

            case "markasdone" | "mad":
                lines, fieldnames = reader(file_path)
                list_state = list_todo(file_path)

                if list_state == False:
                    print()
                    print(Fore.RED + "Failed to print the list of todos" + Fore.RESET)

                if list_state != None:
                    selected_id = get_validated_value("Enter the todo ID that you want to mark as done: ", get_all_ids(lines))

                    mad_state = mark_todo_as_done(file_path, selected_id, lines, fieldnames)

                    if mad_state != False:
                        print()
                        print(Fore.GREEN + selected_id, "has been marked as done." + Fore.RESET)
                    else:
                        print()
                        print(Fore.GREEN + "Todo is already done" + Fore.RESET)
                                        
            case "help" | "commands":
                print_helper_data("todo")

            case "home" | "h":
                break

            case _:
                print()
                print(Fore.RED + "Invalid todo command" + Fore.RESET)

# Todo Section Functions:
def add_todo(filepath, name: str, priority: str):
    check_folder()
    try:
        if name == None or priority == None:
            raise ValueError("Missing argument")

        if priority not in ["high", "medium", "low"]:
            raise ValueError("Wrong priority")

        todo_dict = {
            "id": get_next_id(filepath), 
            "name": name, 
            "priority": priority,
            "done": False
        }

        with open(filepath, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file, 
                fieldnames=["id", "name", "priority", "done"]
            )

            if file.tell() == 0:
                writer.writeheader()

            writer.writerow(todo_dict)

            return True
    except ValueError:
        return False
    
def list_todo(filepath):
    check_folder()
    lines, fieldnames = reader(filepath)
    priorities = {
        "high": 0,
        "medium": 1,
        "low": 2
    }
    copy_lines = lines.copy()

    if len(lines) == 0:
        print(Fore.RED + "No todo exists" + Fore.RESET)
        print()
        return None

    else:
        try:
            t = Texttable()
            t.header(fieldnames)

            display_lines = sorted(
                copy_lines, 
                key= lambda line: priorities.get(line["priority"].lower(), 99)
            )

            for line in display_lines:
                match line["priority"]:
                    case "high":
                        line["priority"] = "⭐⭐⭐"
                    case "medium":
                        line["priority"] = "⭐⭐"
                    case "low":
                        line["priority"] = "⭐"

                if line["done"] == "True":
                    line["done"] = "✔"
                else:
                    line["done"] = "✖"
                        
                t.add_row(line.values())

            print()
            print(t.draw())

        except (KeyError, TypeError, ValueError) as e:
            print(Fore.RED + "ERROR:" + Fore.RESET, e)
            return False

        return True

def mark_todo_as_done(filepath, selected_id, lines, fieldnames): 
    check_folder()

    found = False

    try:
        for line in lines:
            if line["id"] == selected_id:
                found = True
                if line["done"] == "True":
                    return False
                else:
                    line["done"] = "True"

        if found:
            with open(filepath, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames)

                writer.writeheader()
                writer.writerows(lines)
                
                return True

        else:
            raise ValueError("Selected ID not found")

    except (ValueError, KeyError, TypeError) as e:
        print(Fore.RED + "ERROR:" + Fore.RESET, e)
        return 

    
# --------------------------------------------------


# Timer Section
def timer_section(timer, fp_current_timer, fp_timer_history, fp_activity):
    print_helper_data("timer")

    while True:
        print()
        timer_command = get_command(Fore.YELLOW + "Timer command: " + Fore.RESET)

        match timer_command:
            case "start":
                timer.start(fp_current_timer, fp_activity)

            case "stop":
                timer.stop(fp_current_timer, fp_timer_history, fp_activity)

            case "pause":
                timer.pause(fp_current_timer)

            case "help" | "commands":
                print()
                print_helper_data("timer")

            case "home" | "h":
                break

            case _:
                print()
                print(Fore.RED + "Invalid time command" + Fore.RESET)

# Time Section Functions:
def time_validator(time):
    try:
        time = int(time)

        if time >= 0 and time < 60:
            return time
        else:
            return 
        
    except ValueError:
        print(Fore.RED + "Invalid time" + Fore.RESET)
        return

def time_validator_hours(time):
    try:
        time = int(time)

        if time >= 0:
            return time
        else:
            return
        
    except ValueError:
        print(Fore.RED + "Invalid time" + Fore.RESET)
        return

def string_to_timedelta(time_string):
    try:
        hours, minutes, seconds = map(int, time_string.split(":"))

        return timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )
    
    except ValueError:
        return


# --------------------------------------------------


# General Section
def check_folder():
    if not os.path.exists("data"):
        os.mkdir("data")

def reader(filepath=None):
    check_folder()

    stored_lines = []
    stored_fieldnames = []
    
    try:
        if filepath == None or not isinstance(filepath, str):
            raise ValueError

        with open(filepath, "r") as file:
            reader = csv.DictReader(file)
            
            for line in reader:
                stored_lines.append(line)

            stored_fieldnames = reader.fieldnames

            if stored_fieldnames == None:
                stored_fieldnames = []

            return stored_lines, stored_fieldnames        

    except FileNotFoundError:
        return ([], [])

    except ValueError:
        print(Fore.RED + "Couldn't read the file: filepath is invalid or not given" + Fore.RESET)
        return ([], [])
    
def get_all_ids(lines=None):
    check_folder()

    ids = []

    if lines == None:
        lines = []

    try:
        for line in lines:
            ids.append(line["id"])
    except KeyError:
        print(Fore.RED + "Failed to get ids: invalid lines" + Fore.RESET)

    return ids

def get_next_id(file_path = None):
    check_folder()
    try:
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            ids = []
            
            for line in reader:
                ids.append(int(line["id"]))

            if len(ids) == 0:
                return 1
            else:
                return max(ids) + 1

    except FileNotFoundError:
        return 1   

    except (ValueError, KeyError) as e:
        print(Fore.RED + "ERROR:" + Fore.RESET, e)
        return 

def get_command(prompt = "Prompt: "):
    check_folder()
    command = input(Fore.YELLOW + prompt + Fore.RESET).lower().strip()
    if command == "exit":
        sys.exit()

    return command

def get_validated_value(prompt = "Prompt: ", validator_type = None, validator = None):  
    while True:
        check_folder()
        try:
            if validator_type == None:
                raise TypeError

            print()
            value = input(Fore.YELLOW + prompt + Fore.RESET).lower().strip()
            
            if value == "exit":
                sys.exit()

            if validator == None:
                if isinstance(validator_type, (list, tuple, set)):
                    if value in validator_type:
                        return value
                    else:
                        print()
                        print(Fore.RED + "Invalid input" + Fore.RESET)
                        
                else:
                    if validator_type == int:
                        value = int(value)

                    elif validator_type == float:
                        value = float(value)

                    if validator_type == date:
                        print(validator_type, value)
                        value = datetime.fromisoformat(value).date()
                        

                    if isinstance(value, validator_type):
                        if validator_type == str and not value:
                            print(Fore.RED + "Value cannot be empty" + Fore.RESET)

                        else:
                            return value
                    
                    else:
                        print()
                        print(Fore.RED + "Invalid input" + Fore.RESET)

            else:
                value = validator(value)

                if value != None:
                    return value
                
                else:
                    print()
                    print(Fore.RED + "Invalid input" + Fore.RESET)

        except ValueError as e:
            print()
            print(Fore.RED + f"Invalid input" + Fore.RESET)    

        except TypeError:
            print()
            print(Fore.RED + "Unknown type: the type is wrong or not given" + Fore.RESET)

def delete_item(file_path, selected_id, old_lines, fieldnames):
    check_folder()

    found = False
    try:
        for line in old_lines:
            if line["id"] == selected_id:
                found = True

        if found:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames)

                writer.writeheader()
                writer.writerows(filter(lambda line: not line["id"] == selected_id, old_lines))

                return True
        else:
            return
        
    except (ValueError, KeyError) as e:
        print(Fore.RED + "ERROR:" + Fore.RESET, e)
        return False


# --------------------------------------------------


def print_helper_data(section):
    print()
    match section:
        case "activity":
            print(Fore.MAGENTA + "----------- Activity Section ----------" + Fore.RESET)
            print(Fore.GREEN + "Possible commands: " + Fore.RESET)
            print(Fore.BLUE + "-  add OR A :==> Add an activity")
            print("-  delete OR D :==> Delete an activity")
            print("-  list OR L :==> List all the existing activities")
            print("-  markAsDone OR MAD :==> Mark an activity as done"  + Fore.RESET)
            
        case "todo":
            print(Fore.MAGENTA + "----------- ToDo Section ----------" + Fore.RESET)
            print(Fore.GREEN + "Possible commands: " + Fore.RESET)
            print(Fore.BLUE + "-  add OR A :==> Add a todo")
            print("-  delete OR D :==> Delete a todo")
            print("-  list OR L :==> List all the existing todos")
            print("-  markAsDone OR MAD :==> Mark a todo as done"  + Fore.RESET)

        case "timer":
            print(Fore.MAGENTA + "----------- Timer Section ----------" + Fore.RESET)
            print(Fore.GREEN + "Possible commands: " + Fore.RESET)
            print(Fore.BLUE + "-  start :==> Start (or unpause) the timer")
            print("-  stop :==> Stop the timer")
            print("-  pause :==> Pause the timer"  + Fore.RESET)

        case _:
            print(Fore.RED + "Failed to print helper data: invalid section" + Fore.RESET)
            return

    print()
    print(Fore.CYAN + "-  home OR H :==> Back to home")
    print("-  help OR commands :==> See possible commands")
    print("-  exit :==> Exit the program" + Fore.RESET)


# ==================================================

if __name__ == "__main__":
    main()