class Config(object):
    #wtform secret key
    SECRET_KEY='secret_key'
    #reCAPTCHA Public key and Private key
    RECAPTCHA_PUBLIC_KEY = "6LeWqhAUAAAAAHCc18ERrNPCAJ8zbPElvmRkciaE"
    RECAPTCHA_PRIVATE_KEY = "6LeWqhAUAAAAAIGbYs3fAYOTJJDSknhbA6LEc-b_"
class ProConfig(Config):
    CACHE_TYPE = "simple"  # 配置cache类型,生产时配置为simple
class DevConfig(Config):
    DEBUG = True
   # SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/followdb2?charset=utf8" #?charset=utf8mb4
    # 这句话得加上，控制台不然有警告

    # SQLALCHEMY_ECHO = True  #会把SQLAlchemy把代码翻译成SQL查询语句，打印到终端
    # 配置RabbitMQ
    CELERY_RESULT_BACKEND = "amqp://guest:guest@localhost:5672//"
    CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"
    CACHE_TYPE="null" #配置cache类型,生产时配置为simple
    #设置不自动打包，默认是自动打包的，这里是开发环境，先不自动打包css,js
    ASSETS_DEBUG=True