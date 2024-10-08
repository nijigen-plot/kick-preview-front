"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import os
import io
import base64
import urllib.parse
import random

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
    twitter_url = ""
    push_text = ""
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
        link = contents_metadata['link']
        
        image_data = self.get_data(image_uri)['Body'].read()
        self.image = Image.open(io.BytesIO(image_data))
        self.audio = self.generate_presigned_url(audio_uri)
        self.title = title
        self.processing = False
        self.twitter_url = (
                f"https://twitter.com/intent/tweet?"
                f"text=今日のキックはコレ🔊%0A"
                f"{urllib.parse.quote(self.title)}"
                f"&url={urllib.parse.quote(link)}"
                f"&hashtags=kick_preview"
            )
        texts = [
            "Keep it up!",
            "Push it!",
            "Keep pressing!",
            "Just one more!",
            "You’re on fire!",
            "Don’t stop now!",
            "Keep going!"
        ]
        self.push_text = random.choice(texts)

def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.vstack(
            rx.image(
                src="images/kp1.png",
                style={
                    "mix-blend-mode": "difference",
                    "max-height": "100%"
                }
            ),
        rx.box(style={"height": "4vh",}),
            rx.skeleton(
                rx.cond(
                    State.image,
                    rx.flex(
                        rx.text(
                                State.push_text,
                                color_scheme="yellow"
                            ),
                        rx.button(
                            rx.image(
                                src=State.image,
                            ),
                            type="submit",
                            on_click=State.get_contents,
                            color_scheme="yellow",
                            style={
                                "background-color": "transparent", # 元のボタンは透明化
                                "justify-content": "center",    
                                "align-items": "center",        
                                "height": "330px",              
                                "width": "500px",               
                                "margin": "0 auto",             
                                "max-width": "100%",            
                                "max-height": "100%",
                                "transition": "all 0.1s ease",
                            },
                            _active={  # ボタンが押されたときのスタイル
                                "transform": "scale(0.95)",  # 少し縮小する
                                "position": "relative",  # ボタンがずれないようにする
                                "top": "2px",  # 押された感を出すため少し下にずれる
                            }
                        ),
                        style={
                            "flexDirection": "column",      # 縦積み
                            "justify-content": "center",    # 水平方向の中央揃え
                            "align-items": "center",        # 垂直方向の中央揃え
                            "height": "340px",              # 確保するスペースの高さ
                            "width": "500px",               # 確保するスペースの幅
                            "margin": "0 auto",             # 中央寄せ
                            "max-width": "100%",            # 溢れる場合縮小
                            "max-height": "100%",           # 溢れる場合縮小
                        }
                    ),
                    rx.flex(
                        rx.button(
                            rx.image(
                                src="images/yellow_button.png"
                            ),
                            type="submit",
                            on_click=State.get_contents,
                            color_scheme="yellow",
                            style={
                                "background-color": "transparent", # 元のボタンは透明化
                                "justify-content": "center",    
                                "align-items": "center",        
                                "height": "500px",              
                                "width": "500px",               
                                "margin": "0 auto",             
                                "max-width": "110%",            
                                "max-height": "100%",
                                "transition": "all 0.1s ease",
                            },
                            _active={  # ボタンが押されたときのスタイル
                                "transform": "scale(0.95)",  # 少し縮小する
                                "position": "relative",  # ボタンがずれないようにする
                                "top": "2px",  # 押された感を出すため少し下にずれる
                            }
                        ),
                        style={
                            "justify-content": "center",    # 水平方向の中央揃え
                            "align-items": "center",        # 垂直方向の中央揃え
                            "height": "330px",              # 確保するスペースの高さ
                            "width": "500px",               # 確保するスペースの幅
                            "margin": "0 auto",             # 中央寄せ
                            "max-width": "100%",            # 溢れる場合縮小
                            "max-height": "100%",           # 溢れる場合縮小
                        }
                    ),
                ),
                loading=State.processing
            ),
            rx.flex(
                rx.vstack(
                    rx.heading(
                        State.title,
                        size="7",
                        align="center",
                        style={
                            "max-width": "100%",
                            "text-align":"center",
                            "margin": "0 auto"
                        }
                    ),
                    rx.audio(
                        url=State.audio,
                        playing=True,
                        loop=False,
                        controls=False,
                        width="100px",
                        style={
                            "display": "none"
                        }
                    )
                ),
                style={
                    "display": "flex",
                    "flex-direction": "column",
                    "justify-content": "center",
                    "align-items": "center",
                    "width": "100%",
                    "text-align": "center"
                }
            )
        ),
        rx.flex(
            rx.box(style={"height": "4vh",}),
            rx.cond(
                State.image,
                rx.link(
                    rx.button(
                        rx.icon("twitter", size=80),
                        style={
                            "width":"50px",
                            "height":"50px"
                        }
                    ),
                    href=State.twitter_url,
                    is_external=True,
                ),
                rx.text()
            ),
            style={
                "display": "flex",
                "flex-direction": "column",
                "justify-content": "center",
                "align-items": "center",
                "width": "100%",
                "text-align": "center" 
            }         
        ),
        rx.logo(),
        style={
            "overflow-x": "hidden" # これ入れるとiphoneで見たときに右に変な余白無くなる
        },
        width="100%"
    )


app = rx.App()
app.add_page(index)
