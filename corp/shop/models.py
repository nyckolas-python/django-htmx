import random
import string

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def rand_slug():
    """
    Generate a random slug consisting of a combination of three alphanumeric characters.

    Example:
    rand_slug() -> 'aB3'
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(3)
    )


class Category(models.Model):
    """
    This model represents a category for products.
    """

    name = models.CharField(verbose_name="Category", max_length=255, db_index=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='children', null=True, blank=True
    )
    slug = models.SlugField(
        verbose_name="URL", max_length=255, unique=True, null=False, editable=True
    )

    created_at = models.DateTimeField(
        verbose_name="Date of creation", auto_now_add=True
    )
    updated_at = models.DateTimeField(verbose_name="Date of update", auto_now=True)

    class Meta:
        unique_together = ('slug', 'parent')
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        """
        Return a string representing the full path of the current node, including all parent nodes.
        """
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return " -> ".join(full_path[::-1])

    @staticmethod
    def _rand_slug():
        """
        Generates a random slug consisting of lowercase letters and digits.
        Example:
            >>> rand_slug()
            'abc123'
        """
        return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(3))

    def save(self, *args, **kwargs):
        """
        Save the object with a generated slug if it does not already have one.
        """
        if not self.slug:
            self.slug = slugify(self._rand_slug() + '-pickBetter' + self.name)

        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category-list', args=[str(self.slug)])


class Product(models.Model):
    """
    Model representing a product.
    """

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products'
    )
    title = models.CharField(verbose_name="Product", max_length=255, db_index=True)
    brand = models.CharField(
        verbose_name="Brand", max_length=255, null=False, editable=True
    )
    description = models.TextField(verbose_name="Description", null=True, blank=True)
    slug = models.SlugField(
        verbose_name="URL", max_length=255, unique=True, null=False, editable=True
    )
    price = models.DecimalField(
        verbose_name="Price", max_digits=10, decimal_places=2, default=99.99
    )
    image = models.ImageField(
        verbose_name="Image",
        upload_to='images/products/%Y/%m/%d',
        default='images/products/default.jpg'
    )
    available = models.BooleanField(verbose_name="Available", default=True)

    created_at = models.DateTimeField(
        verbose_name="Date of creation", auto_now_add=True, db_index=True
    )
    updated_at = models.DateTimeField(verbose_name="Date of update", auto_now=True)

    class Meta:
        unique_together = ('slug', 'category')
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']

    @property
    def full_image_url(self):
        """
        Returns:
            str: The full image URL.
        """
        return self.image.url if self.image else ''

    def get_absolute_url(self):
        return reverse('shop:product-detail', args=[str(self.slug)])

    def get_discounted_price(self):
        """
        Calculates the discounted price based on the product's price and discount.

        Returns:
            decimal.Decimal: The discounted price.
        """
        discounted_price = self.price - (self.price * self.discount / 100)
        return round(discounted_price, 2)

    def __str__(self):
        return self.title


class ProductManager(models.Manager):
    def get_queryset(self):
        """
        Method to get the queryset with a filter for available products.
        """
        return super(ProductManager, self).get_queryset().filter(available=True)


class ProductProxy(Product):

    objects = ProductManager()

    class Meta:
        proxy = True

    def __str__(self):
        return self.title
