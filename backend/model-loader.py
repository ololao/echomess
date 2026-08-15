"""File for atlas migrate diff"""

from atlas_provider_sqlalchemy.ddl import print_ddl
from src.database import Base
from src.message import Message
from src.rooms import Rooms
from src.users import User

if __name__ == "__main__":
    print_ddl("postgresql", [Base])
