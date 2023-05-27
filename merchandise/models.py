from django.db import models


class Product(models.Model):
    name = models.CharField("Name", max_length=50, unique=True)
    desc = models.TextField("Beschreibung")
    price = models.DecimalField("Preis", max_digits=5, decimal_places=2)
    created_at = models.DateTimeField("Erstellt am", auto_now_add=True)
    updated_at = models.DateTimeField("Bearbeitet am", auto_now=True)

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkte"
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def has_changed(self) -> bool:
        return self.created_at.date() != self.updated_at.date()


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField("Titel", max_length=50)
    file = models.ImageField("Datei")

    class Meta:
        verbose_name = "Bild"
        verbose_name_plural = "Bilder"
        ordering = ['title']

    def __str__(self) -> str:
        return self.title
