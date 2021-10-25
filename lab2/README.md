# Networks Lab 2 - REST API

## About

In this lab, I have created a REST-over-HTTP API that imitates a fake myportal. It contains students' records consisting of their name, id, age, email address and phone number.

Make sure you have [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) installed.

## How to run code

1. Change directory into networks_lab2

    `cd ./networks_lab2`

2. Build the code 

    `docker-compose build`

3. Run docker-compose

    `docker-compose up`

4. Open your web browser and go to [http://127.0.0.1:8000](http://127.0.0.1:8000).


## Making HTTP Requests

### GET requests

1. Go to the checkoff folder and run `get_basic.http`

    This will return a list of dictionary, showing all student records.

    ```
    [
        {
            "name": "Anne Yeo",
            "id": "1005432",
            "age": "22",
            "email": "anne4444@gmail.com",
            "phone": "93456543"
        },
        {
            "name": "Barry Ng",
            "id": "1005555",
            "age": "23",
            "email": "barry5555@gmail.com",
            "phone": "94455449"
        },
        {
            "name": "Jack Ki Chan",
            "id": "1004123",
            "age": "20",
            "email": "jackkichan4123@gmail.com",
            "phone": "98765432"
        },
        {
            "name": "Dylan Tan",
            "id": "1004321",
            "age": "24",
            "email": "dylan4321@gmail.com",
            "phone": "82344328"
        },
        {
            "name": "Daniel Ching",
            "id": "1004567",
            "age": "20",
            "email": "daniel4567@gmail.com",
            "phone": "89998999"
        }
    ]

    ```

2. Run `get_limit.http`

    This sends a GET request with query parameters `sortBy=name`, `count=2` and `offset=1`

    The expected response would be

    ```
    [
        {
            "name": "Barry Ng",
            "id": "1005555",
            "age": "23",
            "email": "barry5555@gmail.com",
            "phone": "94455449"
        },
        {
            "name": "Daniel Ching",
            "id": "1004567",
            "age": "20",
            "email": "daniel4567@gmail.com",
            "phone": "89998999"
        }
    ]
    ```
### POST request

1. Run `post_create_student.http`

    This creates a new student record. The expected response is `"Student record added"`

2. Run `get_specific_student.http` to view the new record

    The resulting response is

    ```
    {
        "name": "Cecelia Tan",
        "id": "1004001",
        "age": "19",
        "email": "cecelia4001@gmail.com",
        "phone": "89101112"
    }
    ```
### DELETE request

1. Run `delete_record.http`

    The response will be `"Deleted records for 1004001"`

2. Run `get_basic.http` to check all records and verify that student record for ID 1004001 is not there

    Response should look like

    ```
    [
        {
            "name": "Anne Yeo",
            "id": "1005432",
            "age": "22",
            "email": "anne4444@gmail.com",
            "phone": "93456543"
        },
        {
            "name": "Barry Ng",
            "id": "1005555",
            "age": "23",
            "email": "barry5555@gmail.com",
            "phone": "94455449"
        },
        {
            "name": "Jack Ki Chan",
            "id": "1004123",
            "age": "20",
            "email": "jackkichan4123@gmail.com",
            "phone": "98765432"
        },
        {
            "name": "Dylan Tan",
            "id": "1004321",
            "age": "24",
            "email": "dylan4321@gmail.com",
            "phone": "82344328"
        },
        {
            "name": "Daniel Ching",
            "id": "1004567",
            "age": "20",
            "email": "daniel4567@gmail.com",
            "phone": "89998999"
        }
    ]

    ```

## Challenges

### File upload in a POST request, using multipart/form-data

1. Run `post_upload_file.http`

    This uploads a file using multipart/form-data to student with ID `1004123`. The response will be `"transcript uploaded"`

2. Go into `get_specific_student.http` and change the id to `1004123`

3. Run `get_specific_student.http`

    You should now be able to see an added field. The response will be

    ```
    {
        "age": "20",
        "essay": "Looking back on a childhood filled with events and memories, I find it rather difficult to pick one that leaves me with\r\nthe fabled \"warm and fuzzy feelings.\" As the daughter of an Air Force major, I had the pleasure of traveling across\r\nAmerica in many moving trips. I have visited the monstrous trees of the Sequoia National Forest, stood on the edge of\r\nthe Grand Canyon and have jumped on the beds at Caesar's Palace in Lake Tahoe.\"\r\n\r\n\"The day I picked my dog up from the pound was one of the happiest days of both of our lives. I had gone to the pound\r\njust a week earlier with the idea that I would just \"look\" at a puppy. Of course, you can no more just look at those\r\nsquiggling little faces so filled with hope and joy than you can stop the sun from setting in the evening. I knew within\r\nminutes of walking in the door that I would get a puppy… but it wasn't until I saw him that I knew I had found my puppy.\"\r\n\r\n\"Looking for houses was supposed to be a fun and exciting process. Unfortunately, none of the ones that we saw seemed to\r\nmatch the specifications that we had established. They were too small, too impersonal, too close to the neighbors. After\r\ndays of finding nothing even close, we began to wonder: was there really a perfect house out there for us?\r\n",
        "id": "1004123",
        "name": "Jack Ki Chan",
        "email": "jackkichan4123@gmail.com",
        "phone": "98765432"
    }
    ```

### A special route that can perform a batch delete of resources matching a certain condition

1. Run `delete_by_batch.http`

    This request takes in query parameters `idStart` and `idEnd` and performs a delete operation iteratively, for all students with IDs that fall in the range of the query parameters.

    For this request, since `idStart=1004000` and `idEnd=1005000`, all student records with IDs between `1004000` and `1005000` will be deleted.

    The expected response is `"Batch Delete is a success"`

2. To validate, run `get_basic.http`

    The Reponse now will be
    ```
    [
        {
            "name": "Anne Yeo",
            "id": "1005432",
            "age": "22",
            "email": "anne4444@gmail.com",
            "phone": "93456543"
        },
        {
            "name": "Barry Ng",
            "id": "1005555",
            "age": "23",
            "email": "barry5555@gmail.com",
            "phone": "94455449"
        }
        ]
    ```

## Analysis

1. Identify which routes in your application are _idempotent_, and provide proof to support your answer.

    Routes in my application that are idempotent consists of `GET` and `DELETE` requests. This is because running `get_limit.http` will always give me the same result of:

    ```
    [
        {
            "name": "Barry Ng",
            "id": "1005555",
            "age": "23",
            "email": "barry5555@gmail.com",
            "phone": "94455449"
        },
        {
            "name": "Daniel Ching",
            "id": "1004567",
            "age": "20",
            "email": "daniel4567@gmail.com",
            "phone": "89998999"
        }
    ]
    ```

    When I run `delete_record.http`, after deleting successfully for the first time, I will only receive a change in response code of `404` due to the record not existing in the database. However, the database still remain unmodified no matter how many times i send the same request.

2. Performance analysis

    ```
    n - number of ids

    m - number of fields for an individual id
    ```

    A `GET` request to obtain all records would take O(nm). Getting all the IDs via `scan()` takes O(n), and as I would have to loop through all IDs taking O(n), and get all values via `hgetall(id)` from each ID taking O(m). Therefore, it would take approximately O(nm). 

    A `GET` request to get a record for an individual student takes O(m). I have reduced the complexity by **NOT** having to check if the id exists as that would take O(n), and simply return an error if I get an empty dictionary.

    A `POST` request for a student's record and file upload would take O(m).

    A `DELETE` record for an individual would take O(m + n) as I would first have to check if the record exists taking O(n), and deleting the fields in the record would take O(m).

    A `DELETE` for the batch would take O(nm). This is because looping through all the IDs would take O(n) and deleting all fields in each ID would take O(m). 
