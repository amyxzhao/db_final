from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Index, Integer, Text, DECIMAL

Base = declarative_base()

class FallCourses(Base):
    """courses table for fall 2022"""
    __tablename__ = 'fallcourses'
    term = Column(Text)
    courseid = Column(Text, primary_key=True)
    coursecode = Column(Text)
    deptcode = Column(Text)
    deptname = Column(Text)
    coursenum = Column(Integer)
    title = Column(Text)
    descrip = Column(Text)

class SpringCourses(Base):
    """courses table for spring 2023"""
    __tablename__ = 'springcourses'
    term = Column(Text)
    courseid = Column(Text, primary_key=True)
    coursecode = Column(Text)
    deptcode = Column(Text)
    deptname = Column(Text)
    coursenum = Column(Integer)
    title = Column(Text)
    descrip = Column(Text)


class FallDemand(Base):
    """demand statistics table for fall 2022"""
    __tablename__ = 'falldemand'
    # dummy = Column(Integer, primary_key=True)
    courseid = Column(Text, primary_key=True)
    coursecode = Column(Text)
    coursetitle = Column(Text)
    coursedemand = Column(Integer)

class SpringDemand(Base):
    """demand statistics table for spring 2023"""
    __tablename__ = 'springdemand'
    courseid = Column(Text, primary_key=True)
    coursecode = Column(Text)
    coursetitle = Column(Text)
    coursedemand = Column(Integer)