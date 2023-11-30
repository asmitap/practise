from django.shortcuts import get_object_or_404, render,redirect
from django.utils import timezone
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from .scrape import scrapdata
from sqlalchemy import create_engine
from django.conf import settings
from .models import Commodity
from .models import CustomUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login,logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import hashlib
import binascii
import os
from .serializers import *

def index(request):
    #return HttpResponse("welcome to index page")
    if request.method == 'GET':
        return render(request, "index.html")
    
    if request.method == 'POST':
        startdate = request.POST.get('startdate')
        initial_date = pd.Timestamp(startdate)
        enddate = request.POST.get('enddate')
        end_date = pd.Timestamp(enddate)
        scraped_data = scrapdata(initial_date, end_date)
        db = settings.POSTGRES_DATABASE # taken from .env file
        auth_db = f'{db}'
        engine = create_engine(auth_db)
        scraped_data.to_sql(Commodity._meta.db_table, engine, if_exists='append', index=False)
        return render(request, "index.html")

@csrf_exempt
def register(request):
    if request.method == 'GET':
        return render(request, "register.html")
    
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_hash = f"pbkdf2_sha256${600000}${binascii.hexlify(os.urandom(16)).decode('utf-8')}${binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), os.urandom(16), 600000, 32)).decode('utf-8')}"
        #formatted_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %z")
        # Get the current time in the appropriate time zone
        formatted_date_time = timezone.now()
        user = CustomUser(firstname=firstname, lastname=lastname, email=email, password=password_hash, last_login=formatted_date_time)
        user.save()
        return render(request, "login.html")
    
    return render(request, "register.html")

def login_view(request):
    if request.method=='POST':
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        if user:
            #print(user)
            login(request, user)
            return redirect('logout_page')
        else:
            return redirect('login_page')
    return render(request, "login.html")   

@csrf_exempt   
@login_required
def logout_view(request):
    if request.method=='POST':
        logout(request)
        return redirect('login_page')
    return render(request, "logout.html")

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserLoginView(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({
                    'token': token,
                    'msg': "Login Successfull",
                    'status': status.HTTP_200_OK
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': {'non_fields_errors': ['Email or Password is not Valid']},
                    'status': status.HTTP_404_NOT_FOUND
                }, status=status.HTTP_404_NOT_FOUND)






class CommodityViewSet(APIView):
    # def get(self,request):
    #     queryset = Commodity.objects.all()
    #     serializer = CommoditySerializer(queryset,many=True)

    #     return Response({"data":serializer.data, 'error':False})
    #     # return Response({
    #     #     'error':False,
    #     #     'data':serializer.data,
    #     #     'status':status.HTTP_200_OK
    #     # },status=status.HTTP_200_OK),

    def get(self, request,pk=None):
        if pk is not None:
            try:
                commodity = Commodity.objects.get(id=pk)
                serializer = CommoditySerializer(commodity)
                return Response(serializer.data)
            except:
                return Response('not found')
        else:
            # creating query set
            commodity = Commodity.objects.all()
            # converting query set to python dictionary or serializing query set
            serializer = CommoditySerializer(commodity, many=True)
            # serializer.data is the serialized data
            return Response(serializer.data)

    def post(self,request):
        #return Response ('THIS IS POST REQUEST')
        datas = request.data
        new_data = Commodity.objects.create(
            date = datas["date"],
            commodity_name = datas["commodity_name"],
            minimum_price = datas["minimum_price"],
            maximum_price = datas["maximum_price"],
            average_price = datas["average_price"])
        new_data.save()
        serializer = CommoditySerializer(new_data)
        # serializer.is_valid():
        return Response(serializer.data)
    
    def put(self, request, pk=None):
        commodity_object = Commodity.objects.get(id=pk)
        data = request.data
        commodity_object.date = data["date"]
        commodity_object.commodity_name = data["commodity_name"]
        commodity_object.minimum_price = data["minimum_price"]
        commodity_object.maximum_price = data["maximum_price"]
        commodity_object.average_price = data["average_price"]
        commodity_object.save()
        serializer = CommoditySerializer(commodity_object)
        return Response(serializer.data)

    def delete(self, pk=None):
        try:
            commodity = Commodity.objects.get(id=pk)
            commodity.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Commodity.DoesNotExist:
            return Response({'error': 'Commodity not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response

class CustomUserViewSet(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, pk=None):
       user = get_object_or_404(CustomUser.objects.all(), pk=pk)
       serializer = CustomUserSerializer(user)
       return Response(serializer.data)

    def post(self,request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, pk=None):
        try:
            unit = CustomUser.objects.get(id=pk)
            unit.delete()
            return Response({
                "error": False,
                "data": "CustomUser has been deleted.",
                "status": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({
                "error": True,
                "data": f"CustomUser not found with unit_id {pk} ",
                "status": status.HTTP_404_NOT_FOUND
            }, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, pk=None):
        user = get_object_or_404(CustomUser.objects.all(), pk=pk)
        serializer = CustomUserSerializer(user,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, pk=None):
        try:
            # made model instance
            user = CustomUser.objects.get(id=pk)
            # convert model instance to python dictionary
            serializer = CustomUserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "error": False,
                    "data": "CustomUser has been updated.",
                    "status": status.HTTP_201_CREATED
                }, status=status.HTTP_201_CREATED)
        except:
            return Response({
                "error": True,
                "data": f"CustomUser not found with user_id {id} ",
                "status": status.HTTP_404_NOT_FOUND
            }, status=status.HTTP_404_NOT_FOUND)
        



