from django.db import models


class Update(models.Model):
    """
    An update about an issue (e.g. "Cory Booker now supports X.")
    """

    text = models.TextField()
    issue = models.ForeignKey("Issue", on_delete=models.PROTECT)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ["-created_on"]
