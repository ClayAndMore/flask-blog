import os

from flask_script import Manager,Server
from MyBlog import models,create_app

from flask_migrate import Migrate,MigrateCommand

#默认使用DevConfig,windows下设置环境变量 set BLOG_ENV
#linux 设置环境变量export BOLG_ENV。echo $BOLG_ENV
env=os.environ.get('BLOG_ENV','dev')
app=create_app('MyBlog.config.%sConfig' %env.capitalize()) #capitalize首字母大写

migrate=Migrate(app,models.db)
manager = Manager(app)
#在控制台运行 python manage.py server可启动
manager.add_command("server",Server())
manager.add_command("db",MigrateCommand)

@manager.shell
def make_shell_context():
    """Create a python CLI.
       return: Default import object
       type: `Dict`
       """
    # 确保有导入 Flask app object，否则启动的 CLI 上下文中仍然没有 app 对象
    # 控制台运行python manage.py shell 再输入app 看看变量值
    return dict(app=app,
                db=models.db,
                User=models.User,
                Role=models.Role,
                Post=models.Post,
                Comment=models.Comment,
                Tag=models.Tag,
                Server=Server)

if __name__ =='__main__':
    manager.run()