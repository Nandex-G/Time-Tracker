# Task Tracker

#### Video Demo: <URL>

#### Description:

- Time and task management is a big problem for many people. So, this app is made for them. This is a command-line productivity manager designed to organize activities and todos.
- The app is capable of creating Activities and Todos and has a built-in timer that can be connected to Activities.
- When users run the app, they'll first come across the HomePage. Then, they can enter different sections of the app, where they can use commands relating to each section. At the end, users can go back to the HomePage by using **"Home"** or **"H"** command, or they can run the **"Exit"** command to stop the app.

## Features

### Activity Section:
- Activities can be made with custom unchangeable names.
- Each activity has its own priority from the Priority List **(Low, Medium, and High)**, which is used to organized activities.
- Activities include a deadline and remaining time so the user knows when they are due and how much is remaining from the activities.
- Just as a todo list, activities also have a todo check that users can mark as done when they finished each activity.

- **Commands for activities are:**
    - **Add**: adds a new activity.
    - **Delete**: deletes an activity based on its ID.
    - **List**: lists all activities.
    - **Mark As Done**: mark an activity as done.

### Todo Section:
- Todos are similar to Activities, however, unlike activities they are no made to be so detailed and are designed for small and simple tasks or subtasks.
- Each todo includes only a custom unchangeable name and a priority.
- Each todo also has a **"done"** state that shows if the todo is finished or not.

- **Commands for todos are:**
    - **Add**: adds a new todo.
    - **Delete**: deletes an todo based on its ID.
    - **List**: lists all activities.
    - **Mark As Done**: mark an todo as done.

### Timer section:
- Timer section, as its names says, is a timer, but it can be connected to a selected activity by the user, then when the timer reduces the remaining time of the activity.

- **Commands for timer are:**
    - **Start**: start the timer.
    - **Stop**: stops the timer.
    - **Pause**: pauses the timer.

## Project Structure

- project/
- │
- ├── project.py
- ├── test_project.py
- ├── README.md
- │
- └── data/
    - ├── activities.csv
    - ├── todo.csv
    - ├── timer_history.csv
    - └── current_timer.json

## Functions and Classes

- The app is made of two types of functions:
    - General Functions: these functions are made to do general tasks in the app, such as reading files or requesting a prompt from the user, which are the same among all sections. They can be found in various locations in the code and are not specific to a certain section of the app. 

    - Section Functions: these functions are only designed for specific sections, such as Activity Section, Todo Section, and Timer Section. They cannot be used in other sections as the need certain data and information from the main section functions.

- For a better performance and an easier control, Timer Section works with a class called **"Timer"** that contain every function, and variable needed for the timer.

## Files
 
### project.py:

- This file includes all the codes for the app.

### test_project.py:

- This file includes the app tests.

### data folder
 
- The folder holds the storage files for each sections.

## Design Choices

- One of the main decisions I made for this project was the use of **CSV** and **JSON** files for data storage because first I didn't want to store the data in any file, but I realized in case that the user closes the app, all data will be lost. So, I designed the app in a way that a file is made for each app section.

### CSV for persistent data

- For sections, namely **Todo**, **Activities**, and **Timer_history**, CSV file are used so all data stays tidy and easy to use.

#### **Activities.csv**: This file stores the information about the activities that the user adds.

#### **Todo.csv**: This file stores the information about he todos that the user adds.

#### **Timer_history.csv**: This file stores the histories of every timer session, so they can later be used for summaries and other statistics.

### JSON for active timer

#### Timer Section uses a JSON file called **Current_timer.json** that stores the data about the current state of timer

#### The data contains:

- Status: whether the timer is **running**, **paused**, or **stopped**.
- Connected Activity: the **name** and **ID** of the activity that the timer can be connected to.
- Date: the **date** when the timer was started.
- Sessions: each session that includes the time when each session **started** and **ended**. (These session will be used at the end when calculating the final timer time)


## How to Run

- To start this app, all a user needs is to run **"python project.py"** command in the command-line interface.

- Then all the information and commands will be shown to the user by the app.

- To close the entire app, **"exit"** should be prompted.
- To see the list of each sections command, **"help"** should be prompted.

## Testing

- The file **"test_project.py"** contains tests for each section of the code that checks if the inputs, outputs, operations, files, and so on are all correct.

## Dependencies

- I tried to use as few dependencies as possible, and the ones used are only for a better, user-friendly interface:

- Texttable: it makes tables and is used when listing the information of Todo and Activity sections.
- Colorama: it is used to give some colors to the interface and inputs to make the app more user-friendly and vibrant.

## Conclusion

Overall, this project allowed me to build a complete command-line productivity manager. While developing it, I worked with concepts such as object-oriented programming, file handling, CSV and JSON data storage, input validation, and even some concepts that I haven't used before. This project also helped me understand how different parts of a real application can work together as one complete program.