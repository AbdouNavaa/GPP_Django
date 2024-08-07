from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from django.utils.text import slugify
# Create your models here.
from account.models import Prof


from django.core.exceptions import ValidationError

sems = (
    ('1,2','1,2'),
    ('3,6','3,6'),
)

class Filiere(models.Model):
    name = models.CharField(max_length=3, default='TC',unique=True)
    description = models.CharField(max_length=50, default='')
    semestres = models.CharField(max_length=4, choices=sems, default='1,2')
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.name
    def clean(self):
        # Condition pour le nom 'TC' si le semestre est '1,2'
        if self.semestres == '1,2':
            self.name = 'TC'

    def get_semesters_list(self):
        if ',' in self.semestres:
            start, end = map(int, self.semestres.split(','))
            return list(range(start, end + 1))
        return [int(self.semestres)]
        # Vérifier l'unicité du nom
        if Filiere.objects.filter(name=self.name).exists():
            raise ValidationError(f'La filière avec le nom "{self.name}" existe déjà.')

    def save(self, *args, **kwargs):
        # Appel de la méthode clean pour valider l'instance
        self.clean()
        super(Filiere, self).save(*args, **kwargs)

        
    def save(self,*args, **kwargs):
        self.slug = slugify(self.name)
        super(Filiere,self).save(*args, **kwargs)
        





class Matiere(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=6, unique=False)
    cred = models.IntegerField(default=2)
    semestre = models.IntegerField()
    nombre_heures = models.IntegerField(default=24)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    prof_cm = models.ManyToManyField(Prof, related_name='matiere_cm')
    prof_tp = models.ManyToManyField(Prof, related_name='matiere_tp')
    prof_td = models.ManyToManyField(Prof, related_name='matiere_td')
    group_cm = models.TextField(default='')  # Format: "Prof1:G1,Prof2:G2,Prof3:G3"
    group_tp = models.TextField(default='')
    group_td = models.TextField(default='')
    prix = models.FloatField(default=500)  # Prix de la matière
   
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.name




    def save(self, *args, **kwargs):
        # Appel de la méthode clean pour valider l'instance
        super(Matiere, self).save(*args, **kwargs)

        
    def save(self,*args, **kwargs):
        self.slug = slugify(self.name)
        super(Matiere,self).save(*args, **kwargs)
        
    def __str__(self):
        return self.name

from django.db import models
from django.utils import timezone
from datetime import *

  
class Cours(models.Model):
    TYPE_CHOICES = [
        ('CM', 'CM'),
        ('TP', 'TP'),
        ('TD', 'TD'),
    ]
    SIGNED_CHOICES = [
        ('effectué', 'effectué'),
        ('en attente', 'en attente'),
        ('annulé', 'annulé'),
    ]
    PAID_CHOICES = [
        ('en attente', 'en attente'),
        ('préparé', 'préparé'),
        ('effectué', 'effectué'),
    ]

    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    prof = models.ForeignKey(Prof, on_delete=models.CASCADE)
    groupe = models.CharField(max_length=10,default='G')  # format: "idprof-groupe_number"
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    nbh = models.FloatField(default=0)  # Nombre d'heures
    date_creation = models.DateTimeField(auto_now_add=False)
    deb = models.TimeField(auto_created=False)  # Heure de début
    fin = models.TimeField()  # Heure de fin, calculée automatiquement
    taux = models.FloatField(default=0)  # Taux de rémunération
    isSigned = models.CharField(max_length=10, choices=SIGNED_CHOICES, default='en attente')
    isPaid = models.CharField(max_length=10, choices=PAID_CHOICES, default='en attente')

    def save(self, *args, **kwargs):
        # Calcul automatique de l'heure de fin (fin = deb + nbh)
        end_time = (datetime.combine(date.today(), self.deb) + timedelta(hours=self.nbh)).time()
        self.fin = end_time

        # Calcul du taux en fonction du type de cours
        if self.type == 'CM':
            taux_horaire = self.nbh
        elif self.type in ['TP', 'TD']:
            taux_horaire = self.nbh * (2/3)
        else:
            taux_horaire = 0
        
        # Calcul du taux total (taux_horaire * prix_matiere)
        self.taux = taux_horaire * self.matiere.prix

        super().save(*args, **kwargs)


class Paiement(models.Model):
    type_CHOICES = [
        ('en attente', 'en attente'),
        ('accepté', 'accepté'),
        ('refusé', 'refusé'),
    ]
    prof = models.ForeignKey(Prof, on_delete=models.CASCADE)
    nbh = models.FloatField(default=0)  
    nbc = models.FloatField(default=0)  
    th = models.FloatField(default=0)  
    date_creation = models.DateTimeField(auto_now_add=False)
    fromDate = models.DateTimeField(auto_now_add=False)
    toDate = models.DateTimeField(auto_now_add=False)
    taux = models.FloatField(default=0)  
    confirmation = models.CharField(max_length=10, choices=type_CHOICES)
    message = models.CharField(max_length=50,default='ok')  



class Emploi(models.Model):
    TYPE_CHOICES = [
        ('CM', 'CM'),
        ('TP', 'TP'),
        ('TD', 'TD'),
    ]
    day_CHOICES = [
        ('Dimanche', 'Dimanche'),
        ('Lundi', 'Lundi'),
        ('Mardi', 'Mardi'),
        ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'),
        ('Vendredi', 'Vendredi'),
        ('Samedi', 'Samedi'),
    ]

    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    nbh = models.FloatField(default=0)  # Nombre d'heures
    deb = models.TimeField(auto_created=False)  # Heure de début
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    groupe = models.CharField(max_length=10,default='G')  # format: "idprof-groupe_number"
    prof = models.ForeignKey(Prof, on_delete=models.CASCADE)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    fin = models.TimeField()  # Heure de fin, calculée automatiquement
    jour = models.CharField(max_length=10, choices=day_CHOICES)

    def save(self, *args, **kwargs):
        # Calcul automatique de l'heure de fin (fin = deb + nbh)
        end_time = (datetime.combine(date.today(), self.deb) + timedelta(hours=self.nbh)).time()
        self.fin = end_time

        
        

        super().save(*args, **kwargs)

