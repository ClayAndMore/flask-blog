from flask_admin import BaseView,expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from MyBlog.forms import CKTextAreaField
#nosql
# from flask_admin.contrib.mongoengine import ModelView

#BaseView 能够生成最基本的视图, 并添加到 Admin 页面上, 如果你希望在 Admin 页面上加入一些 JavaScript 图表的话, 就可以使用 BaseView.
class CustomView(BaseView):
    # BaseView 的子类中可以定义若干个视图函数, 使用 Flask-Admin 的 @expose 装饰器来注册函数为视图, 这与一般的视图函数定义是有区别的.
    #BaseView 子类必须定义一个路由 URL 为 / 的视图函数,
    # 在 Admin 界面中只会默认显示该视图函数, 其他的视图函数是通过 / 中的链接来实现跳转的.
    @expose('/')
    def index(self):
        #expose 和 self.render 的使用方法与 blueprint.route 和 renter_template 的使用方法是一样的.
        return self.render('admin/custom.html')

    @expose('/second_page')
    def second_page(self):
        return self.render('admin/second_page.html')

#ModelView 能够管理 SQLAlchemy Model, 提供一个 CRUD 的界面给我们使用.
class CustomModelView(ModelView):
    pass

class PostView(CustomModelView):

    # Using the CKTextAreaField to replace the Field name is `test`
    form_overrides = dict(text=CKTextAreaField)

    # Using Search box
    column_searchable_list = ('text', 'title')

    # Using Add Filter box
    column_filters = ('publish_date',)

    # Custom the template for PostView
    # Using js Editor of CKeditor
    create_template = 'admin/post_edit.html'
    edit_template = 'admin/post_edit.html'

class CustomFileAdmin(FileAdmin):
    pass
