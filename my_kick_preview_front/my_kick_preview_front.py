"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import os
import io
import base64

from PIL import Image
import reflex as rx
from rxconfig import config
import boto3
from dotenv import load_dotenv
import requests


load_dotenv()

aws_access_key = os.getenv('AWS_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_SECRET_KEY')
host_address = os.getenv('HOST_ADDRESS')

class State(rx.State):
    """The app state."""
    image = ""
    audio = ""
    title = ""
    processing = False
    
    def get_contents_metadata(self):
        url = f'{host_address}:5000/api/get-content'
        # ヘッダーの設定
        headers = {
            'Accept': 'application/json'
        }

        # GETリクエストを送信
        response = requests.get(url, headers=headers)

        # レスポンスのステータスコードと内容を確認
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def generate_presigned_url(self, uri):
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name='ap-northeast-1')
        s3_parts = uri.replace("s3://", "").split("/",1)
        bucket_name = s3_parts[0]
        object_key = s3_parts[1]
        response = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=600
        )
        return response
    
    def get_data(self, uri):
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name='ap-northeast-1')
        s3_parts = uri.replace("s3://", "").split("/",1)
        bucket_name = s3_parts[0]
        object_key = s3_parts[1]
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        return response


    def get_contents(self):
        self.processing = True
        yield
        contents_metadata = self.get_contents_metadata()
        title = contents_metadata['title']
        image_uri = contents_metadata['image_uri']
        audio_uri = contents_metadata['audio_uri']
        
        image_data = self.get_data(image_uri)['Body'].read()
        self.image = Image.open(io.BytesIO(image_data))
        self.audio = self.generate_presigned_url(audio_uri)
        self.title = title
        self.processing = False
    ...


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.vstack(
            rx.heading("Kick Preview", size="9"),
            rx.skeleton(
                rx.hstack(
                    rx.flex(
                        rx.cond(
                            State.image,
                            rx.image(
                                src=State.image,
                                style={"height" : "300px", "width":"300px"}
                            ),
                            rx.flex(
                                rx.icon("image", size=26, color=rx.color("slate", 7)),
                                justify="center",
                                align="center",
                                style={"height": "300px", "width":"300px"}  # 最小の高さを設定
                            ),
                        ),                    
                    ),
                    rx.vstack(
                        rx.heading(
                            State.title,
                            size="3"
                        ),
                        rx.audio(
                            url=State.audio,
                            playing=True,
                            loop=False,
                            width="400px",
                            height="32px"
                        )
                    )
                ),
                loading=State.processing
            ),
            rx.button(
                "Generate",
                type="submit",
                on_click=State.get_contents
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
        style={
            "padding": "20px",  # 外側のパディングを追加
            "margin": "0 auto",  # 中央寄せ
            "maxWidth": "1200px"  # 最大幅を設定
        }
    )


app = rx.App()
app.add_page(index)
