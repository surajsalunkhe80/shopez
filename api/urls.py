from django.urls import path
from . import views


urlpatterns = [
    path("", views.home),
    path("login/", views.login),
    path("register/", views.register),
    path("cart/<str:id>", views.cart),
    path("load-cart/", views.loadCart),
    path("remove-from-cart/<str:id>", views.removeCartProduct),


    path("product/<str:productId>/<str:userId>", views.product),
    path("load-product/<str:id>", views.loadProduct),
    path("category/<str:id>", views.category),
    path("profile/<str:id>", views.profile),
    path("load-profile/", views.loadProfile),
    path("cancel-order/<str:id>", views.cancelOrder),
    path("cancel-admin-order/<str:id>", views.cancelAdminOrder),
    path("deliver-order/<str:id>", views.deliverOrder),

    path("admin/", views.admin),
    path("all-products/", views.allProducts),
    path("all-users/", views.allUsers),
    path("all-orders/", views.allOrders),
    path("new-product/", views.newProduct),
    path("update-product/<str:id>", views.updateProduct),

]