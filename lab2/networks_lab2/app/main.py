from fastapi import FastAPI, Response, Depends, File, UploadFile
from typing import Optional, Dict
from pydantic import BaseModel
from redis import *

initial_data = {
    "1004567": {
        "name": "Daniel Ching",
        "id": "1004567",
        "age" : 20,
        "email": "daniel4567@gmail.com",
        "phone": "89998999"
    },

    "1004321": {
        "name": "Dylan Tan",
        "id": "1004321",
        "age" : 24,
        "email": "dylan4321@gmail.com",
        "phone": "82344328"
    },

    "1005432": {
        "name": "Anne Yeo",
        "id": "1005432",
        "age" : 22,
        "email": "anne4444@gmail.com",
        "phone": "93456543"
    },

    "1005555": {
        "name": "Barry Ng",
        "id": "1005555",
        "age" : 23,
        "email": "barry5555@gmail.com",
        "phone": "94455449"
    },

    "1004123": {
        "name": "Jack Ki Chan",
        "id": "1004123",
        "age" : 20,
        "email": "jackkichan4123@gmail.com",
        "phone": "98765432"
    }
}

def get_redis_client():
    return Redis(host="redis")

def populate_database(initial_data):
    redis_client = get_redis_client()

    for key ,value in initial_data.items():
        redis_client.hmset(key, value)
        print(key, value)

    print(f"Database has been populated with initial data")

populate_database(initial_data)

app = FastAPI()

class Record(BaseModel):
    name: str
    id: str
    age: int
    email: str
    phone: str

@app.get("/")
def read_root():
    return "Hello! Records resource are in /records"

@app.get("/records")
def get_all_records(response: Response, sortBy: Optional[str] = None, count: Optional[int] = None, offset: Optional[int] = None, redis_client: Redis = Depends(get_redis_client)):
    print(f"sortBy: {sortBy}, count: {count}, offset: {offset}")

    if (count is not None and count <=0) or (offset is not None and offset <0):
        response.status_code = 400
        return None

    all_records = redis_client.scan()[1]

    ls_of_records = []
    for id in all_records:
        record = redis_client.hgetall(id)
        ls_of_records.append(record)

    try:
        if count and sortBy and offset:
            new_list = sorted(ls_of_records, key=lambda k: k[sortBy.encode()])
            offset_list = new_list[offset:]
            return offset_list[:count]

        elif count and sortBy:
            new_list = sorted(ls_of_records, key=lambda k: k[sortBy.encode()])
            return new_list[:count]
        
        elif count and offset:
            offset_list = ls_of_records[offset:]
            return offset_list[:count]

        elif sortBy and offset:
            new_list = sorted(ls_of_records, key=lambda k: k[sortBy.encode()])
            return new_list[offset:]

        elif count:
            return ls_of_records[:count]

        elif sortBy:
            return sorted(ls_of_records, key=lambda k: k[sortBy.encode()])
        
        elif offset:
            return ls_of_records[offset:]

        else:
            return ls_of_records
    except:
        response.status_code = 404
        return None

@app.get("/records/{studentID}")
def get_record(studentID: str, response: Response, redis_client: Redis = Depends(get_redis_client)):
    print(studentID)

    try:
        record = redis_client.hgetall(studentID)
        if len(record) == 0:
            response.status_code = 404
            return None

        return record
    except:
        response.status_code = 404
        return None


@app.post("/records")
def create_student(record: Record, response: Response, redis_client: Redis = Depends(get_redis_client)):
    print("Creating", record.name, record.id, record.age, record.email, record.phone)

    if len(record.name) == 0  or len(record.id) == 0 or record.age <= 0 or len(record.email) == 0 or len(record.phone) == 0:
        response.status_code = 422
        return None

    dic = {
        "name": record.name,
        "id": record.id,
        "age": record.age,
        "email": record.email,
        "phone": record.phone
    }

    redis_client.hmset(record.id, dic)
    response.status_code = 201
    return "Student record added"

@app.post("/upload/{studentID}")
async def upload_file(studentID: str, response: Response, file: UploadFile = File(...), redis_client: Redis = Depends(get_redis_client)):

    contents = await file.read()
    redis_client.hmset(studentID, {"essay": contents})
    # redis_client.set(file.filename, contents)
    return "transcript uploaded"

@app.delete("/records/{studentID}")
def del_record(studentID: str, response: Response, redis_client: Redis = Depends(get_redis_client)):
    print(studentID)
    if redis_client.exists(studentID):
        redis_client.delete(studentID)
        return f"Deleted records for {studentID}"
    else:
        response.status_code = 404
        return None

@app.delete("/records")
def del_record_in_batches(response: Response, idStart: Optional[int] = None, idEnd: Optional[int] = None, redis_client: Redis = Depends(get_redis_client)):
    
    if idStart and idEnd:
        if idStart <0 or idEnd <0:
            response.status_code = 404
            return None
        all_records = redis_client.scan()[1] 

        for id in all_records:
            if idStart <= int(id) <= idEnd:
                redis_client.delete(id)
        return "Batch Delete is a success"    

    else:
        response.status_code = 422
        return None

