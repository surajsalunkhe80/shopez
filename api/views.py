import bson.objectid
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm, NewProductForm, BuyProductForm, AddToCartForm, BuyCartForm, UpdateOrderForm
from .models import users_collection, product_collection, orders_collection, cart_collection
import bson
from datetime import datetime, timedelta


def home(request):
    products = [p for p in  product_collection.find({'quantity': {'$gt': 0}})]
    for p in products:
        p['id'] = p['_id']
        p['description'] = p['description'][0:35] + '...'
        p['discountedPrice'] = int(int(p['price'])*((100-float(p['discount']))/100))
    return render(request, 'home.html', {"products": products})


def login(request):
    error=''
    data = {}
    isLogged = False
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                data = users_collection.find_one({'email': email})
                if data.get('password') == password:
                    data['userId'] = str(data['_id'])
                    isLogged = True
                
                else:
                    form = LoginForm()
                    error = 'Wrong credientials. Please try again.'
                    
            except:
                form = LoginForm()
                error = 'User not found!! Please try again.'
        else:
            form = LoginForm()
            error = 'Wrong credientials. Please try again.'
    else:
        form = LoginForm()
    
    context = {'form': form, 'isLogged': isLogged, 'data': data, 'error': error}
    return render(request, 'login.html', context)


def register(request):
    error=''
    data = {}
    isLogged = False
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            usertype = form.cleaned_data['usertype']
            user = {"username": username, "email": email, "password": password, "usertype": usertype}
            result = users_collection.insert_one(user)
            isLogged = True
            data = {
            'userId': str(result.inserted_id),
            'username': username,
            'email': email,
            'password': password,
            'usertype': usertype
            }
            
        else:
            form = RegisterForm()
            error = 'Invalid form data. Please try again.'
    else:
        form = RegisterForm()
    
    context = {'form': form, 'isLogged': isLogged, 'data': data, 'error': error}
    return render(request, 'register.html', context)

def loadCart(request):
    return render(request, 'loading/loadCart.html')

def cart(request, id):
    totalPrice = 0
    discount = 0
    deliveryCharges = 0
    finalPrice = 0
    items = [i for i in cart_collection.find({"userId": id})]
    items.reverse()
    for i in items: 
        i['id'] = i['_id']
        i['description'] = i['description'][0:70] + '....'
        i['totalPrice'] = int(i['price']) * int(i['quantity'])
        i['totalPrice'] = int(int(i['totalPrice']) * (1 - (int(i['discount'])/100)))
        totalPrice += i['price']
        discount += int(int(i['price']) * int(i['discount'])/100)

    if((totalPrice - discount) < 500 and (totalPrice - discount) > 0):
        deliveryCharges = 50

    finalPrice = totalPrice - discount + deliveryCharges

    error = False
    success = False

    form = BuyCartForm()

    if request.method == "POST":
        form = BuyCartForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            mobile = form.cleaned_data['mobile']
            email = form.cleaned_data['email']
            address = form.cleaned_data['address']
            pincode = form.cleaned_data['pincode']
            paymentMethod = form.cleaned_data['paymentMethod']

            currentDateAndTime = datetime.now()    
            deliveryDate = currentDateAndTime + timedelta(days=5) 
            
            for item in items:

                order = {"userId": id, "name": name, "email": email, "mobile": mobile, "address": address, 
                     "pincode": pincode, "paymentMethod":paymentMethod, "quantity": item['quantity'], "title": item['title'],
                     "description": item['description'], "mainImg": item['mainImg'], "price": item['price'], "discount": item['discount'],
                     "orderStatus": "order placed", "orderDate":  str(currentDateAndTime), "deliveryDate": str(deliveryDate)}     
                
                res = orders_collection.insert_one(order)
                if res:
                    objId = bson.ObjectId(item['id'])
                    cart_collection.delete_one({"_id": objId})
                    success = True
                    continue
                else:
                    success = False
                    error = True


        else:
            error = True

    return render(request, 'customer/cart.html', {"items": items, "totalPrice": totalPrice, "discount": discount,
                                                   "deliveryCharges": deliveryCharges, "finalPrice": finalPrice, 
                                                   "form": form, "success": success, "error": error})


def removeCartProduct(request, id):
    objId = bson.ObjectId(id)
    cart_collection.delete_one({"_id": objId})
    return redirect("/load-cart")
    

def loadProduct(request, id):
    return render(request, 'loading/loadIndividualProduct.html', {"id": id})

