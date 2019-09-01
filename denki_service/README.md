## Description

電気使用量の記録、および、Webシステムを自動起動するための設定  
systemdにサービスとして登録し、ラズパイ起動時に自動起動します。

- denkidb : スマートメーターから毎分電気使用量を取得し、DBに記録するサービス
- denkiweb : Webブラウザからのリクエストに対し、電気使用量をグラフ化して応答するサービス

## Usage

- 下記のservice設定ファイルをsystemdフォルダへ配置する  
   sudo cp denkidb.service /etc/systemd/system/denkidb.service  
   sudo cp denkiweb.service /etc/systemd/system/denkiweb.service  

- systemctlのサービス情報の更新  
   sudo systemctl deamon-reload

- サービスの起動  
   sudo systemctl start denkidb.service  
   sudo systemctl start denkiweb.service  

- サービスの自動起動登録  
   sudo systemctl enable denkidb.service  
   sudo systemctl enable denkiweb.service  


