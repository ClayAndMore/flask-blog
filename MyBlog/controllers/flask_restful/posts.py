from flask_restful import Resource,marshal_with,fields
from MyBlog.controllers.flask_restful import fields as my_fields

from MyBlog.models import db,User,Post,Tag
from MyBlog.controllers.flask_restful import parsers
from flask import abort

import datetime

nested_tag_fields={
    'id':fields.String(),
    'name':fields.String()
}
post_fields={
    'author':fields.String(attribute=lambda x:x.user.username),
    'title':fields.String(),
    'text':my_fields.HTMLField(),
    'tags':fields.List(fields.Nested(nested_tag_fields)),
    'publish_date':fields.DateTime(dt_format='iso8601')
}

#每个 REST 资源类都需要继承 flask_restful 的 Resource 类.
# 其所有的子类都可以通过定义同名实例函数来将该函数绑定到 HTTP Methods 中. EG. GET <==> get(), 放
# 接受定位到资源的 HTTP GET 方法时, 就会执行该资源类的实例函数 get() .
class PostApi(Resource):
    @marshal_with(post_fields)
    def get(self,post_id=None):
        if post_id:
            post=Post.query.filter_by(id=post_id).first()
            if not post:
                abort(404)
            return post
        else:
            args=parsers.post_get_parser.parse_args()
            page=args['page'] or 1

            #return the posts with user
            if args['user']:
                user=User.query.filter_by(username=args['user']).first()
                if not user:
                    abort(404)
                posts=user.posts.order_by(
                    Post.publish_date.desc()
                ).paginate(page,30)
            else:
                posts=Post.query.order_by(
                    Post.publish_date.desc()
                ).paginate(page,30)
            return posts.items

    def post(self,post_id=None):
        if post_id:
            abort(400)
        else:
            args=parsers.post_post_parser.parse_args(strict=True)

            user=User.verfy_auth_token(args['token'])
            if not user:
                abort(401)

            new_post=Post()
            new_post.title=args['title']
            new_post.date=datetime.datetime.now()
            new_post.text=args['title']
            new_post.user=user

            if args['tags']:
                for item in args['tags']:
                    tag=Tag.query.filter_by(name=item).first()
                    if tag:
                        new_post.tags.append(tag)
                    else:
                        new_tag=Tag()
                        new_tag=item
                        new_post.tags.append(new_tag)

            db.session.add(new_post)
            db.session.commit()
            return (new_post.id,201)
        