from abc import ABC, abstractmethod
from datetime import datetime
import json
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("clinic.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PatientMeta(type(ABC)):
    _registry = {}

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        if name != 'Patient':  # Исключаем сам базовый класс Patient
            PatientMeta._registry[name.lower()] = new_class  # Регистрация по имени в нижнем регистре
        return new_class

    @classmethod
    def get_patient_class(mcs, patient_type):
        return PatientMeta._registry.get(patient_type.lower())  # Поиск по имени в нижнем регистре


class Patient(ABC, metaclass=PatientMeta):
    """
    Базовый абстрактный класс для представления пациента.
    """

    def __init__(self, patient_id, name, age, gender, medical_history):
        self.__patient_id = patient_id
        self.__name = name
        self.__age = age
        self.__gender = gender
        self.__medical_history = medical_history

    @property
    def patient_id(self):
        return self.__patient_id

    @property
    def name(self):
        return self.__name

    @property
    def age(self):
        return self.__age

    @property
    def gender(self):
        return self.__gender

    @property
    def medical_history(self):
        return self.__medical_history

    @patient_id.setter
    def patient_id(self, patient_id):
        self.__patient_id = patient_id

    @name.setter
    def name(self, name):
        self.__name = name

    @age.setter
    def age(self, age):
        if 1 < age < 110:
            self.__age = age
        else:
            print("Недопустимый возраст")

    @gender.setter
    def gender(self, gender):
        if gender == 'м' or gender == 'ж':
            self.__gender = gender
        else:
            print("Недопустимый пол")

    def __str__(self):
        return f"Пациент: {self.name}, Возраст: {self.age}, Пол: {self.gender}"

    def __lt__(self, other):
        """Пациент меньше другого, если его возраст меньше или количество записей в истории болезней меньше."""
        if self.__age < other.__age:
            return True
        elif self.__age == other.__age:
            return len(self.__medical_history) < len(other.__medical_history)
        else:
            return False

    def __gt__(self, other):
        """Пациент больше другого, если его возраст больше или количество записей в истории болезней больше."""
        if self.__age > other.__age:
            return True
        elif self.__age == other.__age:
            return len(self.__medical_history) > len(other.__medical_history)
        else:
            return False

    def __eq__(self, other):
        """Сравнение пациентов (равны ли) по возрасту и количеству записей в истории болезней."""
        return self.__age == other.__age and len(self.__medical_history) == len(other.__medical_history)

    @abstractmethod
    def get_medical_history(self):
        pass

    def to_dict(self):
        base_dict = {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "medical_history": self.medical_history if self.medical_history else "",
            "type": self.__class__.__name__.lower(),  # Добавляем тип пациента
        }

        # Добавляем специфические поля для каждого подкласса
        if isinstance(self, AdultPatient):
            base_dict["occupation"] = getattr(self, "occupation", "")
        elif isinstance(self, ChildPatient):
            base_dict["guardian"] = getattr(self, "guardian", "")
        elif isinstance(self, SeniorPatient):
            base_dict["chronic_conditions"] = getattr(self, "chronic_conditions", "")
        return base_dict

    @staticmethod
    def from_dict(data):
        patient_class = PatientMeta.get_patient_class(data.get("type"))
        if not patient_class:
            raise ValueError(f"Неизвестный тип пациента: {data.get('type')}")

        # Определяем дополнительные аргументы в зависимости от типа пациента
        extra_args = {}
        if patient_class == AdultPatient:
            extra_args["occupation"] = data.get("occupation", "")
        elif patient_class == ChildPatient:
            extra_args["guardian"] = data.get("guardian", "")
        elif patient_class == SeniorPatient:
            extra_args["chronic_conditions"] = data.get("chronic_conditions", "")

        # Создаем объект пациента
        return patient_class(
            patient_id=data.get("patient_id"),
            name=data.get("name"),
            age=data.get("age"),
            gender=data.get("gender"),
            medical_history=data.get("medical_history", ""),
            **extra_args
        )


class AdultPatient(Patient):
    def __init__(self, patient_id, name, age, gender, medical_history, occupation):
        super().__init__(patient_id, name, age, gender, medical_history)
        self.__occupation = occupation

    @property
    def occupation(self):
        return self.__occupation

    @occupation.setter
    def occupation(self, occupation):
        self.__occupation = occupation

    def get_medical_history(self):
        history = f"Взрослый пациент [{self.name}], Род занятий: {self.occupation}\n " + self.medical_history
        return history

    def __str__(self):
        return f"Пациент: {self.name}, Род занятий: {self.occupation}, Возраст: {self.age}, Пол: {self.gender}"


class ChildPatient(Patient):
    def __init__(self, patient_id, name, age, gender, medical_history, guardian):
        super().__init__(patient_id, name, age, gender, medical_history)
        self.__guardian = guardian

    @property
    def guardian(self):
        return self.__guardian

    @guardian.setter
    def guardian(self, guardian):
        self.__guardian = guardian

    def get_medical_history(self):
        history = f"Ребенок [{self.name}], Опекун: {self.guardian}\n" + self.medical_history
        return history

    def __str__(self):
        return f"Пациент: {self.name}, Опекун: {self.guardian}, Возраст: {self.age}"


class SeniorPatient(Patient):
    def __init__(self, patient_id, name, age, gender, medical_history, chronic_conditions):
        super().__init__(patient_id, name, age, gender, medical_history)
        self.__chronic_conditions = chronic_conditions

    @property
    def chronic_conditions(self):
        return self.__chronic_conditions

    @chronic_conditions.setter
    def chronic_conditions(self, chronic_conditions):
        self.__chronic_conditions = chronic_conditions

    def get_medical_history(self):
        history = f"Пожилой пациент [{self.name}], хронические заболевания: {self.chronic_conditions}\n" \
                  + self.medical_history
        return history

    def __str__(self):
        return f"Пациент: {self.name}, хронические заболевания: {self.chronic_conditions}, Возраст: {self.age}"


# для doctor_info в Appointment
class DoctorInfo:
    def __init__(self, name, specialty, contact_info):
        self.name = name
        self.specialty = specialty
        self.contact_info = contact_info


# для взаимодействия с услугами в Appointment
class Service:
    def __init__(self, name, price):
        self.name = name
        self.price = price


# интерфейс для генерации отчетов о приемах реализован в Appointment
class Reportable(ABC):
    @abstractmethod
    def generate_report(self):
        pass


# информация о приеме
class Appointment(Reportable):
    def __init__(self, appointment_id, patient, doctor, date, diagnosis, prescription, doctor_info):
        self.__appointment_id = appointment_id
        self.__patient = patient
        self.__doctor = doctor
        self.__date = date
        self.__diagnosis = diagnosis
        self.__prescription = prescription
        self.__doctor_info = doctor_info
        self.__services = []

    @property
    def appointment_id(self):
        return self.__appointment_id

    @appointment_id.setter
    def appointment_id(self, appointment_id):
        self.__appointment_id = appointment_id

    @property
    def patient(self):
        return self.__patient

    @patient.setter
    def patient(self, patient):
        self.__patient = patient

    @property
    def doctor(self):
        return self.__doctor

    @doctor.setter
    def doctor(self, doctor):
        self.__doctor = doctor

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, date):
        self.__date = date

    @property
    def diagnosis(self):
        return self.__diagnosis

    @diagnosis.setter
    def diagnosis(self, diagnosis):
        self.__diagnosis = diagnosis

    @property
    def prescription(self):
        return self.__prescription

    @prescription.setter
    def prescription(self, prescription):
        self.__prescription = prescription

    @property
    def doctor_info(self):
        return self.__doctor_info

    @doctor_info.setter
    def doctor_info(self, doctor_info):
        self.__doctor_info = doctor_info

    def add_service(self, service):
        self.__services.append(service)

    def remove_service(self, service):
        if service in self.__services:
            self.__services.remove(service)
        else:
            print("Ошибка: Услуга не найдена в списке услуг.")

    def calculate_total(self):
        total = 0
        for service in self.__services:
            total += service.price
        return total

    def generate_report(self):
        report = (f"Отчет по приему:\n"
                  f"  ID приема: {self.appointment_id}\n"
                  f"  Пациент: {self.patient}\n"
                  f"  Врач: {self.doctor}\n"
                  f"  Дата: {self.date}\n"
                  f"  Диагноз: {self.diagnosis}\n"
                  f"  Рецепт: {self.prescription}\n"
                  f"  Информация о враче: {self.doctor_info}\n"
                  f"  Услуги: {', '.join(s.name for s in self.__services) if self.__services else 'Нет услуг'}\n"
                  f"  Общая стоимость: {self.calculate_total()}")
        return report

    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "patient": self.patient.to_dict(),
            "doctor": self.doctor,
            "date": self.date,
            "diagnosis": self.diagnosis,
            "prescription": self.prescription,
            "doctor_info": {
                "name": self.doctor_info.name,
                "specialty": self.doctor_info.specialty,
                "contact_info": self.doctor_info.contact_info,
            },
            "services": [{"name": s.name, "price": s.price} for s in self._Appointment__services],
        }

    @staticmethod
    def from_dict(data):
        patient = Patient.from_dict(data["patient"])
        doctor_info = DoctorInfo(
            name=data["doctor_info"]["name"],
            specialty=data["doctor_info"]["specialty"],
            contact_info=data["doctor_info"]["contact_info"],
        )
        appointment = Appointment(
            appointment_id=data["appointment_id"],
            patient=patient,
            doctor=data["doctor"],
            date=data["date"],
            diagnosis=data["diagnosis"],
            prescription=data["prescription"],
            doctor_info=doctor_info,
        )
        for service_data in data["services"]:
            service = Service(name=service_data["name"], price=service_data["price"])
            appointment.add_service(service)
        return appointment


