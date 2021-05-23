from django.shortcuts import render, redirect
from .forms import RegisterForm


# Create your views here.
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/wodplannerapp")
        else:
            print('somethings wrong')
            return render(response, "register/register.html", {"form": form})

    else:
        print('yup')
        form = RegisterForm()

        return render(response, "register/register.html", {"form": form})
