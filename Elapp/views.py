from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .forms import profileForm
from django.http import JsonResponse
import threading
import datetime
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.sessions.models import Session
from .forms import *
from pay.stkPush import initiate_stk_push
import json
from .models import *
from django.core.paginator import Paginator
from .utils import DatacookieCart
from .utils import AllcartData
def search_products(request):
    if request.method=="POST":
        searchKeyword=request.POST['search_keyword']
        print(searchKeyword)
        if searchKeyword=='':
            messages.error(request,'Please type something')
            return render(request,'camera.html')
        else:
            results=products.objects.filter(product_name__contains=searchKeyword) or products.objects.filter(product_name__istartswith=searchKeyword) or products.objects.filter(product_name__iendswith=searchKeyword) or products.objects.filter(product_price__contains=searchKeyword)or products.objects.filter(type__contains=searchKeyword) or products.objects.filter(category__contains=searchKeyword)
            return render(request,'search_results.html',{'products':results,'word':searchKeyword})
    else:
        return render(request,'index.html')
    
def index(request):
    featured=products.objects.filter(featured=True)
    data=AllcartData(request)
    order=data['order']  
    context = {'order': order, 'featured':featured}
    return render(request,'index.html',context)
class EmailThread(threading.Thread):
    def __init__(self,email):
        self.email=email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send(fail_silently=False )
def cameras(request):
    cameras=products.objects.filter(category="C")
    p=Paginator(cameras,8)
    page_list=request.GET.get('page')
    
    page=p.get_page(page_list)
    data=AllcartData(request)
    order=data['order']
    items=data['items']
    cartItems=data['cartItems']

    context = {'order': order, 'items': items,'cartItems':cartItems,'page':page,'cameras':cameras}

    return render(request,'camera.html',context)
def accesscontrol(request):
    systems=products.objects.filter(category="A")
    data=AllcartData(request)
    order=data['order']
    items=data['items']
    cartItems=data['cartItems']

    context = {'order': order, 'items': items,'cartItems':cartItems,'systems':systems,'accesscontrol':systems}
    return render(request,'accesscontrol.html',context)
def all_products(request):
    all=products.objects.all()
    p=Paginator(all,8)
    page_list=request.GET.get('page')
    
    page=p.get_page(page_list)
    data=AllcartData(request)
    order=data['order']
    items=data['items']
    cartItems=data['cartItems']

    context = {'order': order, 'items': items,'cartItems':cartItems,'page':page,'all':all}
    return render(request,'products.html',context)
def viewProduct(request,product_id=0):
        product=products.objects.get(product_id=product_id)
        catg=product.category
        print(product.id)
        moreItems=products.objects.filter(category=catg).exclude(product_id=product_id)
        p=Paginator(moreItems,8)
        page_list=request.GET.get('page')
        page=p.get_page(page_list)
        
        data=AllcartData(request)
        order=data['order']
        
        context = {'order': order,"product":product,"page":page}
        return render(request,'view.html',context)


