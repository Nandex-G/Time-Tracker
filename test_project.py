from project import activity_section, todo_section, timer_section, Timer
from project import add_activity, list_activity, mark_activity_as_done
from project import add_todo, list_todo, mark_todo_as_done
from project import time_validator, string_to_timedelta, reader, get_all_ids, get_next_id, get_command, get_validated_value, delete_item

import pytest
import os
import datetime
import csv

# ---- Variables ----

activity_file_path = "test_activity.csv"
todo_file_path = "test_todo.csv"

current_timer_file_path = "test_current_timer.json"
timer_history_file_path = "test_timer_history.csv"

test_file_path = "test.csv"
empty_test_file_path = "empty_test.csv"

# ---- Files ----

@pytest.fixture
def activity_file():
    yield activity_file_path

    if os.path.exists(activity_file_path):
        os.remove(activity_file_path)

@pytest.fixture
def todo_file():
    yield todo_file_path
    
    if os.path.exists(todo_file_path):
        os.remove(todo_file_path)

@pytest.fixture
def timer_file_current():
    yield current_timer_file_path

    if os.path.exists(current_timer_file_path):
        os.remove(current_timer_file_path)

@pytest.fixture
def timer_file_history():
    yield timer_history_file_path

    if os.path.exists(timer_history_file_path):
        os.remove(timer_history_file_path)

@pytest.fixture
def test_file():
    yield test_file_path

    if os.path.exists(test_file_path):
        os.remove(test_file_path)

@pytest.fixture
def empty_test_file():
    yield empty_test_file_path

    if os.path.exists(empty_test_file_path):
        os.remove(empty_test_file_path)

# ---- Activity Section ----

