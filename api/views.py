from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from .models import User, Project, Verification, CarbonCredit, PanchayatVerificationEvidence
from .models import Transaction, CreditRequest, PendingBlockchainTransaction, CompanyNotification, Certificate
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.db.models import Sum
from .blockchain import mint_credits
from .blockchain import transfer_credits

from .ml_service import predict_carbon
# ===============================
# USER REGISTRATION
# ===============================

@csrf_exempt
def register_user(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        location = request.POST.get("location")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if User.objects.filter(email=email).exists():
            return HttpResponse("User already exists")

        User.objects.create(
            name=name,
            email=email,
            phone=phone,
            location=location,
            password=password,
            role=role.upper()
        )

        return HttpResponse("Registration successful")

    return render(request, "register.html")


# ===============================
# USER LOGIN
# ===============================

@csrf_exempt
def login_user(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        try:
            user = User.objects.get(email=email, password=password)

            if user.role.lower() != role:
                return HttpResponse("Role mismatch")

            # Redirect based on role
            if role == "farmer":
                return redirect("/api/farmer/dashboard")

            elif role == "panchayat":
                return redirect("/api/panchayat/dashboard")

            elif role == "company":
                return redirect("/api/marketplace")

            elif role == "admin":
                return redirect("/api/admin/dashboard")

        except User.DoesNotExist:
            return HttpResponse("Invalid login credentials")

    return render(request, "login.html")


# ===============================
# FARMER DASHBOARD
# ===============================

def farmer_dashboard(request):

    farmer = User.objects.filter(role="FARMER").first()

    if not farmer:
        return HttpResponse("Farmer account not found")

    projects = Project.objects.filter(farmer=farmer)

    total_projects = projects.count()

    total_area = projects.aggregate(
        total=Sum("plantation_area")
    )["total"] or 0

    credits = CarbonCredit.objects.filter(
        farmer=farmer
    ).aggregate(total=Sum("credits_amount"))["total"] or 0

    earnings = Transaction.objects.filter(
        seller=farmer
    ).aggregate(total=Sum("total_value"))["total"] or 0

    return render(request,"farmer/dashboard.html",{

        "farmer": farmer,
        "total_projects": total_projects,
        "total_area": total_area,
        "credits": credits,
        "earnings": earnings

    }) 
def farmer_projects(request):

    farmer = User.objects.filter(role="FARMER").first()

    projects = Project.objects.filter(farmer=farmer)

    return render(request, "farmer/projects.html", {
        "projects": projects
    })
@csrf_exempt
def submit_project(request):

    if request.method == "POST":

        project_name = request.POST.get("projectName")
        location = request.POST.get("location")
        coordinates = request.POST.get("coordinates")
        area = request.POST.get("area")
        species = request.POST.get("species")
        plantation_date = request.POST.get("date_planted")

        farmer = User.objects.filter(role="FARMER").first()

        Project.objects.create(
            farmer=farmer,
            project_name=project_name,
            location=location,
            plantation_area=area,
            species=species,
            plantation_date=plantation_date,
            description=coordinates
        )

        return redirect("/api/farmer/dashboard")

    return render(request, "farmer/submit_project.html")

def farmer_notifications(request):
    return render(request, "farmer/notifications.html")


# ===============================
# PANCHAYAT DASHBOARD
# ===============================

def panchayat_dashboard(request):

    projects = Project.objects.filter(status="PENDING_PANCHAYAT")

    return render(request, "panchayat/verification.html", {
        "projects": projects
    })


def panchayat_project_review(request, project_id):
    project = Project.objects.filter(id=project_id).first()
    if not project:
        return HttpResponse("Project not found")
    return render(request, "panchayat/project_review.html", {"project": project})


def panchayat_village_map(request):
    projects = Project.objects.all()
    return render(request, "panchayat/village_map.html", {"projects": projects})


def panchayat_local_farmers(request):
    farmers = User.objects.filter(role="FARMER")
    return render(request, "panchayat/local_farmers.html", {"farmers": farmers})


# ===============================
# PANCHAYAT APPROVE
# ===============================

@csrf_exempt
def panchayat_approve(request):

    if request.method == "POST":

        project_id = request.POST.get("projectId")
        lat = request.POST.get("latitude")
        lon = request.POST.get("longitude")
        image_file = ""  

        if 'evidence_image' in request.FILES:
            file = request.FILES['evidence_image']
            image_file = file.name

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return HttpResponse("Project not found")

        project.status = "PARTIALLY_VERIFIED"
        project.save()

        panchayat = User.objects.filter(role="PANCHAYAT").first()

        evidence = PanchayatVerificationEvidence.objects.create(
            project=project,
            officer=panchayat,
            image=image_file,
            latitude=float(lat) if lat else None,
            longitude=float(lon) if lon else None
        )

        Verification.objects.create(
            project=project,
            verified_by=panchayat,
            role="PANCHAYAT",
            status="APPROVED",
            comments="Verified by Panchayat"
        )

        return redirect("/api/panchayat/dashboard")

    return HttpResponse("Invalid request")


# ===============================
# PANCHAYAT REJECT
# ===============================

@csrf_exempt
def panchayat_reject(request):

    if request.method == "POST":

        project_id = request.POST.get("projectId")
        reject_reason = request.POST.get("rejectReason", "Rejected by Panchayat")

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return HttpResponse("Project not found")

        project.status = "REJECTED"
        project.save()

        panchayat = User.objects.filter(role="PANCHAYAT").first()

        Verification.objects.create(
            project=project,
            verified_by=panchayat,
            role="PANCHAYAT",
            status="REJECTED",
            comments=reject_reason,
            rejection_reason=reject_reason
        )

        return redirect("/api/panchayat/dashboard")

    return HttpResponse("Invalid request")


# ===============================
# ADMIN APPROVE PROJECT
# ===============================
@csrf_exempt
def admin_dashboard(request):

    projects = Project.objects.filter(status="PARTIALLY_VERIFIED").prefetch_related('panchayatverificationevidence_set', 'projectimage_set')
    rejected_projects = Project.objects.filter(status="REJECTED", verification__role="PANCHAYAT", verification__status="REJECTED").distinct()
    approved_projects = Project.objects.filter(status="FULLY_VERIFIED").prefetch_related('panchayatverificationevidence_set', 'projectimage_set')

    for p in projects:
        # Mock AI Confidence Score deterministically based on ID to avoid random jumps 
        base = 75 + (p.id * 7) % 25
        p.ai_score = base

    return render(request, "admin/approvals.html", {
        "projects": projects,
        "rejected_projects": rejected_projects,
        "approved_projects": approved_projects
    })

@csrf_exempt
def admin_approve(request):

    if request.method == "POST":

        project_id = request.POST.get("id")

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return HttpResponse("Project not found")

        project.status = "FULLY_VERIFIED"
        project.save()

        farmer = project.farmer

        # Temporary AI carbon estimation
        area = project.plantation_area

        # Generate feature vector for ML model
        features = [
            1,
            78.5,
            20.5,
            area*2,
            area*1.5,
            area*3.5,
            area*1.2,
            area*1.1,
            area*4.2,
            100,120,130,140,150,160,170,180,190,200,210,220,
            -10,
            -11,
            -12
        ]

        predicted_carbon = predict_carbon(features)

        credits = round(predicted_carbon, 2)

        # Simulated blockchain mint

        tx_hash = mint_credits(
            str(project.id),
            "0x123456789ABCDEF",  # farmer wallet address
            predicted_carbon,
            predicted_carbon,
            project.location
            )

        CarbonCredit.objects.create(
            project=project,
            farmer=farmer,
            credits_amount=credits,
            remaining_credits=credits,
            carbon_amount=predicted_carbon,
            blockchain_tx_hash=tx_hash
            )

        admin = User.objects.filter(role="ADMIN").first()

        Verification.objects.create(
            project=project,
            verified_by=admin,
            role="ADMIN",
            status="APPROVED",
            comments="Approved by Government"
        )

        return redirect("/api/admin/dashboard")

    return HttpResponse("Invalid request")

from django.db.models import Sum

def analytics_dashboard(request):

    total_projects = Project.objects.count()

    total_carbon = CarbonCredit.objects.aggregate(
        total=Sum("carbon_amount")
    )["total"] or 0

    total_tokens = CarbonCredit.objects.aggregate(
        total=Sum("credits_amount")
    )["total"] or 0

    total_transactions = Transaction.objects.count()
    recent_transactions = Transaction.objects.all().order_by('-timestamp')[:5]

    return render(request, "admin/analytics.html", {
        "total_projects": total_projects,
        "total_carbon": total_carbon,
        "total_tokens": total_tokens,
        "total_transactions": total_transactions,
        "recent_transactions": recent_transactions
    })
# ===============================
# ADMIN REJECT PROJECT
# ===============================
def map_view(request):

    return render(request,"admin/map.html")
@csrf_exempt
def admin_reject(request):

    if request.method == "POST":

        project_id = request.POST.get("id")
        reason = request.POST.get("reason", "Rejected by Government")
        notes = request.POST.get("notes", "")
        evidence = request.FILES.get("evidence")

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return HttpResponse("Project not found")

        project.status = "REJECTED"
        project.project_rejection_reason = reason
        project.project_rejection_notes = notes
        if evidence:
            project.rejection_evidence = evidence
        project.save()

        admin = User.objects.filter(role="ADMIN").first()

        Verification.objects.create(
            project=project,
            verified_by=admin,
            role="ADMIN",
            status="REJECTED",
            comments=f"{reason} - {notes}"[:200],
            rejection_reason=reason
        )

        return redirect("/api/admin/dashboard")

    return HttpResponse("Invalid request")
from .models import Transaction, CreditRequest

# ===============================
# MARKETPLACE DASHBOARD
# ===============================

def marketplace_dashboard(request):

    credits = CarbonCredit.objects.filter(remaining_credits__gt=0)

    return render(request, "company/marketplace.html", {
        "credits": credits
    })


# ===============================
# COMPANY PURCHASE REQUEST
# ===============================

@csrf_exempt
def request_farmer_credits(request):
    if request.method == "POST":
        company = User.objects.filter(role="COMPANY").first()
        if not company:
            return HttpResponse("Company account not found")

        credit_id = request.POST.get("credit_id")
        requested_credits = float(request.POST.get("credits", 0))
        company_name = request.POST.get("company_name", company.name)
        purpose = request.POST.get("purpose", "")
        proof_document = request.FILES.get("proof_document")

        if credit_id:
            batch = CarbonCredit.objects.filter(id=credit_id).first()
            if not batch or batch.remaining_credits < requested_credits:
                return HttpResponse("Not enough credits available in this batch")

            CreditRequest.objects.create(
                company=company,
                company_name=company_name,
                credits_requested=requested_credits,
                purpose=purpose,
                proof_document=proof_document,
                request_type="FARMER_REQUEST",
                project=batch.project,
                farmer=batch.farmer,
                status="PENDING"
            )

            CompanyNotification.objects.create(
                company=company,
                title="Credit Request Submitted",
                message=f"Request for {requested_credits} credits from {batch.project.project_name} submitted to Government for approval."
            )

            return redirect("/api/company/portfolio")

    return HttpResponse("Invalid request")

@csrf_exempt
def request_bulk_credits(request):
    if request.method == "POST":
        company = User.objects.filter(role="COMPANY").first()
        if not company:
            return HttpResponse("Company account not found")

        company_name = request.POST.get("company_name", company.name)
        credits_requested = request.POST.get("credits_requested", 0)
        purpose = request.POST.get("purpose", "")
        proof_document = request.FILES.get("proof_document")

        CreditRequest.objects.create(
            company=company,
            company_name=company_name,
            credits_requested=float(credits_requested),
            purpose=purpose,
            proof_document=proof_document,
            request_type="BULK_POOL_REQUEST",
            status="PENDING"
        )

        CompanyNotification.objects.create(
            company=company,
            title="Bulk Request Submitted",
            message=f"Your request for {credits_requested} credits has been sent to the Government."
        )

        return redirect("/api/company/portfolio")
    return HttpResponse("Invalid request")

# ===============================
# ADMIN CREDIT REQUESTS
# ===============================

def admin_credit_requests(request):
    requests = CreditRequest.objects.filter(status="PENDING").order_by('-submitted_at')
    stats = {
        "total": CreditRequest.objects.count(),
        "pending": CreditRequest.objects.filter(status="PENDING").count(),
        "approved": CreditRequest.objects.filter(status__in=["APPROVED", "ALLOCATED"]).count(),
        "rejected": CreditRequest.objects.filter(status="REJECTED").count()
    }
    return render(request, "admin/credit_requests.html", {"requests": requests, "stats": stats})

@csrf_exempt
def admin_approve_credit_request(request):
    if request.method == "POST":
        req_id = request.POST.get("id")
        try:
            req = CreditRequest.objects.get(id=req_id)
        except CreditRequest.DoesNotExist:
            return HttpResponse("Request not found")

        if req.status != "PENDING":
            return HttpResponse("Request already processed")

        price_per_credit = 25
        company = req.company

        if req.request_type == "FARMER_REQUEST":
            batch = CarbonCredit.objects.filter(project=req.project, farmer=req.farmer).first()
            if not batch or batch.remaining_credits < req.credits_requested:
                return HttpResponse("Not enough credits available in this batch")
            
            allocate = req.credits_requested
            batch.remaining_credits -= allocate
            batch.save()
            
            total_price = allocate * price_per_credit
            tx_hash = ""
            try:
                tx_hash = transfer_credits(batch.id, "0xBUYER_ADDRESS", allocate, price_per_credit)
            except Exception as e:
                print("Blockchain error:", e)
                PendingBlockchainTransaction.objects.create(project=batch.project, buyer=company, credits=allocate, status="PENDING")
            
            Transaction.objects.create(
                credit=batch, seller=batch.farmer, buyer=company, credits_transferred=allocate, price_per_credit=price_per_credit, total_value=total_price, blockchain_tx_hash=tx_hash if tx_hash else "PENDING_BLOCKCHAIN"
            )
            
        elif req.request_type == "BULK_POOL_REQUEST":
            needed = req.credits_requested
            batches = CarbonCredit.objects.filter(remaining_credits__gt=0).order_by('created_at')
            for batch in batches:
                if needed <= 0:
                    break
                available = batch.remaining_credits
                allocate = min(needed, available)
                
                batch.remaining_credits -= allocate
                batch.save()
                needed -= allocate
                
                total_price = allocate * price_per_credit
                tx_hash = ""
                try:
                    tx_hash = transfer_credits(batch.id, "0xBUYER_ADDRESS", allocate, price_per_credit)
                except Exception as e:
                    print("Blockchain error:", e)
                    PendingBlockchainTransaction.objects.create(project=batch.project, buyer=company, credits=allocate, status="PENDING")
                
                Transaction.objects.create(
                    credit=batch, seller=batch.farmer, buyer=company, credits_transferred=allocate, price_per_credit=price_per_credit, total_value=total_price, blockchain_tx_hash=tx_hash if tx_hash else "PENDING_BLOCKCHAIN"
                )

        req.status = "ALLOCATED"
        req.save()
        
        CompanyNotification.objects.create(
            company=company,
            title="Credit Request Approved",
            message=f"Government approved your request for {req.credits_requested} credits! It has been allocated."
        )
        
        return redirect("/api/admin/credit-requests")

    return HttpResponse("Invalid request")

@csrf_exempt
def admin_reject_credit_request(request):
    if request.method == "POST":
        req_id = request.POST.get("id")
        reason = request.POST.get("reason", "Rejected by Government")
        
        try:
            req = CreditRequest.objects.get(id=req_id)
        except CreditRequest.DoesNotExist:
            return HttpResponse("Request not found")

        req.status = "REJECTED"
        req.government_reason = reason
        req.save()
        
        CompanyNotification.objects.create(
            company=req.company,
            title="Credit Request Rejected",
            message=f"Your request for {req.credits_requested} credits was rejected. Reason: {reason}"
        )
        
        return redirect("/api/admin/credit-requests")

    return HttpResponse("Invalid request")

from django.http import FileResponse

def download_certificate(request, tx_hash):

    tx = Transaction.objects.filter(blockchain_tx_hash=tx_hash).first()
    if not tx:
        return HttpResponse("Certificate not found", status=404)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 700, "BlueCarbon Ledger")
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 650, "[ GOVERNMENT VERIFIED STAMP ]")
    
    c.setFont("Helvetica", 14)
    c.drawString(100, 600, f"Company Name: {tx.buyer.name}")
    c.drawString(100, 570, f"Project Name: {tx.credit.project.project_name}")
    c.drawString(100, 540, f"Credits Purchased: {tx.credits_transferred} tCO2e")
    c.drawString(100, 510, f"Date of Issue: {tx.timestamp.strftime('%Y-%m-%d')}")
    c.drawString(100, 480, f"Blockchain TX Hash: {tx.blockchain_tx_hash}")
    
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(100, 100, "Verified by Government Carbon Authority.")
    
    c.save()
    buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename=f"certificate_{tx_hash}.pdf")

