# Apple Wallet pass: your 5-minute part

I already made the private key and the signing request, so you don't need Keychain Access or a .p12 export.
The request is `certs/pass.csr`, and its key stays in `certs/pass.key`. That folder is git-ignored and never leaves this Mac.

1. Open https://developer.apple.com/account/resources/identifiers/list/passTypeId and sign in.
2. Click **+** (next to "Identifiers"), choose **Pass Type IDs**, then **Continue**.
3. Description: `Ari Nakos card`. Identifier: `pass.com.arinakos.card`. Click **Continue**, then **Register**.
4. Click the new `pass.com.arinakos.card` row, then **Create Certificate**.
   (If it asks for a name, use `Ari Nakos card`.)
5. When it asks for a Certificate Signing Request, upload
   `~/Documents/personal-biz-card/certs/pass.csr` and click **Continue**.
6. Click **Download**. You get `pass.cer`. Move it into `~/Documents/personal-biz-card/certs/`.
7. Tell me "cert is in". I'll read your Team ID from the certificate and build the pass.

Expires: Pass Type ID certificates last about a year. Passes you've already added keep working after it expires.
You only need a new certificate to rebuild the pass.
