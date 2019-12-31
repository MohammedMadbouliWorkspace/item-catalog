from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class session(object):
    def __init__(self, base, url):
        self.base = base
        self.url = url

    def fetch(self, callback):
        def wrapper(**kwargs):
            engine = create_engine(self.url)
            self.base.metadata.bind = engine
            s = sessionmaker(bind=engine)
            session = s()
            data = callback(session, **kwargs)
            session.close()
            try:
                return data
            except BaseException:
                return None

        return wrapper

    def change(self, callback):
        def wrapper(**kwargs):
            engine = create_engine(self.url)
            self.base.metadata.bind = engine
            s = sessionmaker(bind=engine)
            session = s()
            change_status = callback(session, **kwargs)
            session.close()
            return change_status

        return wrapper
