from django.urls import include, path

from . import views


app_name='GPP'

urlpatterns = [
    path('',views.home , name='home'),
    
    path('filieres',views.filieres , name='filieres'),
    path('F<int:id>',views.update_filiere , name='update_filiere'),
    path('add_fil',views.add_fil , name='add_fil'), 
    path('Fd<int:id>',views.delete_filiere , name='delete_filiere'),

    
    path('paie_list',views.paie_list , name='paie_list'),
    path('paies',views.paies , name='paies'),
    path('dP<int:id>',views.delete_paie , name='delete_paie'),
    path('conf<int:id>',views.confirmer , name='confirmer'),
    path('refus<int:id>',views.refus , name='refus'),
    
    path('emps',views.emploi , name='emps'),
    path('days_emp',views.days_emp , name='days_emp'),
    path('add_emp',views.add_emp , name='add_emp'),
    path('Ed<int:id>',views.delete_emp , name='delete_emp'),
    
    path('prof_cours',views.prof_cours , name='prof_cours'),
    path('send',views.send_notification_email , name='send_notification_email'),
    
    path('cours',views.cours , name='cours'),
    path('create_cours',views.create_cours , name='create_cours'),
    path('generate_courses',views.generate_courses , name='generate_courses'),
    path('create_courses_for_day',views.create_courses_for_day , name='create_courses_for_day'),
    # path('create_courses_task',views.create_courses_task , name='create_courses_task'),
    path('SC<int:id>',views.signer , name='signer'),
    path('Cd<int:id>',views.delete_cour , name='delete_cour'),
    path('CU<int:id>',views.update_cour , name='update_cour'),
    
    
    path('M<int:id>',views.matieres , name='matieres'),
    path('Mat<int:id>',views.matiere , name='matiere'),
    path('create_paiements',views.create_paiements , name='create_paiements'),
    
    path('MU<int:id>',views.update_mat , name='update_mat'),
    
    path('load_mats',views.load_mats , name='load_mats'),
    path('load_matieres',views.load_matieres , name='load_matieres'),
    path('load_groupes',views.load_groupes , name='load_groupes'),
    path('upload_matieres/', views.upload_matieres, name='upload_matieres'),
]