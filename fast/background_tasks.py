from fastapi import BackgroundTasks, FastAPI, Depends
from typing import Annotated

app = FastAPI()


#TODO background task function

def write_notification(email: str, message=""):
    with open("bg_log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)

def print_name(n: str):
    with open("bg_log.txt", mode="a") as log:
        log.write(f"\nName: {n}\n")



@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}


@app.post("/name")
async def name_noti(b_tasks:BackgroundTasks, name: str = "xyz"):
    b_tasks.add_task(print_name, name)
    return {"message": "Name sent in the background"}



#TODO Background tasks with dependencies


# BackgroundTasks object
#         │
#         ├────────► get_query()          # Same BackgroundTasks object injected
#         │
#         └────────► send_notification()  # Same object reused here


# BackgroundTasks

# Task 1
# write_log("found query: hello")         # Added by dependency (get_query)

# Task 2
# write_log("message to test@gmail.com")  # Added by endpoint (send_notification)


def write_log(message: str):
    with open("bg_log.txt", mode="a") as log:
        log.write(f"\n{message}\n")


def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    if q:
        message = f"found query: {q}\n"
        background_tasks.add_task(write_log, message)
    return q


@app.post("/send-notification-with-dependency/{email}")
async def send_notification(
    email: str, background_tasks: BackgroundTasks, q: Annotated[str, Depends(get_query)]
):
    message = f"message to {email}\n"
    background_tasks.add_task(write_log, message)
    return {"message": "Message sent"}