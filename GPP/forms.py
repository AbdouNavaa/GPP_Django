from django import forms
from .models import *
from account .models import *



class FilForm(forms.ModelForm):
    class Meta:
        model = Filiere
        fields = '__all__'
        exclude = ['slug']
        


class MatForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = '__all__'
        exclude = ['slug']
    



class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['prof', 'matiere', 'type', 'groupe', 'nbh', 'date_creation', 'deb', 'isSigned', 'isPaid']
        widgets = {
            'date_creation': forms.DateInput(attrs={'type': 'date'}),
            'deb': forms.TimeInput(attrs={'type': 'time'}),
        }

    type = forms.ChoiceField(choices=[('CM', 'CM'), ('TP', 'TP'), ('TD', 'TD')], required=True)
    groupe = forms.ChoiceField(choices=[], required=True)

    def __init__(self, *args, **kwargs):
        super(CoursForm, self).__init__(*args, **kwargs)
        self.fields['groupe'].choices = [('', '--  --')]

        # Initialiser les choix des groupes si une instance est passée
        if self.instance and self.instance.pk:
            data = {
                'prof': self.instance.prof.id,
                'matiere': self.instance.matiere.id,
                'type': self.instance.type
            }
            self.populate_groupe_choices(data)

        # Initialiser les choix des groupes si des données sont passées
        if 'data' in kwargs:
            self.populate_groupe_choices(kwargs['data'])

    def populate_groupe_choices(self, data):
        prof_id = data.get('prof')
        matiere_id = data.get('matiere')
        type_cours = data.get('type')

        if prof_id and matiere_id and type_cours:
            try:
                matiere = Matiere.objects.get(id=matiere_id)
                prof = Prof.objects.get(id=prof_id)

                type_group_mapping = {
                    'CM': 'group_cm',
                    'TP': 'group_tp',
                    'TD': 'group_td'
                }

                type_group = type_group_mapping.get(type_cours)
                if type_group:
                    group_data = getattr(matiere, type_group, [])
                    group_data = group_data.strip('[]').split(',')
                    choices = [('', '--  --')]
                    for group in group_data:
                        group = group.strip().strip("'")
                        prof_group_id, group_number = group.split('-')
                        prof_group_id = int(prof_group_id)
                        if prof_group_id == prof.id:
                            choices.append((f'G-{group_number}', f'G-{group_number}'))

                    self.fields['groupe'].choices = choices
            except (Matiere.DoesNotExist, Prof.DoesNotExist):
                pass

    def clean(self):
        cleaned_data = super().clean()
        date_creation = cleaned_data.get('date_creation')
        deb = cleaned_data.get('deb')
        nbh = cleaned_data.get('nbh')
        prof = cleaned_data.get('prof')

        if self.instance.pk is not None:
            return cleaned_data

        end_time = (datetime.combine(date.today(), deb) + timedelta(hours=nbh)).time()

        overlapping_prof = Cours.objects.filter(
            prof=prof,
            date_creation=date_creation,
            deb__lt=end_time,
            fin__gt=deb
        ).exists()

        if overlapping_prof:
            raise ValidationError("Ce professeur est déjà programmé dans cette plage de temps.")

        return cleaned_data
       
from django.core.exceptions import ValidationError

class EmploiForm(forms.ModelForm):
    class Meta:
        model = Emploi
        fields = ['prof', 'filiere', 'matiere', 'type', 'groupe', 'nbh', 'jour', 'deb']
        widgets = {
            'deb': forms.TimeInput(attrs={'type': 'time'}),
            'fin': forms.TimeInput(attrs={'type': 'time'}),
        }

    type = forms.ChoiceField(choices=[('CM', 'CM'), ('TP', 'TP'), ('TD', 'TD')], required=True)
    groupe = forms.ChoiceField(choices=[], required=True)

    def __init__(self, *args, **kwargs):
        super(EmploiForm, self).__init__(*args, **kwargs)
        self.fields['groupe'].choices = [('', '--  --')]

        if 'data' in kwargs:
            self.populate_groupe_choices(kwargs['data'])

    def populate_groupe_choices(self, data):
        prof_id = data.get('prof')
        matiere_id = data.get('matiere')
        type_cours = data.get('type')

        if prof_id and matiere_id and type_cours:
            try:
                matiere = Matiere.objects.get(id=matiere_id)
                prof = Prof.objects.get(id=prof_id)

                type_group_mapping = {
                    'CM': 'group_cm',
                    'TP': 'group_tp',
                    'TD': 'group_td'
                }

                type_group = type_group_mapping.get(type_cours)
                if type_group:
                    group_data = getattr(matiere, type_group, [])
                    group_data = group_data.strip('[]').split(',')
                    choices = [('', '--  --')]
                    for group in group_data:
                        group = group.strip().strip("'")
                        prof_group_id, group_number = group.split('-')
                        prof_group_id = int(prof_group_id)
                        if prof_group_id == prof.id:
                            choices.append((f'G-{group_number}', f'G-{group_number}'))

                    self.fields['groupe'].choices = choices
            except (Matiere.DoesNotExist, Prof.DoesNotExist):
                pass

    def clean(self):
        cleaned_data = super().clean()
        jour = cleaned_data.get('jour')
        deb = cleaned_data.get('deb')
        nbh = cleaned_data.get('nbh')
        prof = cleaned_data.get('prof')
        filiere = cleaned_data.get('filiere')
        groupe = cleaned_data.get('groupe')
        matiere = cleaned_data.get('matiere')

        # Calculer l'heure de fin
        end_time = (datetime.combine(date.today(), deb) + timedelta(hours=nbh)).time()

        # Obtenir le semestre de la matière courante
        semestre = matiere.semestre

        # Vérifier les cours qui chevauchent dans la même filière et le même semestre
        overlapping_filiere = Emploi.objects.filter(
            filiere=filiere,
            jour=jour,
            deb__lt=end_time,
            fin__gt=deb,
            matiere__semestre=semestre
        ).exists()

        if overlapping_filiere:
            raise ValidationError("Il y a déjà un créneau prévu dans cette filière pour ce semestre.")

        # Vérifier les cours qui chevauchent pour le même professeur
        overlapping_prof = Emploi.objects.filter(
            prof=prof,
            jour=jour,
            deb__lt=end_time,
            fin__gt=deb
        ).exists()

        if overlapping_prof:
            raise ValidationError("Ce professeur est déjà programmé dans cette plage de temps.")

        return cleaned_data