# интерфейс для записи на прием реализован в AppointmentProcess
class Schedulable(ABC):
    @abstractmethod
    def schedule_appointment(self):
        pass


# Миксин для записи действия
class LoggingMixin:
    def log_action(self, action):
        print(f"Действие: {action}")


# Миксин для отправки уведомления
class NotificationMixin:
    def send_notification(self, message):
        print(f"Уведомление: {message}")


# для записи о приеме в лог
class AppointmentWithLogging(Appointment, LoggingMixin):
    def __init__(self, appointment_id, patient, doctor, date, diagnosis, prescription, doctor_info):
        super().__init__(appointment_id, patient, doctor, date, diagnosis, prescription, doctor_info)
        self.log_action(f"Прием {appointment_id} создан")

    def update_diagnosis(self, new_diagnosis):
        self.diagnosis = new_diagnosis
        self.log_action(f"Диагноз приема {self.appointment_id} обновлен: {new_diagnosis}")


# для отправки уведомления о запросе приема
class PatientWithNotifications(Patient, NotificationMixin):
    def __init__(self, patient_id, name, age, gender, medical_history):
        super().__init__(patient_id, name, age, gender, medical_history)

    def request_appointment(self, date):
        self.send_notification(f"Запрос на прием на {date} отправлен")

    def get_medical_history(self):
        return f"История болезни пациента: {self.name}\n{self.medical_history}"


