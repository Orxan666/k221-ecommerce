from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from .forms import RegisterForm
from shop.models import Product
from django.contrib.auth.decorators import login_required
from .models import WishItem,BasketItem
from django.db.models import Sum,F

# Create your views here.

def contact(request):
    return render(request,'contact.html')


@login_required
def basket(request):
    basketlist=request.user.customer.basketlist.all().annotate(total_price=F('count')*F('product__price')) 

    return render(request,'basket.html',{
        'basketlist':basketlist,

    })


from django.shortcuts import get_object_or_404

def add_basket(request, product_pk):
    if request.method == 'POST':
        size_pk = request.POST.get('size')
        color_pk = request.POST.get('color')
        count = request.POST.get('count')
        customer = request.user.customer

        existing_item = BasketItem.objects.filter(
            product_id=product_pk, size_id=size_pk, color_id=color_pk, customer=customer
        ).first()

        if existing_item:
            existing_item.count = F('count') + int(count)
            existing_item.save()
        else:
            BasketItem.objects.create(
                product_id=product_pk, size_id=size_pk, color_id=color_pk, count=count, customer=customer
            )

        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('shop:home')



def increase_basket_item(request,basket_pk):
    basket=get_object_or_404(BasketItem,pk=basket_pk)
    basket.count=F('count')+1
    basket.save()
    return redirect('customer:basket')

def decrease_basket_item(request,basket_pk):
    basket=get_object_or_404(BasketItem,pk=basket_pk)
    if basket.count==1:
        basket.delete()
    else:
        basket.count=F('count')-1
        basket.save()
    return redirect('customer:basket')


@login_required
def remove_basket(request,basket_pk):
    basket=get_object_or_404(BasketItem,pk=basket_pk)
    basket.delete()
    return redirect('customer:basket')

def wishlist_view(request):

    wishlist=request.user.customer.wishlist.all()
    total_price=wishlist.aggregate(total_price=Sum('product__price'))['total_price'] or 0

    return render(request,'wishlist.html',{
        'wishlist':wishlist,
        'total_price':total_price
    })

@login_required
def unwish_product(request,pk):
    product=get_object_or_404(Product,pk=pk)
    customer=request.user.customer
    WishItem.objects.filter(product=product,customer=customer).delete()
    return redirect(request.META.get('HTTP_REFERER'))



@login_required
def wish_product(request,pk):
    product=get_object_or_404(Product,pk=pk)
    customer=request.user.customer
    WishItem.objects.create(product=product,customer=customer)
    return redirect(request.META.get('HTTP_REFERER'))






def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next')
            if not remember_me:
                # Set a reasonable session timeout (e.g., 30 minutes)
                request.session.set_expiry(1800)
            # Redirect to the 'next' URL if available, otherwise redirect to 'shop:home'
            return redirect(next_url or 'shop:home')
        else:
            # Display a generic error message for incorrect credentials
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def register(request):
    form=RegisterForm()
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():
            customer=form.save()
            login(request,customer.user)
            return redirect('shop:home')
    return render(request,'register.html',{'form':form})
        
        



def logout_view(request):
    logout(request)
    return redirect('customer:login')




