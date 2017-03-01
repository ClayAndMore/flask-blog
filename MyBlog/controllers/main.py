from os import path
from uuid import uuid4

from flask import flash,url_for,redirect,render_template,Blueprint,request,session
from MyBlog.forms import LoginForm,RegisterForm,OpenIDFrom
from MyBlog.models import db,User
from MyBlog.extensions import qq,openid

from flask_login import login_user,logout_user
from flask_principal import Identity, AnonymousIdentity, identity_changed, current_app


main_bluprint=Blueprint(
    'main',
    __name__,
    template_folder=path.join(path.pardir,'templates','main')
)

@main_bluprint.route('/')
def index():
    return redirect(url_for('blog.home'))

@main_bluprint.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    openid_from=OpenIDFrom()

    # Send the request for login to relay party(URL)
    if openid_from.validate_on_submit():
        return openid.try_login(
            openid_from.openid_url.data,
            ask_for=['nickname','email'],
            ask_for_optional=['fullname']
        )
    # Try to login the relay party failed.
    openid_errors=openid.fetch_error()
    if openid_errors:
        flash(openid_errors,category='danger')

    if form.validate_on_submit():

        user=User.query.filter_by(username=form.username.data).one()
        #login_user() 能够将已登录并通过 load_user() 的用户对应的 User 对象,
        # 保存在 session 中, 所以该用户在访问不同的页面的时候不需要重复登录.
        # 如果希望应用记住用户的登录状态, 只需要为 login_user()的形参 remember 传入 True 实参就可以了.
        login_user(user,remember=form.remember.data)

        identity_changed.send(
            current_app._get_current_object(),
            identity=Identity(user.id))

        flash("You have been logger in",category='success')
        return redirect(url_for('blog.home'))

    return render_template('login.html',form=form,
                           openid_from=openid_from)

@main_bluprint.route('/logout',methods=['GET','POST'])
def logout():
#Logout 时, 使用 logout_user 来将用户从 session 中删除.
    logout_user()

    identity_changed.send(
        current_app._get_current_object(),
        identity=AnonymousIdentity())

    flash("You have been logged out",category='success')
    return redirect(url_for('blog.home'))

@main_bluprint.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        new_user=User(id=str(uuid4()),
                      username=form.username.data,
                      password=form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash('You user has been created,please login',category='success')

        return redirect(url_for('main.login'))

    return render_template('register.html',form=form)

# 第三方授权流程
@main_bluprint.route('/qq')
def qq_login():
    return qq.authorize(
        callback=url_for('main.qq_authorized',
                         next=request.referrer or None,
                         _external=True
                         )
    )

# 该视图会接受从 facebook 认证服务器返回的 resp 对象, 可以通过 resp 对象来判断 Client 在 Server 上的认证结果.
@main_bluprint.route('/facebook/authorized')
@qq.authorized_handler
def qq_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description'])

    session['facebook_oauth_token'] = (resp['access_token'], '')

    me = qq.get('/me')

    if me.data.get('first_name', False):
        facebook_username = me.data['first_name'] + " " + me.data['last_name']
    else:
        facebook_username = me.data['name']

    user = User.query.filter_by(username=facebook_username).first()
    if user is None:
        user = User(id=str(uuid4()), username=facebook_username, password='claymore')
        db.session.add(user)
        db.session.commit()

    flash('You have been logged in.', category='success')

    return redirect(url_for('blog.home'))