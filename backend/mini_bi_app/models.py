from django.db import models
from djago.contrib.auth.models import User  

# Create your models here.

class File (models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Name = models.CharField(max_length=50)
    File = models.FileField(upload_to='datasets/')
    created_at = models.DateTimeField(auto_now_add=True)

    #Metdata:
    num_rows = models.IntegerField(null =True, blank=True)
    num_columns = models.IntegerField(null =True, blank=True)

    def __str__(self):
        return self.Name

class Report(models.Model):
    File = models.ForeignKey(File, on_delete=models.CASCADE)
    Name = models.CharField(max_length=50)
    Summary = models.JSONField()
    Charts = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Name

class ColumnTrainingData(models.Model):
    column_name = models.CharField(max_length=100)
    features = models.JSONField()
    semantic_label = models.CharField(max_length=100)
    aggregation = models.CharField(max_length=50, null=True, blank=True)  # Optional field for aggregation type

    def __str__(self):
        return self.column_name