# для отправки уведомлений и логирования при подтверждении и отмене приема
class AppointmentWithLoggingAndNotification(Appointment, LoggingMixin, NotificationMixin):
    def __init__(self, appointment_id, patient, doctor, date, diagnosis, prescription, doctor_info):
        super().__init__(appointment_id, patient, doctor, date, diagnosis, prescription, doctor_info)
        self.log_action(f"Прием {appointment_id} создан")

    def confirm_appointment(self):
        self.send_notification(f"Ваш прием на {self.date} подтвержден.")
        self.log_action(f"Прием {self.appointment_id} подтвержден")

    def cancel_appointment(self):
        self.send_notification(f"Прием {self.appointment_id} отменен.")
        self.log_action(f"Прием {self.appointment_id} отменен")


# метод для создания пациентов в программе
class PatientFactory:
    @staticmethod
    def create_patient(patient_type, *args, **kwargs):
        patient_class = PatientMeta.get_patient_class(patient_type)
        if patient_class:
            return patient_class(*args, **kwargs)
        else:
            raise ValueError(f"Неизвестный тип пациента: {patient_type}")


# "Цепочка обязанностей" для обработки запросов на изменение диагноза
class DiagnosisChangeHandler(ABC):
    def __init__(self, successor=None):
        self._successor = successor

    @abstractmethod
    def handle_request(self, appointment, new_diagnosis):
        pass

    def set_successor(self, successor):
        self._successor = successor


