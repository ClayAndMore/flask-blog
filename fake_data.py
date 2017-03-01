import datetime
import random
from uuid import uuid4

from MyBlog.models import db,User,Tag,Post

user=User(id=str(uuid4()),username='pp1',password='pp10')
db.session.add(user)
db.session.commit()

user=db.session.query(User).first()
tag_one=Tag(id=str(uuid4()),name='t1')
tag_two=Tag(id=str(uuid4()),name='t2')
tag_three=Tag(id=str(uuid4()),name='t3')
tag_four=Tag(id=str(uuid4()),name='t4')
tag_list=[tag_one,tag_two,tag_three,tag_four]

for i in range(100):
    new_post=Post(id=str(uuid4()),title="Post"+str(i))
    new_post.user=user
    new_post.publish_date=datetime.datetime.now()
    new_post.text="this is post test"
    new_post.tags=random.sample(tag_list,random.randint(1,3))
    db.session.add(new_post)

db.session.commit()