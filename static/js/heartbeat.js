function checkServer() {
    serverUrl="http://192.168.0.101:8888/heartbeat", //ハートビートエンドポイント
    fetch(serverUrl)
        .then(response => {
            if (response.ok) {
                console.log("Server is up.");
                if (window.serverDown) {
                    window.location.reload();
                }
                window.serverDown = false;
            } else {
                throw new Error('Server not responding properly');
            }
        })
        .catch(error => {
	    if (!window.sererDown) {
           	console.log("Server is down.", error.message);
	    }
            window.serverDown = true;
        })
        .finally(() => {
            setTimeout(() => checkServer(serverUrl), 5000); // 5秒後に再度チェック
        });
}

window.serverDown = false; // グローバル状態を初期化
checkServer(); // 設定の読み込みと初回のサーバーチェックを開始
