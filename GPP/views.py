from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from .models import *
from account.models import *
import openpyxl
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files import File
from django.utils.text import slugify
from datetime import datetime
import os
# Create your views here.

def home(request ):
    users = User.objects.all()
    user = User.objects.get(username=request.user)
    profs = Prof.objects.all()
    fils = Filiere.objects.all()
    cours = []
    if user.is_staff:
        cours = Cours.objects.all()
        paies = Paiement.objects.all()
        
        cours_signees = Cours.objects.filter(isSigned='effectué')
        cours_non_signees = Cours.objects.filter(isSigned='en attente')
                
        paie_en_cours = Paiement.objects.filter(confirmation='en attente')
        paie_conf = Paiement.objects.filter(confirmation='accepté')
        paie_ref = Paiement.objects.filter(confirmation='refusé')
    else:
        print('Mous',user)
        cours = Cours.objects.filter(prof=user.id)
        paies = Paiement.objects.all()
        
        cours_signees = Cours.objects.filter(prof=user.id ,isSigned='effectué')
        cours_non_signees = Cours.objects.filter(prof=user.id ,isSigned='en attente')
        
        paie_en_cours = Paiement.objects.filter(prof=user.id ,confirmation='en attente')
        paie_conf = Paiement.objects.filter(prof=user.id ,confirmation='accepté')
        paie_ref = Paiement.objects.filter(prof=user.id ,confirmation='refusé')

    
    emps = Emploi.objects.all()
    
    emplois_par_jour = Emploi.objects.values('jour').annotate(count=Count('id'))
    labels_emplois = []
    data_emplois = []
    for emploi in emplois_par_jour:
        labels_emplois.append(emploi['jour'])
        data_emplois.append(emploi['count'])
    
    print('emplois_par_jour',emplois_par_jour.count)
    context = {'fils' : fils,'profs' : profs,'users':users,
               'cours':cours,'paies':paies,'emps':emps,'cours_signees':cours_signees,
               'cours_non_signees':cours_non_signees, 'labels_emplois': labels_emplois,
    'data_emplois': data_emplois,'paie_en_cours': paie_en_cours,'paie_conf': paie_conf,'paie_ref': paie_ref,
    }
    return render(request,'home.html',context)

from django.core.paginator import Paginator
from django.contrib import messages


# filiere start
def filieres(request ):
    fils = Filiere.objects.all()
    context = {'fils' : fils,}
    return render(request,'fils.html',context)


from .forms import *
def add_fil(request):
    if request.method == 'POST':
        print('1')
        form = FilForm(request.POST)
        print('11')
        if form.is_valid():
            print('2')
            fil = form.save()
            return redirect('GPP:filieres')
    else:
        print('3')
        form = FilForm()
        return render(request, 'add_fil.html', {'form': form})


def update_filiere(request, id):
    filiere = get_object_or_404(Filiere, id=id)
    if request.method == 'POST':
        form = FilForm(request.POST, request.FILES, instance=filiere)
        if form.is_valid():
            form.save()
            messages.success(request, "User mis à jour avec succès.")
            return redirect('GPP:filieres')
        else:
            messages.error(request, "Erreur lors de la mise à jour du filiere.")
    else:
        form = FilForm(instance=filiere)
    
    return render(request, 'update_filiere.html', {'form': form, 'filiere': filiere})


def delete_filiere(request,id ):
    filiere = get_object_or_404(Filiere, id=id)
    filiere.delete()
    return redirect('GPP:filieres')
