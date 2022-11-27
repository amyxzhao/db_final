from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Index, Integer, Text, DECIMAL

Base = declarative_base()

class Courses(Base):
    """courses table"""
    __tablename__ = 'courses'
    term = Column(Text)
    courseid = Column(Text, primary_key=True)
    coursecode = Column(Text)
    deptcode = Column(Text)
    deptname = Column(Text)
    coursenum = Column(Integer)
    title = Column(Text)
    descrip = Column(Text)
    prereqs = Column(Text)

class Demand(Base):
    """demand statistics table"""
    __tablename__ = 'demand'
    courseid = Column(Text, ForeignKey('courses.courseid'), primary_key=True)
    coursecode = Column(Text)
    coursedemand = Column(Integer)