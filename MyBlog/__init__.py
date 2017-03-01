import os
from flask import Flask,redirect,url_for
from sqlalchemy import event

from MyBlog.models import db,Reminder,Tag,Post,Role
from MyBlog.controllers import blog,main
from MyBlog.controllers.admin import CustomView,CustomModelView,PostView,CustomFileAdmin
from MyBlog.controllers.flask_restful.posts import PostApi
from MyBlog.controllers.flask_restful.auth import AuthApi
from MyBlog.extensions import (
    bcrypt,principals,login_manager,flask_celery,
    cache,assert_env,main_css,main_js,flaskAdmin,restful_api)

from flask_login import current_user
from flask_principal import identity_loaded,UserNeed,RoleNeed
from MyBlog.tasks import on_reminder_save

# app = Flask(__name__)
# # 因为 Flask Server 的 Route 使用 main 模块中查询路由函数(EG. home)的，
# # 所以必须将 views 模块中的视图函数(路由函数)导入到 main 模块的全局作用域中。
# db.init_app(app)
#
# app.config.from_object(DevConfig)
#
# @app.route('/')
# def index():
#     return redirect(url_for('blog.home'))
#
# app.register_blueprint(blog.blog_blueprint)


def create_app(object_name):
    app=Flask(__name__)
    app.config.from_object(object_name)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    principals.init_app(app)
    flask_celery.init_app(app)
    cache.init_app(app)
    #指定了资源类 PostApi 所对应的资源名称为 posts, 访问路由为 /api/posts, 这样才完成了对一个资源的完整定义.
    restful_api.add_resource(
        PostApi,
        '/api/posts',
        '/api/posts/<string:post_id>', #添加多条路由
        endpoint='restful_api_post'
    )
    restful_api.add_resource(
        AuthApi,
        '/api/auth',
        endpoint='restful_api_auth')

    restful_api.init_app(app)

    flaskAdmin.init_app(app)
    flaskAdmin.add_view(CustomView(name='Custom'))# name 定义了在 Admin 页面的导航栏中该视图类对应的名字.
    models=[Role,Tag,Reminder]
    for model in models:
        flaskAdmin.add_view(
            CustomModelView(model,db.session,category='Models')
        )
    flaskAdmin.add_view(
        PostView(Post,db.session,name='PostManager')
    )
    flaskAdmin.add_view(
        CustomFileAdmin(
            os.path.join(os.path.dirname(__file__),'static'),
            '/static',
            name='Static Files'
        )
    )

    # assert_env.init_app(app)
    # assert_env.register('main_js',main_js)
    # assert_env.register('main_js',main_css)
#QLAlchemy 允许在 Model 上注册回调函数, 当 Model 对象发生特定的情景时, 就会执行这个回调函数, 这就是所谓的 event, 这里我们使用 after_insert
# 来指定当创建一个新的 Reminder 对象(插入一条记录)时就触发这个回调函数. 而是回调函数中的形参, 会由 event 来负责传入.
    event.listen(Reminder, 'after_insert', on_reminder_save)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender,identity):
        identity.user=current_user
        if hasattr(current_user,'id'):
            identity.provides.add(UserNeed(current_user.id))

        if hasattr(current_user,'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    # @app.route('/')
    # def index():
    #     return redirect(url_for('blog.home'))

    app.register_blueprint(blog.blog_blueprint)
    app.register_blueprint(main.main_bluprint)
    return app

# if __name__ == '__main__':
#     app.run()