# matiere start
def matieres(request,id ):
    mats = Matiere.objects.filter(filiere=id)
    
    paginator = Paginator(mats, 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj' : page_obj}   
    return render(request,'mats.html',context)

def matiere(request,id ):
    mat = Matiere.objects.get(id=id)
    print("MatId:",mat.filiere)
    filiere = Filiere.objects.filter(name=mat.filiere)
    return redirect('GPP:matieres', id=mat.filiere.id)
def update_mat(request, id):
    mat = get_object_or_404(Matiere, id=id)
    
    if request.method == 'POST':
        form = MatForm(request.POST, request.FILES, instance=mat)
        
        if form.is_valid():
            print('1')
            # Validation des groupes pour éviter les duplications
            group_cm = form.cleaned_data['group_cm']
            group_tp = form.cleaned_data['group_tp']
            group_td = form.cleaned_data['group_td']
            print(group_cm)
            print('11')

            def validate_groups(groups):
                group_numbers = []
                # Nettoyage des données pour enlever les crochets
                groups = groups.strip('[]').split(',')
                # Enlève les crochets autour de la chaîne et divise les éléments par des virgules. 
                # Cela permet de traiter chaque élément comme une chaîne séparée sans crochets.
                for group in groups:
                    group = group.strip().strip("'")  # Enlever les espaces et les guillemets
                    # Supprime les espaces et les guillemets autour de chaque élément de groupe pour 
                    # garantir que les valeurs sont correctes et ne contiennent pas de caractères superflus.
                    try:
                        print(f"Checking group: {group}")  # Débogage
                        # Split to get the ID and group number
                        prof_id, group_number = group.split('-')
                        print(f"prof_id: {prof_id}, group_number: {group_number}")  # Débogage
                        group_numbers.append(int(group_number))
                    except ValueError:
                        raise ValidationError(f"Format incorrect pour le groupe: {group}")
                
                # Check for duplicates in group numbers
                if len(group_numbers) != len(set(group_numbers)):
                    raise ValidationError("Un groupe ne peut pas être attribué à plusieurs professeurs dans le même type.")

            try:
                validate_groups(group_cm)
                validate_groups(group_tp)
                validate_groups(group_td)
            except ValidationError as e:
                messages.error(request, e.message)
                return render(request, 'update_mat.html', {'form': form, 'mat': mat})

            form.save()
            messages.success(request, "matiere mis à jour avec succès.")
            return redirect('GPP:matieres', id=mat.filiere.id)
        else:
            messages.error(request, "Erreur lors de la mise à jour du matiere.")
    else:
        form = MatForm(instance=mat)
    
    return render(request, 'update_mat.html', {'form': form, 'mat': mat})

import pandas as pd


def upload_matieres(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        data = pd.read_excel(file, sheet_name='Sheet1', skiprows=3)  # Sauter les 3 premières lignes

        # Parcourir les lignes pertinentes (4 à 15 et 21 à 51)
        for index, row in data.iterrows():
            if (0 <= index <= 100) :
                code = str(row['code'])
                name = row['nom de la matiere']
                cred = row['Crédits EM']
                prof_cm = row['CM']
                prof_tp = row['TP']
                prof_td = row['TD']

                filiere = None
                semestre = None
                
                # Identifier la filière et le semestre
                if code == 'nan':
                    continue  # Ignorer les lignes où le code est NaN
                if code[3].isdigit():
                    if code[3] in ['1', '2']:
                        filiere = Filiere.objects.get(name='TC')
                        semestre = 1 if code[3] == '1' else 2

                        
                    elif code.startswith('DSI') or code.startswith('RSS') or code.startswith('CNM'):
                        filiere = Filiere.objects.get(name=code[:3])
                        print('fildd',filiere)
                        semestre = int(code[3]) if code[3].isdigit() else None
                    else:
                        autres_filieres = Filiere.objects.exclude(name='TC')
                        for filiere in autres_filieres:
                            matiere = Matiere.objects.create(
                                name=name,
                                code=code,
                                filiere=filiere,
                                cred=cred,
                                semestre=int(code[3]) if code[3].isdigit() else None
                            )
                            matiere.prof_cm.set(parse_profs(prof_cm))
                            matiere.prof_tp.set(parse_profs(prof_tp))
                            matiere.prof_td.set(parse_profs(prof_td))
                            matiere.group_cm = assign_default_groups(parse_profs(prof_cm))
                            matiere.group_tp = assign_default_groups(parse_profs(prof_tp))
                            matiere.group_td = assign_default_groups(parse_profs(prof_td))
                            matiere.save()

                        continue  # Passer à la ligne suivante
                else:
                    continue  # Ignorer les lignes où le code ne commence pas par un chiffre

                # Créer la matière pour la filière déterminée
                matiere = Matiere.objects.create(
                    name=name,
                    code=code,
                    filiere=filiere,
                    semestre=semestre,
                    cred=cred
                )
                matiere.prof_cm.set(parse_profs(prof_cm))
                matiere.prof_tp.set(parse_profs(prof_tp))
                matiere.prof_td.set(parse_profs(prof_td))
                matiere.group_cm = assign_default_groups(parse_profs(prof_cm))
                matiere.group_tp = assign_default_groups(parse_profs(prof_tp))
                matiere.group_td = assign_default_groups(parse_profs(prof_td))
                matiere.save()

        return redirect('GPP:filieres')
    return render(request, 'upload_matieres.html')


def parse_profs(prof_string):
    if not isinstance(prof_string, str) or pd.isna(prof_string):
        return []

    profs = []
    for prof in prof_string.split('/'):
        prof = prof.strip()
        if prof:
            parts = prof.split()
            nom = parts[0]
            prenom = parts[1] if len(parts) > 1 else nom
            nom_complet = f"{nom} {prenom}"
            try:
                us = User.objects.get(username=nom_complet)
                pr = Prof.objects.get(user=us)
                profs.append(pr)
            except User.DoesNotExist:
                print(f"Utilisateur '{nom_complet}' non trouvé.")
            except Prof.DoesNotExist:
                print(f"Professeur pour l'utilisateur '{nom_complet}' non trouvé.")
    
    return profs

def assign_default_groups(prof_instances):
    """
    Assigne des groupes par défaut aux professeurs pour une matière sous forme de liste de dictionnaires.
    """
    groups = []
    for index, prof in enumerate(prof_instances):
        group_info = f"{prof.id}-{index + 1}"
        # group_info = {"prof_id": prof.id, "group": index + 1}
        groups.append(group_info)
    return groups


# Cours start
def cours(request):
    cours = []
    if request.user.is_staff:
        cours = Cours.objects.all()
    else:
        print('Mous',request.user)
        cours = Cours.objects.filter(prof=request.user.id)
        # Pagination: Show only one row per page
    paginator = Paginator(cours, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    day_name = datetime.now().weekday()
    daysOfWeek = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"  ]
    print("Today:",day_name)
    print("Today:",daysOfWeek[0])
    context = {'page_obj' : page_obj, 'day_name':daysOfWeek[day_name]}
    return render(request,'cours.html',context)

def prof_cours(request):
    prof = Prof.objects.get(user=request.user)
    cours = Cours.objects.filter(prof=prof)
        # Pagination: Show only one row per page
    paginator = Paginator(cours, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj' : page_obj,}
    return render(request,'cours.html',context)


from django.http import JsonResponse

def create_cours(request):
    if request.method == 'POST':
        print('1')
        form = CoursForm(data=request.POST)
        print("Form",form['groupe'])
        if form.is_valid():
            print('2')
            nb_cours_non_signes = Cours.objects.filter(prof=form.instance.prof, isSigned='en attente').count()
            send_notification_email(form.instance.prof, nb_cours_non_signes)
            form.save()
            print('3')
            messages.success(request, "Cours créé avec succès.")
            return redirect('GPP:cours')  # Rediriger vers une liste des cours ou une autre page
        else:
            print('4')
            messages.error(request, "Erreur lors de la création du cours.")
    else:
        form = CoursForm()
    
    return render(request, 'add_cours.html', {'form': form})

from django.db.models import Q 
def load_matieres(request):
    prof_id = request.GET.get('prof_id')
    print("prof_id",prof_id)
    
    matieres = Matiere.objects.filter(
        Q(prof_cm__id=prof_id) | Q(prof_tp__id=prof_id) | Q(prof_td__id=prof_id)
    ).distinct()
    return JsonResponse(list(matieres.values('id', 'name','filiere__name')), safe=False)

from datetime import date, time

def create_courses_for_day(day_name):
    # Get current date
    current_date = date.today()
    
    # Get all employment records for the given day name
    emplois = Emploi.objects.filter(jour=day_name)

    for emploi in emplois:
        # Check if a course already exists with the same attributes to avoid duplication
        if not Cours.objects.filter(
            matiere=emploi.matiere,
            prof=emploi.prof,
            groupe=emploi.groupe,
            type=emploi.type,
            date_creation=current_date,
            deb=emploi.deb,
            fin=emploi.fin
        ).exists():
            # Create a new course based on the emploi record
            Cours.objects.create(
                matiere=emploi.matiere,
                prof=emploi.prof,
                groupe=emploi.groupe,
                type=emploi.type,
                nbh=emploi.nbh,
                date_creation=current_date,
                deb=emploi.deb,
                fin=emploi.fin
            )
            nb_cours_non_signes = Cours.objects.filter(prof=emploi.prof, isSigned='en attente').count()
            send_notification_email(emploi.prof, nb_cours_non_signes)
          


def generate_courses(request):
    if request.method == 'POST':
        print("Post")
        day_name = datetime.now().weekday()
        daysOfWeek = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"  ]
        
        
        # day_name = request.POST.get('day_name')  # Get the day name from the form/button
        print("day_name",day_name)
        print("day_name",daysOfWeek[day_name])
        create_courses_for_day(daysOfWeek[day_name])
        messages.success(request, f"Courses created for {day_name}.")
    return redirect('GPP:cours')  # Redirect to a desired view

from django.core.mail import send_mail

def send_notification_email(prof, nb_cours_non_signes):
    subject = "Nouveau(x) cours à signer"
    message = f"Cher(e) {prof.user.username}, vous avez {nb_cours_non_signes} nouveaux cours à signer."
    email_from = 'ie19284.etu@iscae.mr'
    recipient_list = [prof.user.email]
    send_mail(subject, message, email_from, recipient_list)

def send_notification_email_for_paie(prof, paie_a_conf):
    subject = "Nouveau(x) paiement à confirmer"
    message = f"Cher(e) {prof.user.username}, vous avez {paie_a_conf} nouveaux paiements à Confirmer."
    email_from = 'ie19284.etu@iscae.mr'
    recipient_list = [prof.user.email]
    send_mail(subject, message, email_from, recipient_list)
def signer(request, id):
    cours = Cours.objects.get(id=id)
    if cours.isSigned == 'effectué':
        cours.isSigned  = 'en attente'
    else:
        cours.isSigned  = 'effectué'
    cours.save()
    
    if request.user.is_staff:
        cours = Cours.objects.all()
    else:
        # print('Mous',user)
        cours = Cours.objects.filter(prof=request.user.id)
    paginator = Paginator(cours, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj' : page_obj,}
    return render(request,'cours.html',context)


def update_cour(request, id):
    cour = get_object_or_404(Cours, id=id)
    if request.method == 'POST':
        form = CoursForm(request.POST,  instance=cour)
        if form.is_valid():
            form.save()
            messages.success(request, "Cours mis à jour avec succès.")
            return redirect('GPP:cours')
        else:
            messages.error(request, "Erreur lors de la mise à jour du cour.")
    else:
        form = CoursForm(instance=cour)
    
    return render(request, 'update_cour.html', {'form': form, 'cour': cour})


def delete_cour(request,id ):
    cour = get_object_or_404(Cours, id=id)
    cour.delete()
    return redirect('GPP:cours')
# cours end
# views.py
from django.http import JsonResponse

def load_groupes(request):
    prof_id = request.GET.get('prof_id')
    matiere_id = request.GET.get('matiere_id')
    type_cours = request.GET.get('type_cours')  # CM, TP, TD

    matiere = Matiere.objects.get(id=matiere_id)
    prof = Prof.objects.get(id=prof_id)
    print("PID", prof.id)

    groups = []

    # Récupération des groupes pour le type sélectionné
    type_group_mapping = {
        'CM': 'group_cm',
        'TP': 'group_tp',
        'TD': 'group_td'
    }

    type_group = type_group_mapping.get(type_cours)
    if type_group:
        print('1')
        group_data = getattr(matiere, type_group, [])
        print('group_data', group_data)
        group_data = group_data.strip('[]').split(',')
        for group in group_data:
            group = group.strip().strip("'")
            print('2')
            print('group', group)
            prof_group_id, group_number = group.split('-')
            prof_group_id = int(prof_group_id)  # Convertir en entier
            print('prof_group_id', prof_group_id)
            print('profID', prof.id)
            print('bool', prof_group_id == prof.id)
            if prof_group_id == prof.id: # Conversion de prof_group_id en entier
                print('555')
                groups.append(f'G-{group_number}')
                print(f"groups: {groups}, group: {group}")
            else:
                continue
    print(f"groups: {groups}")
       
    return JsonResponse(groups, safe=False)


# Emploi start
def emploi(request):
    emplois = Emploi.objects.all()
    paginator = Paginator(emplois, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj' : page_obj}
    return render(request,'emploi.html',context)

def days_emp(request):
    # Get date range from request
    jour = request.GET.get('jour')
    print('jour',jour)

    # Base query for courses with signed_status 'effectué' and payment status 'en attente'
    emplois = Emploi.objects.filter(jour=jour)
    paginator = Paginator(emplois, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'jour': jour}
    return render(request, 'emploi.html', context)

from django.http import JsonResponse

def add_emp(request):
    if request.method == 'POST':
        print('1')
        form = EmploiForm(data=request.POST)
        # print("Form",form['groupe'])
        if form.is_valid():
            print('2')
            form.save()
            print('3')
            messages.success(request, "Cours créé avec succès.")
            return redirect('GPP:emps')  # Rediriger vers une liste des cours ou une autre page
        else:
            print('4')
            messages.error(request, "Erreur lors de la création du cours.")
    else:
        form = EmploiForm()
    
    return render(request, 'add_emp.html', {'form': form})

def load_mats(request):
    prof_id = request.GET.get('prof_id')
    filiere_id = request.GET.get('filiere_id')
    
    matieres = Matiere.objects.filter(
        Q(filiere=filiere_id) &
        (Q(prof_cm__id=prof_id) | Q(prof_tp__id=prof_id) | Q(prof_td__id=prof_id))
    ).distinct()
    return JsonResponse(list(matieres.values('id', 'name', 'filiere__name')), safe=False)


def delete_emp(request,id ):
    emp = get_object_or_404(Emploi, id=id)
    emp.delete()
    return redirect('GPP:emps')

# Paiement

def paie_list(request):
    paies = Paiement.objects.all()
    paginator = Paginator(paies, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj' : page_obj}
    return render(request,'paies.html',context)

from django.db.models import Sum, Count
from django.core.paginator import Paginator
def paies(request):
    # Get date range from request
    date_deb = request.GET.get('date_deb')
    date_fin = request.GET.get('date_fin')

    # Base query for courses with signed_status 'effectué' and payment status 'en attente'
    paiements = Cours.objects.filter(isSigned='effectué', isPaid='en attente')

    # Filter by date range if provided
    if date_deb and date_fin:
        try:
            date_deb = datetime.strptime(date_deb, '%Y-%m-%d')
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d')
            paiements = paiements.filter(date_creation__range=(date_deb, date_fin))
        except ValueError:
            # Handle the case where the dates are not properly formatted
            pass
    elif date_deb:
        try:
            date_deb = datetime.strptime(date_deb, '%Y-%m-%d')
            paiements = paiements.filter(date_creation__gte=date_deb)
        except ValueError:
            pass
    elif date_fin:
        try:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d')
            paiements = paiements.filter(date_creation__lte=date_fin)
        except ValueError:
            pass

    # Group by professor and aggregate the total hours (nbh), total amount (taux), and count of courses (nbc)
    paiements = paiements.values(
        'prof_id',
        'prof__user__username',
        'prof__compte',
        'prof__banc'
    ).annotate(
        total_nbh=Sum('nbh'),
        total=Sum('taux'),
        nbc=Count('id')  # Count the number of courses
    ).order_by('prof__user__username')

    # Pagination: Show only four rows per page
    paginator = Paginator(paiements, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'date_deb': date_deb, 'date_fin': date_fin}
    return render(request, 'Paiements.html', context)

def create_paiements(request):
    if request.method == "POST":
        prof_ids = request.POST.getlist('prof_ids')
        date_deb = request.POST.get('date_deb')
        date_fin = request.POST.get('date_fin')
        
        print('Requête POST reçue:', request.POST)
        print('Identifiants des professeurs sélectionnés:', prof_ids)

        if date_deb and date_fin and prof_ids:
            date_deb = datetime.strptime(date_deb, '%Y-%m-%d')
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d')
            print('Dates:', date_deb, date_fin)

            for prof_id in prof_ids:
                prof = Prof.objects.get(id=prof_id)
                cours_selectionnes = Cours.objects.filter(
                    prof=prof,
                    date_creation__gt=date_deb,
                    date_creation__lt=date_fin,
                    isSigned='effectué'
                )
                print('nnbc',cours_selectionnes.count)

                total_nbh = cours_selectionnes.aggregate(Sum('nbh'))['nbh__sum'] or 0
                total_taux = cours_selectionnes.aggregate(Sum('taux'))['taux__sum'] or 0
                total_nbc = cours_selectionnes.aggregate(Count('id'))['id__count'] or 0

                if cours_selectionnes.exists():
                    from_date = cours_selectionnes.earliest('date_creation').date_creation
                    to_date = cours_selectionnes.latest('date_creation').date_creation

                    # Créer le paiement
                    paiement = Paiement.objects.create(
                        prof=prof,
                        nbh=total_nbh,
                        nbc=total_nbc,
                        date_creation=datetime.now(),
                        fromDate=from_date,
                        toDate=to_date,
                        taux=total_taux,
                        confirmation='en attente',
                        message='ok'
                    )
                    
                    paie_a_conf = Paiement.objects.filter(prof=prof, confirmation='en attente').count()
                    send_notification_email_for_paie(prof, paie_a_conf)
            

                    # Mettre à jour les cours sélectionnés comme "préparé"
                    cours_selectionnes.update(isPaid='préparé')

            return redirect('GPP:paies')
    return redirect('GPP:paies')

def confirmer(request, id):
    paie = Paiement.objects.get(id=id)
    if paie.confirmation == 'en attente':
        paie.confirmation  = 'accepté'
    
    paie.save()
    return redirect('GPP:paie_list')

def refus(request, id):
    paie = Paiement.objects.get(id=id)
    if paie.confirmation == 'en attente':
        paie.confirmation  = 'refusé'
    
    paie.save()
    return redirect('GPP:paie_list')

def delete_paie(request,id ):
    paie = get_object_or_404(Paiement, id=id)
    paie.delete()
    return redirect('GPP:paie_list')