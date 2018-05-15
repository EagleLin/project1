from django.shortcuts import render

# Create your views here.
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.contrib.auth.models import User, Group
from django.http import FileResponse


# 注册

class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')





def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            user.is_staff = True
            group = Group.objects.filter(name="student").get()
            user.groups.add(group)

            user.save()
            return redirect('/admin/')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})




def download(request):
    filename = request.GET.get('filename')
    print(filename)
    from . import models
    allfile = models.UploadFile.objects.all()
    for i in allfile:
        print(i.upload_file)
    import os
    print(os.getcwd())
    file = open('./upload_dir/desktop.ini', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="desktop.ini"'
    return response




