
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import TaskAnalyzer

@csrf_exempt
def analyze_tasks(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tasks = data.get('tasks', [])
            strategy = data.get('strategy', 'smart')
            
            # This calls the class you just created!
            analyzer = TaskAnalyzer(tasks, strategy)
            sorted_tasks = analyzer.analyze()
            
            return JsonResponse({'status': 'success', 'data': sorted_tasks})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

def suggest_tasks(request):
    return JsonResponse({'message': 'Use the analyze endpoint'})