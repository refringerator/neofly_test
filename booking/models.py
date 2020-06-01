from django.db import models
from django.contrib.auth import get_user_model


class Order(models.Model):
    ORDER_STATUS = (
        ('payed', 'Оплачен'),
        ('new', 'Новый'),
    )

    ORDER_TYPE = (
        ('deposit', 'Депозита'),
        ('certificate', 'Сертификатов'),
        ('flightTime', 'Полетное время'),
    )

    sum = models.DecimalField(max_digits=8, decimal_places=2)
    order_id = models.CharField(max_length=30)
    trans_id = models.CharField(max_length=50, null=True)
    order_data = models.TextField()
    payed = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    owner = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=30, null=True, choices=ORDER_STATUS)
    type = models.CharField(max_length=30, null=True, choices=ORDER_TYPE)

    def __str__(self):
        return f"#{self.order_id} {self.owner_id} {self.type} {self.status}"


class Certificate(models.Model):
    cert_type = models.CharField(max_length=50)
    cert_number = models.CharField(max_length=50, null=True)
    flight_time = models.DecimalField(max_digits=3, decimal_places=0)
    is_used = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    owner = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.cert_number} {self.cert_type} {'Использован' if self.is_used else 'Не использован'}"


class Flights(models.Model):
    FLIGHT_STATUS = (
        ('flied', 'Отлетан'),
        ('payed', 'Оплачен'),
        ('canceled', 'Отменен'),
    )

    flight_time = models.DecimalField(max_digits=3, decimal_places=0)
    flight_type = models.CharField(max_length=50)
    is_used = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    flight_date = models.DateTimeField(null=True)
    owner = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=FLIGHT_STATUS, null=True)

    def __str__(self):
        return f"#{self.id} {self.flight_type} {self.flight_time} min"