def update_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if product_id is not None and quantity is not None:
            try:
                product = products.objects.get(id=product_id)
                # Your logic for updating the quantity in the cart
                cart = json.loads(request.COOKIES.get('cart', '{}'))
                if str(product_id) in cart:
                    cart[str(product_id)]['quantity'] = quantity
                else:
                    cart[str(product_id)] = {'quantity': quantity}

                response = JsonResponse({'message': 'Quantity updated successfully'})
                response.set_cookie('cart', json.dumps(cart))
                return response

            except products.DoesNotExist:
                return JsonResponse({'error': 'Product does not exist'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def cart(request):
    data=AllcartData(request)
    order=data['order']
    items=data['items']
    cartItems=data['cartItems']

    context = {'order': order, 'items': items,'cartItems':cartItems}

    return render(request, 'cart.html', context)
def complete_orders(request,id=0):
   if request.user.is_authenticated:
        customer=request.user.customer
        orders = Order.objects.filter(customer=customer).order_by('-date_ordered').filter(complete=True)
    

    
   else:
       orders=None

   context = {'orders': orders}
   return render(request, 'orders.html', context)
def complete_orders_items(request,order_id=0):
    customer=request.user.customer
    orders = Order.objects.filter(customer=customer).order_by('-date_ordered').filter(complete=True)
    
    order = Order.objects.get(order_id=order_id)
    orderItems=OrderItem.objects.filter(order=order)
    
    

    context = {'orders': orders,'orderItems':orderItems}
    return render(request, 'orders.html', context)
def checkout(request):
    data=AllcartData(request)
    order=data['order']
    
    items=data['items']
    try:
        Customer=request.user.customer
    except:
        Customer=None
    cartItems=data['cartItems']
        
    context = {'order': order, 'items': items,'cartItems':cartItems,'customer':Customer}
    return render(request,'checkout.html',context)

def processorder(request):
    data = json.loads(request.body)
    transaction_id = datetime.datetime.now().timestamp()
        
    
    if request.user.is_authenticated:
        customer = request.user.customer
        phoneNo = data['shipping']['phone']
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        
        if total == order.get_cart_total:
            order.transaction_id = transaction_id
            amountTotal = order.get_cart_total
            phoneNo = data['shipping']['phone']
            
            # Call the initiate_stk_push function with dynamic values
            stk_push_response = initiate_stk_push(request, phoneNo, amountTotal)
            stk_push_data = json.loads(stk_push_response.content)

            
            
            if stk_push_data.get('ResponseCode') == "0":
                shipping_address.objects.create(
                    customer=customer,
                    order=order,
                    city=data['shipping']['county'],
                    zipcode=data['shipping']['zipcode'],
                    state=data['shipping']['location']
                )
                order.complete = True
                order.save()
                return JsonResponse({'success': 'Order placed successfully.'})
            else:
                return JsonResponse({'error': 'Failed to initiate STK push.'})
        
        return JsonResponse({'error': 'Total mismatch.'})
    
    else:
        first_name = data['form']['first_name']
        last_name = data['form']['last_name']
        email = data['form']['email']
        phoneNo = data['shipping']['phone']
        cookieData = DatacookieCart(request)
        items = cookieData['items']
        
        customer, created = Customer.objects.get_or_create(email=email)
        customer.first_name = first_name
        customer.last_name = last_name
        customer.save()
        
        order = Order.objects.create(customer=customer, complete=False)
        for item in items:
            product = products.objects.get(id=item['product']['id'])
            orderitem = OrderItem.objects.create(product=product, order=order, quantity=item['quantity'])
        
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        Amount = order.get_cart_total
        
        if total == Amount:
            # Call the initiate_stk_push function with dynamic values
            stk_push_response = initiate_stk_push(request, phoneNo, Amount)
            stk_push_data = json.loads(stk_push_response.content)
            
            if stk_push_data.get('ResponseCode') == "0":
                order.complete = True
                order.save()
                shipping_address.objects.create(
                    customer=customer,
                    order=order,
                    city=data['shipping']['county'],
                    zipcode=data['shipping']['zipcode'],
                    state=data['shipping']['location']
                )
                return JsonResponse({'success': 'Order placed successfully.'})
            else:
                return JsonResponse({'error': 'Failed to initiate STK push.'})
    
    return JsonResponse({'error': 'Order processing failed.'})



def signup_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['user_password']
        cpassword = request.POST['cpassword']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return render(request, 'signup.html')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'email already taken')
            return render(request, 'signup.html')
        else:
            if password == cpassword:
                try:
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                    )
                    user.email = email
                    user.save()

                    customer = Customer.objects.create(
                        user=user,
                        email=email,
                    )
                    customer.save()
                    email_subject='Account created Succesfully'
                    email_body=f"Dear {user},Your account was created successfully, start purchasing our products today and enjoy great dicounts and offers "
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [user.email, ]
                    email=EmailMessage(
                            email_subject,
                            email_body,
                            email_from,
                            recipient_list
                    )
                    EmailThread(email).start()

                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        login(request, user)
                        messages.success(request, f'Welcome to ElphaMatt {user}')
                        return redirect('index') 
                except Exception as e:
                    messages.error(request, f'Error occurred: {str(e)}')
            else:
                messages.error(request, 'Passwords do not match')
                
    return render(request, 'signup.html')

def user_profile(request,customer_id=0):
    if request.method=="GET":
        user=request.user.customer
        form=profileForm(instance=user)
        return render(request,'update_user_profile.html',{"user":user,"form":form})
 
    else:
        if customer_id==0:
            form=profileForm(request.POST)
            
        else:
            user=Customer.objects.get(customer_id=customer_id)
            form=profileForm( request.POST,instance=user)
        if form.is_valid():
                form.save()
                messages.success(request,'Changes saved successfully')
    
    
        return redirect('profile')
  


    
def new_profile(request):
    user=request.user.customer
    return render(request,'user_profile.html',{"user":user})

