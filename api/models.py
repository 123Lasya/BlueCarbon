from django.db import models
class User(models.Model):

    ROLE_CHOICES = [
        ('FARMER', 'Farmer'),
        ('PANCHAYAT', 'Panchayat'),
        ('ADMIN', 'Admin'),
        ('COMPANY', 'Company'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=255)
    location = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    wallet_address = models.CharField(
        max_length=255,
        default="0" )    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class Project(models.Model):

    STATUS_CHOICES = [
        ('PENDING_PANCHAYAT', 'Pending Panchayat'),
        ('PARTIALLY_VERIFIED', 'Partially Verified'),
        ('FULLY_VERIFIED', 'Fully Verified'),
        ('REJECTED', 'Rejected'),
        ('NEEDS_INFO', 'Needs Info'),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE)

    project_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    plantation_area = models.FloatField()
    species = models.CharField(max_length=200)

    plantation_date = models.DateField()

    description = models.TextField()

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='PENDING_PANCHAYAT'
    )

    project_rejection_reason = models.TextField(default="", blank=True)
    project_rejection_notes = models.TextField(default="", blank=True)
    rejection_evidence = models.FileField(upload_to='rejections/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name
class Verification(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    verified_by = models.ForeignKey(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=50)

    status = models.CharField(max_length=50)

    comments = models.TextField(blank=True)
    
    rejection_reason = models.TextField(default="", blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
class CarbonCredit(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)

    credits_amount = models.FloatField()
    remaining_credits = models.FloatField()
    carbon_amount = models.FloatField()

    blockchain_tx_hash = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
class CreditRequest(models.Model):

    REQUEST_TYPES = (
        ('FARMER_REQUEST', 'Farmer Request'),
        ('BULK_POOL_REQUEST', 'Bulk Pool Request'),
    )

    company = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, default="", blank=True)
    credits_requested = models.FloatField()
    purpose = models.TextField()
    proof_document = models.FileField(upload_to='proofs/', null=True, blank=True)
    
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES, default='BULK_POOL_REQUEST')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    farmer = models.ForeignKey(User, related_name="requested_farmer", on_delete=models.SET_NULL, null=True, blank=True)
    government_reason = models.TextField(default="", blank=True)

    credit_request_rejection_reason = models.TextField(default="", blank=True)
    credit_request_rejection_notes = models.TextField(default="", blank=True)

    status = models.CharField(max_length=50, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)
class Transaction(models.Model):

    credit = models.ForeignKey(CarbonCredit, on_delete=models.CASCADE)

    seller = models.ForeignKey(User, related_name='seller', on_delete=models.CASCADE)

    buyer = models.ForeignKey(User, related_name='buyer', on_delete=models.CASCADE)

    credits_transferred = models.FloatField()

    price_per_credit = models.FloatField()

    total_value = models.FloatField()

    blockchain_tx_hash = models.CharField(max_length=255, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
class Certificate(models.Model):

    company = models.ForeignKey(User, on_delete=models.CASCADE)

    credits_retired = models.FloatField()

    carbon_offset = models.FloatField()

    blockchain_tx_hash = models.CharField(max_length=255)

    certificate_file = models.CharField(max_length=255)

    issued_date = models.DateTimeField(auto_now_add=True)

class ProjectImage(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    image_file = models.CharField(max_length=255, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class PanchayatVerificationEvidence(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    officer = models.ForeignKey('User', on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class PendingBlockchainTransaction(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    credits = models.FloatField()
    status = models.CharField(max_length=50, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)


class CompanyNotification(models.Model):
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
