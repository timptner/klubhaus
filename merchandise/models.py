from django.db import models

from accounts.models import User


class Product(models.Model):
    name = models.CharField("Name", max_length=50, unique=True)
    desc = models.TextField("Beschreibung")
    price = models.DecimalField("Preis", max_digits=5, decimal_places=2)
    is_stocked = models.BooleanField("Auf Lager", default=False)
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


class Size(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    label = models.CharField("Bezeichnung", max_length=15)

    class Meta:
        verbose_name = "Größe"
        verbose_name_plural = "Größen"
        ordering = ['label']
        constraints = [
            models.UniqueConstraint(fields=['product', 'label'], name='unique_size'),
        ]

    def __str__(self):
        return self.label


class Order(models.Model):
    PENDING = 0
    CONFIRMED = 1
    PAID = 2
    READY = 3
    COMPLETED = 4
    STATE_CHOICES = [
        (PENDING, "Ausstehend"),
        (CONFIRMED, "Bestätigt"),
        (PAID, "Bezahlt"),
        (READY, "Abholbereit"),
        (COMPLETED, "Abgeschlossen"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.PROTECT)
    state = models.PositiveSmallIntegerField("Status", choices=STATE_CHOICES, default=PENDING)
    created_at = models.DateTimeField("Erstellt am", auto_now_add=True)

    class Meta:
        verbose_name = "Bestellung"
        verbose_name_plural = "Bestellungen"
        ordering = ['created_at']

    def get_state_color(self) -> str:
        colors = {
            self.PENDING: 'is-light is-info',
            self.CONFIRMED: 'is-light is-warning',
            self.PAID: 'is-light is-success',
            self.READY: 'is-light is-link',
            self.COMPLETED: 'is-light ',
        }
        return colors[self.state]
