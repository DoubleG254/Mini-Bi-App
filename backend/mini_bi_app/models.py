from django.db import models
from django.contrib.auth.models import User  

# Create your models here.

class Dataset (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    file = models.FileField(upload_to='datasets/')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

class Report(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    summary = models.JSONField()
    charts = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ColumnTrainingData(models.Model):
    column_name = models.CharField(max_length=100)
    features = models.JSONField()
    semantic_label = models.CharField(max_length=100)
    aggregation = models.CharField(max_length=50, null=True, blank=True)  # Optional field for aggregation type

    def __str__(self):
        return self.column_name

class ColumnPrediction(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    column_name = models.CharField(max_length=100)
    semantic_label = models.CharField(max_length=100)
    confidence_score = models.FloatField()
    aggregation = models.CharField(max_length=50, null=True, blank=True)  # Optional field for aggregation type

    def __str__(self):
        return self.column_name