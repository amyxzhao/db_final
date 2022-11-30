from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, Text

Base = declarative_base()

class SpringCourses(Base):
    """courses table for spring 2023"""
    __tablename__ = 'springcourses'
    term = Column(Text)
    courseid = Column(Integer, primary_key=True)
    fullcode = Column(Text)
    deptcode = Column(Text)
    subcode = Column(Text)
    deptname = Column(Text)
    coursenum = Column(Integer)
    title = Column(Text)
    description = Column(Text)
    school = Column(Text)

class SpringDemand(Base):
    """demand statistics table for spring 2023"""
    __tablename__ = 'springdemand'
    courseid = Column(Integer, primary_key=True)
    coursecode = Column(Text)
    coursetitle = Column(Text)
    coursedemand = Column(Integer)

class NLPFormat(Base):
    __tablename__ = 'nlpformat'
    courseid = Column(Integer, primary_key=True)
    cleansentence = Column(Text)
    tokenlemmasentence = Column(Text)