from fastapi import FastAPI

from sqlalchemy import create_engine, select, Column, String, ForeignKey, Integer 
from sqlalchemy.orm import declarative_base, relationship, Session



app = FastAPI()

Base = declarative_base()

# to connect which db and show sql query inside terminal console
engine = create_engine("sqlite:///text_sqlalchemy_using_sqlite.db", echo=True, future=True) 

# use for alchemy orm / database operation such as alter , delete, insert, rollback etc
session = Session(engine)





#TODO creating models ( python class ) that represent database tables
class User(Base):
    __tablename__ = "user_table"

    id = Column(Integer, primary_key = True)
    name = Column(String(30), nullable = False)
    fullname = Column(String)

    addresses = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
     __tablename__ = "address"

     id = Column(Integer, primary_key=True)    
     email_address = Column(String, nullable=False)
     user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)

     user = relationship("User", back_populates="addresses")

     def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"



# creating tables
def create_tables():
    Base.metadata.create_all(engine)


create_tables()






#TODO insert data using session ( un-comment if u want to insert data)
# with Session(engine) as session:
#     spongebob = User(
#         name="spongebob",
#         fullname="Spongebob Squarepants",
#         addresses=[Address(email_address="spongebob@sqlalchemy.org")],
#     )
#     sandy = User(
#         name="sandy",
#         fullname="Sandy Cheeks",
#         addresses=[
#             Address(email_address="sandy@sqlalchemy.org"),
#             Address(email_address="sandy@squirrelpower.org"),
#         ],
#     )
#     patrick = User(name="patrick", fullname="Patrick Star")

#     # add data in db user table
#     session.add_all([spongebob, sandy, patrick])

#     # finally commit changes after this u can see data
#     session.commit()






#TODO # This creates a new temporary Session inside the with block; the outer session remains separate.

# session = Session(engine)       ← Session A

# with Session(engine) as session:
#     ...                         ← Session B
#                                 ↓
#                             auto close

# Session A abhi bhi open hai

#TODO select query
stmt = select(User).where(User.name.in_(["spongebob", "sandy"]))

print("\nDatabase Data\n")
for user in session.scalars(stmt):
    print(user)
# session.close() #in simple old session u have close session manualy or use modern for auto close like below






#TODO Join Query
# fetch sandy address data
stmt = (
    select(Address)
    .join(Address.user)
    .where(User.name == "sandy")
    .where(Address.email_address == "sandy@squirrelpower.org")
)
sandy_address = session.scalars(stmt).one() # Expect exactly one object; throws an error if 0 or more than 1 result is found.
print(sandy_address)
session.close()






#TODO update or make changes
# with Session(engine) as session:
#     # fetch sandy address data
#     stmt = (
#     select(Address)
#     .join(Address.user)
#     .where(User.name == "sandy")
#     .where(Address.email_address == "sandy@sqlalchemy.org")
#     )
#
#     sandy_address = session.scalars(stmt).one() 
#     sandy_address.email_address = "sandy_cheeks@sqlalchemy.org"

#     stmt = select(User).where(User.name == "patrick")
#     patrick = session.scalars(stmt).one()
#     patrick.addresses.append(Address(email_address="patrickstar222@sqlalchemy.org"))
    
#     session.commit()






#TODO Delete query
with Session(engine) as session:

    # single delete based on id
    user_sandy = session.get(User, 2)

    # fetch sandy address data
    # stmt = (
    #     select(Address)
    #     .where(Address.user_id == user_sandy.id)
    #     .where(Address.email_address == "sandy@sqlalchemy.org")
    # )

    # sandy_address = session.scalars(stmt).one()

    print(user_sandy)
    # user_sandy.addresses.remove(sandy_address)

    # delete entire user
    # session.delete(user_sandy) 

    # delete all same users
    # stmt = select(User).where(User.name == "patrick")
    # users = session.scalars(stmt).all()

    # for user in users:
    #     session.delete(user)

    session.commit()