### Certificate management
#### confluent CA
```
> openssl s_client -connect pkc-09zmdp.us-east-1.aws.confluent.cloud:9092 -showcerts </dev/null \
  | openssl x509 -noout -subject -issuer -fingerprint -sha256

depth=2 C = US, O = Internet Security Research Group, CN = ISRG Root X1
verify return:1
depth=1 C = US, O = Let's Encrypt, CN = R12
verify return:1
depth=0 CN = *.us-east-1.aws.confluent.cloud
verify return:1
DONE
subject=CN = *.us-east-1.aws.confluent.cloud
issuer=C = US, O = Let's Encrypt, CN = R12
SHA256 Fingerprint=25:8E:16:24:5C:CB:C0:8A:C0:E6:38:F8:CF:81:78:24:7D:A3:0F:B7:7C:97:54:A1:01:1A:4A:10:72:CC:13:79
```
#### check if the JAVA default trust store has confluent CA root
```
> $JAVA_HOME/bin/keytool -list -v   -keystore /usr/lib/jvm/java-1.17.0-openjdk-amd64/lib/security/cacerts   -storepass changeit
. . .
Alias name: debian:isrg_root_x1.pem
Creation date: Feb 9, 2023
Entry type: trustedCertEntry

Owner: CN=ISRG Root X1, O=Internet Security Research Group, C=US
Issuer: CN=ISRG Root X1, O=Internet Security Research Group, C=US
Serial number: 8210cfb0d240e3594463e0bb63828b00
Valid from: Thu Jun 04 11:04:38 UTC 2015 until: Mon Jun 04 11:04:38 UTC 2035
Certificate fingerprints:
         SHA1: CA:BD:2A:79:A1:07:6A:31:F2:1D:25:36:35:CB:03:9D:43:29:A5:E8
         SHA256: 96:BC:EC:06:26:49:76:F3:74:60:77:9A:CF:28:C5:A7:CF:E8:A3:C0:AA:E1:1A:8F:FC:EE:05:C0:BD:DF:08:C6
Signature algorithm name: SHA256withRSA
Subject Public Key Algorithm: 4096-bit RSA key
Version: 3

Extensions:

#1: ObjectId: 2.5.29.19 Criticality=true
BasicConstraints:[
  CA:true
  PathLen: no limit
]

#2: ObjectId: 2.5.29.15 Criticality=true
KeyUsage [
  Key_CertSign
  Crl_Sign
]

#3: ObjectId: 2.5.29.14 Criticality=false
SubjectKeyIdentifier [
KeyIdentifier [
0000: 79 B4 59 E6 7B B6 E5 E4   01 73 80 08 88 C8 1A 58  y.Y......s.....X
0010: F6 E9 9B 6E                                        ...n
]
]
```
#### convert jks to pem
```
keytool -importkeystore -srckeystore srini-keystore.jks -destkeystore srini-keystore.p12 -srcstoretype jks -deststoretype pkcs12
Importing keystore srini-keystore.jks to srini-keystore.p12...
Enter destination keystore password:
Re-enter new password:
Enter source keystore password:
Entry for alias srini successfully imported.
Import command completed:  1 entries successfully imported, 0 entries failed or cancelled
```
#### pkcs12 to PEM - with encrypted private key "-----BEGIN ENCRYPTED PRIVATE KEY-----"
```
openssl pkcs12 -in srini-keystore.p12 -out srini-keystore.pem
Enter Import Password:
Enter PEM pass phrase:
Verifying - Enter PEM pass phrase:
```

#### pkcs12 to PEM - with non encrypted private key "-----BEGIN PRIVATE KEY-----"

```
openssl pkcs12 -nodes -in srini-keystore.p12 -out srini-keystore_notencryptedpvtkey.pem
Enter Import Password:
```

#### validate client authentication when mTLS is enabled
```
[ubuntu@jumpbox /tmp]# keytool -importkeystore -srckeystore kafka-connect-keystore.jks -destkeystore kafka-connect-keystore.p12 -srcstoretype jks -deststoretype pkcs12

[ubuntu@jumpbox /tmp]# openssl pkcs12 -nodes -in  kafka_connect-keystore.p12 -nocerts -out kafka_connect_key.pem
Enter Import Password: changeme

[ubuntu@jumpbox /tmp]# openssl pkcs12 -nodes -in  kafka_connect-keystore.p12 -nokeys -cacerts -out kafka_connect_chain.pem
Enter Import Password: changeme

[ubuntu@jumpbox /tmp]# openssl pkcs12 -nodes -in  kafka_connect-keystore.p12 -nokeys -clcerts -out kafka_connect_cert.pem
Enter Import Password:

[ubuntu@jumpbox /tmp]# openssl s_client -connect ip-172-32-52-37.us-west-2.compute.internal:8083 -key kafka_connect_key.pem -cert kafka_connect_cert.pem -CAfile kafka_connect_chain.pem -state -debug
```

#### Debug a ssl3 alert bad cert when mTLS is enabled  (https://confluent.zendesk.com/agent/tickets/146881)
Get the private.crt and root.crt from the JKS to PEM conversions approach above
```
[ubuntu@jumpbox /tmp]# openssl s_client -connect ip-172-32-52-37.us-west-2.compute.internal:8083 -key private.crt -CAfile root.crt -state -debug
. . .
SSL3 alert read:fatal:bad certificate
140164300694848:error:14094412:SSL routines:ssl3_read_bytes:sslv3 alert bad certificate:../ssl/record/rec_layer_s3.c:1543:SSL alert number 42
read from 0x55e5b5695460 [0x55e5b568bfa0] (8192 bytes => 0 (0x0))
```
