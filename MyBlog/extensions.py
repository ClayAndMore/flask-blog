# from MyBlog.models import User
#所有的扩展文件
from flask import session

from flask_bcrypt import Bcrypt
from flask_openid import OpenID
from flask_login import LoginManager
from flask_principal import Principal,Permission,RoleNeed
from flask_celery import Celery
from flask_mail import Mail
from flask_cache import Cache
from flask_assets import Environment,Bundle
from flask_admin import Admin
from flask_restful import Api
from flask_oauth import OAuth

bcrypt=Bcrypt()
openid=OpenID()
principals=Principal()
login_manager=LoginManager()
flask_celery=Celery()
mail=Mail()
cache=Cache()
flaskAdmin=Admin()
restful_api=Api()
assert_env=Environment()
#Bundel() 的构造器能够接受无限个文件名作为非关键字参数, 定义那些文件需要被打包,
# 这里主要打包本地 static 下的 CSS 和 JS 两种类型文件.
main_css=Bundle(
    'css/bootstrap.css',
    'css/bootstrap-theme.css',
    #filters 定义了这些需要被打包的文件通过那些过滤器(可以为若干个)进行预处理,
    # 这里使用了 cssmin/jsmin 会将 CSS/JS 文件中的空白符和换行符去除.
    filters='cssmin',
    output='assets/css/common.css'
)
main_js=Bundle(
    'js/bootstrap.js',
    filters='jsmin',
    output='assets/js/common.js'#关键字参数 output 定义了打包后的包文件的存放路径
)

login_manager.login_view="main.login"#z指定登陆页面的视图函数
login_manager.session_protection="strong"#当发现 cookies 被篡改时, 该用户的 session 对象会被立即删除, 导致强制重新登录.
login_manager.login_message="please login to accese this page"#用户登陆的文案
login_manager.login_message_category="info"# 登陆信息的类别为info

#回调函数，用户登录并调用 login_user() 的时候, 根据 user_id 找到对应的 user, 如果没有找到，返回None,
# 此时的 user_id 将会自动从 session 中移除, 若能找到 user ，则 user_id 会被继续保存.
@login_manager.user_loader
def load_user(user_id):
    # 这个一定要写在这里，而不是顶部，不然会出现cannot import name user的错误
    from MyBlog.models import User
    return User.query.filter_by(id=user_id).first()


#第三方登陆
oauth=OAuth()
qq = oauth.remote_app(
  'qq',
  consumer_key= '1105920855', #QQ_APP_ID,
  consumer_secret= '9pscmOXUaJVeCvdH', #QQ_APP_KEY,
  base_url='https://graph.qq.com',
  request_token_url=None,
  request_token_params={'scope': 'get_user_info'},
  access_token_url='/oauth2.0/token',
  authorize_url='/oauth2.0/authorize',
)

@qq.tokengetter
def get_facebook_token():
    return session.get('qq_token')

#flask-principal
# 这里设定了 3 种权限, 这些权限会被绑定到 Identity 之后才会发挥作用.
# Init the role permission via RoleNeed(Need).
admin_permission = Permission(RoleNeed('admin'))
poster_permission = Permission(RoleNeed('poster'))
default_permission = Permission(RoleNeed('default'))