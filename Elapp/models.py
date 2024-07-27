from django.db import models
from django.contrib.auth.models import User
import uuid
class Customer(models.Model):
    customer_id=models.UUIDField(default=uuid.uuid4,unique=True)
    user=models.OneToOneField(User,null=True,blank=True,on_delete=models.CASCADE)
    first_name=models.CharField(max_length=200,null=True)
    last_name=models.CharField(max_length=200,null=True)
    email=models.CharField(max_length=200,null=True)
    date_created=models.DateTimeField(auto_now_add=True)
    image=models.ImageField(blank=True,null=True)
    @property
    def imageURL(self):
        try:
            url=self.image.url
        except:
            url=''
        return url
class products(models.Model):
    product_id=models.UUIDField(default=uuid.uuid4,unique=True)
    product_name=models.CharField(max_length=200,null=True)
    options=[
        ('A','accesscontrol'),
        ('C','cctv'),
        ('L','alarm'),
        ('F','fence'),
        ('G','gate'),
        ('I','intercom'),
        ('S','accessories'),
    ]
    category=models.CharField(max_length=1,null=True,choices=options)
    select=[
        ('Q','Dahua'),
        ('W','Hikvision'),
        ('E','suprema'),
        ('R','Tiandy'),
        ('T','Uniview'),
        ('Y','Bulb camera'),
        ('U','secolink'),
        ('I','ezviz'),
        ('O','Zkteco'),
        ('P','Lytsys'),
        ('Z','Convectional'),
        ('X','Addressable'),
        ('C','Ip'),
        ('V','Analog'),
        ('B','Centurion D5'),
        ('N','Centurion D 10'),
        ('S','Accessories'),
        ('F','Fence'),
        ('R','RJ59'),
        ('J','RJ45'),

    ]
    type=models.CharField(max_length=200,null=True,choices=select)
    featured=models.BooleanField(default=False)
    description=models.CharField(max_length=200,null=True)
    previous_price=models.FloatField()
    product_price=models.FloatField(null=True,blank=True)
    def get_category_name(self):
        return dict(self.options).get(self.category, '')

    def get_type_name(self):
        return dict(self.select).get(self.type, '')
  
 
    image=models.ImageField(blank=True,null=True)
    def __str__(self):
        return self.product_name

class Order(models.Model):
    order_id=models.UUIDField(default=uuid.uuid4,unique=True)
    customer=models.ForeignKey(Customer,on_delete=models.SET_NULL,blank=True,null=True)
    date_ordered=models.DateTimeField(auto_now_add=True)
    session_key=models.CharField(max_length=40,null=True)
    transaction_id=models.CharField(max_length=200,null=True)
    complete=models.BooleanField(default=False,null=True,blank=False)
    @property
    def get_cart_total(self):
        orderitems=self.orderitem_set.all()
        total=sum([item.get_total for item in orderitems])
        return total
    @property
    def get_cart_items(self):
        orderitems=self.orderitem_set.all()
        total=sum([item.quantity for item in orderitems])
        return total
class OrderItem(models.Model):
    product=models.ForeignKey(products,on_delete=models.SET_NULL,blank=True,null=True)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    quantity=models.IntegerField(default=0,null=True,blank=True)
    date_added=models.DateTimeField(auto_now_add=True)
    @property
    def get_total(self):
        total=self.product.product_price * self.quantity
        return total
class shipping_address(models.Model):
    orderitem_id=models.UUIDField(default=uuid.uuid4,unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.city if self.city else f"Shipping Address {self.pk}"
class Customer_feedback(models.Model):
    email=models.CharField(max_length=200,null=True)
    username=models.CharField(max_length=200,null=True)
    subject=models.CharField(max_length=200,null=True)
    message=models.CharField(max_length=200,null=True)
    def __str__(self):
        return self.subject 

class subscribed_emails(models.Model):
    email=models.CharField(max_length=200,null=True)
class PaymentTransaction(models.Model):
    merchant_request_id = models.CharField(max_length=100)
    checkout_request_id = models.CharField(max_length=100)
    result_code = models.IntegerField()
    result_desc = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    user_phone_number = models.CharField(max_length=15)
    expected_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Transaction {self.transaction_id} - Amount: {self.amount}"