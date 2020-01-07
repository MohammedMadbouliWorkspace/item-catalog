from sqlalchemy.orm import joinedload
from dbsetup import Base, User, Category, Item, Colors
import dbsession
import re

s = dbsession.session(Base, "postgresql+psycopg2://grader:grader@127.0.0.1/catalog")


def not_empty(type):
    try:
        int(type)
        return not not type

    except BaseException:
        return not not re.sub(r"[\n\t\s]*", "", type)


@s.fetch
def user(session, pointer):
    pointer = str(pointer)
    try:
        user = session.query(User).filter_by(username=pointer).one()
        return user
    except:
        try:
            pointer = int(pointer)
            user = session.query(User).filter_by(id=pointer).one()
            return user
        except:
            return None



@s.fetch
def category(session, id):
    return (
        session.query(Category)
        .options(joinedload(Category.colors), joinedload(Category.user))
        .filter_by(id=id)
        .first()
    )


@s.fetch
def item(session, id):
    return (
        session.query(Item)
        .options(
            joinedload(Item.user),
            joinedload(Item.category).joinedload(Category.colors),
        )
        .filter_by(id=id)
        .first()
    )


@s.fetch
def categories(session, user_id):
    return (
        session.query(Category)
        .options(joinedload(Category.colors), joinedload(Category.user))
        .filter_by(user_id=user_id)
        .all()
    )


@s.fetch
def items(session, For, pointer):
    if For == "user":
        return (
            session.query(Item)
            .options(
                joinedload(Item.user),
                joinedload(Item.category).joinedload(Category.colors),
            )
            .filter_by(user_id=pointer)
            .all()
        )
    elif For == "category":
        return (
            session.query(Item)
            .options(
                joinedload(Item.user),
                joinedload(Item.category).joinedload(Category.colors),
            )
            .filter_by(category_id=pointer)
            .all()
        )


@s.fetch
def all_users(session):
    return session.query(User).all()


@s.fetch
def all_categories(session):
    return (
        session.query(Category)
        .options(joinedload(Category.colors), joinedload(Category.user))
        .all()
    )


@s.fetch
def all_items(session):
    return (
        session.query(Item)
        .options(
            joinedload(Item.user),
            joinedload(Item.category).joinedload(Category.colors),
        )
        .all()
    )


@s.fetch
def latest_items(session):
    return (
        session.query(Item)
        .options(
            joinedload(Item.user),
            joinedload(Item.category).joinedload(Category.colors),
        )
        .order_by(Item.creation_date.desc())
        .all()
    )


@s.fetch
def all_colors(session):
    return session.query(Colors).all()


@s.fetch
def add_user(session, username, name, email, image):
    if not_empty(username) and not_empty(name) and not_empty(email):

        user = User(username=username, name=name, email=email, image=image)
        session.add(user)
        session.commit()

        return user.id


@s.change
def add_category(session, user_id, name, colors_id):
    if not_empty(user_id) and not_empty(name) and not_empty(colors_id):

        session.add(Category(user_id=user_id, name=name, colors_id=colors_id))
        session.commit()
        return True


@s.change
def add_item(session, user_id, category_id, name, description, image):
    if (
        not_empty(user_id)
        and not_empty(category_id)
        and not_empty(name)
        and not_empty(description)
    ):

        if not_empty(image):
            session.add(
                Item(
                    user_id=user_id,
                    category_id=category_id,
                    name=name,
                    description=description,
                    image=image,
                )
            )
            session.commit()

        else:
            session.add(
                Item(
                    user_id=user_id,
                    category_id=category_id,
                    name=name,
                    description=description,
                )
            )
            session.commit()

        return True


@s.change
def edit_category(session, category, name, colors_id):
    if not_empty(name) and not_empty(colors_id):
        category.name = name
        category.colors_id = colors_id

        session.add(category)
        session.commit()
        return True


@s.change
def edit_item(session, item, category_id, name, description, image):
    if not_empty(category_id) and not_empty(name) and not_empty(description):

        item.category_id = category_id
        item.name = name
        item.description = description

        if not_empty(image):
            item.image = image

        session.add(item)
        session.commit()

        return True


@s.change
def delete_category(session, category):
    session.delete(category)
    session.commit()
    return True


@s.change
def delete_items(session, items):
    for item in items:
        session.delete(item)

    session.commit()
    return True


@s.change
def delete_item(session, item):
    session.delete(item)
    session.commit()
    return True
