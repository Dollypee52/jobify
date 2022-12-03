from django.db import models


class Base(models.Model):
    base_type = "all"
    obj_id = models.CharField(max_length=255, default=None, null=True)
    type = models.CharField(max_length=255)
    generated = models.BooleanField(default=False)
    by = models.CharField(max_length=255, null=True)
    time = models.DateTimeField(editable=True, auto_now_add=True)  # creation date
    url = models.URLField(max_length=500, null=True)
    title = models.CharField(max_length=255, null=True)
    text = models.TextField(null=True)
    score = models.BigIntegerField(default=0, null=True)

    class Meta:
        ordering = ['-time', 'title']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = self.base_type
        super().save(*args, **kwargs)

    @classmethod
    def _check_model(cls):
        return []


class StoryQuerySet(models.QuerySet):
    def story(self):
        return self.filter(type="story")


class StoryManager(models.Manager):
    def get_queryset(self):
        return StoryQuerySet(self.model, using=self._db).story()


class Story(Base):
    base_type = "story"
    objects = StoryManager()

    class Meta:
        ordering = ['-time', 'title']
        proxy = True
        verbose_name = "Story"
        verbose_name_plural = "Stories"

    def __str__(self):
        return f"Story {self.by} {self.id}"


class JobQuerySet(models.QuerySet):
    def job(self):
        return self.filter(type="job")


class JobManager(models.Manager):
    def get_queryset(self):
        return JobQuerySet(self.model, using=self._db).job()


class Job(Base):
    base_type = "job"
    objects = JobManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f"Job {self.by} -{self.id}"


class PollQuerySet(models.QuerySet):
    def poll(self):
        return self.filter(type="poll")


class PollManager(models.Manager):
    def get_queryset(self):
        return PollQuerySet(self.model, using=self._db).poll()


class Poll(Base):
    base_type = "poll"
    objects = PollManager()

    class Meta:
        proxy = True
        ordering = ['-time', 'title']

    def __str__(self):
        return f"Poll {self.by} - {self.id}"


class Comment(Base):
    base_type = "comment"
    kids = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="comment_comments", null=True
    )
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name="story_comments", null=True
    )
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='poll_comments', null=True)

    def __str__(self):
        return f"Comment {self.by} - {self.id}"


class PollOption(Base):
    base_type = "pollopt"
    poll = models.ForeignKey(
        Poll, on_delete=models.CASCADE, related_name="poll_polloptions"
    )

    def __str__(self):
        return f"PollOption {self.by} - {self.id}"
