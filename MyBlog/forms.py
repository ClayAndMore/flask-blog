from flask_wtf import FlaskForm,RecaptchaField
from wtforms import (
    widgets,
    StringField,
    TextAreaField,
    TextField,
    PasswordField,
    BooleanField,
    ValidationError)
from wtforms.validators import DataRequired,Length,EqualTo,URL,Email,StopValidation

from MyBlog.models import User

class CommentForm(FlaskForm):
    name=StringField(
        'Name',
        validators=[DataRequired(),Length(max=255)]
    )
    text=TextAreaField(u'Comment',validators=[DataRequired()])

class LoginForm(FlaskForm):
    username=StringField('Username',[DataRequired(),Length(max=255)])
    password=PasswordField('Password',[DataRequired()])
    remember=BooleanField('Remember Me')

#重载,返回布尔类型
    def validate(self):
        check_validata=super(LoginForm,self).validate()

        if not check_validata:
            return False

        user=User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('Invalid username or password')
            return False

        if not user.check_password(self.password.data):
            self.username.errors.append('Invalid username or password')
            return False

        return True

class RegisterForm(FlaskForm):
    username=StringField('Username',[DataRequired(),Email(message="it is`t an email")])
    password=PasswordField('Password',[DataRequired(),Length(min=255)])
    comfirm=PasswordField('Confirm Password',[DataRequired(),EqualTo('password')])
    recaptcha=RecaptchaField()

    def validate(self):
        check_validate=super(RegisterForm,self).validate()

        if not check_validate:
            return False

        user=User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append('User with that name already exists.')
            return False
        return True

class PostForm(FlaskForm):
    title=StringField('Title',[DataRequired(),Length(max=255)])
    text=TextAreaField('Blog Content',[DataRequired()])

class CKTextAreaWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_','ckeditor')
        return super(CKTextAreaWidget,self).__call__(field,**kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class OpenIDFrom(FlaskForm):
    openid_url=StringField('OpenID URL',[DataRequired(),URL()])