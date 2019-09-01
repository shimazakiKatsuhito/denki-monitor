## usage

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


