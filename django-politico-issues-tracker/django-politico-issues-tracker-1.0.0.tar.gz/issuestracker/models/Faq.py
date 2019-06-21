from django.db import models


class Faq(models.Model):
    """
    A question about a specific issue (e.g. "What is a Carbon Tax?")
    """

    question = models.CharField(max_length=500)
    answer = models.TextField(null=True, blank=True)
    issue = models.ForeignKey("Issue", on_delete=models.PROTECT)
    order = models.IntegerField()

    def __str__(self):
        return self.question

    class Meta:
        unique_together = ("question", "issue")
        ordering = ["order"]
