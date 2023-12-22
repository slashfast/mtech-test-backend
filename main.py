from datetime import datetime, UTC
from os import makedirs, path
from sys import stdout

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel
from database import db, BusinessUnit, Employee, Domain, Product


class EmployeeBody(BaseModel):
    uuid: str
    lead_uuid: str
    bid: str
    business_unit: str
    capitalization: str
    role: str


class ProductBody(BaseModel):
    manager_uuid: str
    name: str
    jira_link: str
    domain: str


app = FastAPI()

LOGS_DIR = 'logs'

makedirs(LOGS_DIR, exist_ok=True)
logger.add(stdout, format='{time} {level} {message}', filter='my_module', level='INFO')
logger.add(path.join(LOGS_DIR, f'{datetime.now(UTC).strftime("%Y%m%d%H%M%S")}.log'))

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/business_units')
async def read_business_units():
    db.connect()
    business_units = [field.name for field in list(BusinessUnit.select(BusinessUnit.name))]
    db.close()
    return business_units


@app.get('/employees/')
async def read_employees(role: str = None):
    db.connect()
    employees = [
        {'value': field.uuid, 'title': ' '.join([field.first_name, field.middle_name, field.last_name])} for field in
        list(
            Employee.
            select(Employee.uuid, Employee.last_name, Employee.first_name, Employee.middle_name).
            where(Employee.role == role if role else Employee.role.is_null())
        )
    ]
    db.close()
    return employees


@app.post('/new_employee')
async def write_employee(employee: EmployeeBody):
    try:
        db.connect()
        Employee.update(role=employee.role,
                        business_unit=employee.business_unit, superiors=employee.lead_uuid,
                        capitalization=employee.capitalization,
                        bid=employee.bid).where(Employee.uuid == employee.uuid).execute()
    except Exception as e:
        logger.warning(f'{e}'.replace('\n', ' '))
    finally:
        db.close()
    return employee


@app.get('/domains')
async def read_domains():
    db.connect()
    domains = [field.name for field in list(Domain.select(Domain.name))]
    db.close()
    return domains


@app.post('/new_product')
async def write_product(product: ProductBody):
    db.connect()
    Product.create(name=product.name, manager_id=product.manager_uuid, domain=product.domain,
                   jira_link=product.jira_link)
    db.close()
    return product