def test_activity_section(monkeypatch, capsys, activity_file):
    inputs = iter([
        "add", "Test", "2026-01-01", "high", "11", "11", "11", 
        "markasdone", "1", 
        "markasdone", "1", 
        "delete", "1", 
        "home"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    try:
        activity_section(activity_file)

    except StopIteration:
        pytest.fail("Not enough test inputs")

    captured = capsys.readouterr()

    assert "Activity created" in captured.out
    assert "1 was successfully deleted" in captured.out
    assert "1 has been marked as done" in captured.out
    assert "Activity is already done" in captured.out

class TestActivity:
    def test_list_activity_empty(self, activity_file):
        assert list_activity(activity_file) == None

    def test_add_activity(self, activity_file):
        assert add_activity(activity_file, "Test", "00:00:00", "2026-01-01", "high") == True
            
    def test_mark_activity_as_done(self, activity_file):
        add_activity(activity_file, "Test", "00:00:00", "2026-01-01", "high")
        lines, fieldnames = reader(activity_file)

        assert mark_activity_as_done(activity_file, "1", lines, fieldnames) == True

    def test_already_mark_activity_as_done(self, activity_file):
        add_activity(activity_file, "Test", "00:00:00", "2026-01-01", "high")
        lines, fieldnames = reader(activity_file)
        mark_activity_as_done(activity_file, "1", lines, fieldnames)

        assert mark_activity_as_done(activity_file, "1", lines, fieldnames) == False

    def test_list_activity(self, activity_file):
        add_activity(activity_file, "Test", "00:00:00", "2026-01-01", "high")

        assert list_activity(activity_file) == True
        assert list_activity("Nothing") == None

    def test_delete_activity(self, activity_file):
        add_activity(activity_file, "Test", "00:00:00", "2026-01-01", "high")
        lines, fieldnames = reader(activity_file)
    
        assert delete_item(activity_file, "1", lines, fieldnames) == True

    def test_delete_nonexistent_activity(self, activity_file):
        add_activity(activity_file, "Test", "00:00:00", "2026-01-01", "high")
        lines, fieldnames = reader(activity_file)
    
        assert delete_item(activity_file, "99", lines, fieldnames) == None


# ---- Todo Section ----
        
def test_todo_section(capsys, monkeypatch, todo_file):
    inputs = iter([
        "add", "Test", "low", 
        "markasdone", "1",
        "markasdone", "1",
        "delete", "1",
        "list",
        "home"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    try:
        todo_section(todo_file)

    except StopIteration:
        pytest.fail("Not enough test inputs")

    captured = capsys.readouterr()

    assert "ToDo created" in captured.out
    assert "1 was successfully deleted" in captured.out
    assert "1 has been marked as done" in captured.out
    assert "Todo is already done" in captured.out

class TestTodo:
    def test_list_todo_empty(self, todo_file):
        assert list_todo(todo_file) == None

    def test_add_todo(self, todo_file):
        assert add_todo(todo_file, "Test", "high") == True

    def test_list_todo_undone(self, todo_file):
        add_todo(todo_file, "Test", "high")

        assert list_todo(todo_file) == True

    def test_mark_todo_as_done(self, todo_file):
        add_todo(todo_file, "Test", "high")

        lines, fieldnames = reader(todo_file)

        assert mark_todo_as_done(todo_file, "1", lines, fieldnames) == True

    def test_list_todo_done(self, todo_file):
        add_todo(todo_file, "Test", "high")

        assert list_todo(todo_file) == True

    def test_already_mark_todo_as_done(self, todo_file):
        add_todo(todo_file, "Test", "high")

        lines, fieldnames = reader(todo_file)

        mark_todo_as_done(todo_file, "1", lines, fieldnames)

        assert mark_todo_as_done(todo_file, "1", lines, fieldnames) == False

    def test_delete_todo(self, todo_file):
        add_todo(todo_file, "Test", "high")

        lines, fieldnames = reader(todo_file)

        assert delete_item(todo_file, "1", lines, fieldnames) == True

    def test_delete_nonexistent_todo(self, todo_file):
        add_todo(todo_file, "Test", "high")

        lines, fieldnames = reader(todo_file)

        assert delete_item(todo_file, "99", lines, fieldnames) == None


# ---- Timer Section ----

def test_timer_section(capsys, monkeypatch, timer_file_current, timer_file_history, activity_file):
    inputs = iter([
        "start", 
        "none",
        "pause",
        "start", 
        "stop",
        "home"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    try:
        timer = Timer(timer_file_current)
        timer_section(timer, timer_file_current, timer_file_history, activity_file)

    except StopIteration:
        pytest.fail("Not enough test inputs")

    captured = capsys.readouterr()

    assert "Timer started" in captured.out
    assert "Timer paused" in captured.out
    assert "Timer stopped" in captured.out

class TestTimer:
    def test_start(self, timer_file_current, activity_file):
        timer = Timer(timer_file_current)

        assert timer.start(timer_file_current, activity_file, selected_id="none") == True

    def test_already_start(self, timer_file_current, activity_file):
        timer = Timer(timer_file_current)
        timer.start(timer_file_current, activity_file, selected_id="none")

        assert timer.start(timer_file_current, activity_file, selected_id="none") == False

    def test_pause(self, timer_file_current, activity_file):
        timer = Timer(timer_file_current)
        timer.start(timer_file_current, activity_file, selected_id="none")

        assert timer.pause(timer_file_current) == True

    def test_already_paused(self, timer_file_current, activity_file):
        timer = Timer(timer_file_current)
        timer.start(timer_file_current, activity_file, selected_id="none")
        timer.pause(timer_file_current)

        assert timer.pause(timer_file_current) == False

    def test_unpause(self, timer_file_current, activity_file):
        timer = Timer(timer_file_current)
        timer.start(timer_file_current, activity_file, selected_id="none")
        timer.pause(timer_file_current)

        assert timer.start(timer_file_current, activity_file, selected_id="none") == True

    def test_stop(self, timer_file_current, timer_file_history, activity_file):
        timer = Timer(timer_file_current)
        timer.start(timer_file_current, activity_file, selected_id="none")

        assert timer.stop(timer_file_current, timer_file_history, activity_file) == True

    def test_stop_paused(self, timer_file_current, timer_file_history, activity_file):
        timer = Timer(timer_file_current)
        timer.start(timer_file_current, activity_file, selected_id="none")
        timer.pause(timer_file_current)

        assert timer.stop(timer_file_current, timer_file_history, activity_file) == True

    def test_not_timer_is_running(self, timer_file_current, timer_file_history):
        timer = Timer(timer_file_current)

        assert timer.stop(timer_file_current, timer_file_history, activity_file) == False


# ---- General Functions ----

def test_time_validator():
    assert time_validator(50) == 50
    assert time_validator(100) == None

def test_string_to_timedelta():
    assert isinstance(string_to_timedelta("01:00:00"), datetime.timedelta)
    assert string_to_timedelta("HELLO") == None

def test_reader(test_file, empty_test_file):
    with open(test_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, ["id"])
        writer.writeheader()
        writer.writerow({"id": 1})

    open(empty_test_file, "w").close()

    lines1, fieldnames1 = reader(test_file)
    lines2, fieldnames2 = reader("NOTHING")

    assert lines1 == [{"id": "1"}]
    assert fieldnames1 == ["id"]

    assert lines2 == []
    assert fieldnames2 == []

    assert reader(empty_test_file) == ([], [])

def test_get_all_ids(test_file):
    with open(test_file, "w", newline="", encoding="utf-8") as file:
        dict_reader = csv.DictWriter(file, ["id"])
        dict_reader.writeheader()
        dict_reader.writerows([
            {"id": "1"},
            {"id": "2"}
        ])


    lines, _ = reader(test_file)

    assert get_all_ids(lines) == ["1", "2"]
    assert get_all_ids() == []

def test_get_next_id(test_file):
    with open(test_file, "w", newline="", encoding="utf-8") as file:
        dict_reader = csv.DictWriter(file, ["id"])
        dict_reader.writeheader()
        dict_reader.writerows([
            {"id": "1"}, 
            {"id": "2"}
        ])

    assert get_next_id(test_file) == 3
    assert get_next_id("NOTING") == 1

def test_get_command(monkeypatch):
    inputs = iter([
        "1"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    assert get_command("Hello") == "1"

def test_get_validated_value(monkeypatch):
    inputs = iter([
        "1",
        "HELLO",
        "10",
        "0",

        "test",
        "",
        "yo",

        "test1",
        "test2",
        "high",

        "asdf",
        "2000/01/01",
        "2000-1-1",
        "2000-01-01"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    assert get_validated_value("Number: ", int) == 1
    assert get_validated_value("Number: ", int) == 10
    assert get_validated_value("Number: ", int) == 0

    assert get_validated_value("String: ", str) == "test"
    assert get_validated_value("String: ", str) == "yo"

    assert get_validated_value("Priority: ", ["high", "medium", "low"]) == "high"

    assert get_validated_value("Date: ", datetime.date) == datetime.date(2000, 1, 1)

def test_delete_item(test_file):
    with open(test_file, "w", newline="", encoding="utf-8") as file:
        dict_reader = csv.DictWriter(file, ["id"])
        dict_reader.writeheader()
        dict_reader.writerows([
            {"id": "1"}, 
            {"id": "2"}
        ])

    lines, fieldnames = reader(test_file)

    assert delete_item(test_file, "1", lines, fieldnames) == True