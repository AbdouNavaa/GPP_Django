from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
import openpyxl
from .models import *
from GPP.models import *
from .forms import *
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files import File
from datetime import datetime
import os
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
# Create your views here.
from django.core.paginator import Paginator
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            profile_image = form.cleaned_data.get('profile_image')
            author = Prof.objects.create(user=user, image=profile_image)
            auth_login(request, user)
            return redirect('accounts:authors')
    else:
        form = SignUpForm()
        return render(request, 'registration/signup.html', {'form': form})




def login(request):
    if request.method == 'POST':
        form = LogInForm(request, data=request.POST)
        print('Form:' ,form)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                next_url = request.POST.get('next', 'accounts:authors')
                print('1')
                return redirect('account:profile')
            else:
                print('Authentication failed')
        else:
            print('11')
            print(form.errors)
    else:
        print('12')
        form = LogInForm()
    print('222222')
    return render(request, 'registration/login.html', {'form': form, 'next': request.GET.get('next', '')})


def logout(request):
    auth_logout(request)
    return render(request, 'registration/login.html',{})


from django.db.models import Q 
def profile(request):
    print('User',request.user)
    user = User.objects.get(username=request.user)
    if user.is_staff:
        return redirect('GPP:home')
    else:
        prof = get_object_or_404(Prof, user=request.user)
        matieres = Matiere.objects.filter(
            Q(prof_cm__id=prof.id) | Q(prof_tp__id=prof.id) | Q(prof_td__id=prof.id)
        ).distinct()
        return render(request,'accounts/profile.html',{'user':user,'prof': prof,'matieres':matieres})
        


def profile_edit(request):
    profile = Prof.objects.get(user=request.user)

    if request.method=='POST':
        userform = UserForm(request.POST,instance=request.user)
        profileform = ProfileForm(request.POST,request.FILES,instance=profile )
        if userform.is_valid() and profileform.is_valid():
            userform.save()
            myprofile = profileform.save(commit=False)
            myprofile.user = request.user
            myprofile.save()
            return redirect(reverse('accounts:profile'))

    else :
        userform = UserForm(instance=request.user)
        profileform = ProfileForm(instance=profile)

    return render(request,'accounts/profile_edit.html',{'userform':userform , 'profileform':profileform})

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

@login_required
def users(request):
    if not request.user.is_staff:
        raise PermissionDenied("Vous n'avez pas l'autorisation d'accéder à cette page.")
    users = User.objects.all()
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'users.html', context)

@login_required
def update_user(request, id):
    if not request.user.is_staff:
        raise PermissionDenied("Vous n'avez pas l'autorisation d'accéder à cette page.")
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User mis à jour avec succès.")
            return redirect('account:users')
        else:
            messages.error(request, "Erreur lors de la mise à jour du user.")
    else:
        form = UserForm(instance=user)

    return render(request, 'update_user.html', {'form': form, 'user': user})
def delete_user(request,id ):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('account:users')
# Profs
@login_required
def profs(request ):
    profs = Prof.objects.all()
    paginator = Paginator(profs, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj' : page_obj}    
    return render(request,'profs.html',context)

@login_required
def update_prof(request, id):
    prof = get_object_or_404(Prof, id=id)
    if request.method == 'POST':
        form = ProfForm(request.POST, request.FILES, instance=prof)
        if form.is_valid():
            form.save()
            messages.success(request, "Prof mis à jour avec succès.")
            return redirect('account:profs')
        else:
            messages.error(request, "Erreur lors de la mise à jour du professeur.")
    else:
        form = ProfForm(instance=prof)
    
    return render(request, 'update_prof.html', {'form': form, 'prof': prof})

@login_required
def delete_prof(request, id):
    prof = get_object_or_404(Prof, id=id)
    prof.delete()
    return redirect('account:profs')

# Upload profs

@login_required
def upload_professeurs(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        filename = default_storage.save(file.name, file)
        file_path = default_storage.path(filename)

        # Charger le fichier Excel
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        # Fonction pour créer ou récupérer un professeur
        def create_professeur(prof_name):
            parts = prof_name.split()
            nom = parts[0]
            prenom = parts[1] if len(parts) > 1 else parts[0]
            email = f"{nom}.{prenom}@supnum.mr".lower()

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": f"{nom} {prenom}",
                    "first_name": nom,
                    "last_name": prenom,
                    "password": "1234@supnum",  # Set a default password or use a secure way to set it
                },
            )

            if created:
                 # Chemin relatif de l'image
                image_path = 'static/images/pic-1.jpg'
                # Vérifier si le fichier existe et le charger
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        image_file = File(img_file)
                        # Sauvegarder l'image avec le système de gestion des fichiers de Django
                        
                        prof = Prof.objects.create(
                            user=user,
                            compte=f"{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            banc="bmci",
                            image=image_file,
                            role="user",
                        )
                else:
                    # Si l'image n'existe pas, créer le prof sans image
                    prof = Prof.objects.create(
                        user=user,
                        compte=f"{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        banc="bmci",
                        role="user",
                    )

                # Récupérer les lignes spécifiées
        rows_to_process = list(range(5, 15)) + list(range(22, 41))
        processed_profs = set()

        for row_idx in rows_to_process:
            row = sheet[row_idx]
            for col_idx in [4, 5, 6]:  # E, F, G correspond aux index 4, 5, 6
                cell_value = row[col_idx].value
                if cell_value and isinstance(cell_value, str):
                    prof_names = cell_value.split('/')
                    for prof_name in prof_names:
                        prof_name = prof_name.strip()
                        if prof_name and prof_name not in processed_profs:
                            processed_profs.add(prof_name)
                            create_professeur(prof_name)

        return redirect('account:profs')

    return JsonResponse({"status": "error", "message": "Erreur lors de l'importation"})

