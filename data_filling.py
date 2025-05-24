import logging
from sqlalchemy.orm import Session
from orm_models import Manager, Area, Building, Entrance, Apartment, Resident, Plumbing, Heating, Electrical, Status, Request, Worker, Assignment, Material
from config import engine
from datetime import datetime
import bcrypt

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    # Создаем сессию
    with Session(engine) as db:
        try:
            # 1. Заполнение таблицы managers
            logger.info("Заполнение таблицы managers...")
            manager1 = Manager(
                login="ivan_ivanov",
                hashed_password=bcrypt.hashpw("пароль123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                phone="+79012345678",
                full_name="Иван Иванов",
                email="ivan.ivanov@example.com"
            )
            manager2 = Manager(
                login="anna_smirnova",
                hashed_password=bcrypt.hashpw("пароль456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                phone="+79087654321",
                full_name="Анна Смирнова",
                email="anna.smirnova@example.com"
            )
            db.add_all([manager1, manager2])
            db.commit()
            logger.info("Таблица managers заполнена.")

            # 2. Заполнение таблицы areas
            logger.info("Заполнение таблицы areas...")
            area1 = Area(area_name="Центральный район", manager_id=manager1.manager_id)
            area2 = Area(area_name="Пригород", manager_id=manager2.manager_id)
            db.add_all([area1, area2])
            db.commit()
            logger.info("Таблица areas заполнена.")

            # 3. Заполнение таблицы buildings
            logger.info("Заполнение таблицы buildings...")
            building1 = Building(area_id=area1.area_id, address="ул. Ленина, 10", entrances=2)
            building2 = Building(area_id=area2.area_id, address="ул. Садовая, 5", entrances=1)
            db.add_all([building1, building2])
            db.commit()
            logger.info("Таблица buildings заполнена.")

            # 4. Заполнение таблицы entrances
            logger.info("Заполнение таблицы entrances...")
            entrance1 = Entrance(building_id=building1.building_id, entrance_number=1, electrical_panel_info="Щиток А")
            entrance2 = Entrance(building_id=building1.building_id, entrance_number=2, electrical_panel_info="Щиток Б")
            entrance3 = Entrance(building_id=building2.building_id, entrance_number=1, electrical_panel_info="Щиток В")
            db.add_all([entrance1, entrance2, entrance3])
            db.commit()
            logger.info("Таблица entrances заполнена.")

            # 5. Заполнение таблицы apartments
            logger.info("Заполнение таблицы apartments...")
            apartment1 = Apartment(entrance_id=entrance1.entrance_id, apartment_number="101", floor=1, rooms=2, total_residents=3)
            apartment2 = Apartment(entrance_id=entrance1.entrance_id, apartment_number="102", floor=1, rooms=1, total_residents=1)
            apartment3 = Apartment(entrance_id=entrance2.entrance_id, apartment_number="201", floor=2, rooms=3, total_residents=4)
            apartment4 = Apartment(entrance_id=entrance3.entrance_id, apartment_number="101", floor=1, rooms=2, total_residents=2)
            db.add_all([apartment1, apartment2, apartment3, apartment4])
            db.commit()
            logger.info("Таблица apartments заполнена.")

            # 6. Заполнение таблицы residents
            logger.info("Заполнение таблицы residents...")
            resident1 = Resident(apartment_id=apartment1.apartment_id, full_name="Петр Сергеев", passport_data="1234 567890", phone="+79012345679")
            resident2 = Resident(apartment_id=apartment2.apartment_id, full_name="Мария Петрова", passport_data="0987 654321", phone="+79012345680")
            resident3 = Resident(apartment_id=apartment3.apartment_id, full_name="Алексей Кузнецов", passport_data="1111 222222", phone="+79012345681")
            resident4 = Resident(apartment_id=apartment4.apartment_id, full_name="Елена Соколова", passport_data="3333 444444", phone="+79012345682")
            db.add_all([resident1, resident2, resident3, resident4])
            db.commit()
            logger.info("Таблица residents заполнена.")

            # 7. Заполнение таблицы plumbing
            logger.info("Заполнение таблицы plumbing...")
            plumbing1 = Plumbing(building_id=building1.building_id, pipe_type="Полипропилен", riser_number=1, passes_through_flats="Квартиры 101-401")
            plumbing2 = Plumbing(building_id=building2.building_id, pipe_type="Медь", riser_number=1, passes_through_flats="Квартиры 101-301")
            db.add_all([plumbing1, plumbing2])
            db.commit()
            logger.info("Таблица plumbing заполнена.")

            # 8. Заполнение таблицы heating
            logger.info("Заполнение таблицы heating...")
            heating1 = Heating(building_id=building1.building_id, riser_number=1, return_riser=True, passes_through_flats="Квартиры 101-401")
            heating2 = Heating(building_id=building2.building_id, riser_number=1, return_riser=False, passes_through_flats="Квартиры 101-301")
            db.add_all([heating1, heating2])
            db.commit()
            logger.info("Таблица heating заполнена.")

            # 9. Заполнение таблицы electrical
            logger.info("Заполнение таблицы electrical...")
            electrical1 = Electrical(building_id=building1.building_id, cable_type="ВВГнг", distribution_panel="Щиток на 1 этаже")
            electrical2 = Electrical(building_id=building2.building_id, cable_type="ВВГ", distribution_panel="Щиток в подвале")
            db.add_all([electrical1, electrical2])
            db.commit()
            logger.info("Таблица electrical заполнена.")

            # 10. Заполнение таблицы statuses
            logger.info("Заполнение таблицы statuses...")
            status1 = Status(status_name="Новая")
            status2 = Status(status_name="В работе")
            status3 = Status(status_name="Завершена")
            db.add_all([status1, status2, status3])
            db.commit()
            logger.info("Таблица statuses заполнена.")

            # 11. Заполнение таблицы requests
            logger.info("Заполнение таблицы requests...")
            request1 = Request(
                resident_id=resident1.resident_id,
                apartment_id=apartment1.apartment_id,
                type="Водоснабжение",
                description="Протечка трубы в ванной",
                created_at=datetime.now(),
                status_id=status1.status_id
            )
            request2 = Request(
                resident_id=resident2.resident_id,
                apartment_id=apartment2.apartment_id,
                type="Электрика",
                description="Не работает розетка в кухне",
                created_at=datetime.now(),
                status_id=status2.status_id
            )
            request3 = Request(
                resident_id=resident3.resident_id,
                apartment_id=apartment3.apartment_id,
                type="Отопление",
                description="Холодные батареи",
                created_at=datetime.now(),
                status_id=status1.status_id
            )
            db.add_all([request1, request2, request3])
            db.commit()
            logger.info("Таблица requests заполнена.")

            # 12. Заполнение таблицы workers
            logger.info("Заполнение таблицы workers...")
            worker1 = Worker(full_name="Сергей Васильев", specialization="Сантехник", phone="+79012345683")
            worker2 = Worker(full_name="Дмитрий Ковалёв", specialization="Электрик", phone="+79012345684")
            db.add_all([worker1, worker2])
            db.commit()
            logger.info("Таблица workers заполнена.")

            # 13. Заполнение таблицы assignments
            logger.info("Заполнение таблицы assignments...")
            assignment1 = Assignment(
                request_id=request1.request_id,
                worker_id=worker1.worker_id,
                assigned_at=datetime.now(),
                is_set_to_worker=True
            )
            assignment2 = Assignment(
                request_id=request2.request_id,
                worker_id=worker2.worker_id,
                assigned_at=datetime.now(),
                is_set_to_worker=True
            )
            db.add_all([assignment1, assignment2])
            db.commit()
            logger.info("Таблица assignments заполнена.")

            # 14. Заполнение таблицы materials
            logger.info("Заполнение таблицы materials...")
            material1 = Material(assignment_id=assignment1.assignment_id, name="Труба полипропиленовая", quantity=2)
            material2 = Material(assignment_id=assignment1.assignment_id, name="Фитинг", quantity=4)
            material3 = Material(assignment_id=assignment2.assignment_id, name="Розетка электрическая", quantity=1)
            db.add_all([material1, material2, material3])
            db.commit()
            logger.info("Таблица materials заполнена.")

            logger.info("Все таблицы успешно заполнены данными.")

        except Exception as e:
            db.rollback()
            logger.error(f"Ошибка при заполнении таблиц: {str(e)}")
            raise

if __name__ == "__main__":
    seed_database()