# my-kick-preview-front

## Run Application

1. rye install
2. run `rye sync`
3. add .env
4. set AWS_ACCESS_KEY, AWS_SECRET_KEY, HOST_ADDRESS environment
5. run `rye run reflex run`

## DNS A Record Update

サービスをローカルで動かすときの便利スクリプト

1. LightsailのDNSサービスの設定を変更できる`update_grobal_ip.sh`を作った
2. IAMで適切な権限を設定したポリシーを作ってアタッチする
3. MY_DOMAINの環境変数を設定
4. crontabで動かせばOK
