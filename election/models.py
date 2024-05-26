from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import reverse, get_object_or_404, redirect
from django.db import models
from django.utils import timezone

from PIL import Image


class Election(models.Model):
    """
    Represents an election event.

    Attributes
    ----------
    DEFAULT_IMAGE : str
      The default image used for elections.
    title : CharField
      The title of the election.
    description : TextField
      A detailed description of the election.
    image : ImageField
      The image associated with the election.
    start_date : DateTimeField
      The start date and time of the election.
    end_date : DateTimeField
      The end date and time of the election.
    max_candidates_choice : PositiveIntegerField
      The maximum number of candidates a voter can choose.
    """
    DEFAULT_IMAGE = 'pictures/abstract-gradient.jpg'

    title = models.CharField(max_length=30)
    description = models.TextField(max_length=500, blank=True)
    image = models.ImageField(default=DEFAULT_IMAGE, upload_to='pictures/', blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_candidates_choice = models.PositiveIntegerField(default=1)

    def __str__(self):
        """
        Returns the title of the election.

        Returns
        -------
        str
            The title of the election.
        """
        return self.title

    def save(self, *args, **kwargs):
        """
        Saves the election instance to the database. If no image is provided, sets the default image.

        Parameters
        ----------
        *args : list
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.
        """
        if not self.image:
            self.image = self.DEFAULT_IMAGE
        super(Election, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns the URL to view the election details.

        Returns
        -------
        str
            The URL to view the election details.
        """
        return reverse('election:election-detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        """
        Returns the URL to update the election details.

        Returns
        -------
        str
           The URL to update the election details.
        """
        return reverse('election:election-update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        """
        Returns the URL to delete the election.

        Returns
        -------
        str
            The URL to delete the election.
        """
        return reverse('election:election-delete', kwargs={'pk': self.pk})

    def get_result_url(self):
        """
        Returns the URL to view the election results.

        Returns
        -------
        str
           The URL to view the election results.
        """
        return reverse('election:election-result', kwargs={'pk': self.pk})

    def has_finished(self):
        """
        Checks if the election has finished.

        Returns
        -------
        bool
            True if the current date and time is after the election end date, False otherwise.
        """
        return self.end_date <= timezone.now()


class Party(models.Model):
    """
    Represents a political party.

    Attributes
    ----------
    name : CharField
        The name of the party.
    description : TextField
        A detailed description of the party.
    creation_date : DateField
        The date when the party was created.

    Methods
    -------
    __str__()
        Returns the name of the party.
    """
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500, blank=True)
    creation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        """
        Returns the name of the party.

        Returns
        -------
        str
           The name of the party.
        """
        return self.name


class Candidate(models.Model):
    """
     Represents a candidate running in an election.

     Attributes
     ----------
     DEFAULT_PICTURE : str
         The default picture used for candidates.
     election : ForeignKey
         The election in which the candidate is running.
     name : CharField
         The name of the candidate.
     picture : ImageField
         The picture of the candidate.
     party : ForeignKey
         The party affiliation of the candidate.
     """
    DEFAULT_PICTURE = 'pictures/default_pic.jpg'

    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    picture = models.ImageField(default=DEFAULT_PICTURE, upload_to='pictures/', blank=True, null=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        """
        Returns the name of the candidate.

        Returns
        -------
        str
          The name of the candidate.
        """
        return self.name

    def get_absolute_url(self):
        """
        Returns the URL to view the candidate details.

        Returns
        -------
        str
           The URL to view the candidate details.
        """
        return reverse('election:candidate-detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        """
        Returns the URL to update the candidate details.

        Returns
        -------
        str
            The URL to update the candidate details.
        """
        return reverse('election:candidate-update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        """
        Returns the URL to delete the candidate.

        Returns
        -------
        str
            The URL to delete the candidate.
        """
        return reverse('election:candidate-delete', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """
        Saves the candidate instance to the database. Resizes the picture if necessary.

        Parameters
        ----------
        *args : list
           Variable length argument list.
        **kwargs : dict
           Arbitrary keyword arguments.
        """
        if not self.picture:
            self.picture = self.DEFAULT_PICTURE

        super(Candidate, self).save(*args, **kwargs)

        picture = Image.open(self.picture.path)
        if picture.height > 300 or picture.width > 300:
            output_size = (300, 300)
            picture.thumbnail(output_size)
            picture.save(self.picture.path)

    def vote_count(self):
        """
        Returns the number of votes received by the candidate.

        Returns
        -------
        int
            The number of votes received by the candidate.
        """
        return self.votes.count()


class Voter(models.Model):
    """
    Represents a voter registered for an election.

    Attributes
    ----------
    user : ForeignKey
       The user associated with the voter.
    election : ForeignKey
       The election in which the voter is registered.
    has_voted : BooleanField
       Indicates whether the voter has cast their vote.

    Methods
    -------
    __str__()
       Returns a string representation of the voter.
    clean()
       Validates the voter instance. Raises ValidationError if the election has already started.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        """
        Returns a string representation of the voter.

        Returns
        -------
        str
           A string representation of the voter.
        """
        return f"{self.user} can vote in {self.election}"

    def clean(self):
        """
        Validates the voter instance.

        Raises
        ------
        ValidationError
            If the current date and time is after the start date of the associated election.
        """
        if timezone.now() > self.election.start_date:
            raise ValidationError(f"You can't sign up for {self.election.title}, the election has already started")


class Vote(models.Model):
    """
    Represents a vote cast by a voter in an election.

    Attributes
    ----------
    election : ForeignKey
       The election in which the vote is cast.
    chosen_candidates : ManyToManyField
       The candidates chosen by the voter in the vote.
    timestamp : DateTimeField
       The date and time when the vote was cast.

    Methods
    -------
    __str__()
       Returns a string representation of the vote.
    chosen_candidate_count()
       Returns the number of candidates chosen in the vote.
    clean()
       Validates the vote instance. Raises ValidationError if constraints are violated.
    """
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    chosen_candidates = models.ManyToManyField(Candidate, related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the vote.

        Returns
        -------
        str
           A string representation of the vote.
        """
        candidates_str = ", ".join(candidate.name for candidate in self.chosen_candidates.all())
        return f"{candidates_str} in {self.election}"

    def chosen_candidate_count(self):
        """
        Returns the number of candidates chosen in the vote.

        Returns
        -------
        int
            The number of candidates chosen in the vote.
        """
        return self.chosen_candidates.count()

    def clean(self):
        """
        Validates the vote instance.

        Raises
        ------
        ValidationError
            If the number of chosen candidates exceeds the maximum allowed for the election,
            or if the vote is cast after the end date of the associated election.
        """
        if self.election.max_candidates_choice < self.chosen_candidate_count():
            raise ValidationError(f"You can only choose up to {self.election.max_candidates_choice} candidates")
        elif self.timestamp >= self.election.end_date:
            raise ValidationError(f"The {self.election.title} has already ended")


class SentEmail(models.Model):
    """
    Represents an email sent from one user to another.

    Attributes
    ----------
    sender : EmailField
        The email address of the sender.
    recipient : EmailField
        The email address of the recipient.
    subject : CharField
        The subject of the email.
    body : TextField
        The content of the email.
    reply_to : EmailField, optional
        The email address to which replies should be directed.
    timestamp : DateTimeField
        The date and time when the email was sent.
    """
    sender = models.EmailField()
    recipient = models.EmailField()
    subject = models.CharField(max_length=100)
    body = models.TextField()
    reply_to = models.EmailField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the sent email.

        Returns
        -------
        str
            A string representation of the sent email.
        """
        return f"From {self.reply_to} to {self.recipient}"
