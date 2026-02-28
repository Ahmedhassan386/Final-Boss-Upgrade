# Example for Project 3 (Task + Project).
# Same pattern works for other projects.
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


STATUS = ("TODO", "DOING", "DONE")

@dataclass
class Task:
    task_id: int
    title: str
    desc: str
    priority: int
    __status: str = field(default="TODO", repr=False)
    tags: set[str] = field(default_factory=set)
    history: List[Tuple[int, str, str, str]] = field(default_factory=list)

    @property
    def status(self) -> str:
     return self.__status

    def to_dict(self) -> dict:
     return {
       "task_id": self.task_id,
       "title": self.title,
       "desc": self.desc,
       "priority": self.priority,
       "status": self.__status,
       "tags": sorted(self.tags), # sets become lists in JSON
       "history": self.history, # list of tuples becomes list of lists in JSON
      }

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
      t = cls(d["task_id"], d["title"], d["desc"], d["priority"])
      t.__status = d.get("status", "TODO")
      t.tags = set(d.get("tags", []))
      t.history = [tuple(x) for x in d.get("history", [])]
      return t

#==========================================================================
class Project:
    def __init__(self, project_id: str, name: str):
      self.project_id = project_id
      self.name = name
      self.tasks: Dict[int, Task] = {}
      self._next_task_id = 1

    def to_dict(self) -> dict:
      return {
        "project_id": self.project_id,
         "name": self.name,
         "next_task_id": self._next_task_id,
         "tasks": [t.to_dict() for t in self.tasks.values()],
      }

    @classmethod
    def from_dict(cls, d: dict) -> "Project":
      p = cls(d["project_id"], d["name"])
      p._next_task_id = d.get("next_task_id", 1)
      for td in d.get("tasks", []):
        t = Task.from_dict(td)
        p.tasks[t.task_id] = t
      return p

#=========================================================================
# STEP - 2 (Storage Interface)
from abc import ABC, abstractmethod
import json
from typing import Any


class Storage(ABC):
  @abstractmethod
  def load(self) -> dict:
    pass

  @abstractmethod
  def save(self, data: dict) -> None:
    pass


class JsonFileStorage(Storage):
  def __init__(self, filename: str):
    self.filename = filename
  def load(self) -> dict:
    try:
      with open(self.filename, "r", encoding="utf-8") as f:
        return json.load(f)
    except FileNotFoundError:
      return {}

  def save(self, data: dict) -> None:
    with open(self.filename, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=2)


class MemoryStorage(Storage):
  # Great for unit tests: no real files
  def __init__(self, initial: dict | None = None):
     self.data = initial or {}

  def load(self) -> dict:
     return dict(self.data)

  def save(self, data: dict) -> None:
     self.data = dict(data)
  

class TaskBoard:
  def __init__(self, storage: Storage):
     self.storage = storage
     self.projects: dict[str, Project] = {}

  def load(self) -> None:
     raw = self.storage.load()
     self.projects = {}
     for pd in raw.get("projects", []):
       p = Project.from_dict(pd)
       self.projects[p.project_id] = p

  def save(self) -> None:
     data = {"projects": [p.to_dict() for p in self.projects.values()]}
     self.storage.save(data)

#==================================================================
# STEP - 3 (Unit Tests)

import unittest
class TestGradebook(unittest.TestCase):
  def test_average_empty(self):
    s = Student("S1", "Ayesha")
    self.assertEqual(s.average(), 0.0)

  def test_subject_topper(self):
    gb = Gradebook()
    gb.add_student("S1", "Ayesha")
    gb.add_student("S2", "Hassan")
    gb.record_mark("S1", "Math", 90)
    gb.record_mark("S2", "Math", 95)
    sid, score = gb.subject_topper("Math")
    self.assertEqual(sid, "S2")
    self.assertEqual(score, 95)

  def test_validation(self):
    s = Student("S1", "Ayesha")
    with self.assertRaises(ValueError):
      s.set_mark("Math", 200) # invalid


if __name__ == "__main__":
  unittest.main()