class Doctor(DiagnosisChangeHandler):
    def handle_request(self, appointment, new_diagnosis):
        if "незначительное изменение" in new_diagnosis.lower():
            print("Врач одобрил изменение диагноза.")
            appointment.diagnosis = new_diagnosis
        elif self._successor:
            print("Врач передал запрос выше по цепочке.")
            self._successor.handle_request(appointment, new_diagnosis)
        else:
            print("Изменение диагноза не может быть одобрено.")


class DepartmentHead(DiagnosisChangeHandler):
    def handle_request(self, appointment, new_diagnosis):
        if "пересмотр лечения" in new_diagnosis.lower():
            print("Заведующий отделением одобрил изменение диагноза.")
            appointment.diagnosis = new_diagnosis
        elif self._successor:
            print("Заведующий отделением передал запрос выше по цепочке.")
            self._successor.handle_request(appointment, new_diagnosis)
        else:
            print("Изменение диагноза не может быть одобрено.")


class ChiefPhysician(DiagnosisChangeHandler):
    def handle_request(self, appointment, new_diagnosis):
        print("Главный врач одобрил изменение диагноза.")
        appointment.diagnosis = new_diagnosis


# Исключения
class InvalidPatientError(Exception):
    """Исключение для некорректных данных пациента."""

    def __init__(self, message="Некорректные данные пациента"):
        self.message = message
        super().__init__(self.message)


class PermissionDeniedError(Exception):
    """Исключение для отсутствия прав доступа."""

    def __init__(self, message="У вас нет прав доступа"):
        self.message = message
        super().__init__(self.message)


class AppointmentNotFoundError(Exception):
    """Исключение для случая, если прием не найден."""

    def __init__(self, message="Прием не найден"):
        self.message = message
        super().__init__(self.message)


# Шаблонный метод (Template Method)
class AppointmentProcess(Schedulable):
    def schedule_appointment(self):
        """Шаблонный метод для записи на прием."""
        try:
            self.check_doctor_availability()
            self.make_appointment()
            self.confirm_appointment()
        except Exception as e:
            print(f"Ошибка при записи на прием: {e}")

    @abstractmethod
    def check_doctor_availability(self):
        """Проверка доступности врача."""
        pass

    @abstractmethod
    def make_appointment(self):
        """Запись на прием."""
        pass

    @abstractmethod
    def confirm_appointment(self):
        """Подтверждение записи."""
        pass


class OnlineAppointmentProcess(AppointmentProcess):
    def check_doctor_availability(self):
        print("Проверка доступности врача онлайн...")

    def make_appointment(self):
        print("Запись на прием через онлайн-систему...")

    def confirm_appointment(self):
        print("Подтверждение записи через SMS или email...")


class OfflineAppointmentProcess(AppointmentProcess):
    def check_doctor_availability(self):
        print("Проверка доступности врача офлайн...")

    def make_appointment(self):
        print("Запись на прием через регистратуру...")

    def confirm_appointment(self):
        print("Подтверждение записи через телефонный звонок...")


