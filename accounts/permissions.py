from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    message = "Only administrators are allowed to perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.ADMIN
        )


class IsDoctor(BasePermission):
    message = "Only doctors are allowed to perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.DOCTOR
        )


class IsPatient(BasePermission):
    message = "Only patients are allowed to perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.PATIENT
        )


class IsReceptionist(BasePermission):
    message = "Only receptionists are allowed to perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.RECEPTIONIST
        )



class IsAdmin(BasePermission):
    message = "Only administrators are allowed to perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.ADMIN
        )