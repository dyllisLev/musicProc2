from .setup import *


class ModelMusicItem(ModelBase):
    P = P
    __tablename__ = 'musicProc2_item'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = P.package_name

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime)

    title = db.Column(db.String)
    artist = db.Column(db.String)
    album = db.Column(db.String)
    titleByTag = db.Column(db.String)
    artistByTag = db.Column(db.String)
    albumByTag = db.Column(db.String)
    searchKey = db.Column(db.String)
    filePath = db.Column(db.String)

    def __init__(self):
        self.created_time = datetime.now()