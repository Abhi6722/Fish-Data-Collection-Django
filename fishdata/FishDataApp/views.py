from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import os
import io
import re
from .models import fishinfo
from PIL import Image
import boto3
from datetime import datetime
import pytz
import numpy as np
import cv2
def clear_blur_classify(image):
    image_bytes = image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply average blur
    ksize = 5
    average_blur = cv2.blur(gray_image, (ksize, ksize))
    
    # Convert to float32
    average_blur = average_blur.astype(np.float32)

    # Apply Sobel operator
    sobelx = cv2.Sobel(average_blur, cv2.CV_32F, 1, 0, ksize=3)
    sobely = cv2.Sobel(average_blur, cv2.CV_32F, 0, 1, ksize=3)
    sobel_edges = cv2.magnitude(sobelx, sobely)
    variance = np.var(sobel_edges)
    
    threshold = 100
    if variance < threshold:
        return False  # Blur image
    else:
        return True  # Clear image


# Create your views here.
class insert_fish_details(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def current_datetime(self, type, label, format):
        IST = pytz.timezone('Asia/Kolkata')
        datetime_utc = datetime.now(IST)
        datetime_string = str(datetime_utc.strftime('%Y%m%d%H%M%S%f'))[:-3] + '_' + type + '_' + label + '.' + format
        #datetime_object = datetime_utc.strftime('%Y-%m-%d %H:%M:%S:%f')
    
        return datetime_string #datetime_object, datetime_string
    
    def post(self, request):
        
        image = request.data.get('ImageFile')
        type = request.data.get('type')
        label = request.data.get('labels')
        if clear_blur_classify(image):
            return Response({'message':'Image is Blur, click again'}, status = status.HTTP_200_OK)
        img = Image.open(image)
        format = img.format
        
        type = type.strip().lower()
        label = label.strip().lower()
        format = format.lower()
        
        type = re.sub(' +', ' ',type)
        label = re.sub(' +', ' ',label)
        
        access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        access_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN')
        
        client = boto3.resource('s3',
                        aws_access_key_id = access_key,
                        aws_secret_access_key = access_secret_key,
                        region_name = 'ap-south-1')
    
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format)
        img_byte_arr = img_byte_arr.getvalue()
        # Uploading to S3
        # entry_datetime , image_name = self.current_datetime(type, label, format)
        image_name = self.current_datetime(type, label, format)
        object = client.Object(bucket_name, f'{type}/{label}/{image_name}')
        object.put(Body=img_byte_arr)
        
        Fish_Info = fishinfo.objects.create(
                    image_url = f'https://{AWS_S3_CUSTOM_DOMAIN}/{type}/{label}/{image_name}',
                    type = type,
                    labels = label,
                    description = request.data.get('description') if request.data.get('description') else None
                )
        Fish_Info.save()
        return Response({'message':'Data inserted successfully'}, status = status.HTTP_200_OK)