def product(request, productId, userId):
    productObjId = bson.ObjectId(productId)
    product = product_collection.find_one({"_id": productObjId})
    product['carousel1'] = product['carousel'][0] or ""
    product['carousel2'] = product['carousel'][1] or ""
    product['carousel3'] = product['carousel'][2] or ""
    product['discountedPrice'] = int(int(product['price'])*((100-float(product['discount']))/100))
    
    form = BuyProductForm()
    addForm = AddToCartForm()
    bought = False
    addedToCart = False
    error = False

    if request.method == 'POST':
        buyForm = BuyProductForm(request.POST)
        addForm = AddToCartForm(request.POST)
        if buyForm.is_valid():
            quantity = buyForm.cleaned_data['quantity']           
            name = buyForm.cleaned_data['name']           
            mobile = buyForm.cleaned_data['mobile']           
            email = buyForm.cleaned_data['email']           
            address = buyForm.cleaned_data['address']           
            pincode = buyForm.cleaned_data['pincode']           
            paymentMethod = buyForm.cleaned_data['paymentMethod'] 

            currentDateAndTime = datetime.now()    
            deliveryDate = currentDateAndTime + timedelta(days=5) 

            order = {"userId": userId, "name": name, "email": email, "mobile": mobile, "address": address, 
                     "pincode": pincode, "paymentMethod":paymentMethod, "quantity": quantity, "title": product['title'],
                     "description": product['description'], "mainImg": product['mainImg'], "price": product['price'], "discount": product['discount'],
                     "orderStatus": "order placed", "orderDate":  str(currentDateAndTime), "deliveryDate": str(deliveryDate)}     

            res = orders_collection.insert_one(order)
            if res:
                bought = True
            else:
                error = True

        elif addForm.is_valid():
            quantity = addForm.cleaned_data['quantity']     
            cart = {"userId": userId, "quantity": quantity, "title": product['title'],
                     "description": product['description'], "mainImg": product['mainImg'], "price": product['price'], "discount": product['discount']}     

            res = cart_collection.insert_one(cart)
            if res:
                addedToCart = True
            else:
                error = True

        else: 
            error: True
    
    
    return render(request, 'customer/individualProduct.html', {"product": product, "form": form, "addForm": addForm, "bought": bought, "addedToCart": addedToCart, "error": error})

def category(request, id):
    products = [p for p in product_collection.find({"category": id})]
    productsCount = len(products)
    for p in products:
        p['id'] = p['_id']
        p['description'] = p['description'][0:40] + '...'
        p['discountedPrice'] = int(int(p['price'])*((100-float(p['discount']))/100))
        
    return render(request, 'customer/categoryProducts.html', {"products": products, "productsCount": productsCount})

def loadProfile(request):
    return render(request, 'loading/loadProfile.html')

def profile(request, id):
    userObjId = bson.ObjectId(id)
    user = users_collection.find_one({"_id": userObjId})

    orders = [o for o in orders_collection.find({"userId": id})]
    orders.reverse()
    for i in orders:
        i['id'] = i['_id']
        i['description'] = i['description'][0:70] + '....'
        i['totalPrice'] = int(i['price']) * int(i['quantity'])
        i['totalPrice'] = int(int(i['totalPrice']) * (1 - (int(i['discount'])/100)))    

        i['orderDate'] = i['orderDate'][0:11]
    ordersCount = len(orders) or 0
    return render(request, 'customer/profile.html', {"user": user, "orders": orders, "ordersCount": ordersCount})

def cancelOrder(request, id):
    orders_collection.update_one({"_id": bson.ObjectId(id)}, {"$set": {"orderStatus": "Cancelled"}})

    return redirect("/load-profile")

def cancelAdminOrder(request, id):
    orders_collection.update_one({"_id": bson.ObjectId(id)}, {"$set": {"orderStatus": "Cancelled"}})

    return redirect("/all-orders")

def deliverOrder(request, id):
    orders_collection.update_one({"_id": bson.ObjectId(id)}, {"$set": {"orderStatus": "Delivered"}})

    return redirect("/all-orders")


def admin(request):
    users = [u for u in users_collection.find()]
    products = [p for p in product_collection.find()]
    orders = [p for p in orders_collection.find()]

    usersCount = len(users) or 0
    productsCount = len(products) or 0
    ordersCount = len(orders) or 0
    return render(request, 'admin/admin.html', {"usersCount": usersCount, "productsCount": productsCount, "ordersCount": ordersCount})

