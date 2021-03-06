from dataclasses import dataclass
import datetime
from typing import Generic, Set, TypeVar
import firebase_admin

T = TypeVar("T")


@dataclass
class CloudEvent(Generic[T]):
  specversion: str
  source: str
  subject: str
  type: str
  time: datetime
  data: T


_apps: Set[firebase_admin.App] = None


def apps() -> firebase_admin.App:
  global _apps
  if _apps is None:
    _apps = {firebase_admin.initialize_app()}
  return _apps.pop()
