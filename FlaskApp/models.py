from FlaskApp import app, db
from flask import flash,jsonify
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
import uuid

blob_container = app.config['BLOB_CONTAINER']
storage_url = "https://{}.blob.core.windows.net/".format(app.config['BLOB_ACCOUNT'])
blob_service = BlobServiceClient(account_url=storage_url, credential=app.config['BLOB_STORAGE_KEY'])

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username



class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(75))
    body = db.Column(db.Text())
    author = db.Column(db.String(800))
    image_path = db.Column(db.String(100))

    def __repr__(self):
        return '<Article {}>'.format(self.body)

    def save_changes(self, file):
        if file:
            filename = secure_filename(file.filename)
            fileExtension = filename.rsplit('.', 1)[1]
            randomFilename = str(uuid.uuid1())
            filename = randomFilename + '.' + fileExtension
            try:
             blob_client = blob_service.get_blob_client(container=blob_container, blob=filename)
             blob_client.upload_blob(file)
             if self.image_path: # Get rid of old image, since it's replaced
                blob_client = blob_service.get_blob_client(container=blob_container, blob=self.image_path)
                blob_client.delete_blob()
            except Exception as err:
                print(err)
            self.image_path = filename
        db.session.commit()
