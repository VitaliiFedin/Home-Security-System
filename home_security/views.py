from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .decorators import admin_required
from .forms import (
    ApartmentForm,
    BuildingForm,
    CustomUserCreationForm,
    EntranceForm,
    LoginForm,
)
from .models import Apartment, Building, Entrance, Event
from .serializers import (
    ApartmentSerializer,
    BuildingSerializer,
    EntranceSerializer,
    LoginSerializer,
    UserRegistrationSerializer,
)


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_event(user, "Registered", f"User {user} is registered")
            messages.success(request, "Registration successful. You can now login.")
            return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                log_event(request.user, "Log IN", f"User {request.user} log in")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def user_logout(request):
    user_to_logout = request.user
    logout(request)
    log_event(user_to_logout, "Log OUT", f"User {user_to_logout} log out")
    return redirect("login")


@login_required
def dashboard_admin(request):
    if request.user.is_admin():
        buildings = Building.objects.all().prefetch_related("entrances__apartments")
    elif request.user.is_manager():
        buildings = Building.objects.filter(manager=request.user).prefetch_related(
            "entrances__apartments"
        )
    else:  # Guard
        guarded_entrances = (
            Entrance.objects.filter(guard=request.user)
            .select_related("building")
            .prefetch_related("apartments")
        )
        buildings = (
            Building.objects.filter(entrances__in=guarded_entrances)
            .distinct()
            .prefetch_related("entrances__apartments")
        )

    context = {
        "buildings": buildings,
        "is_guard": not (request.user.is_admin() or request.user.is_manager()),
        "guarded_entrances": (
            guarded_entrances
            if not (request.user.is_admin() or request.user.is_manager())
            else None
        ),
    }
    return render(request, "dashboard.html", context)


@login_required
def home(request):
    return render(request, "home.html")


@login_required
@admin_required
def add_building(request):
    if request.method == "POST":
        form = BuildingForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data.get("number")
            manager = form.cleaned_data.get("manager")

            # Check if a building with the same number already exists
            if Building.objects.filter(number=number).exists():
                messages.error(
                    request, f"Building with number {number} already exists."
                )
            else:
                building = form.save()
                log_event(
                    request.user, "Added Building", f"Building {building.number} added"
                )
                messages.success(
                    request,
                    f"Successfully added building {number} with manager {manager}",
                )
                return redirect(
                    "add-building"
                )  # Redirect to a relevant page after successful addition
        else:
            messages.error(
                request, "Error adding building. Make sure number is greater than 0."
            )
    else:
        form = BuildingForm()
    return render(request, "add-building.html", {"form": form})


@login_required
@admin_required
def delete_building(request, number):
    building = get_object_or_404(Building, number=number)
    if request.method == "POST":
        # Delete the building
        building.delete()
        log_event(
            request.user, "Deleted Building", f"Building {building.number} deleted"
        )
        messages.success(
            request,
            "Successfully deleted building ",
        )
        # Redirect to a success page or another appropriate URL
        return redirect(
            "dashboard-admin"
        )  # Example: Redirect to dashboard after deletion

    # Handle other HTTP methods (GET, etc.) gracefully if needed
    return redirect("dashboard-admin")  # Redirect to dashboard if not a POST request


@login_required
@admin_required
def edit_building(request, number):
    building = get_object_or_404(Building, number=number)

    if request.method == "POST":
        form = BuildingForm(request.POST, instance=building)

        if form.is_valid():
            new_number = form.cleaned_data["number"]
            if (
                new_number != number
                and Building.objects.filter(number=new_number).exists()
            ):
                messages.error(
                    request, f"Building with number {new_number} already exists."
                )
            else:
                updated_building = form.save()
                log_event(
                    request.user,
                    "Edited Building",
                    f"Building {number} edited to {updated_building.number}",
                )
                messages.success(
                    request, f"Building {number} has been updated successfully."
                )
                return redirect("dashboard-admin")
        else:
            messages.error(
                request, "Error updating building. Please check the details."
            )
    else:
        form = BuildingForm(instance=building)
    return render(request, "edit-building.html", {"form": form, "building": building})


@login_required
@admin_required
def add_entrance(request):
    if request.method == "POST":
        form = EntranceForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data.get("number")
            guard = form.cleaned_data.get("guard")
            building = form.cleaned_data.get("building")
            if Entrance.objects.filter(number=number, building=building).exists():
                messages.error(request, "Entrance already exists.")
            else:
                entrance = form.save()
                log_event(
                    request.user,
                    "Added Entrance",
                    f"Entrance {number} added with guard {guard} for {building}",
                )
                messages.success(
                    request,
                    f"Successfully added  entrance  {number} with guard {guard} for {building}",
                )
        else:
            messages.error(request, "Error")
    else:
        form = EntranceForm()
    return render(request, "add-entrance.html", {"form": form})


