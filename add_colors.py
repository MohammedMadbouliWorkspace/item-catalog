from dbsetup import Base, Colors
import dbsession

colors = [
    "009688,f5f5f5",
    "ff5722,f5f5f5",
    "ffeb3b,424242",
    "3f51b5,f5f5f5",
    "795548,f5f5f5",
    "8bc34a,f5f5f5",
    "e91e63,f5f5f5",
    "2196f3,f5f5f5",
    "607d8b,f5f5f5",
]

item_catalog_session = dbsession.session(Base, "postgresql+psycopg2://grader:grader@127.0.0.1/catalog")


@item_catalog_session.change
def add_colors(session):
    for color in colors:
        session.add(Colors(colors=color))
        session.commit()


add_colors()
