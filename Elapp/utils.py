from .models import *
import json
def DatacookieCart(request):
    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))
        print(cart, "sdbzm,")
    except json.JSONDecodeError:
        cart = {}
        print('no cart')

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}
    cartItems = 0  # Initialize cartItems to 0

    print(cart)
    for i in cart:
        try:
            quantity = cart[i]['quantity']
            if quantity is None or not isinstance(quantity, int) or quantity <= 0:
                continue  # Skip invalid quantities

            cartItems += quantity
            product = products.objects.get(id=i)
            total = product.product_price * quantity
            order['get_cart_total'] += total
            order['get_cart_items'] += quantity

            item = {
                'product': {
                    'id': product.id,
                    'product_price': product.product_price,
                    'product_description': product.description,
                    'product_name': product.product_name,
                    'image': product.image,
                },
                'get_total': total,
                'quantity': quantity
            }
            items.append(item)
        except products.DoesNotExist:
            print(f"Product with id {i} does not exist.")
            continue  # Skip this item if the product doesn't exist

    return {'order': order, 'items': items, 'cartItems': cartItems}

def AllcartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer).order_by('-date_ordered').filter(complete=False)
        print(orders)
       
        if orders.exists():
            for i in range(orders.__len__()):
                order = orders[i] 
                items = order.orderitem_set.all()
                cartItems=order.get_cart_items
        else:
            order = None
            items = []
            cartItems=0
    else:
       cookieData=DatacookieCart(request)
       order=cookieData['order']
       items=cookieData['items']
       cartItems=cookieData['cartItems']
    return {'order': order, 'items': items,'cartItems':cartItems}