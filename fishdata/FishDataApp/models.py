from django.db import models

# Create your models here.      
class fishinfo(models.Model):
    # id = models.AutoField(primsary_key=True)
    type = models.CharField(max_length=20, blank=True, null=True) # Tuna, seer, Mackerel, sardine, others
    labels = models.CharField(max_length=4, blank=True, null=True) # good, bad, ok
    description = models.TextField(blank=True, null=True, default = None) # a text box so that user can give input for the label
    image_url = models.TextField(blank=False, null=False)

    class Meta:
        managed = False
        db_table = 'fishinfo'