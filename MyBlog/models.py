from uuid import uuid4

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature,SignatureExpired

from flask_sqlalchemy import SQLAlchemy
from MyBlog.extensions import bcrypt,cache
from flask_login import AnonymousUserMixin
from flask_principal import current_app

# SQLAlchemy 会自动的从 app 对象中的 DevConfig 中加载连接数据库的配置项
db = SQLAlchemy() #use_native_unicode="utf8mb4"

#用户和权限的关联表
users_roles=db.Table('users_roles',
                     db.Column('user_id',db.String(45),db.ForeignKey('users.id')),
                     db.Column('role_id',db.String(45),db.ForeignKey('roles.id')))

# 定义数据模型
class User(db.Model):
    __tablename__= "users"
    id = db.Column(db.String(45),primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))

    #和post的外键user_id建立联系
    posts=db.relationship(
        'Post',
        backref='users',
        lazy='dynamic'
    )

    roles = db.relationship(
        'Role',
        secondary=users_roles,
        backref=db.backref('users', lazy='dynamic'))

    def __init__(self,id,username,password):
        self.id=id
        self.username = username
        self.password = self.set_password(password)

        # default=Role.query.filter_by(name='default').one()
        # self.roles.append(default)

    def __repr__(self):
        """Define the string format for instance of User."""
        return "<Model User `{}`>".format(self.username)

#：在设定密码的时候，将明文密码转换成为 Bcrypt 类型的哈希值。
    def set_password(self,password):
        return bcrypt.generate_password_hash(password)

#检验输入的密码的哈希值，与存储在数据库中的哈希值是否一致。
    def check_password(self,password):
        return bcrypt.check_password_hash(self.password,password)

#检验 User 的实例化对象是否登录了.
    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

#检验用户是否通过某些验证
    def is_active(self):
        return True

#检验用户是否为匿名用户
    def is_anonymous(self):
        """Check the user's login status whether is anonymous."""

        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

 # 返回user实例化对象的唯一标识id
    def get_id(self):
        """Get the user's uuid from database."""
        return str(self.id)  # unicode

    @staticmethod
    @cache.memoize(60)
    def verfy_auth_token(token):

        serializer=Serializer(
            current_app.config['SECRET_KEY']
        )
        try:
            data=serializer.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        user=User.query.filter_by(id=data['id']).first()
        return user



class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.String(45),primary_key=True)
    name=db.Column(db.String(255),unique=True)
    description=db.Column(db.String(255))

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return "<Model Role `{}`>".format(self.name)

posts_tags=db.Table('posts_tags',
                    db.Column('post_id',db.String(45),db.ForeignKey('posts.id')),
                    db.Column('tag_id',db.String(45),db.ForeignKey('tags.id')))


class Post(db.Model):
    __tablename__='posts'
    id=db.Column(db.String(45),primary_key=True)
    title=db.Column(db.String(255))
    text=db.Column(db.Text())
    publish_date=db.Column(db.DateTime)
    #为post设置外键
    user_id=db.Column(db.String(45),db.ForeignKey('users.id'))
    # 如果没有制定user表的名字，我们要这么写：db.ForeignKey('User.id')

    user=db.relationship(
        'User',
        back_populates='posts'
    )
    #评论comment的外键：post_id one to many
    comments=db.relationship(
        'Comment',
        backref='posts',
        lazy='dynamic'
    )
    #定义和tag的关系，多对多 many to many
    tags=db.relationship(
        'Tag',
        secondary=posts_tags,
        #声明表之间的关系是双向，需要注意的是：在 one to many 中的 backref 是一个普通的对象，而在 many to many 中的 backref 是一个 List 对象。
        backref=db.backref('posts',lazy='dynamic')
    )

    def __init__(self, id,title):
        self.id = id
        self.title = title

    def __repr__(self):
        return "<Model Post `{}`>".format(self.title)

class Comment(db.Model):
    __tablename__='comments'
    id=db.Column(db.String(45),primary_key=True)
    name=db.Column(db.String(255))
    text=db.Column(db.Text())
    date=db.Column(db.DateTime())

    post_id=db.Column(db.String(45),db.ForeignKey('posts.id'))

    def __init__(self,id,name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<Model Comment `{}`>'.format(self.name)


class Tag(db.Model):
    __tablename__='tags'
    id=db.Column(db.String(45),primary_key=True)
    name=db.Column(db.String(255))

    def __init__(self,id,name):
        self.id = id
        self.name = name

    def __repr__(self):
        return "<Model Tag `{}`>".format(self.name)

#在用户创建账户之后, 在指定的时间内异步的向新用户发送欢迎邮件.
class Reminder(db.Model):
    __tablename__='reminders'
    id=db.Column(db.String(45),primary_key=True)
    date=db.Column(db.DateTime())
    email=db.Column(db.String(255))
    text=db.Column(db.Text())

    def __init__(self,id,text):
        self.id=id
        self.email=text

    def __repr__(self):
        return '<Model Reminder `{}`>'.format(self.text[:20])