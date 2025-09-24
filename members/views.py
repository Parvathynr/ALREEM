from datetime import datetime, timedelta
import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Member, Plan
from django.views.decorators.csrf import csrf_exempt

from .models import TrainerStaff
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from payments.models import Invoice   # import your Invoice model


@csrf_exempt
def add_member(request):
    if request.method == 'POST':
        data = request.POST

        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        age = data.get('age')
        weight = data.get('weight')
        blood_group = data.get('blood_group')
        joining = data.get('joining_day')
        status = data.get('status')
        location = data.get('location')
        profession = data.get('profession')
        fee = data.get('fee')
        paid = data.get('paid')  
        due = data.get('due')
        leave = data.get('leave')
        rejoin = data.get('rejoin')
        plan = Plan.objects.get(id=data.get('plan'))

        joining_date = datetime.strptime(joining, "%Y-%m-%d").date()
        expiry = joining_date + timedelta(days=plan.duration_days)

        leave_date = None
        rejoin_date = None
        paused_days = 0
        if leave and rejoin:
            leave_date = datetime.strptime(leave, "%Y-%m-%d").date()
            rejoin_date = datetime.strptime(rejoin, "%Y-%m-%d").date()
            paused_days = (rejoin_date - leave_date).days

        expire_date = expiry + timedelta(days=paused_days)

        member = Member.objects.create(
            name=name,
            phone=phone,
            email=email,
            age=age,
            weight=weight,
            blood_group=blood_group,
            joining_date=joining_date,
            expire_date=expire_date,
            status=status,
            plan_type=plan,
            location=location,
            profession=profession,
            total_fee=fee,
            due_amount=due,
            leave_date=leave_date,
            rejoin_date=rejoin_date
        )


        invoice_number = f"INV-{member.id:05d}"  # Example format: INV-00001
        invoice = Invoice.objects.create(
            member=member,
            invoice_number=invoice_number,
            total_amount=fee,
            paid_amount=paid,
            due_amount=due,
            payment_method=data.get("payment_method", "cash")
        )


        receipt_dir = os.path.join(settings.MEDIA_ROOT, "receipts")
        os.makedirs(receipt_dir, exist_ok=True)
        file_path = os.path.join(receipt_dir, f"receipt_{invoice.invoice_number}.pdf")

        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Membership Receipt", styles["Title"]))
        elements.append(Spacer(1, 12))

      
        data_table = [
            ["Field", "Details"],
            ["Invoice No", invoice.invoice_number],
            ["Name", member.name],
            ["Phone", member.phone],
            ["Email", member.email],
            ["Plan", f"{plan.name} ({plan.duration_days} days)"],
            ["Joining Date", member.joining_date.strftime("%Y-%m-%d")],
            ["Expiry Date", member.expire_date.strftime("%Y-%m-%d")],
            ["Total Fee", str(invoice.total_amount)],
            ["Paid Amount", str(invoice.paid_amount)],
            ["Due Amount", str(invoice.due_amount)],
        ]

        table = Table(data_table, colWidths=[120, 300])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Thank you for joining with us!", styles['Heading3']))
        doc.build(elements)

        pdf_url = f"{settings.MEDIA_URL}receipts/receipt_{invoice.invoice_number}.pdf"

        return JsonResponse({
            'message': 'Successfully added new member',
            'member_id': member.id,
            'invoice_number': invoice.invoice_number,
            'expiry': expire_date.strftime("%Y-%m-%d"),
            'receipt_url': pdf_url
        }, status=200)

    return JsonResponse({'message': 'Invalid request method'}, status=405)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import os
from django.conf import settings
from .models import Member, Plan

