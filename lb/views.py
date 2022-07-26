from time import time
from urllib import response
from django.http import (
    HttpRequest,
    JsonResponse,
    HttpResponseNotAllowed,
)
from lb.models import Submission, User
from django.forms.models import model_to_dict
from django.db.models import F
import json
from lb import utils
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods as method

def hello(req: HttpRequest):
    return JsonResponse({
        "code": 0,
        "msg": "hello"
    })

# TODO: Add HTTP method check
@method(["GET"])
def leaderboard(req: HttpRequest):
    return JsonResponse(
        utils.get_leaderboard(),
        safe=False,
    )


@method(["GET"])
def history(req: HttpRequest, qusername: str):
    # TODO: Complete `/history/<slug:username>` API
    try:
        quser = User.objects.filter(username=qusername).first()
    except:
        return JsonResponse(
            {
                'code': -1
            }
        )
    submissions = Submission.objects.filter(user=quser).order_by("time")
    return JsonResponse(
        {
            "code": 0,
            "submissions":[
                model_to_dict(sub, exclude=["id","user","avatar"])
                for sub in submissions
            ]
        }
    )
        
    


@method(["POST"])
@csrf_exempt
def submit(req: HttpRequest):
    info = json.loads(req.body)
    try:
        pusername = info["user"]
        pavatar = info["avatar"]
        pcontent = info["content"]
    except KeyError as ke:
        return JsonResponse(
            {
                "code": 1,
                "msg": "参数不全啊"    
            }
        )
        
    if len(pusername) > 255:
        return JsonResponse(
            {
                "code": -1,
                "msg": "用户名太长了啊"    
            }
        )        
    
    if len(pavatar) > 100 * 1024:
        return JsonResponse(
            {
                "code": -2,
                "msg": "图像太大了啊"    
            }
        ) 
        
    try:
        [pscore,psubs] = utils.judge(pcontent)
    except Exception as e:
        return JsonResponse(
            {
                "code": -3,
                "msg": "提交内容非法呜呜",
                "error": e,
                "content": pcontent,
            }
        ) 
    
    try:
        puser = User.objects.get(username=pusername)
    except Exception as e:
        puser = User.objects.create(username=pusername)
    
    Submission.objects.create(user=puser, avatar=pavatar, time=time(),score=pscore,subs=psubs)

    return JsonResponse({
        "code": 0,
        "msg": "提交成功",
        "data": {
            "leaderboard": utils.get_leaderboard()
        }
    })
    


@method(["POST"])
@csrf_exempt
def vote(req: HttpRequest):
    if 'User-Agent' not in req.headers \
            or 'requests' in req.headers['User-Agent']:
        return JsonResponse({
            "code": -1,
            "msg": "请求不合理啊"
        })
    try:
        puser = json.loads(req.body)["user"]
        user = User.objects.get(username=puser)
        user.votes += 1
        user.save()
        return JsonResponse({
            "code": 0,
            "data": {
                "leaderboard": utils.get_leaderboard()
            }
        })
    except Exception as e:
        return JsonResponse({
            "code": -1,
            "msg": "用户不存在呜呜",
            "error": e,
        })

    # TODO: Complete `/vote` API
