from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from config import engine

# Создаем базовый класс для моделей
Base = declarative_base()


# Модель для таблицы managers
class Manager(Base):
    __tablename__ = 'managers'
    manager_id = Column(Integer, primary_key=True)
    login = Column(String(100), unique=True)
    hashed_password = Column(String(100))
    phone = Column(String(100))
    full_name = Column(String(100))
    email = Column(String(100), unique=True)
    areas = relationship("Area", back_populates="manager")


# Модель для таблицы areas
class Area(Base):
    __tablename__ = 'areas'
    area_id = Column(Integer, primary_key=True)
    area_name = Column(String(100))
    manager_id = Column(Integer, ForeignKey('managers.manager_id'))
    manager = relationship("Manager", back_populates="areas")
    buildings = relationship("Building", back_populates="area")


# Модель для таблицы buildings
class Building(Base):
    __tablename__ = 'buildings'
    building_id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey('areas.area_id'))
    address = Column(String(200))
    entrances = Column(Integer)
    area = relationship("Area", back_populates="buildings")
    entrances_rel = relationship("Entrance", back_populates="building")
    plumbing = relationship("Plumbing", back_populates="building")
    heating = relationship("Heating", back_populates="building")
    electrical = relationship("Electrical", back_populates="building")


# Модель для таблицы entrances
class Entrance(Base):
    __tablename__ = 'entrances'
    entrance_id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey('buildings.building_id'))
    entrance_number = Column(Integer)
    electrical_panel_info = Column(String(10))
    building = relationship("Building", back_populates="entrances_rel")
    apartments = relationship("Apartment", back_populates="entrance")


# Модель для таблицы apartments
class Apartment(Base):
    __tablename__ = 'apartments'
    apartment_id = Column(Integer, primary_key=True)
    entrance_id = Column(Integer, ForeignKey('entrances.entrance_id'))
    apartment_number = Column(String(10))
    floor = Column(Integer)
    rooms = Column(Integer)
    total_residents = Column(Integer)
    entrance = relationship("Entrance", back_populates="apartments")
    residents = relationship("Resident", back_populates="apartment")
    requests = relationship("Request", back_populates="apartment")


# Модель для таблицы residents
class Resident(Base):
    __tablename__ = 'residents'
    resident_id = Column(Integer, primary_key=True)
    apartment_id = Column(Integer, ForeignKey('apartments.apartment_id'))
    full_name = Column(String(100))
    passport_data = Column(String(100))
    phone = Column(String(20))
    apartment = relationship("Apartment", back_populates="residents")
    requests = relationship("Request", back_populates="resident")


# Модель для таблицы plumbing
class Plumbing(Base):
    __tablename__ = 'plumbing'
    plumbing_id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey('buildings.building_id'))
    pipe_type = Column(String(50))
    riser_number = Column(Integer)
    passes_through_flats = Column(Text)
    building = relationship("Building", back_populates="plumbing")


# Модель для таблицы heating
class Heating(Base):
    __tablename__ = 'heating'
    heating_id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey('buildings.building_id'))
    riser_number = Column(Integer)
    return_riser = Column(Boolean)
    passes_through_flats = Column(Text)
    building = relationship("Building", back_populates="heating")


# Модель для таблицы electrical
class Electrical(Base):
    __tablename__ = 'electrical'
    electrical_id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey('buildings.building_id'))
    cable_type = Column(String(50))
    distribution_panel = Column(Text)
    building = relationship("Building", back_populates="electrical")


# Модель для таблицы requests
class Request(Base):
    __tablename__ = 'requests'
    request_id = Column(Integer, primary_key=True)
    resident_id = Column(Integer, ForeignKey('residents.resident_id'))
    apartment_id = Column(Integer, ForeignKey('apartments.apartment_id'))
    type = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status_id = Column(Integer, ForeignKey('statuses.status_id'))
    resident = relationship("Resident", back_populates="requests")
    apartment = relationship("Apartment", back_populates="requests")
    assignments = relationship("Assignment", back_populates="request")
    status = relationship("Status", back_populates="requests")  # Связь с таблицей statuses


class Status(Base):
    __tablename__ = 'statuses'
    status_id = Column(Integer, primary_key=True)
    status_name = Column(String(100))
    requests = relationship("Request", back_populates="status")  # Обратная связь


# Модель для таблицы workers
class Worker(Base):
    __tablename__ = 'workers'
    worker_id = Column(Integer, primary_key=True)
    full_name = Column(String(100))
    specialization = Column(String(50))
    phone = Column(String(20))
    assignments = relationship("Assignment", back_populates="worker")


# Модель для таблицы assignments
class Assignment(Base):
    __tablename__ = 'assignments'
    assignment_id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('requests.request_id'))
    worker_id = Column(Integer, ForeignKey('workers.worker_id'))
    assigned_at = Column(DateTime)
    is_set_to_worker = Column(Boolean)
    request = relationship("Request", back_populates="assignments")
    worker = relationship("Worker", back_populates="assignments")
    materials = relationship("Material", back_populates="assignment")


# Модель для таблицы materials
class Material(Base):
    __tablename__ = 'materials'
    material_id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey('assignments.assignment_id'))
    name = Column(String(100))
    quantity = Column(Integer)
    assignment = relationship("Assignment", back_populates="materials")


# Создаем базу данных и таблицы
if __name__ == "__main__":
    # Создаем все таблицы
    Base.metadata.create_all(engine)