def login_user(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['user_password']
        if User.objects.filter(username=username).exists():
            user=authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                messages.success(request,f"Welcome back {user} continue shopping and enjoy great discounts")
                return redirect('index')
            else:
                messages.error(request,"Incorrect password")
                return redirect('login')
        else:
            messages.error(request,'Username does not exist')
            return render(request,'signin.html') 
    else:
        return render(request,'signin.html')
def logout_user_profile(request):
    redirect_url = request.POST.get('redirect_url', 'index')
    logout(request)
    
    messages.success(request,'You have been logged out successfully')
    return redirect(redirect_url)
def updateCart(request):
     for i in range(0,1):
        data=json.loads(request.body)
     productId=data['product_id']
     action=data['action']
     print(data,'update cart')
     if request.user.is_authenticated:
        customer=request.user.customer
        product=products.objects.get(id=productId)
        print(productId)
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        orderItem,created=OrderItem.objects.get_or_create(order=order,product=product)

        
        if action=='add':
            orderItem.quantity=(orderItem.quantity+1)
            # messages.success(request,f'{orderItem.product.product_name} has been added successfully')
        elif action== 'remove':
            orderItem.quantity=(orderItem.quantity-1)
        elif action=='delete':
            orderItem.quantity=0
            messages.error(request,f'{orderItem.product.product_name} has been removed')
        orderItem.save()
        if orderItem.quantity <=0:
            orderItem.delete()
            messages.error(request,f'{orderItem.product.product_name} has been removed')
            
        return JsonResponse('item was added successfully',safe=False)



def gates(request):
    gates=products.objects.filter(category="G")
    p=Paginator(gates,8)
    page_list=request.GET.get('page')
    page=p.get_page(page_list)
    page=p.get_page(page_list)
    data=AllcartData(request)
    order=data['order']
    items=data['items']
    cartItems=data['cartItems']

    context = {'order': order, 'items': items,'cartItems':cartItems,'page':page,'gates':gates}
    return render(request,'automaticgates.html',context)

def fence(request):
    fence=products.objects.filter(category="F")
    p=Paginator(fence,8)
    page_list=request.GET.get('page')
    page=p.get_page(page_list)
    page=p.get_page(page_list)
    data=AllcartData(request)
    order=data['order']
    items=data['items']
    cartItems=data['cartItems']

    context = {'order': order, 'items': items,'cartItems':cartItems,'page':page,'fence':fence}
    return render(request,'fence.html',context)

def alarms(request):
    alarms=products.objects.filter(category="L")
    p=Paginator(alarms,8)
    page_list=request.GET.get('page')
    page=p.get_page(page_list)
    page=p.get_page(page_list)
    data=AllcartData(request)
    order=data['order']
    items=data['items']
    cartItems=data['cartItems']

    context = {'order': order, 'items': items,'cartItems':cartItems,'page':page,'alarms':alarms}
    return render(request,'alarm.html',context)
def intercom(request):
    intercom=products.objects.filter(category="I")
    p=Paginator(intercom,8)
    page_list=request.GET.get('page')
    page=p.get_page(page_list)
    data=AllcartData(request)
    order=data['order']
    items=data['items']
    cartItems=data['cartItems']

    context = {'order': order, 'items': items,'cartItems':cartItems,'page':page,'intercom':intercom}
    return render(request,'intercom.html',context)
def Accessories(request):
    Accessories=products.objects.filter(category="S")
    p=Paginator(Accessories,8)
    page_list=request.GET.get('page')
    page=p.get_page(page_list)
    data=AllcartData(request)
    order=data['order']
    items=data['items']
    cartItems=data['cartItems']

    context = {'order': order, 'items': items,'cartItems':cartItems,'page':page,'Accessories':Accessories}
    return render(request,'intercom.html',context)
def customer_feedback(request):
    if request.method=="POST":
        email=request.POST['email']
        username=request.POST['username']
        subject=request.POST['subject']
        message=request.POST['message']
        Feedback=Customer_feedback.objects.create(
                            email=email,
                            username=username,
                            subject=subject,
                            message=message

        )
        Feedback.save()
        messages.success(request,f'Thank you {username} for sending us your feedback,We will get back to you as soon as we can')
        return render(request,'index.html')
    return render(request,'index.html')
def newsletter_emails(request):
    data=json.loads(request.body)
    print(data)
    email=data['form']['email']
    print(email)
    newsletter_emails=subscribed_emails.objects.create(
                            email=email,

        )
    newsletter_emails.save()
    messages.succes(request,'Thank you for subscribing to our newsletter,now you will get updated with our latest and new arrivals')
    return JsonResponse('item was added successfully',safe=False)