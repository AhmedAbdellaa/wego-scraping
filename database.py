from motor import motor_asyncio

MONGO_URL = 'mongodb://127.0.0.1:27017/'


client = motor_asyncio.AsyncIOMotorClient(MONGO_URL)

database=client.flights

flight_collection= database.get_collection('flight_collection')

# def student_helper(student) -> dict:
#     return {
#         "id": str(student["_id"]),
#         "fullname": student["fullname"],
#         "email": student["email"],
#         "course_of_study": student["course_of_study"],
#         "year": student["year"],
#         "GPA": student["gpa"],
#     }