def allProducts(request):
    products = [p for p in product_collection.find()]
    for p in products:
        p['id'] = p['_id']
        p['description'] = p['description'][0:40] + '...'
        p['discountedPrice'] = int(int(p['price'])*((100-float(p['discount']))/100))
    return render(request, "admin/allProducts.html", {"products": products})

def allUsers(request):
    users = [u for u in users_collection.find()]
    for u in users:
        u['id'] = u['_id']
    return render(request, "admin/allUsers.html",{"users": users})

def allOrders(request):
    orders = [o for o in orders_collection.find()]
    for o in orders:
        o['id'] = o['_id']
        o['description'] = o['description'][0:110] + '....'
        o['orderDate'] = o['orderDate'][0:11]
        o['totalPrice'] = int(o['price']) * int(o['quantity'])
        o['totalPrice'] = int(int(o['totalPrice']) * (1 - (int(o['discount'])/100)))  

    form = UpdateOrderForm()
    if request.method == "POST":
        form = UpdateOrderForm(request.POST)
        if form.is_valid():
            orderId = form.cleaned_data['orderId']
            status = form.cleaned_data['status']
            print("jjks", orderId, status)
        else:
            print("kkkkkk")
    return render(request, "admin/allOrders.html", {"orders": orders, "form": form})

def newProduct(request):
    success = False
    error = ''
    if request.method == 'POST':
        form = NewProductForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            mainImg = form.cleaned_data['mainImg']
            carousel1 = form.cleaned_data['carousel1']
            carousel2 = form.cleaned_data['carousel2']
            carousel3 = form.cleaned_data['carousel3']
            gender = form.cleaned_data['gender']
            category = form.cleaned_data['category']
            price = form.cleaned_data['price']
            discount = form.cleaned_data['discount']
            quantity = form.cleaned_data['quantity']

            carousel = [carousel1, carousel2, carousel3]

            product = {"title": title, "description": description, "mainImg": mainImg,
                          "carousel": carousel, "gender": gender, "category": category, 
                          "price": price, "discount": discount, "quantity": quantity}
            print(product)
            result = product_collection.insert_one(product)
            print(result)
            success = True
            
        else:
            form = NewProductForm()
            print("erroruu")
            success = False
            error = 'Invalid form data. Please try again.'
    else:
        form = NewProductForm()
    
    context = {'form': form, 'success': success, 'error': error}
    return render(request, 'admin/newProduct.html', context)


def updateProduct(request, id):
    success = False
    error = ''
    if request.method == 'POST':
        form = NewProductForm(request.POST)
        if form.is_valid():
            object_id = bson.ObjectId(id)

            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            mainImg = form.cleaned_data['mainImg']
            carousel1 = form.cleaned_data['carousel1']
            carousel2 = form.cleaned_data['carousel2']
            carousel3 = form.cleaned_data['carousel3']
            gender = form.cleaned_data['gender']
            category = form.cleaned_data['category']
            price = form.cleaned_data['price']
            discount = form.cleaned_data['discount']
            quantity = form.cleaned_data['quantity']

            carousel = [carousel1, carousel2, carousel3]

            product_collection.update_one({"_id": object_id}, {"$set": {"title": title, "description": description, "mainImg": mainImg,
                          "carousel": carousel, "gender": gender, "category": category, 
                          "price": price, "discount": discount, "quantity": quantity}})
            success = True
  
            
        else:
            form = NewProductForm()
            print("erroruu")
            success = False
            error = 'Invalid form data. Please try again.'
    else:
        object_id = bson.ObjectId(id)
        product = product_collection.find_one({'_id': object_id})
        if product is None:
            error = "Error in fetching product!!"
            form = NewProductForm()
        else:
            if product['carousel']:
                carousel1 = product['carousel'][0] or ""
                carousel2 = product['carousel'][1] or "" 
                carousel3 = product['carousel'][2] or ""
            form = NewProductForm(initial={
                            "title": product['title'],
                            "description": product['description'], 
                            "mainImg": product['mainImg'], 
                            "carousel1": carousel1, 
                            "carousel2": carousel2, 
                            "carousel3": carousel3, 
                            "gender": product['gender'], 
                            "category": product['category'], 
                            "price": product['price'], 
                            "discount": product['discount'], 
                            "quantity": product['quantity'],
                        })
    
    context = {'form': form, 'success': success, 'error': error}
    return render(request, 'admin/updateProduct.html', context)
