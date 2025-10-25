# EC2 (Amazon Linux 2023) から CloudWatch にアクセスログを送る手順

目的: **EC2 のアクセスログを CloudWatch に送信する**

---

## 1. EC2 を作成

- セキュリティグループ（SG）を作成
- `.pem` キーを作成し、権限を `chmod 400` で付与しておく

---

## 2. CloudWatch へのログ送信権限を付与（IAM ロール作成）

参考: [AWS公式 Quick Start - EC2 Instance](https://docs.aws.amazon.com/ja_jp/AmazonCloudWatch/latest/logs/QuickStartEC2Instance.html)

`policies.json` の例:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 3. EC2 に SSH 接続

- 作成した `.pem` キーを用いて接続

---

## 4. EC2 内で必要な設定を行う

参考: [CloudWatch Agent のインストール手順](https://docs.aws.amazon.com/ja_jp/AmazonCloudWatch/latest/monitoring/download-CloudWatch-Agent-on-EC2-Instance-commandline-first.html)

### rsyslog の導入と設定

```bash
# rsyslog をインストール
sudo dnf install rsyslog
sudo systemctl enable --now rsyslog

# 出力ファイル指定
echo 'auth,authpriv.* /var/log/secure' | sudo tee /etc/rsyslog.d/10-sshd.conf

# ファイル内容確認
cat /etc/rsyslog.d/10-sshd.conf

# rsyslog 再起動
sudo systemctl restart rsyslog
```

### CloudWatch Agent の導入

```bash
# エージェントをインストール
sudo dnf install amazon-cloudwatch-agent

# 設定ウィザードを実行
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

※ ウィザード回答時の注意:

- **root ユーザーとして操作すること**
- **監視対象に files を追加すること**

### 設定ファイル確認

```bash
cat /opt/aws/amazon-cloudwatch-agent/bin/config.json
```

### CloudWatch Agent の起動

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json -s
```

---

## 5. 動作確認

### EC2 側でのログ確認

```bash
sudo tail -n 100 /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log
```

### CloudWatch 側でのログ確認

- AWS マネジメントコンソール → **CloudWatch → ロググループ** から確認

---

👉 この流れで EC2 の `/var/log/secure` のログが CloudWatch に送信されます。