# ===============================
# COMPANY PORTFOLIO
# ===============================

def company_portfolio(request):

    company = User.objects.filter(role="COMPANY").first()

    transactions = Transaction.objects.filter(buyer=company).order_by('-timestamp')
    requests = CreditRequest.objects.filter(company=company).order_by('-submitted_at')
    
    total_volume = transactions.aggregate(total=Sum('credits_transferred'))['total'] or 0

    return render(request, "company/portfolio.html", {
        "transactions": transactions,
        "requests": requests,
        "total_volume": total_volume
    })

def company_certificates(request):

    company = User.objects.filter(role="COMPANY").first()
    transactions = Transaction.objects.filter(buyer=company)

    return render(request, "company/certificates.html", {"transactions": transactions})
from django.http import JsonResponse
import csv

def project_map_data(request):
    import random
    projects = Project.objects.all()
    requests_data = CreditRequest.objects.all()

    data = []
    
    for p in projects:
        random.seed(p.id)
        ai_score = 75 + (p.id * 7) % 25
        data.append({
            "type": "project",
            "name": p.project_name,
            "farmer": p.farmer.name,
            "area": p.plantation_area,
            "credits": round(p.plantation_area * 1.5, 2),
            "status": p.status,
            "ai_score": ai_score,
            "lat": 20.5937 + (random.random() - 0.5) * 10,
            "lng": 78.9629 + (random.random() - 0.5) * 10
        })

    for r in requests_data:
        random.seed(r.id + 1000)
        data.append({
            "type": "request",
            "name": f"Request {r.id}: {r.company_name}",
            "credits": r.credits_requested,
            "status": r.status,
            "lat": 20.5937 + (random.random() - 0.5) * 15,
            "lng": 78.9629 + (random.random() - 0.5) * 15
        })

    return JsonResponse(data, safe=False)

