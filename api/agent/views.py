from django.http import JsonResponse, HttpResponse
from .actions import pre_compensation
#from api.models import Agence
from users.models import Transfert, Transaction, Agent
#from api.serializers import TransfertFullSerializer
#from users.serializers import PreTransactionFullSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import json


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def demande_compensation(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            agent = Agent.objects.get(id=data['agent'])
            result = pre_compensation(agent, data)
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)