@login_required
def edit_entrance(request, building_number):
    if request.user.is_admin():
        building = get_object_or_404(Building, number=building_number)
    elif request.user.is_manager():
        building = get_object_or_404(
            Building, number=building_number, manager=request.user
        )
    entrances = building.entrances.all()
    if request.method == "POST":
        print("POST data:", request.POST)
        entrance_number = request.POST.get("entrance_number")
        entrance = get_object_or_404(
            Entrance, number=entrance_number, building=building
        )

        # Create a new dictionary with the correct field names
        form_data = {
            "number": request.POST.get(f"{entrance_number}-number"),
            "guard": request.POST.get(f"{entrance_number}-guard"),
            "building": request.POST.get(f"{entrance_number}-building"),
        }

        form = EntranceForm(form_data, instance=entrance)
        if form.is_valid():
            try:
                # Check if an entrance with the same number already exists for this building
                existing_entrance = (
                    Entrance.objects.filter(
                        number=form.cleaned_data["number"], building=building
                    )
                    .exclude(id=entrance.id)
                    .first()
                )

                if existing_entrance:
                    messages.error(
                        request,
                        f"An entrance with number {form.cleaned_data['number']} already exists for this building.",
                    )
                else:
                    form.save()
                    log_event(
                        request.user,
                        "Edited Entrance",
                        f"Entrance {entrance_number} has been updated successfully for {building}",
                    )
                    messages.success(
                        request,
                        f"Entrance {entrance_number} has been updated successfully.",
                    )
            except IntegrityError:
                messages.error(
                    request,
                    f"An entrance with number {form.cleaned_data['number']} already exists for this building.",
                )
        else:
            print("Form errors:", form.errors)
            messages.error(
                request,
                "Error updating Entrance.",
            )
        return redirect("edit-entrance", building_number=building_number)
    entrance_forms = [
        EntranceForm(instance=entrance, prefix=str(entrance.number))
        for entrance in entrances
    ]
    context = {
        "building": building,
        "entrance_forms": entrance_forms,
    }
    return render(request, "edit-entrance.html", context)


@login_required
@admin_required
def delete_entrance(request, number):
    entrance = get_object_or_404(Entrance, number=number)
    if request.method == "POST":
        # Delete the building
        entrance.delete()
        log_event(
            request.user,
            "Deleted Entrance",
            f"Entrance {number} has been deleted",
        )
        # Redirect to a success page or another appropriate URL
        return redirect(
            "dashboard-admin"
        )  # Example: Redirect to dashboard after deletion

    # Handle other HTTP methods (GET, etc.) gracefully if needed
    return redirect("dashboard-admin")  # Redirect to dashboard if not a POST request


@login_required
@admin_required
def add_apartment(request):
    if request.method == "POST":
        form = ApartmentForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data.get("number")
            entrance = form.cleaned_data.get("entrance")
            if Apartment.objects.filter(number=number, entrance=entrance).exists():
                messages.error(request, "Apartment already exists.")
            else:
                apartment = form.save()
                log_event(
                    request.user,
                    "Added Apartment",
                    f"Apartment {number} has been added for {apartment.entrance} in {apartment.entrance.building}",
                )
                messages.success(
                    request,
                    f"Successfully added { apartment} for {entrance}",
                )
        else:
            messages.error(request, "Error")
    else:
        form = ApartmentForm()
    return render(request, "add-apartment.html", {"form": form})


@login_required
@admin_required
def edit_apartment(request, building_number):
    building = get_object_or_404(Building, number=building_number)
    apartments = Apartment.objects.filter(entrance__building=building).order_by(
        "entrance__number", "number"
    )

    if request.method == "POST":
        apartment_id = request.POST.get("apartment_id")
        apartment = get_object_or_404(
            Apartment, id=apartment_id, entrance__building=building
        )

        form_data = {
            "number": request.POST.get(f"{apartment_id}-number"),
            "owner": request.POST.get(f"{apartment_id}-owner"),
            "entrance": request.POST.get(f"{apartment_id}-entrance"),
        }

        form = ApartmentForm(form_data, instance=apartment)
        if form.is_valid():
            try:
                # Check for existing apartment with the same number in this entrance
                existing_apartment = (
                    Apartment.objects.filter(
                        number=form.cleaned_data["number"],
                        entrance=form.cleaned_data["entrance"],
                    )
                    .exclude(id=apartment.id)
                    .first()
                )

                if existing_apartment:
                    messages.error(
                        request,
                        f"An apartment with number {form.cleaned_data['number']} already exists in this entrance.",
                    )
                else:
                    form.save()
                    log_event(
                        request.user,
                        "Edited Apartment",
                        f"Apartment {apartment.number} has been edited",
                    )
                    messages.success(
                        request,
                        f"Apartment {apartment.number} has been updated successfully.",
                    )
            except IntegrityError:
                messages.error(
                    request,
                    f"An apartment with number {form.cleaned_data['number']} already exists in this entrance.",
                )
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Error updating Apartment.")

        return redirect("edit-apartment", building_number=building_number)

    apartment_forms = [
        ApartmentForm(instance=apartment, prefix=str(apartment.id))
        for apartment in apartments
    ]

    context = {
        "building": building,
        "apartment_forms": apartment_forms,
    }
    return render(request, "edit-apartment.html", context)


@login_required
@admin_required
def delete_apartment(request, number):
    apartment = get_object_or_404(Apartment, number=number)
    if request.method == "POST":
        # Delete the building
        apartment.delete()
        log_event(
            request.user,
            "Deleted Apartment",
            f"Apartment {number} has been deleted",
        )
        # Redirect to a success page or another appropriate URL
        return redirect(
            "dashboard-admin"
        )  # Example: Redirect to dashboard after deletion

    # Handle other HTTP methods (GET, etc.) gracefully if needed
    return redirect("dashboard-admin")  # Redirect to dashboard if not a POST request


def log_event(user, action, details=""):
    Event.objects.create(user=user, action=action, details=details)


@login_required
@admin_required
def view_event_log(request):
    logs = Event.objects.all().order_by("-timestamp")
    return render(request, "event-log.html", {"logs": logs})


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [IsAuthenticated]


class EntranceViewSet(viewsets.ModelViewSet):
    queryset = Entrance.objects.all()
    serializer_class = EntranceSerializer


class ApartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer


class UserRegistrationViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Registration successful"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                log_event(request.user, "Log IN", f"User {request.user} log in")
                return Response(
                    {"message": "Login successful"}, status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        user_to_logout = request.user
        logout(request)
        log_event(user_to_logout, "Log OUT", f"User {user_to_logout} log out")
        return Response({"message": "Logout successfully"}, status=status.HTTP_200_OK)
