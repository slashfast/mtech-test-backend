from os import getenv
from random import Random

from dotenv import load_dotenv
from faker import Faker
from peewee import ForeignKeyField
from playhouse.pool import PooledPostgresqlExtDatabase
from playhouse.postgres_ext import Model, UUIDField, TextField, FloatField

from uuid6 import uuid7

load_dotenv()

DB_NAME = getenv('DB_NAME')
DB_USER = getenv('DB_USER')
DB_PASSWORD = getenv('DB_PASSWORD')
DB_HOST = getenv('DB_HOST')
DB_PORT = getenv('DB_PORT')

db = PooledPostgresqlExtDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT,
                                 autoconnect=False, max_connections=32, stale_timeout=300)


class BaseModel(Model):
    class Meta:
        database = db


class Employee(BaseModel):
    class Meta:
        table_name = 'employees'

    uuid = UUIDField(default=uuid7, primary_key=True)
    first_name = TextField()
    middle_name = TextField()
    last_name = TextField()
    business_unit = TextField(null=True)
    role = TextField(null=True)
    bid = TextField(null=True)
    capitalization = FloatField(null=True)
    superiors = UUIDField(null=True)


class BusinessUnit(BaseModel):
    class Meta:
        table_name = 'business_units'

    id = UUIDField(default=uuid7, primary_key=True)
    name = TextField(unique=True)


class Domain(BaseModel):
    class Meta:
        table_name = 'domains'

    id = UUIDField(default=uuid7, primary_key=True)
    name = TextField(unique=True)


class Product(BaseModel):
    class Meta:
        table_name = 'products'

    id = UUIDField(default=uuid7, primary_key=True)
    name = TextField()
    manager = ForeignKeyField(Employee, backref='products')
    domain = TextField()
    jira_link = TextField()


db.connect()
db.drop_tables([Employee, BusinessUnit, Domain, Product], cascade=True)
db.create_tables([Employee, BusinessUnit, Domain, Product])

seed = 0
random = Random(seed)

CHIEF_ID = '018c8da1-bb27-72bd-b2eb-25cf5521de7e'

fake = Faker(['ru_RU'])
Faker.seed(seed)
business_units = ['MVM', 'MTech']
domains = ['Бэк-офис', 'Техплатформа', 'Офис больших данных', 'Цифровой опыт поставщика']
bid = ['opex', 'capex']

for unit in business_units:
    BusinessUnit.create(name=unit)

for domain in domains:
    Domain.create(name=domain)

for _ in range(5):
    name = fake.name().split(' ')
    Employee.create(uuid=uuid7(), first_name=name[0], middle_name=name[1], last_name=name[2], role='manager',
                    superiors=CHIEF_ID, business_unit=random.choice(business_units),
                    capitalization=random.uniform(4, 6), bid='capex')

managers = list(Employee.select().where(Employee.role == 'manager'))
for _ in range(10):
    name = fake.name().split(' ')
    manage = random.choice(managers)
    Employee.create(uuid=uuid7(), first_name=name[0], middle_name=name[1], last_name=name[2],
                    business_unit=manage.business_unit, role='lead', superiors=manage.uuid,
                    capitalization=random.uniform(2, 4), bid='capex')

leads = list(Employee.select().where(Employee.role == 'lead'))
for _ in range(30):
    name = fake.name().split(' ')
    lead = random.choice(leads)
    Employee.create(uuid=uuid7(), first_name=name[0], middle_name=name[1], last_name=name[2], role='developer',
                    business_unit=lead.business_unit, superiors=lead.uuid, capitalization=random.uniform(1, 2),
                    bid=random.choice(bid))

for _ in range(15):
    name = fake.name().split(' ')
    Employee.create(uuid=uuid7(), first_name=name[0], middle_name=name[1], last_name=name[2])

db.close()
