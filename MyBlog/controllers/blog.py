import datetime,pdb
from os import path
from uuid import uuid4

from flask import render_template, Blueprint,redirect,url_for,abort,request
from sqlalchemy import  func  # func 提供了一个计数器count用于post最多的tag
from flask_login import login_required,current_user#某些页面不想被匿名用户查看
from flask_principal import Permission,UserNeed

from MyBlog.models import db,User,Post,Tag,Comment,posts_tags
from MyBlog.forms import CommentForm,PostForm

from MyBlog.extensions import poster_permission,admin_permission,cache

@cache.cached(timeout=7200,key_prefix='sidebar_data')
def siderbar_data():
    # get post of recent
    recent=db.session.query(Post).order_by(
        Post.publish_date.desc()
    ).limit(5).all()

    # get the tags and sort by count of posts
    top_tags=db.session.query(
        Tag,func.count(posts_tags.c.post_id).label('total')
    ).join(posts_tags).group_by(Tag).order_by('total DESC').limit(5).all()
    return recent,top_tags

blog_blueprint=Blueprint(
    'blog',
    __name__,
    template_folder=path.join(path.pardir,'templates','blog'),
    url_prefix='/blog'
)

# @app.route('/')
@blog_blueprint.route('/')
@blog_blueprint.route('/<int:page>')
def home(page=1):
    posts=Post.query.order_by(
        Post.publish_date.desc()
    ).paginate(page,10)

    recent,top_tags=siderbar_data()

    return render_template('home.html',
                           posts=posts,
                           recent=recent,
                           top_tags=top_tags)

def make_cache_key(*args,**kwargs):
    path=request.path
    args=str(hash(frozenset(request.args.items())))
    return path+args #unicode('utf-8') .enconde在三中早已经被遗弃了，默认str就是unicode

@blog_blueprint.route('/post/<string:post_id>',methods=('GET','POST'))
@cache.cached(timeout=60,key_prefix=make_cache_key)
def post(post_id):

    form=CommentForm()
    if form.validate_on_submit():
        new_comment=Comment(id=str(uuid4()),name=form.name.data)
        new_comment.text=form.text.data
        new_comment.date=datetime.datetime.now()
        new_comment.post_id=post_id
        db.session.add(new_comment)
        db.session.commit()

    post=Post.query.get_or_404(post_id)
    tags=post.tags
    comments=post.comments.order_by(Comment.date.desc()).all()
    recent,top_tags=siderbar_data()

    return render_template('post.html',
                           post=post,
                           tags=tags,
                           comments=comments,
                           form=form,
                           recent=recent,
                           top_tags=top_tags)

@blog_blueprint.route('/tag/<string:tag_name>')
def tag(tag_name):
    #tag=db.session.query(Tag).filter_by(title=tag_name).first_or_404()
    # Tag.qurey() 对象才有 first_or_404()，而 db.session.query(Model) 是没有的
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    posts=tag.posts.order_by(Post.publish_date.desc()).all()
    recent,top_tags=siderbar_data()

    return render_template('tag.html',
                           tag=tag,
                           posts=posts,
                           recent=recent,
                           top_tags=top_tags)

@blog_blueprint.route('/user/<string:username>')
def user(username):
    user=db.session.query(User).filter_by(username=username).first_or_404()
    posts=user.posts.order_by(Post.publish_date.desc()).all()
    recent,top_tags=siderbar_data()

    return render_template('user.html',
                           user=user,
                           posts=posts,
                           recent=recent,
                           top_tags=top_tags)

@blog_blueprint.route('/new',methods=['GET','POST'])
@login_required#引用了这个装饰器之后, 当匿名用户像创建文章时, 就会跳转到登录页面.
def new_post():
    form=PostForm()
#Flask-Login 提供了一个代理对象 current_user 来访问和表示当前登录的对象, 这个对象在视图或模板中都是能够被访问的.
    # 所以我们常在需要判断用户是否为当前用户时使用(EG. 用户登录后希望修改自己创建的文章).
    if not current_user:
        return redirect(url_for('main.login'))

    if form.validate_on_submit():
        new_post=Post(id=str(uuid4()),title=form.title.data)
        new_post.text=form.text.data
        new_post.publish_date=datetime.datetime.now()

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('blog.home'))
    return render_template('new_post.html',form=form)

@blog_blueprint.route('/edit/<string:id>',methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403) #注意这里admin_persission,数据库里只有admin这个权限
def edit_post(id):

    post=Post.query.get_or_404(id)

    if not current_user:
        return redirect(url_for('main.login'))

    if current_user !=post.users:
        return redirect(url_for('blog.post',post_id=id))

    # 当 user 是 poster 或者 admin 时, 才能够编辑文章
    permission=Permission(UserNeed(post.users.id))

    if permission.can() or admin_permission.can():
        form=PostForm()

        if form.validate_on_submit():
            post.title=form.title.data
            post.text=form.text.data
            post.publish_date=datetime.datetime.now()

            # Update the post
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('blog.post',post_id=post.id))

        # Still retain the original content, if validate is false.
        form.title.data = post.title
        form.text.data = post.text
        return render_template('edit_post.html', form=form, post=post)
    else:
        abort(403)


