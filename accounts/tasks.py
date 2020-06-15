
from celery import Celery
from django.contrib.auth import get_user_model

import logging

app = Celery('tasks', broker='redis://localhost:6379')


@app.task
def update_users_info(user_id):
    user_model = get_user_model()
    user = user_model.objects.get(pk=user_id)
    user.name = "test"
    user.save()
    logging.warning(f"celery task {user_id}")