@csrf_exempt
def update_member(request, id):
    if request.method == "POST" or request.method == "PUT":
        member = get_object_or_404(Member, id=id)

        data = request.POST

        # Update basic fields
        member.name = data.get("name", member.name)
        member.phone = data.get("phone", member.phone)
        member.email = data.get("email", member.email)
        member.age = data.get("age", member.age)
        member.weight = data.get("weight", member.weight)
        member.blood_group = data.get("blood_group", member.blood_group)
        member.status = data.get("status", member.status)
        member.location = data.get("location", member.location)
        member.profession = data.get("profession", member.profession)
        member.total_fee = data.get("fee", member.total_fee)
        member.due_amount = data.get("due", member.due_amount)

        # Update plan if provided
        plan_id = data.get("plan")
        if plan_id:
            member.plan_type = Plan.objects.get(id=plan_id)

        # Handle joining date
        joining = data.get("joining_day")
        if joining:
            member.joining_date = datetime.strptime(joining, "%Y-%m-%d").date()

        # Handle leave & rejoin
        leave = data.get("leave")
        rejoin = data.get("rejoin")
        paused_days = 0
        if leave and rejoin:
            member.leave_date = datetime.strptime(leave, "%Y-%m-%d").date()
            member.rejoin_date = datetime.strptime(rejoin, "%Y-%m-%d").date()
            paused_days = (member.rejoin_date - member.leave_date).days
        else:
            member.leave_date = None
            member.rejoin_date = None

        # Recalculate expiry
        if member.joining_date and member.plan_type:
            expiry = member.joining_date + timedelta(days=member.plan_type.duration_days)
            member.expire_date = expiry + timedelta(days=paused_days)

        member.save()

        # 🔹 Regenerate PDF
        receipt_dir = os.path.join(settings.MEDIA_ROOT, "receipts")
        os.makedirs(receipt_dir, exist_ok=True)
        file_path = os.path.join(receipt_dir, f"receipt_{member.id}.pdf")

        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Membership Receipt (Updated)", styles["Title"]))
        elements.append(Spacer(1, 12))

        data_table = [
            ["Field", "Details"],
            ["Name", member.name],
            ["Phone", member.phone],
            ["Email", member.email],
            ["Plan", f"{member.plan_type.name} ({member.plan_type.duration_days} days)"] if member.plan_type else "",
            ["Joining Date", member.joining_date.strftime("%Y-%m-%d") if member.joining_date else ""],
            ["Expiry Date", member.expire_date.strftime("%Y-%m-%d") if member.expire_date else ""],
            ["Total Fee", str(member.total_fee)],
            ["Due Amount", str(member.due_amount)],
        ]

        table = Table(data_table, colWidths=[120, 300])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Thank you for staying with us!", styles['Heading3']))

        doc.build(elements)

        pdf_url = f"{settings.MEDIA_URL}receipts/receipt_{member.id}.pdf"

        return JsonResponse({
            "message": "Member updated successfully",
            "member_id": member.id,
            "expiry": member.expire_date.strftime("%Y-%m-%d") if member.expire_date else None,
            "receipt_url": pdf_url
        }, status=200)

    return JsonResponse({"message": "Invalid request method"}, status=405)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Member
import json

@csrf_exempt
def delete_member(request, id):
    if request.method == 'DELETE':
        try:
            member = Member.objects.get(id=id)
            member.delete()
            return JsonResponse({'message': 'Member deleted successfully'}, status=200)
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Member not found'}, status=404)

    return JsonResponse({'message': 'Invalid request method'}, status=405)

@csrf_exempt
def view_members(request):
    if request.method == 'GET':
        members = Member.objects.all().values(
            'id',
            'name',
            'phone',
            'email',
            'age',
            'weight',
            'blood_group',
            'joining_date',
            'expire_date',
            'status',
            'plan_type',  
            'location',
            'profession',
            'total_fee',
            'due_amount',
            'leave_date',
            'rejoin_date'
        )
        return JsonResponse(list(members), safe=False, status=200)

    return JsonResponse({'message': 'Invalid request method'}, status=405)


