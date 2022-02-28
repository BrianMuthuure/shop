from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:item_list_by_category', args=[self.slug])


class Item(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='laptops/pictures', default='default.png')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    marked_price = models.PositiveIntegerField(default=0)
    selling_price = models.PositiveIntegerField(default=0)
    warranty = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    average_rating = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        ordering = ('-id', )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:item_detail', args=[self.slug])


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    comment = models.CharField(max_length=250, blank=True)
    rate = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{str(self.rate)}'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}"


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    total = models.PositiveIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart: {str(self.id)}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    rate = models.PositiveIntegerField(default=0)
    subtotal = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ('-id', )

    def save(self, **kwargs):
        self.rate = self.item.selling_price
        self.subtotal = self.rate * self.quantity
        super(CartItem, self).save(**kwargs)

    def __str__(self):
        return f"{self.item} in cart {str(self.cart.id)}"


class Order(models.Model):
    STATUS = (
        ('Received', 'Received'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    )
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS)
    subtotal = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f'Order: {self.id}'


