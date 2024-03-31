"""
    Pets models
"""
from django.db import models
from users.models import CustomUser

# Create your models here.


class BasePermissionModel(models.Model):
    class Meta:
        abstract = True


class Category(BasePermissionModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def can_be_featured(self):
        return True  # Override to return True


class Product(BasePermissionModel):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image_url = models.URLField()

    def __str__(self) -> str:
        return self.name


class Customer(BasePermissionModel):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(BasePermissionModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_placed = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    products = models.ManyToManyField(Product, through='OrderLine')

    def __str__(self):
        return f"Order #{self.id} - {self.customer.first_name} {self.customer.last_name}"


class OrderLine(BasePermissionModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