@csrf_exempt
def add_plan(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            name = data.get("name")
            duration_days = data.get("duration_days")
            price = data.get("price")

            # Validate inputs
            if not name or not duration_days:
                return JsonResponse({"error": "Name and duration_days are required"}, status=400)

            # Create Plan
            plan = Plan.objects.create(
                name=name,
                duration_days=duration_days,
                price=price if price else None
            )

            return JsonResponse({
                "message": "Plan created successfully",
                "plan": {
                    "id": plan.id,
                    "name": plan.name,
                    "duration_days": plan.duration_days,
                    "price": str(plan.price) if plan.price else None
                }
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def view_plans(request):
    if request.method == "GET":
        plans = [
            {
                "id": plan.id,
                "name": plan.name,
                "duration_days": plan.duration_days,
                "price": str(plan.price) if plan.price else None
            }
            for plan in Plan.objects.all()
        ]
        return JsonResponse({"plans": plans})
    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def edit_plan(request, plan_id):
    try:
        plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        return JsonResponse({"error": "Plan not found"}, status=404)

    if request.method == "GET":
        # Return plan details
        return JsonResponse({
            "id": plan.id,
            "name": plan.name,
            "duration_days": plan.duration_days,
            "price": str(plan.price) if plan.price else None
        })

    elif request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            plan.name = data.get("name", plan.name)
            plan.duration_days = data.get("duration_days", plan.duration_days)
            plan.price = data.get("price", plan.price)
            plan.save()
            return JsonResponse({
                "message": "Plan updated successfully",
                "plan": {
                    "id": plan.id,
                    "name": plan.name,
                    "duration_days": plan.duration_days,
                    "price": str(plan.price) if plan.price else None
                }
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
# Delete a plan
@csrf_exempt
def delete_plan(request, plan_id):
    if request.method == "DELETE":
        try:
            plan = Plan.objects.get(id=plan_id)
            plan.delete()
            return JsonResponse({"message": "Plan deleted successfully"}, status=200)
        except Plan.DoesNotExist:
            return JsonResponse({"error": "Plan not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)
@csrf_exempt
def add_trainer_staff(request):
    if request.method == "POST":
        # Directly take uploaded file
        profile_picture = request.FILES.get("profile_picture")

        # Collect form data
        name = request.POST.get("name")
        phone_number = request.POST.get("phone")
        email = request.POST.get("email")
        location = request.POST.get("location")
        trainer_or_staff = request.POST.get("trainer_or_staff")
        age = request.POST.get("age")
        weight = request.POST.get("weight")
        blood_group = request.POST.get("blood_group")

        # Save to DB (Django handles file saving)
        trainer_staff = TrainerStaff.objects.create(
            profile_picture=profile_picture,
            user=name,
            phone_number=phone_number,
            email=email,
            location=location,
            trainer_or_staff=trainer_or_staff,
            age=age,
            weight=weight,
            blood_group=blood_group,
        )

        return JsonResponse({
            "status": "success",
            "message": "Trainer/Staff added successfully!",
            "id": trainer_staff.id
        })

    return JsonResponse({"status": "failed", "message": "Invalid request method"})



def view_all_trainers_staff(request):
    if request.method == "GET":
        trainers_staff = TrainerStaff.objects.all().values(
            "id",
            "user",
            "phone_number",
            "email",
            "location",
            "trainer_or_staff",
            "age",
            "weight",
            "blood_group",
            "profile_picture"
        )
        
        # Convert QuerySet to list
        data = list(trainers_staff)

        # Add full URL for profile pictures
        for item in data:
            if item["profile_picture"]:
                item["profile_picture"] = request.build_absolute_uri("/media/" + item["profile_picture"])

        return JsonResponse({"status": "success", "data": data}, safe=False)

    return JsonResponse({"status": "failed", "message": "Invalid request method"})


def view_single_trainer_staff(request, id):
    if request.method == "GET":
        trainer_staff = get_object_or_404(TrainerStaff, id=id)

        data = {
            "id": trainer_staff.id,
            "user": trainer_staff.user,
            "phone_number": trainer_staff.phone_number,
            "email": trainer_staff.email,
            "location": trainer_staff.location,
            "trainer_or_staff": trainer_staff.trainer_or_staff,
            "age": trainer_staff.age,
            "weight": trainer_staff.weight,
            "blood_group": trainer_staff.blood_group,
            "profile_picture": request.build_absolute_uri(trainer_staff.profile_picture.url) if trainer_staff.profile_picture else None
        }

        return JsonResponse({"status": "success", "data": data})

    return JsonResponse({"status": "failed", "message": "Invalid request method"})





@csrf_exempt
def edit_trainer_staff(request, id):
    if request.method == "POST" or request.method == "PUT":
        trainer_staff = get_object_or_404(TrainerStaff, id=id)

        # Update fields only if provided
        trainer_staff.user = request.POST.get("user", trainer_staff.user)
        trainer_staff.phone_number = request.POST.get("phone_number", trainer_staff.phone_number)
        trainer_staff.email = request.POST.get("email", trainer_staff.email)
        trainer_staff.location = request.POST.get("location", trainer_staff.location)
        trainer_staff.trainer_or_staff = request.POST.get("trainer_or_staff", trainer_staff.trainer_or_staff)
        trainer_staff.age = request.POST.get("age", trainer_staff.age)
        trainer_staff.weight = request.POST.get("weight", trainer_staff.weight)
        trainer_staff.blood_group = request.POST.get("blood_group", trainer_staff.blood_group)

        if "profile_picture" in request.FILES:
            trainer_staff.profile_picture = request.FILES["profile_picture"]

        trainer_staff.save()

        return JsonResponse({"status": "success", "message": "Trainer/Staff updated successfully!"})

    return JsonResponse({"status": "failed", "message": "Invalid request method"})


@csrf_exempt
def delete_trainer_staff(request, pk):
    if request.method == "DELETE" or request.method == "POST":
        trainer_staff = get_object_or_404(TrainerStaff, pk=pk)
        trainer_staff.delete()
        return JsonResponse({"status": "success", "message": "Trainer/Staff deleted successfully!"})

    return JsonResponse({"status": "failed", "message": "Invalid request method"})