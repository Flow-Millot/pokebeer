from django.shortcuts import render
from django.db.models import Avg, Q
from django.utils import timezone

from .models import Beer, Drinks

def index(request):
    month = timezone.now().month
    year = timezone.now().year
    top10 = Beer.objects.annotate(avg_rating=Avg('drinks__note')).order_by('-avg_rating')[:10]
    top10Month = Beer.objects.annotate(avg_rating=Avg('drinks__note', filter=Q(drinks__date__year=year, drinks__date__month=month))).filter(avg_rating__isnull=False).order_by('-avg_rating')[:10]

    context = {"top":top10, "topMonth":top10Month}
    return render(request, "home.html", context)