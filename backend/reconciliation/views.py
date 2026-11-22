
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.serializers.json import DjangoJSONEncoder

from reconciliation.models import Location
from reconciliation.services import reconcile_organization


@require_GET
def reconciliation_api(request):
    org_id = request.GET.get("org")

    if not org_id:
        return JsonResponse(
            {"error": "Organization is required"},
            status=400
        )

    if not Location.objects.filter(org_id=org_id).exists():
        return JsonResponse(
            {"error": "Organization not found"},
            status=404
        )

    results = reconcile_organization(org_id)

    return JsonResponse({
        "organization": org_id,
        "total_disagreements": len(results),
        "results": results,
    }, encoder=DjangoJSONEncoder)
