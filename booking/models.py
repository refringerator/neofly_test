from django.db import models
from django.contrib.auth import get_user_model


class Order(models.Model):
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    ORDER_STATUS = (
        ('payed', 'Оплачен'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
    )

    ORDER_TYPE = (
        ('buy_deposit', 'Покупка депозита'),
        ('buy_certificate', 'Покупка сертификатов'),
        ('buy_tariff', 'Покупка полетного времени по тарифу'),
        ('flight_certificate', 'Бронирование полетного времени по сертификатам'),
        ('flight_deposit', 'Бронирование полетного времени по депозиту'),
    )

    sum = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Сумма заказа")
    order_id = models.CharField(max_length=30, verbose_name="Идентификатор заказа клиента 1С")
    order_data = models.TextField(verbose_name="Детали заказа в JSON")
    payed = models.BooleanField(default=False, verbose_name="Заказ оплачен")
    date_created = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Дата создания")
    owner = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL, verbose_name="Клиент")
    status = models.CharField(max_length=30, null=True, choices=ORDER_STATUS, verbose_name="Статус")
    type = models.CharField(max_length=30, null=True, choices=ORDER_TYPE, verbose_name="Вид заказа")

    def __str__(self):
        return f"#{self.order_id} {self.owner_id} {self.type} {self.status}"


class Certificate(models.Model):
    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"

    cert_type = models.CharField(max_length=50, verbose_name="Категория сертификата")
    cert_number = models.CharField(max_length=50, null=True, verbose_name="Номер сертификата")
    flight_time = models.DecimalField(max_digits=3, decimal_places=0, verbose_name="Длительность полета")
    is_used = models.BooleanField(default=False, verbose_name="Использован")
    date_created = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Дата создания")
    owner = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL, verbose_name="Клиент")
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL, verbose_name="Заказ")

    def __str__(self):
        return f"{self.cert_number} {self.cert_type} {'Использован' if self.is_used else 'Не использован'}"


class Flights(models.Model):
    class Meta:
        verbose_name = "Полет"
        verbose_name_plural = "Полеты"

    FLIGHT_STATUS = (
        ('flied', 'Отлетан'),
        ('payed', 'Оплачен'),
        ('canceled', 'Отменен'),
        ('new', 'ОжидаетОплаты'),
    )

    flight_time = models.DecimalField(max_digits=3, decimal_places=0, verbose_name="Длительность полета")
    flight_type = models.CharField(max_length=50, verbose_name="Вид полета")
    is_used = models.BooleanField(default=False, verbose_name="Отлетан")
    date_created = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Дата создания")
    flight_date = models.DateTimeField(null=True, verbose_name="Дата бронирования")
    owner = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL, verbose_name="Клиент")
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL, verbose_name="Заказ")
    status = models.CharField(max_length=20, choices=FLIGHT_STATUS, null=True, verbose_name="Статус")
    remote_record_id = models.CharField(max_length=40, verbose_name="Идентификатор записи на полет 1С", null=True)

    def __str__(self):
        return f"#{self.id} {self.flight_type} {self.flight_time} min"

