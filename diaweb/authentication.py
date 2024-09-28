from rest_framework.permissions import IsAuthenticated


class IsAuthenticatedPostLeak(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return super(IsAuthenticatedPostLeak, self).has_permission(request, view)
