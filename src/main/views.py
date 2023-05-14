from django.shortcuts import render,redirect , get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .filters import ListingFilter
from .models import Listing, LikedListing
from users.forms import LocationForm
from .forms import ListingForm
def landing_view(request):
    return render(request, "views/main.html",{"name": "Automax"})

@login_required
def home_view(request):
    listings = Listing.objects.all()
    listing_filter = ListingFilter(request.GET,queryset=listings)
    user_liked_listing = LikedListing.objects.filter(profile = request.user.profile).values_list('listing')
    liked_listing_ids = [l[0] for l in user_liked_listing]
    context = {
        'listings': listings,
        'listing_filter': listing_filter,
        'liked_listing_ids': liked_listing_ids,
    }
    return render(request, "views/home.html",context)

@login_required
def list_view(request):
    if request.method == 'POST':
        try:
            listing_form = ListingForm(request.POST,request.FILES)
            location_form = LocationForm(request.POST)
            if listing_form.is_valid() and location_form.is_valid():
                listing = listing_form.save(commit=False)
                listing_location = location_form.save()
                listing.seller = request.user.profile
                listing.location = listing_location
                listing.save()
                messages.info(request, f'{listing.model} Listing Posted Successfully')
                return redirect('home')
        except Exception as e:
            print(e)
            messages.error(request, 'Error occured while posting the listing.')
    elif request.method == 'GET':
        listing_form = ListingForm()
        location_form = LocationForm()
    return render(request, "views/list.html",{'listing_form': listing_form, 'location_form': location_form})

@login_required
def listing_view(request, id):
    try:
        listing = Listing.objects.get(id=id)
        if listing is None:
            raise Exception
        return render(request, "views/listing.html", {'listing': listing, })
    except Exception as e:
        messages.error(request, f'Invalid UID {id} was provided')
        return redirect('home')
    # return render(request, "views/listing.html", {})
def edit_view(request,id):
    try:
        listing = Listing.objects.get(id=id)
        if listing is None:
            raise Exception
        if request.method == 'POST':
            listing_form = ListingForm(request.POST,request.FILES,instance=listing)
            location_form = LocationForm(request.POST,instance=listing.location)
            if location_form.is_valid() and listing_form.is_valid():
                location_form.save()
                listing_form.save()
                messages.info(request,'Successfully Updated')
                return redirect('home')
            else:
                messages.error(request, 'Error occured while trying to update the listing')
                
        else:
            listing_form = ListingForm(instance=listing)
            location_form = LocationForm(instance=listing.location)
        context = {
            'location_form': location_form,
            'listing_form': listing_form
            }
        return render(request, "views/edit.html",context)
    except Exception as e:
        messages.error(request, 'Error occured while trying to update the listing')
        return redirect('home')

def like_listing_view(request, id):
    listing = get_object_or_404(Listing, id=id)
    like_listing,created = LikedListing.objects.get_or_create(profile=request.user.profile,listing=listing)

    if not created:
        like_listing.delete()
    else:
        like_listing.save()
    return JsonResponse(
        {
            'is_liked_by_user':created,
        }
    )

    