def export_analytics(request):
    format_type = request.GET.get('format', 'csv')
    
    projects = list(Project.objects.values())
    transactions = list(Transaction.objects.values())
    requests_data = list(CreditRequest.objects.values())
    
    if format_type == 'json':
        data = {
            "projects": projects,
            "transactions": transactions,
            "credit_requests": requests_data
        }
        return JsonResponse(data, safe=False, encoder=DjangoJSONEncoder)
        
    elif format_type == 'pdf':
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, 800, "BlueCarbon Global Analytics Report")
        
        c.setFont("Helvetica", 14)
        c.drawString(50, 760, f"Total Projects Verified: {len(projects)}")
        c.drawString(50, 730, f"Total Transactions Processed: {len(transactions)}")
        c.drawString(50, 700, f"Total Credit Requests: {len(requests_data)}")
        
        c.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="bluecarbon_report.pdf")

    # Default CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bluecarbon_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Type', 'ID', 'Details', 'Status'])
    for p in projects:
        writer.writerow(['Project', p['id'], p['project_name'], p['status']])
    for t in transactions:
        writer.writerow(['Transaction', t['id'], t['credits_transferred'], 'Completed'])
    for r in requests_data:
        writer.writerow(['CreditRequest', r['id'], r['credits_requested'], r['status']])
    return response