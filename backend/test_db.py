from app.database import engine


try:
    with engine.connect() as connection:
        result = connection.exec_driver_sql("SELECT 1")
        print("数据库连接成功！")
        print("测试结果：", result.scalar())

except Exception as e:
    print("数据库连接失败！")
    print("错误信息：", e)