# Декоратор для проверки прав доступа
def check_permissions(*required_roles):
    def decorator(func):
        def wrapper(user_role, *args, **kwargs):
            if user_role not in required_roles:
                raise PermissionDeniedError(f"Требуется одна из ролей: {', '.join(required_roles)}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


# использования декоратора для проверки доступа на изменение диагноза
@check_permissions("Doctor", 'Department_head', 'Chief_physician')
def change_diagnosis(appointment, new_diagnosis, handler):
    """
    Функция для изменения диагноза с использованием цепочки обязанностей.
    :appointment: Прием, диагноз которого нужно изменить.
    :new_diagnosis: Новый диагноз.
    :handler: Цепочка обязанностей для обработки запроса.
    """
    print(f"Запрос на изменение диагноза на '{new_diagnosis}'...")
    handler.handle_request(appointment, new_diagnosis)


# Класс клиники для управления пациентами
class Clinic:
    def __init__(self):
        self.patients = []

    def add_patient(self, patient):
        if not isinstance(patient, Patient):
            logger.error("Ошибка: Некорректный объект пациента.")
            raise InvalidPatientError("Некорректный объект пациента.")
        self.patients.append(patient)
        print(f"Пациент {patient.name} добавлен в клинику.")
        logger.info(f"Пациент {patient.name} добавлен в клинику.")

    def remove_patient(self, patient_id):
        for patient in self.patients:
            if patient.patient_id == patient_id:
                self.patients.remove(patient)
                print(f"Пациент с ID {patient_id} удален из клиники.")
                logger.info(f"Пациент с ID {patient_id} удален из клиники.")
                return
        logger.error("Ошибка: Пациент не найден.")
        raise AppointmentNotFoundError("Пациент не найден.")

    def get_all_patients(self):
        return self.patients

    def search_by_name(self, name):
        return [patient for patient in self.patients if name.lower() in patient.name.lower()]


def save_to_file(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_from_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


# Основная функция main

def main():
    try:
        # Пример использования программы

        # --- Создание пациентов ---
        # Используйте PatientFactory для создания пациентов разных типов.
        print("\n--- Создание пациентов ---")
        adult_patient = PatientFactory.create_patient(
            "adultpatient", "A123", "Иван Петров", 35, "м", "Аллергия на пыльцу", occupation="Программист"
        )
        child_patient = PatientFactory.create_patient(
            "childpatient", "C456", "Маша Сидорова", 8, "ж", "Простуда", guardian="Анна Сидорова"
        )
        senior_patient = PatientFactory.create_patient(
            "seniorpatient", "S789", "Петр Иванов", 70, "м", "Гипертония", chronic_conditions="Диабет"
        )

        # Добавьте пациентов в клинику с помощью метода add_patient.
        clinic = Clinic()
        clinic.add_patient(adult_patient)
        clinic.add_patient(child_patient)
        clinic.add_patient(senior_patient)

        # --- Управление данными ---
        # Редактируйте данные пациентов через сеттеры.
        print("\n--- Редактирование данных пациентов ---")
        adult_patient.age = 36  # Изменение возраста
        child_patient.guardian = "Ольга Сидорова"  # Изменение опекуна
        print(f"Обновленные данные пациента: {adult_patient}")
        print(f"Обновленные данные пациента: {child_patient}")

        # Удаляйте пациентов из клиники с помощью метода remove_patient.
        print("\n--- Удаление пациента ---")
        clinic.remove_patient("C456")

        # --- Анализ данных ---
        # Получите список всех пациентов с помощью метода get_all_patients.
        print("\n--- Получение списка всех пациентов ---")
        all_patients = clinic.get_all_patients()
        for patient in all_patients:
            print(patient)

        # Найдите пациентов по имени с помощью метода search_by_name.
        print("\n--- Поиск пациентов по имени ---")
        search_result = clinic.search_by_name("Иван")
        for patient in search_result:
            print(f"Найден пациент: {patient}")

        # --- Логирование и уведомления ---
        # Используйте миксины LoggingMixin и NotificationMixin для записи действий и отправки уведомлений.
        print("\n--- Логирование и уведомления ---")
        doctor_info = DoctorInfo("Доктор Иванов", "Терапевт", "ivanov@example.com")
        appointment = AppointmentWithLoggingAndNotification(
            appointment_id="AP101",
            patient=adult_patient,
            doctor="Доктор Иванов",
            date=datetime.now().strftime("%Y-%m-%d"),
            diagnosis="Грипп",
            prescription="Парацетамол",
            doctor_info=doctor_info
        )

        # Подтверждение и отмена приема
        appointment.confirm_appointment()
        appointment.cancel_appointment()

        # Запрос на прием с уведомлением
        patient_with_notifications = PatientWithNotifications(
            patient_id="P123",
            name="Иван Петров",
            age=35,
            gender="м",
            medical_history="Аллергия на пыльцу"
        )
        patient_with_notifications.request_appointment(date="2023-10-15")

        # --- Сериализация и десериализация ---
        # # НОВОЕ: Демонстрация сохранения и загрузки данных о пациентах и приемах.
        print("\n--- Сериализация и десериализация ---")
        save_to_file(adult_patient.to_dict(), "patient.json")  # Сохранение пациента в файл
        loaded_data = load_from_file("patient.json")  # Загрузка данных из файла
        # Восстановление объекта пациента
        try:
            loaded_patient = Patient.from_dict(loaded_data)
            print(f"Загруженный пациент: {loaded_patient}")
        except ValueError as e:
            print(f"Произошла ошибка при загрузке пациента: {e}")

        # --- Методы сравнения ---
        # # НОВОЕ: Демонстрация сравнения пациентов.
        print("\n--- Методы сравнения ---")
        if adult_patient == senior_patient:
            print("Пациенты равны.")
        else:
            print("Пациенты не равны.")

        if adult_patient < senior_patient:
            print("Первый пациент младше второго.")
        else:
            print("Первый пациент старше или равен второму.")

        # --- Обработка исключений ---
        # Обрабатывайте пользовательские исключения при попытке записи на прием с некорректными данными или при отсутствии прав доступа.
        print("\n--- Обработка исключений ---")
        try:
            # Попытка создания пациента с некорректным типом
            invalid_patient = PatientFactory.create_patient(
                "invalidtype", "X999", "Некорректный Пациент", 200, "м", "Ошибка"
            )
        except ValueError as e:
            print(f"Перехвачено исключение: {e}")

        try:
            # Попытка удаления несуществующего пациента
            clinic.remove_patient("UNKNOWN_ID")
        except AppointmentNotFoundError as e:
            print(f"Перехвачено исключение: {e}")

        # Пример изменения диагноза с цепочкой обязанностей
        print("\n--- Изменение диагноза с цепочкой обязанностей ---")
        doctor = Doctor()
        department_head = DepartmentHead()
        chief_physician = ChiefPhysician()

        # Установка последовательности обработчиков
        doctor.set_successor(department_head)
        department_head.set_successor(chief_physician)

        # # НОВОЕ: Добавлены дополнительные вызовы для демонстрации работы цепочки обязанностей.
        try:
            change_diagnosis('user', appointment, "Незначительное изменение", doctor)  # Роль: Doctor
        except PermissionDeniedError as e:
            print(f"Перехвачено исключение: {e}")

        try:
            change_diagnosis('Department_head', appointment, "Пересмотр лечения",
                             department_head)  # Роль: DepartmentHead
        except PermissionDeniedError as e:
            print(f"Перехвачено исключение: {e}")

        try:
            change_diagnosis('Chief_physician', appointment, "Серьезное изменение",
                             chief_physician)  # Роль: ChiefPhysician
        except PermissionDeniedError as e:
            print(f"Перехвачено исключение: {e}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
