from app.database import Base, engine
from app.models.dataset import Dataset
from app.models.dataset_analysis import DatasetAnalysis


print("正在创建数据库表...")

Base.metadata.create_all(bind=engine)

print("数据库表创建完成！")